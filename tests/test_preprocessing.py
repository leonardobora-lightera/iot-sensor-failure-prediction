"""
Unit Tests for utils/preprocessing.py
Tests feature validation, type checking, missing value handling
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.preprocessing import (
    REQUIRED_FEATURES,
    validate_features,
    check_feature_types,
    get_missing_stats,
    prepare_for_prediction
)


class TestRequiredFeatures:
    """Test REQUIRED_FEATURES constant"""
    
    def test_required_features_count(self):
        """Test that we have exactly 29 features"""
        assert len(REQUIRED_FEATURES) == 29
    
    def test_required_features_no_duplicates(self):
        """Test that all feature names are unique"""
        assert len(REQUIRED_FEATURES) == len(set(REQUIRED_FEATURES))
    
    def test_required_features_categories(self):
        """Test feature categories are present"""
        # Telemetry features
        optical_features = [f for f in REQUIRED_FEATURES if 'optical' in f]
        temp_features = [f for f in REQUIRED_FEATURES if 'temp' in f]
        battery_features = [f for f in REQUIRED_FEATURES if 'battery' in f]
        
        # Connectivity features
        snr_features = [f for f in REQUIRED_FEATURES if 'snr' in f]
        rsrp_features = [f for f in REQUIRED_FEATURES if 'rsrp' in f]
        rsrq_features = [f for f in REQUIRED_FEATURES if 'rsrq' in f]
        
        # Messaging features
        assert 'total_messages' in REQUIRED_FEATURES
        assert 'max_frame_count' in REQUIRED_FEATURES
        
        # Verify counts
        assert len(optical_features) == 7
        assert len(temp_features) == 6
        assert len(battery_features) == 5
        assert len(snr_features) == 3
        assert len(rsrp_features) == 3
        assert len(rsrq_features) == 3


class TestValidateFeatures:
    """Test suite for validate_features function"""
    
    @pytest.fixture
    def complete_df(self):
        """Create DataFrame with all required features"""
        data = {feature: np.random.randn(10) for feature in REQUIRED_FEATURES}
        return pd.DataFrame(data)
    
    @pytest.fixture
    def incomplete_df(self):
        """Create DataFrame missing some features"""
        # Only include first 20 features (missing 9)
        data = {feature: np.random.randn(10) for feature in REQUIRED_FEATURES[:20]}
        return pd.DataFrame(data)
    
    def test_validate_features_complete(self, complete_df):
        """Test validation passes with all features"""
        with patch('utils.preprocessing.st.error'):  # Mock streamlit
            is_valid, missing = validate_features(complete_df, show_warnings=False)
            
            assert is_valid is True
            assert len(missing) == 0
    
    def test_validate_features_incomplete(self, incomplete_df):
        """Test validation fails with missing features"""
        with patch('utils.preprocessing.st.error'):  # Mock streamlit
            is_valid, missing = validate_features(incomplete_df, show_warnings=False)
            
            assert is_valid is False
            assert len(missing) == 9  # Missing 9 features
    
    def test_validate_features_extra_columns(self, complete_df):
        """Test validation passes even with extra columns"""
        # Add extra columns
        complete_df['device_id'] = ['DEV_' + str(i) for i in range(10)]
        complete_df['extra_column'] = np.random.randn(10)
        
        with patch('utils.preprocessing.st.error'):
            is_valid, missing = validate_features(complete_df, show_warnings=False)
            
            assert is_valid is True
    
    def test_validate_features_returns_correct_missing_list(self, incomplete_df):
        """Test that missing features list is accurate"""
        with patch('utils.preprocessing.st.error'):
            is_valid, missing = validate_features(incomplete_df, show_warnings=False)
            
            expected_missing = set(REQUIRED_FEATURES[20:])  # Last 9 features
            assert set(missing) == expected_missing


class TestCheckFeatureTypes:
    """Test suite for check_feature_types function"""
    
    @pytest.fixture
    def numeric_df(self):
        """Create DataFrame with numeric types"""
        data = {feature: np.random.randn(10) for feature in REQUIRED_FEATURES}
        return pd.DataFrame(data)
    
    @pytest.fixture
    def mixed_types_df(self):
        """Create DataFrame with mixed types (some strings)"""
        data = {}
        for i, feature in enumerate(REQUIRED_FEATURES):
            if i % 3 == 0:  # Every 3rd feature as string
                data[feature] = [str(x) for x in np.random.randn(10)]
            else:
                data[feature] = np.random.randn(10)
        return pd.DataFrame(data)
    
    def test_check_feature_types_already_numeric(self, numeric_df):
        """Test that numeric features remain unchanged"""
        with patch('utils.preprocessing.st.info'):  # Mock streamlit
            df_converted = check_feature_types(numeric_df, show_info=False)
            
            # Check all features are numeric
            for feature in REQUIRED_FEATURES:
                assert pd.api.types.is_numeric_dtype(df_converted[feature])
            
            # Values should be unchanged
            pd.testing.assert_frame_equal(df_converted, numeric_df)
    
    def test_check_feature_types_converts_strings(self, mixed_types_df):
        """Test that string features are converted to numeric"""
        with patch('utils.preprocessing.st.info'):  # Mock streamlit
            df_converted = check_feature_types(mixed_types_df, show_info=False)
            
            # All features should now be numeric
            for feature in REQUIRED_FEATURES:
                assert pd.api.types.is_numeric_dtype(df_converted[feature])
    
    def test_check_feature_types_handles_non_convertible(self):
        """Test handling of non-convertible strings"""
        df = pd.DataFrame({
            'optical_mean': ['abc', 'def', '1.5'],  # Mix of invalid and valid
            'battery_mean': [1.0, 2.0, 3.0]
        })
        
        with patch('utils.preprocessing.st.info'):
            df_converted = check_feature_types(df, show_info=False)
            
            # Non-convertible values should become NaN
            assert df_converted['optical_mean'].isna()[0]  # 'abc' -> NaN
            assert df_converted['optical_mean'].isna()[1]  # 'def' -> NaN
            assert df_converted['optical_mean'][2] == 1.5  # '1.5' -> 1.5
    
    def test_check_feature_types_preserves_original(self, mixed_types_df):
        """Test that function doesn't modify original DataFrame"""
        original_copy = mixed_types_df.copy()
        
        with patch('utils.preprocessing.st.info'):
            df_converted = check_feature_types(mixed_types_df, show_info=False)
        
        # Original should be unchanged
        pd.testing.assert_frame_equal(mixed_types_df, original_copy)


class TestGetMissingStats:
    """Test suite for get_missing_stats function"""
    
    @pytest.fixture
    def no_missing_df(self):
        """DataFrame with no missing values"""
        data = {feature: np.random.randn(100) for feature in REQUIRED_FEATURES}
        return pd.DataFrame(data)
    
    @pytest.fixture
    def partial_missing_df(self):
        """DataFrame with some missing values"""
        data = {}
        for i, feature in enumerate(REQUIRED_FEATURES):
            values = np.random.randn(100)
            if i < 5:  # First 5 features have 20% missing
                mask = np.random.choice([True, False], 100, p=[0.2, 0.8])
                values[mask] = np.nan
            data[feature] = values
        return pd.DataFrame(data)
    
    @pytest.fixture
    def extreme_missing_df(self):
        """DataFrame with extreme missing values (>90% in some features)"""
        data = {}
        for i, feature in enumerate(REQUIRED_FEATURES):
            values = np.random.randn(100)
            if i < 3:  # First 3 features have 95% missing
                mask = np.random.choice([True, False], 100, p=[0.95, 0.05])
                values[mask] = np.nan
            data[feature] = values
        return pd.DataFrame(data)
    
    def test_get_missing_stats_no_missing(self, no_missing_df):
        """Test stats when no missing values"""
        stats = get_missing_stats(no_missing_df)
        
        assert stats['total_missing'] == 0
        assert stats['features_with_missing'] == 0
    
    def test_get_missing_stats_partial_missing(self, partial_missing_df):
        """Test stats calculation with partial missing"""
        stats = get_missing_stats(partial_missing_df)
        
        assert stats['total_missing'] > 0
        assert stats['features_with_missing'] == 5
        assert 'by_feature' in stats
        assert isinstance(stats['by_feature'], pd.DataFrame)
    
    def test_get_missing_stats_extreme_missing(self, extreme_missing_df):
        """Test stats with extreme missing values"""
        stats = get_missing_stats(extreme_missing_df)
        
        # Check that extreme features are identified
        by_feature = stats['by_feature']
        top_missing = by_feature.head(3)
        
        # Top 3 features should have ~95% missing
        for pct in top_missing['percentage']:
            assert pct > 90.0
    
    def test_get_missing_stats_structure(self, partial_missing_df):
        """Test structure of returned stats dictionary"""
        stats = get_missing_stats(partial_missing_df)
        
        assert 'total_missing' in stats
        assert 'features_with_missing' in stats
        assert 'by_feature' in stats
        
        # by_feature should have count and percentage columns
        assert 'count' in stats['by_feature'].columns
        assert 'percentage' in stats['by_feature'].columns
        
        # Should be sorted by count descending
        counts = stats['by_feature']['count'].values
        assert all(counts[i] >= counts[i+1] for i in range(len(counts)-1))


class TestPrepareForPrediction:
    """Test suite for prepare_for_prediction function"""
    
    @pytest.fixture
    def raw_df_with_extra_cols(self):
        """DataFrame with required features + extra columns"""
        data = {feature: np.random.randn(10) for feature in REQUIRED_FEATURES}
        data['device_id'] = ['DEV_' + str(i) for i in range(10)]
        data['extra_col_1'] = np.random.randn(10)
        data['extra_col_2'] = ['A', 'B', 'C'] * 3 + ['A']
        return pd.DataFrame(data)
    
    def test_prepare_for_prediction_extracts_features(self, raw_df_with_extra_cols):
        """Test that only required features are extracted"""
        with patch('utils.preprocessing.st.info'):
            prepared_df = prepare_for_prediction(raw_df_with_extra_cols)
            
            assert len(prepared_df.columns) == 29
            assert set(prepared_df.columns) == set(REQUIRED_FEATURES)
            assert 'device_id' not in prepared_df.columns
            assert 'extra_col_1' not in prepared_df.columns
    
    def test_prepare_for_prediction_converts_types(self):
        """Test that types are converted to numeric"""
        # Create DataFrame with string numeric values
        data = {}
        for feature in REQUIRED_FEATURES:
            data[feature] = [str(x) for x in np.random.randn(10)]
        df = pd.DataFrame(data)
        
        with patch('utils.preprocessing.st.info'):
            prepared_df = prepare_for_prediction(df)
            
            # All features should be numeric
            for feature in REQUIRED_FEATURES:
                assert pd.api.types.is_numeric_dtype(prepared_df[feature])
    
    def test_prepare_for_prediction_preserves_order(self, raw_df_with_extra_cols):
        """Test that feature order matches REQUIRED_FEATURES"""
        with patch('utils.preprocessing.st.info'):
            prepared_df = prepare_for_prediction(raw_df_with_extra_cols)
            
            assert list(prepared_df.columns) == REQUIRED_FEATURES
    
    def test_prepare_for_prediction_handles_missing(self):
        """Test that missing values are preserved (imputer handles them)"""
        data = {feature: np.random.randn(10) for feature in REQUIRED_FEATURES}
        # Add missing values
        data['optical_mean'][0:3] = np.nan
        data['battery_mean'][5:8] = np.nan
        df = pd.DataFrame(data)
        
        with patch('utils.preprocessing.st.info'):
            prepared_df = prepare_for_prediction(df)
            
            # Missing values should still be present (pipeline imputes them)
            assert prepared_df['optical_mean'].isna().sum() == 3
            assert prepared_df['battery_mean'].isna().sum() == 3
    
    def test_prepare_for_prediction_doesnt_modify_original(self, raw_df_with_extra_cols):
        """Test that original DataFrame is not modified"""
        original_copy = raw_df_with_extra_cols.copy()
        
        with patch('utils.preprocessing.st.info'):
            prepared_df = prepare_for_prediction(raw_df_with_extra_cols)
        
        # Original should be unchanged
        pd.testing.assert_frame_equal(raw_df_with_extra_cols, original_copy)
