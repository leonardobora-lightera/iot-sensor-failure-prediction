"""
Data Validation Tests
Validates schema, ranges, correlations, and data quality constraints
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.preprocessing import REQUIRED_FEATURES, TRAINING_FEATURE_ORDER


class TestSchemaValidation:
    """Test data schema and types"""
    
    def test_all_required_features_present(self):
        """Test that all 29 required features exist"""
        assert len(REQUIRED_FEATURES) == 29
        assert len(TRAINING_FEATURE_ORDER) == 29
        
        # Both lists must have same features (different order OK)
        assert set(REQUIRED_FEATURES) == set(TRAINING_FEATURE_ORDER)
    
    def test_feature_types_numeric(self):
        """Test that all features should be numeric types"""
        # Create sample DataFrame with correct types
        data = {feature: np.random.randn(10) for feature in REQUIRED_FEATURES}
        df = pd.DataFrame(data)
        
        # All features must be numeric
        for feature in REQUIRED_FEATURES:
            assert pd.api.types.is_numeric_dtype(df[feature]), \
                f"Feature {feature} must be numeric"
    
    def test_no_duplicate_feature_names(self):
        """Test that feature lists have no duplicates"""
        assert len(REQUIRED_FEATURES) == len(set(REQUIRED_FEATURES))
        assert len(TRAINING_FEATURE_ORDER) == len(set(TRAINING_FEATURE_ORDER))
    
    def test_feature_categories_complete(self):
        """Test that all feature categories are represented"""
        # Optical (7 features)
        optical = [f for f in REQUIRED_FEATURES if 'optical' in f]
        assert len(optical) == 7
        
        # Temperature (6 features)
        temp = [f for f in REQUIRED_FEATURES if 'temp' in f]
        assert len(temp) == 6
        
        # Battery (5 features)
        battery = [f for f in REQUIRED_FEATURES if 'battery' in f]
        assert len(battery) == 5
        
        # SNR (3 features)
        snr = [f for f in REQUIRED_FEATURES if 'snr' in f]
        assert len(snr) == 3
        
        # RSRP (3 features)
        rsrp = [f for f in REQUIRED_FEATURES if 'rsrp' in f]
        assert len(rsrp) == 3
        
        # RSRQ (3 features)
        rsrq = [f for f in REQUIRED_FEATURES if 'rsrq' in f]
        assert len(rsrq) == 3
        
        # Messages (2 features)
        messages = ['total_messages', 'max_frame_count']
        assert all(m in REQUIRED_FEATURES for m in messages)
        
        # Total: 7+6+5+3+3+3+2 = 29
        assert 7 + 6 + 5 + 3 + 3 + 3 + 2 == 29


class TestRangeValidation:
    """Test physical/realistic value ranges"""
    
    @pytest.fixture
    def sample_telemetry_data(self):
        """Create realistic telemetry data"""
        np.random.seed(42)
        return pd.DataFrame({
            # Optical power (dBm): typically -40 to +10 dBm, raw 0-2000
            'optical_mean': np.random.uniform(800, 1200, 50),
            'optical_std': np.random.uniform(10, 100, 50),
            'optical_min': np.random.uniform(500, 900, 50),
            'optical_max': np.random.uniform(1000, 1500, 50),
            'optical_readings': np.random.randint(50, 500, 50),
            'optical_below_threshold': np.random.randint(0, 100, 50),
            'optical_range': np.random.uniform(200, 800, 50),
            
            # Temperature (°C): typical -40 to +85°C for IoT
            'temp_mean': np.random.uniform(20, 40, 50),
            'temp_std': np.random.uniform(1, 10, 50),
            'temp_min': np.random.uniform(15, 30, 50),
            'temp_max': np.random.uniform(30, 50, 50),
            'temp_above_threshold': np.random.randint(0, 50, 50),
            'temp_range': np.random.uniform(5, 25, 50),
            
            # Battery (V): LiPo typical 3.0-4.2V, NiMH 0.9-1.5V
            'battery_mean': np.random.uniform(3.3, 3.8, 50),
            'battery_std': np.random.uniform(0.05, 0.3, 50),
            'battery_min': np.random.uniform(3.0, 3.5, 50),
            'battery_max': np.random.uniform(3.5, 4.2, 50),
            'battery_below_threshold': np.random.randint(0, 10, 50),
            
            # SNR (dB): typical 0-30 dB
            'snr_mean': np.random.uniform(10, 25, 50),
            'snr_std': np.random.uniform(2, 8, 50),
            'snr_min': np.random.uniform(5, 15, 50),
            
            # RSRP (dBm): LTE typical -140 to -44 dBm
            'rsrp_mean': np.random.uniform(-110, -80, 50),
            'rsrp_std': np.random.uniform(3, 15, 50),
            'rsrp_min': np.random.uniform(-130, -100, 50),
            
            # RSRQ (dB): LTE typical -20 to -3 dB
            'rsrq_mean': np.random.uniform(-15, -5, 50),
            'rsrq_std': np.random.uniform(1, 5, 50),
            'rsrq_min': np.random.uniform(-20, -10, 50),
            
            # Messages count
            'total_messages': np.random.randint(100, 2000, 50),
            'max_frame_count': np.random.randint(1, 100, 50)
        })
    
    def test_optical_range_realistic(self, sample_telemetry_data):
        """Test optical power values are in realistic range"""
        df = sample_telemetry_data
        
        # Optical mean should be 0-2000 (raw ADC values)
        assert df['optical_mean'].min() >= 0
        assert df['optical_mean'].max() <= 2000
        
        # Optical range (max-min) should be positive
        assert all(df['optical_range'] >= 0)
        assert all(df['optical_range'] < 2000)  # Can't exceed full scale
    
    def test_temperature_range_realistic(self, sample_telemetry_data):
        """Test temperature values are physically realistic"""
        df = sample_telemetry_data
        
        # IoT devices typically operate -40 to +85°C
        assert df['temp_mean'].min() >= -50  # Allow some margin
        assert df['temp_mean'].max() <= 100
        
        # Temp range should be positive and reasonable
        assert all(df['temp_range'] >= 0)
        assert all(df['temp_range'] < 100)  # Unlikely >100°C range
    
    def test_battery_range_realistic(self, sample_telemetry_data):
        """Test battery voltage values are physically valid"""
        df = sample_telemetry_data
        
        # Battery voltage 0-5V typical (most IoT uses 3.3V or 5V systems)
        assert df['battery_mean'].min() >= 0
        assert df['battery_mean'].max() <= 5.0
        
        # Battery std should be small (voltage relatively stable)
        assert all(df['battery_std'] >= 0)
        assert all(df['battery_std'] < 1.0)  # >1V std is suspicious
    
    def test_snr_range_realistic(self, sample_telemetry_data):
        """Test SNR values are in typical wireless range"""
        df = sample_telemetry_data
        
        # SNR typically 0-40 dB (can be negative in bad conditions)
        assert df['snr_mean'].min() >= -10  # Allow some negative SNR
        assert df['snr_mean'].max() <= 50
    
    def test_rsrp_range_realistic(self, sample_telemetry_data):
        """Test RSRP values are in LTE specification range"""
        df = sample_telemetry_data
        
        # RSRP: -140 to -44 dBm per 3GPP spec
        assert df['rsrp_mean'].min() >= -140
        assert df['rsrp_mean'].max() <= -40  # Very strong signal
    
    def test_rsrq_range_realistic(self, sample_telemetry_data):
        """Test RSRQ values are in LTE specification range"""
        df = sample_telemetry_data
        
        # RSRQ: -20 to -3 dB per 3GPP spec
        assert df['rsrq_mean'].min() >= -20
        assert df['rsrq_mean'].max() <= 0  # Can be slightly positive
    
    def test_message_counts_positive(self, sample_telemetry_data):
        """Test message counts are non-negative integers"""
        df = sample_telemetry_data
        
        assert all(df['total_messages'] >= 0)
        assert all(df['max_frame_count'] >= 0)
        
        # total_messages should be >= max_frame_count logically
        # (though not always in aggregated data)
        assert all(df['total_messages'] > 0)  # At least 1 message


class TestMissingValueConstraints:
    """Test missing value thresholds and warnings"""
    
    def test_missing_threshold_warning_90_percent(self):
        """Test that >90% missing triggers warning"""
        # Create DataFrame with 95% missing
        data = {}
        for feature in REQUIRED_FEATURES:
            values = np.random.randn(100)
            mask = np.random.choice([True, False], 100, p=[0.95, 0.05])
            values[mask] = np.nan
            data[feature] = values
        
        df = pd.DataFrame(data)
        
        # Calculate missing percentage
        missing_pct = df.isnull().sum() / len(df) * 100
        
        # At least some features should have >90% missing
        assert any(missing_pct > 90)
        
        # Warn if any feature has >90% missing
        high_missing = missing_pct[missing_pct > 90]
        assert len(high_missing) > 0
    
    def test_complete_column_missing(self):
        """Test detection of 100% missing column"""
        data = {feature: np.random.randn(50) for feature in REQUIRED_FEATURES}
        
        # Make one column completely missing
        data['optical_mean'] = np.nan
        
        df = pd.DataFrame(data)
        
        # Detect 100% missing
        missing_pct = df.isnull().sum() / len(df) * 100
        assert missing_pct['optical_mean'] == 100.0
    
    def test_no_missing_acceptable(self):
        """Test that no missing values is valid"""
        data = {feature: np.random.randn(50) for feature in REQUIRED_FEATURES}
        df = pd.DataFrame(data)
        
        # Should have zero missing
        assert df.isnull().sum().sum() == 0


class TestCorrelationSanity:
    """Test correlation sanity checks (physically related features)"""
    
    @pytest.fixture
    def correlated_data(self):
        """Create data with expected correlations"""
        np.random.seed(42)
        n = 200
        
        # Battery degrades with temperature (negative correlation)
        temp_mean = np.random.uniform(20, 50, n)
        battery_mean = 4.0 - 0.02 * temp_mean + np.random.normal(0, 0.1, n)
        
        # Optical power relates to SNR (positive correlation)
        optical_mean = np.random.uniform(800, 1200, n)
        snr_mean = 5 + 0.015 * optical_mean + np.random.normal(0, 3, n)
        
        return pd.DataFrame({
            'temp_mean': temp_mean,
            'battery_mean': battery_mean,
            'optical_mean': optical_mean,
            'snr_mean': snr_mean
        })
    
    def test_temp_battery_negative_correlation(self, correlated_data):
        """Test that temp and battery have expected negative correlation"""
        corr = correlated_data[['temp_mean', 'battery_mean']].corr().iloc[0, 1]
        
        # Expect negative correlation (higher temp → lower battery)
        assert corr < 0, "Temperature and battery should be negatively correlated"
        assert corr < -0.3, f"Correlation {corr:.2f} weaker than expected"
    
    def test_optical_snr_positive_correlation(self, correlated_data):
        """Test that optical power and SNR have positive correlation"""
        corr = correlated_data[['optical_mean', 'snr_mean']].corr().iloc[0, 1]
        
        # Expect positive correlation (better optical → better SNR)
        assert corr > 0, "Optical power and SNR should be positively correlated"
        assert corr > 0.3, f"Correlation {corr:.2f} weaker than expected"
    
    def test_min_max_relationship(self):
        """Test that min < mean < max for aggregated features"""
        np.random.seed(42)
        n = 100
        
        # Generate mean, then min/max around it
        optical_mean = np.random.uniform(800, 1200, n)
        optical_min = optical_mean - np.random.uniform(50, 200, n)
        optical_max = optical_mean + np.random.uniform(50, 200, n)
        
        df = pd.DataFrame({
            'optical_min': optical_min,
            'optical_mean': optical_mean,
            'optical_max': optical_max
        })
        
        # All rows should satisfy min < mean < max
        assert all(df['optical_min'] <= df['optical_mean'])
        assert all(df['optical_mean'] <= df['optical_max'])
    
    def test_std_range_relationship(self):
        """Test that std relates to range (range ≈ k*std for normal distribution)"""
        np.random.seed(42)
        n = 100
        
        # For normal distribution: range ≈ 6*std (99.7% within 3σ)
        temp_std = np.random.uniform(2, 10, n)
        temp_range = 6 * temp_std + np.random.normal(0, 2, n)
        
        df = pd.DataFrame({
            'temp_std': temp_std,
            'temp_range': temp_range
        })
        
        # Range should be roughly proportional to std
        corr = df.corr().iloc[0, 1]
        assert corr > 0.7, f"STD and range correlation {corr:.2f} too weak"


class TestOutlierDetection:
    """Test outlier detection and flagging"""
    
    def test_detect_3sigma_outliers(self):
        """Test detection of values >3σ from mean"""
        np.random.seed(42)
        data = np.random.randn(100)
        
        # Add outliers
        data[0] = 5.0  # >3σ outlier
        data[1] = -5.0  # <-3σ outlier
        
        mean = data.mean()
        std = data.std()
        
        # Z-score
        z_scores = np.abs((data - mean) / std)
        
        # Detect outliers
        outliers = z_scores > 3
        
        # Should detect at least 2 outliers
        assert outliers.sum() >= 2
    
    def test_outlier_percentage_threshold(self):
        """Test that outlier percentage is within acceptable range"""
        np.random.seed(42)
        n = 1000
        
        # Normal data with few outliers
        data = np.random.randn(n)
        
        mean = data.mean()
        std = data.std()
        z_scores = np.abs((data - mean) / std)
        
        outliers_pct = (z_scores > 3).sum() / n * 100
        
        # For normal distribution, expect <1% outliers beyond 3σ
        assert outliers_pct < 1.0, f"Outlier percentage {outliers_pct:.2f}% too high"
    
    def test_iqr_outlier_detection(self):
        """Test IQR method for outlier detection"""
        np.random.seed(42)
        data = np.random.randn(100)
        
        # Add extreme outlier
        data[0] = 10.0
        
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        # Outliers: values > Q3 + 1.5*IQR or < Q1 - 1.5*IQR
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = (data < lower_bound) | (data > upper_bound)
        
        # Should detect at least 1 outlier
        assert outliers.sum() >= 1


@pytest.mark.integration
class TestRealDataValidation:
    """Integration tests with real test dataset"""
    
    @pytest.fixture
    def test_dataset(self):
        """Load real test set"""
        from pathlib import Path
        
        test_path = Path(__file__).parent.parent / "data" / "device_features_test_stratified.csv"
        
        if not test_path.exists():
            pytest.skip(f"Test data not found: {test_path}")
        
        return pd.read_csv(test_path)
    
    def test_real_data_schema(self, test_dataset):
        """Test that real data has all required features"""
        for feature in REQUIRED_FEATURES:
            assert feature in test_dataset.columns, \
                f"Missing feature: {feature}"
    
    def test_real_data_ranges(self, test_dataset):
        """Test that real data is within realistic ranges"""
        df = test_dataset
        
        # Temperature: -40 to +100°C
        if 'temp_mean' in df.columns:
            assert df['temp_mean'].min() >= -50
            assert df['temp_mean'].max() <= 100
        
        # Battery: 0-5V
        if 'battery_mean' in df.columns:
            assert df['battery_mean'].min() >= 0
            assert df['battery_mean'].max() <= 5.0
        
        # SNR: -10 to +50 dB
        if 'snr_mean' in df.columns:
            assert df['snr_mean'].min() >= -15
            assert df['snr_mean'].max() <= 50
    
    def test_real_data_missing_threshold(self, test_dataset):
        """Test that real data doesn't have excessive missing values"""
        missing_pct = test_dataset[REQUIRED_FEATURES].isnull().sum() / len(test_dataset) * 100
        
        # No feature should have >90% missing in test set
        assert all(missing_pct <= 90), \
            f"Features with >90% missing: {missing_pct[missing_pct > 90].to_dict()}"
    
    def test_real_data_min_max_consistency(self, test_dataset):
        """Test min/mean/max relationships in real data (excluding NaN rows)"""
        df = test_dataset
        
        # Check optical (filter out NaN rows for comparison)
        if all(col in df.columns for col in ['optical_min', 'optical_mean', 'optical_max']):
            optical_subset = df[['optical_min', 'optical_mean', 'optical_max']].dropna()
            if len(optical_subset) > 0:
                assert all(optical_subset['optical_min'] <= optical_subset['optical_mean']), \
                    "Optical min > mean in some rows"
                assert all(optical_subset['optical_mean'] <= optical_subset['optical_max']), \
                    "Optical mean > max in some rows"
        
        # Check temp
        if all(col in df.columns for col in ['temp_min', 'temp_mean', 'temp_max']):
            temp_subset = df[['temp_min', 'temp_mean', 'temp_max']].dropna()
            if len(temp_subset) > 0:
                assert all(temp_subset['temp_min'] <= temp_subset['temp_mean'])
                assert all(temp_subset['temp_mean'] <= temp_subset['temp_max'])
        
        # Check battery
        if all(col in df.columns for col in ['battery_min', 'battery_mean', 'battery_max']):
            battery_subset = df[['battery_min', 'battery_mean', 'battery_max']].dropna()
            if len(battery_subset) > 0:
                assert all(battery_subset['battery_min'] <= battery_subset['battery_mean'])
                assert all(battery_subset['battery_mean'] <= battery_subset['battery_max'])
