"""
Unit Tests for utils/model_loader.py
Tests model and metadata loading with error handling
"""
import pytest
import json
import joblib
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.model_loader import load_pipeline, load_metadata


class TestLoadPipeline:
    """Test suite for load_pipeline function"""
    
    def test_load_pipeline_success(self, tmp_path):
        """Test successful model loading"""
        # Create a simple pickleable object (dict with named_steps)
        simple_pipeline = {'named_steps': {'imputer': 'SimpleImputer', 'smote': 'SMOTE', 'classifier': 'CatBoost'}}
        model_path = tmp_path / "test_model.pkl"
        joblib.dump(simple_pipeline, model_path)
        
        # Mock streamlit cache decorator to make it a no-op
        with patch('utils.model_loader.st.cache_resource', lambda x: x):
            pipeline = load_pipeline(str(model_path))
            
            assert pipeline is not None
            assert 'named_steps' in pipeline
            assert pipeline['named_steps']['imputer'] == 'SimpleImputer'
    
    def test_load_pipeline_file_not_found(self):
        """Test FileNotFoundError when model doesn't exist"""
        non_existent_path = "non_existent_model.pkl"
        
        with patch('utils.model_loader.st.cache_resource', lambda x: x):
            with patch('utils.model_loader.st.error'):  # Mock streamlit error
                with pytest.raises(FileNotFoundError):
                    load_pipeline(non_existent_path)
    
    def test_load_pipeline_default_path(self):
        """Test loading with default path"""
        # Mock the default model path to exist
        simple_pipeline = {'named_steps': {'imputer': 'SimpleImputer', 'smote': 'SMOTE', 'classifier': 'CatBoost'}}
        
        with patch('utils.model_loader.st.cache_resource', lambda x: x):
            with patch('utils.model_loader.Path') as mock_path:
                with patch('utils.model_loader.joblib.load', return_value=simple_pipeline):
                    pipeline = load_pipeline()
                    
                    assert pipeline is not None
                    assert 'named_steps' in pipeline
    
    def test_load_pipeline_corrupted_file(self, tmp_path):
        """Test error handling for corrupted pickle file"""
        # Create corrupted file
        corrupted_path = tmp_path / "corrupted.pkl"
        with open(corrupted_path, 'w') as f:
            f.write("This is not a valid pickle file")
        
        with patch('utils.model_loader.st.cache_resource', lambda x: x):
            with patch('utils.model_loader.st.error'):  # Mock streamlit error
                with pytest.raises(Exception):
                    load_pipeline(str(corrupted_path))


class TestLoadMetadata:
    """Test suite for load_metadata function"""
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata dictionary"""
        return {
            "model_type": "CatBoost",
            "smote_strategy": 0.5,
            "features": ["optical_mean", "battery_mean", "snr_mean"],
            "performance": {
                "recall": 0.786,
                "precision": 0.846,
                "f1_score": 0.815
            },
            "feature_importance_top5": [
                {"feature": "max_frame_count", "importance": 51.8},
                {"feature": "total_messages", "importance": 11.7}
            ]
        }
    
    @pytest.fixture
    def temp_metadata_file(self, tmp_path, sample_metadata):
        """Create temporary metadata JSON file"""
        metadata_path = tmp_path / "test_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(sample_metadata, f)
        return str(metadata_path)
    
    def test_load_metadata_success(self, temp_metadata_file, sample_metadata):
        """Test successful metadata loading"""
        with patch('utils.model_loader.st.cache_resource', lambda x: x):
            metadata = load_metadata(temp_metadata_file)
            
            assert metadata is not None
            assert metadata["model_type"] == "CatBoost"
            assert metadata["smote_strategy"] == 0.5
            assert "performance" in metadata
            assert metadata["performance"]["recall"] == 0.786
    
    def test_load_metadata_file_not_found(self):
        """Test graceful handling when metadata file doesn't exist"""
        non_existent_path = "non_existent_metadata.json"
        
        with patch('utils.model_loader.st.cache_resource', lambda x: x):
            with patch('utils.model_loader.st.warning'):  # Mock streamlit warning
                metadata = load_metadata(non_existent_path)
                
                # Should return empty dict instead of raising
                assert metadata == {}
    
    def test_load_metadata_default_path(self, sample_metadata):
        """Test loading metadata with default path"""
        with patch('utils.model_loader.st.cache_resource', lambda x: x):
            with patch('utils.model_loader.Path'):
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(sample_metadata)
                    with patch('json.load', return_value=sample_metadata):
                        metadata = load_metadata()
                        
                        assert metadata is not None
                        assert "model_type" in metadata
    
    def test_load_metadata_invalid_json(self, tmp_path):
        """Test error handling for invalid JSON"""
        invalid_path = tmp_path / "invalid.json"
        with open(invalid_path, 'w') as f:
            f.write("This is not valid JSON {{{")
        
        with patch('utils.model_loader.st.cache_resource', lambda x: x):
            with patch('utils.model_loader.st.warning'):  # Mock streamlit warning
                metadata = load_metadata(str(invalid_path))
                
                # Should return empty dict gracefully
                assert metadata == {}
    
    def test_load_metadata_feature_importance_format(self, temp_metadata_file):
        """Test that feature_importance_top5 is correctly formatted"""
        with patch('utils.model_loader.st.cache_resource', lambda x: x):
            metadata = load_metadata(temp_metadata_file)
            
            assert "feature_importance_top5" in metadata
            assert isinstance(metadata["feature_importance_top5"], list)
            assert len(metadata["feature_importance_top5"]) == 2
            assert "feature" in metadata["feature_importance_top5"][0]
            assert "importance" in metadata["feature_importance_top5"][0]
