"""
Integration Tests for End-to-End Inference Pipeline
Tests complete CSV → predictions workflow with real model
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.inference import load_model, predict_device, predict_batch
from utils.preprocessing import REQUIRED_FEATURES, TRAINING_FEATURE_ORDER, prepare_for_prediction


class TestRealModelPipeline:
    """Integration tests using the actual production model"""
    
    @pytest.fixture(scope="class")
    def model_path(self):
        """Path to production model"""
        base_dir = Path(__file__).parent.parent
        return base_dir / "models" / "catboost_pipeline_v1_20251107.pkl"
    
    @pytest.fixture(scope="class")
    def test_data_path(self):
        """Path to test set CSV"""
        base_dir = Path(__file__).parent.parent
        return base_dir / "data" / "device_features_test_stratified.csv"
    
    @pytest.fixture(scope="class")
    def loaded_pipeline(self, model_path):
        """Load the actual production pipeline (cached for class)"""
        if not model_path.exists():
            pytest.skip(f"Model file not found: {model_path}")
        return load_model(str(model_path))
    
    @pytest.fixture(scope="class")
    def test_dataset(self, test_data_path):
        """Load test set (cached for class)"""
        if not test_data_path.exists():
            pytest.skip(f"Test data not found: {test_data_path}")
        
        df = pd.read_csv(test_data_path)
        return df
    
    def test_model_loads_successfully(self, model_path, loaded_pipeline):
        """Test that production model loads without errors"""
        assert loaded_pipeline is not None
        assert hasattr(loaded_pipeline, 'predict')
        assert hasattr(loaded_pipeline, 'predict_proba')
    
    def test_pipeline_has_correct_steps(self, loaded_pipeline):
        """Test that pipeline contains expected steps (SimpleImputer, SMOTE, CatBoost)"""
        assert hasattr(loaded_pipeline, 'named_steps')
        
        # Expected steps
        steps = loaded_pipeline.named_steps
        assert 'simpleimputer' in steps or 'imputer' in steps, "Missing imputer step"
        assert 'smote' in steps, "Missing SMOTE step"
        assert 'catboostclassifier' in steps or 'classifier' in steps, "Missing classifier step"
    
    @pytest.mark.integration
    def test_test_set_reproduction(self, loaded_pipeline, test_dataset):
        """
        Test that model reproduces expected performance on test set
        Expected: 11/14 critical devices detected (78.6% recall)
        """
        # Extract features in TRAINING ORDER (critical!)
        X_test = test_dataset[TRAINING_FEATURE_ORDER]
        y_test = test_dataset['is_critical_target']
        
        # Make predictions
        y_pred = loaded_pipeline.predict(X_test)
        
        # Calculate metrics
        from sklearn.metrics import recall_score, precision_score, confusion_matrix
        
        recall = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        
        tn, fp, fn, tp = cm.ravel()
        
        # Assertions with tolerance (±2% for recall/precision)
        assert 0.76 <= recall <= 0.81, f"Recall {recall:.2%} outside expected range [76%, 81%]"
        assert 0.82 <= precision <= 0.87, f"Precision {precision:.2%} outside expected range [82%, 87%]"
        
        # Expected ~11 critical detected out of 14 total (±1)
        assert 10 <= tp <= 12, f"True Positives {tp} outside expected range [10, 12]"
        
        print(f"\n✅ Test set metrics: Recall={recall:.2%}, Precision={precision:.2%}, TP={tp}/14")
    
    @pytest.mark.integration
    def test_single_device_prediction(self, loaded_pipeline, test_dataset):
        """Test predict_device function with single device from test set"""
        # Get first device features in TRAINING ORDER
        first_device = test_dataset.iloc[0][TRAINING_FEATURE_ORDER].to_dict()
        
        # Predict
        result = predict_device(first_device, loaded_pipeline)
        
        # Validate result structure
        assert 'prediction' in result
        assert 'probability' in result
        assert 'risk_level' in result
        assert 'verdict' in result
        
        # Validate types and ranges
        assert isinstance(result['prediction'], int)
        assert result['prediction'] in [0, 1]
        assert isinstance(result['probability'], float)
        assert 0.0 <= result['probability'] <= 1.0
        assert result['risk_level'] in ['Low', 'Medium', 'High']
        assert result['verdict'] in ['NORMAL', 'CRITICAL']
    
    @pytest.mark.integration
    def test_batch_prediction(self, loaded_pipeline, test_dataset):
        """Test predict_batch function with multiple devices"""
        # Use first 50 devices in TRAINING ORDER
        batch_df = test_dataset.head(50)[TRAINING_FEATURE_ORDER].copy()
        
        # Predict batch
        result_df = predict_batch(batch_df, loaded_pipeline)
        
        # Validate result structure
        assert 'prediction' in result_df.columns
        assert 'probability' in result_df.columns
        assert 'risk_level' in result_df.columns
        assert 'verdict' in result_df.columns
        
        # Validate all predictions
        assert len(result_df) == 50
        assert all(result_df['prediction'].isin([0, 1]))
        assert all((result_df['probability'] >= 0) & (result_df['probability'] <= 1))
        assert all(result_df['risk_level'].isin(['Low', 'Medium', 'High']))
        assert all(result_df['verdict'].isin(['NORMAL', 'CRITICAL']))


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create mock pipeline for edge case testing"""
        from unittest.mock import MagicMock
        
        pipeline = MagicMock()
        pipeline.predict = MagicMock(return_value=np.array([0, 1, 0]))
        pipeline.predict_proba = MagicMock(return_value=np.array([[0.8, 0.2], [0.3, 0.7], [0.9, 0.1]]))
        
        return pipeline
    
    def test_missing_values_handling(self, mock_pipeline):
        """Test that pipeline handles missing values (>50% NaN)"""
        # Create DataFrame with 60% missing values
        data = {}
        for feature in REQUIRED_FEATURES:
            values = np.random.randn(10)
            mask = np.random.choice([True, False], 10, p=[0.6, 0.4])  # 60% missing
            values[mask] = np.nan
            data[feature] = values
        
        df = pd.DataFrame(data)
        
        # Ajustar mock para retornar o número correto de predições
        mock_pipeline.predict = MagicMock(return_value=np.random.randint(0, 2, 10))
        probs = np.random.uniform(0, 1, 10)
        mock_pipeline.predict_proba = MagicMock(return_value=np.column_stack([1 - probs, probs]))
        
        # Should not raise error (pipeline has SimpleImputer)
        try:
            result = predict_batch(df, mock_pipeline)
            assert len(result) == 10
            assert 'prediction' in result.columns
        except Exception as e:
            pytest.fail(f"Pipeline should handle missing values, but raised: {e}")
    
    def test_outliers_handling(self, mock_pipeline):
        """Test handling of extreme outliers (3σ)"""
        # Create DataFrame with extreme outliers
        data = {}
        for feature in REQUIRED_FEATURES:
            values = np.random.randn(10)
            values[0] = 10.0  # 3σ outlier (mean=0, std=1)
            values[1] = -10.0  # -3σ outlier
            data[feature] = values
        
        df = pd.DataFrame(data)
        
        # Ajustar mock para retornar o número correto de predições
        mock_pipeline.predict = MagicMock(return_value=np.random.randint(0, 2, 10))
        probs = np.random.uniform(0, 1, 10)
        mock_pipeline.predict_proba = MagicMock(return_value=np.column_stack([1 - probs, probs]))
        
        # Should not raise error
        try:
            result = predict_batch(df, mock_pipeline)
            assert len(result) == 10
        except Exception as e:
            pytest.fail(f"Pipeline should handle outliers, but raised: {e}")
    
    def test_empty_dataframe(self, mock_pipeline):
        """Test graceful handling of empty DataFrame"""
        df_empty = pd.DataFrame(columns=REQUIRED_FEATURES)
        
        # Mock pipeline to handle empty input
        mock_pipeline.predict = MagicMock(return_value=np.array([]))
        mock_pipeline.predict_proba = MagicMock(return_value=np.array([]).reshape(0, 2))
        
        try:
            result = predict_batch(df_empty, mock_pipeline)
            assert len(result) == 0
        except Exception as e:
            pytest.fail(f"Should handle empty DataFrame gracefully, but raised: {e}")
    
    def test_single_device_all_nan(self):
        """Test single device prediction with all NaN features"""
        # Create device with all NaN
        device_nan = {feature: np.nan for feature in REQUIRED_FEATURES}
        
        # This should work with imputer (will replace with median)
        # We just test it doesn't crash - actual prediction depends on model
        mock_pipeline = MagicMock()
        mock_pipeline.predict = MagicMock(return_value=np.array([0]))
        mock_pipeline.predict_proba = MagicMock(return_value=np.array([[0.7, 0.3]]))
        
        try:
            result = predict_device(device_nan, mock_pipeline)
            assert 'prediction' in result
        except Exception as e:
            pytest.fail(f"Should handle all-NaN device, but raised: {e}")


class TestProbabilityRanges:
    """Test that probabilities are in valid ranges"""
    
    @pytest.fixture
    def sample_features_df(self):
        """Create sample features DataFrame"""
        np.random.seed(42)
        data = {feature: np.random.randn(20) for feature in REQUIRED_FEATURES}
        return pd.DataFrame(data)
    
    def test_probabilities_in_range(self, sample_features_df):
        """Test that all probabilities are between 0 and 1"""
        # Mock pipeline with random probabilities
        mock_pipeline = MagicMock()
        mock_pipeline.predict = MagicMock(return_value=np.random.randint(0, 2, 20))
        
        # Generate valid probabilities
        probs = np.random.uniform(0, 1, 20)
        probs_2d = np.column_stack([1 - probs, probs])
        mock_pipeline.predict_proba = MagicMock(return_value=probs_2d)
        
        result = predict_batch(sample_features_df, mock_pipeline)
        
        # All probabilities must be in [0, 1]
        assert all(result['probability'] >= 0.0)
        assert all(result['probability'] <= 1.0)
    
    def test_predictions_binary(self, sample_features_df):
        """Test that all predictions are binary (0 or 1)"""
        mock_pipeline = MagicMock()
        mock_pipeline.predict = MagicMock(return_value=np.random.randint(0, 2, 20))
        mock_pipeline.predict_proba = MagicMock(
            return_value=np.column_stack([np.random.uniform(0, 1, 20), np.random.uniform(0, 1, 20)])
        )
        
        result = predict_batch(sample_features_df, mock_pipeline)
        
        # All predictions must be 0 or 1
        assert all(result['prediction'].isin([0, 1]))
    
    def test_risk_level_consistency(self, sample_features_df):
        """Test that risk levels are consistent with probabilities"""
        # Mock with specific probabilities
        mock_pipeline = MagicMock()
        mock_pipeline.predict = MagicMock(return_value=np.array([0, 0, 1, 1]))
        
        # Low (0.1), Medium (0.5), High (0.8), High (0.95)
        probs = np.array([0.1, 0.5, 0.8, 0.95])
        probs_2d = np.column_stack([1 - probs, probs])
        mock_pipeline.predict_proba = MagicMock(return_value=probs_2d)
        
        result = predict_batch(sample_features_df.head(4), mock_pipeline)
        
        # Check risk levels match probabilities
        assert result.iloc[0]['risk_level'] == 'Low'  # prob=0.1 < 0.3
        assert result.iloc[1]['risk_level'] == 'Medium'  # 0.3 <= prob=0.5 < 0.7
        assert result.iloc[2]['risk_level'] == 'High'  # prob=0.8 >= 0.7
        assert result.iloc[3]['risk_level'] == 'High'  # prob=0.95 >= 0.7


@pytest.mark.slow
class TestPerformance:
    """Performance tests for batch prediction"""
    
    def test_batch_prediction_performance(self):
        """Test that batch prediction completes in reasonable time"""
        import time
        
        # Create large batch (1000 devices)
        np.random.seed(42)
        data = {feature: np.random.randn(1000) for feature in REQUIRED_FEATURES}
        large_batch = pd.DataFrame(data)
        
        # Mock pipeline (fast prediction)
        mock_pipeline = MagicMock()
        mock_pipeline.predict = MagicMock(return_value=np.random.randint(0, 2, 1000))
        probs = np.random.uniform(0, 1, 1000)
        mock_pipeline.predict_proba = MagicMock(return_value=np.column_stack([1 - probs, probs]))
        
        # Measure time
        start = time.time()
        result = predict_batch(large_batch, mock_pipeline)
        elapsed = time.time() - start
        
        # Should complete in < 1 second for mock (real model ~2-5s acceptable)
        assert elapsed < 5.0, f"Batch prediction took {elapsed:.2f}s (too slow)"
        assert len(result) == 1000
        
        print(f"\n✅ Batch prediction (1000 devices): {elapsed:.3f}s")
