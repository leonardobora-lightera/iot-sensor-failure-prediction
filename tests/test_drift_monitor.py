"""
Unit tests for drift_monitor.py - Distribution Shift Detection

Tests cover:
1. KS statistic calculation
2. Lifecycle drift detection
3. Drift status classification
4. Synthetic drift scenarios
5. Real data integration
"""

import numpy as np
import pandas as pd
import pytest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from drift_monitor import (
    compute_ks_statistics,
    detect_lifecycle_drift,
    classify_drift_status,
    ALL_FEATURES
)


class TestKSStatisticsCalculation:
    """Test Kolmogorov-Smirnov statistic computation."""
    
    def test_identical_distributions_zero_ks(self):
        """KS statistic should be near zero for identical distributions."""
        np.random.seed(42)
        
        # Create identical distributions
        data = np.random.normal(loc=50, scale=10, size=200)
        reference = pd.DataFrame({feat: data for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: data for feat in ALL_FEATURES})
        
        results = compute_ks_statistics(reference, production)
        
        # All KS statistics should be very small (< 0.05)
        for feat in ALL_FEATURES:
            assert results[feat]['ks_statistic'] < 0.05, f"{feat} KS too high for identical distributions"
            assert results[feat]['p_value'] > 0.05, f"{feat} p-value too low (false positive)"
    
    def test_shifted_distribution_high_ks(self):
        """KS statistic should be high for shifted distributions."""
        np.random.seed(42)
        
        # Create shifted distribution (mean shift)
        reference_data = np.random.normal(loc=50, scale=10, size=200)
        production_data = np.random.normal(loc=60, scale=10, size=200)  # Shifted +10
        
        reference = pd.DataFrame({'battery_mean': reference_data})
        production = pd.DataFrame({'battery_mean': production_data})
        
        # Add other features (identical) to meet ALL_FEATURES requirement
        for feat in ALL_FEATURES:
            if feat != 'battery_mean':
                reference[feat] = np.random.normal(0, 1, 200)
                production[feat] = reference[feat].values
        
        results = compute_ks_statistics(reference, production)
        
        # battery_mean should have high KS statistic (distribution shifted)
        assert results['battery_mean']['ks_statistic'] > 0.3, "KS statistic too low for shifted distribution"
        assert results['battery_mean']['production_mean'] > results['battery_mean']['reference_mean'], "Mean not shifted"
    
    def test_different_variance_detected(self):
        """KS test should detect changes in variance (std)."""
        np.random.seed(42)
        
        # Same mean, different variance
        reference_data = np.random.normal(loc=50, scale=5, size=200)   # std=5
        production_data = np.random.normal(loc=50, scale=15, size=200)  # std=15
        
        reference = pd.DataFrame({'optical_mean': reference_data})
        production = pd.DataFrame({'optical_mean': production_data})
        
        for feat in ALL_FEATURES:
            if feat != 'optical_mean':
                reference[feat] = np.random.normal(0, 1, 200)
                production[feat] = reference[feat].values
        
        results = compute_ks_statistics(reference, production)
        
        # Variance change should be detected
        assert results['optical_mean']['ks_statistic'] > 0.2, "KS failed to detect variance change"
        assert results['optical_mean']['production_std'] > results['optical_mean']['reference_std'], "Std not increased"
    
    def test_handles_nan_values(self):
        """KS computation should handle NaN values gracefully."""
        np.random.seed(42)
        
        # Create data with NaN values
        reference_data = np.random.normal(50, 10, 200)
        reference_data[::10] = np.nan  # 10% NaN
        
        production_data = np.random.normal(50, 10, 200)
        production_data[::15] = np.nan  # ~7% NaN
        
        reference = pd.DataFrame({feat: reference_data for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: production_data for feat in ALL_FEATURES})
        
        results = compute_ks_statistics(reference, production)
        
        # Should compute valid statistics after dropping NaN
        for feat in ALL_FEATURES:
            assert not np.isnan(results[feat]['ks_statistic']), f"{feat} KS is NaN"
            assert results[feat]['reference_n'] < 200, "NaN values not dropped from reference"
            assert results[feat]['production_n'] < 200, "NaN values not dropped from production"


class TestLifecycleDriftDetection:
    """Test lifecycle pattern drift detection logic."""
    
    def test_no_lifecycle_drift_stable_patterns(self):
        """No lifecycle drift when activity and variability stable."""
        np.random.seed(42)
        
        # Create stable distributions
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        assert not lifecycle_drift['lifecycle_drift_detected'], "False positive lifecycle drift"
        assert lifecycle_drift['lifecycle_drift_score'] < 0.3, "Drift score too high for stable data"
        assert "STABLE" in lifecycle_drift['interpretation']
    
    def test_lifecycle_drift_activity_change(self):
        """Detect lifecycle drift when total_messages distribution changes."""
        np.random.seed(42)
        
        # Reference: High message count (always active)
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        reference['total_messages'] = np.random.normal(5000, 500, 200)  # High activity
        
        # Production: Low message count (more inactive periods)
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production['total_messages'] = np.random.normal(2000, 300, 200)  # Low activity (SHIFT)
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        assert lifecycle_drift['lifecycle_drift_detected'], "Failed to detect activity drift"
        assert lifecycle_drift['activity_drift'] > 0.3, "Activity drift score too low"
        assert "CHANGED" in lifecycle_drift['interpretation']
    
    def test_lifecycle_drift_variability_change(self):
        """Detect lifecycle drift when variability (std features) change."""
        np.random.seed(42)
        
        # Reference: Low variability (direct deploy, no phase mixing)
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        reference['optical_std'] = np.random.normal(100, 20, 200)  # Low variability
        reference['battery_std'] = np.random.normal(0.2, 0.05, 200)
        
        # Production: High variability (lab→inactive→production mixing)
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production['optical_std'] = np.random.normal(400, 50, 200)  # High variability (SHIFT)
        production['battery_std'] = np.random.normal(0.6, 0.1, 200)
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        assert lifecycle_drift['lifecycle_drift_detected'], "Failed to detect variability drift"
        assert lifecycle_drift['variability_drift'] > 0.3, "Variability drift score too low"
    
    def test_lifecycle_drift_score_calculation(self):
        """Lifecycle drift score should be max of activity and variability drift."""
        np.random.seed(42)
        
        # Moderate activity drift, high variability drift
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        
        # Activity drift: moderate (KS ~ 0.25)
        reference['total_messages'] = np.random.normal(4000, 500, 200)
        production['total_messages'] = np.random.normal(3000, 500, 200)
        
        # Variability drift: high (KS ~ 0.5)
        reference['optical_std'] = np.random.normal(100, 20, 200)
        production['optical_std'] = np.random.normal(300, 40, 200)
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        # Drift score should be close to max(activity_drift, variability_drift)
        max_expected = max(lifecycle_drift['activity_drift'], lifecycle_drift['variability_drift'])
        assert abs(lifecycle_drift['lifecycle_drift_score'] - max_expected) < 0.05, "Drift score not maximum"


class TestDriftStatusClassification:
    """Test overall drift status classification logic."""
    
    def test_ok_status_no_drift(self):
        """Status should be OK when all KS statistics < WARNING threshold."""
        np.random.seed(42)
        
        # All features stable (KS < 0.2)
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        status, alerts = classify_drift_status(ks_results, lifecycle_drift, threshold_warning=0.2, threshold_critical=0.4)
        
        assert status == 'OK', f"Status should be OK, got {status}"
        assert len(alerts) == 0, "Should have no alerts for OK status"
    
    def test_warning_status_moderate_drift(self):
        """Status should be WARNING when 0.2 <= KS < 0.4 for some features."""
        np.random.seed(42)
        
        # Most features stable, battery_mean has moderate drift
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        
        # Introduce moderate drift in battery_mean (KS ~ 0.25)
        production['battery_mean'] = np.random.normal(55, 10, 200)  # Shift +5
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        status, alerts = classify_drift_status(ks_results, lifecycle_drift, threshold_warning=0.2, threshold_critical=0.4)
        
        assert status == 'WARNING', f"Status should be WARNING, got {status}"
        assert any('battery_mean' in alert for alert in alerts), "battery_mean should be in alerts"
        assert any('WARNING drift' in alert for alert in alerts), "Should mention WARNING level"
    
    def test_critical_status_high_drift(self):
        """Status should be CRITICAL when KS >= 0.4 for any feature."""
        np.random.seed(42)
        
        # Most features stable, optical_mean has high drift
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        
        # Introduce critical drift in optical_mean (KS ~ 0.6)
        production['optical_mean'] = np.random.normal(70, 10, 200)  # Large shift +20
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        status, alerts = classify_drift_status(ks_results, lifecycle_drift, threshold_warning=0.2, threshold_critical=0.4)
        
        assert status == 'CRITICAL', f"Status should be CRITICAL, got {status}"
        assert any('CRITICAL drift' in alert for alert in alerts), "Should mention CRITICAL level"
        assert any('optical_mean' in alert for alert in alerts), "optical_mean should be in alerts"
    
    def test_critical_status_lifecycle_drift(self):
        """Status should be CRITICAL when lifecycle drift detected."""
        np.random.seed(42)
        
        # All individual features OK, but lifecycle pattern changed
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        reference['total_messages'] = np.random.normal(5000, 500, 200)
        
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production['total_messages'] = np.random.normal(1500, 300, 200)  # Huge activity drop
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        status, alerts = classify_drift_status(ks_results, lifecycle_drift, threshold_warning=0.2, threshold_critical=0.4)
        
        assert status == 'CRITICAL', "Lifecycle drift should trigger CRITICAL status"
        assert any('LIFECYCLE PATTERN DRIFT' in alert for alert in alerts), "Should alert lifecycle drift"


class TestSyntheticDriftScenarios:
    """Test drift detection on synthetic realistic scenarios."""
    
    def test_deployment_pattern_change_direct_deploy(self):
        """Simulate deployment pattern change: lab-tested → direct-deploy."""
        np.random.seed(42)
        
        # Reference: Lab-tested devices (high variability from phase mixing)
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        reference['optical_std'] = np.random.normal(400, 80, 200)  # High variability
        reference['battery_std'] = np.random.normal(0.6, 0.1, 200)
        reference['total_messages'] = np.random.normal(3000, 500, 200)  # Moderate activity
        
        # Production: Direct-deploy devices (low variability, always active)
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production['optical_std'] = np.random.normal(150, 30, 200)  # Low variability
        production['battery_std'] = np.random.normal(0.2, 0.05, 200)
        production['total_messages'] = np.random.normal(8000, 800, 200)  # High activity
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        # Should detect both variability drift and activity drift
        assert lifecycle_drift['lifecycle_drift_detected'], "Failed to detect deployment pattern change"
        assert lifecycle_drift['variability_drift'] > 0.3, "Should detect low variability (no phase mixing)"
        assert lifecycle_drift['activity_drift'] > 0.3, "Should detect high activity (always active)"
    
    def test_hardware_batch_change_battery_supplier(self):
        """Simulate hardware change: different battery supplier (voltage baseline shift)."""
        np.random.seed(42)
        
        # Reference: Battery supplier A (nominal 3.7V)
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        reference['battery_mean'] = np.random.normal(3.5, 0.3, 200)  # Mean ~3.5V
        reference['battery_min'] = np.random.normal(3.0, 0.2, 200)
        reference['battery_max'] = np.random.normal(4.0, 0.1, 200)
        
        # Production: Battery supplier B (nominal 3.85V)
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production['battery_mean'] = np.random.normal(3.65, 0.3, 200)  # Mean ~3.65V (SHIFT +0.15V)
        production['battery_min'] = np.random.normal(3.15, 0.2, 200)
        production['battery_max'] = np.random.normal(4.15, 0.1, 200)
        
        ks_results = compute_ks_statistics(reference, production)
        status, alerts = classify_drift_status(ks_results, detect_lifecycle_drift(ks_results))
        
        # Should detect drift in battery features
        assert ks_results['battery_mean']['ks_statistic'] > 0.2, "Failed to detect battery baseline shift"
        assert status in ['WARNING', 'CRITICAL'], "Should alert on hardware change"
    
    def test_environmental_shift_temperature(self):
        """Simulate environmental change: temperate → tropical climate."""
        np.random.seed(42)
        
        # Reference: Temperate climate (temp_mean ~22°C)
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        reference['temp_mean'] = np.random.normal(22, 5, 200)
        reference['temp_max'] = np.random.normal(30, 3, 200)
        
        # Production: Tropical climate (temp_mean ~32°C)
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production['temp_mean'] = np.random.normal(32, 6, 200)  # +10°C shift
        production['temp_max'] = np.random.normal(42, 4, 200)
        
        ks_results = compute_ks_statistics(reference, production)
        status, alerts = classify_drift_status(ks_results, detect_lifecycle_drift(ks_results))
        
        # Should detect drift in temperature features
        assert ks_results['temp_mean']['ks_statistic'] > 0.3, "Failed to detect temperature shift"
        assert status == 'CRITICAL', "Major environmental shift should be CRITICAL"


@pytest.mark.integration
class TestRealDataIntegration:
    """Integration tests with real test dataset."""
    
    @pytest.fixture
    def test_data(self):
        """Load real test dataset."""
        test_file = Path(__file__).parent.parent / 'data' / 'device_features_test_stratified.csv'
        if not test_file.exists():
            pytest.skip(f"Test data not found: {test_file}")
        
        df = pd.read_csv(test_file)
        return df
    
    def test_self_comparison_minimal_drift(self, test_data):
        """Comparing test data to itself should show minimal drift."""
        # Split test data in half
        split_idx = len(test_data) // 2
        reference = test_data.iloc[:split_idx][ALL_FEATURES]
        production = test_data.iloc[split_idx:][ALL_FEATURES]
        
        ks_results = compute_ks_statistics(reference, production)
        status, alerts = classify_drift_status(ks_results, detect_lifecycle_drift(ks_results))
        
        # Most features should have low drift (same distribution)
        low_drift_count = sum(1 for res in ks_results.values() if res['ks_statistic'] < 0.2)
        assert low_drift_count >= 20, f"Too many features with drift in self-comparison ({low_drift_count}/29)"
    
    def test_handles_real_data_nan_patterns(self, test_data):
        """Real data may have NaN patterns - should handle gracefully."""
        reference = test_data[ALL_FEATURES]
        
        # Create production with same distribution but different NaN pattern
        production = test_data[ALL_FEATURES].sample(frac=1, random_state=42).reset_index(drop=True)
        
        ks_results = compute_ks_statistics(reference, production)
        
        # All features should have valid KS statistics (no NaN errors)
        for feat in ALL_FEATURES:
            if 'error' not in ks_results[feat]:
                assert not np.isnan(ks_results[feat]['ks_statistic']), f"{feat} KS is NaN"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_production_data(self):
        """Handle empty production dataset gracefully."""
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: [] for feat in ALL_FEATURES})
        
        ks_results = compute_ks_statistics(reference, production)
        
        # Should have error messages, not crash
        for feat in ALL_FEATURES:
            assert 'error' in ks_results[feat] or np.isnan(ks_results[feat]['ks_statistic'])
    
    def test_single_value_production(self):
        """Handle production data with single unique value (no variance)."""
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: [42.0] * 100 for feat in ALL_FEATURES})  # All same value
        
        ks_results = compute_ks_statistics(reference, production)
        
        # Should detect extreme drift (no variance = very different from normal distribution)
        assert ks_results['battery_mean']['ks_statistic'] > 0.5, "Failed to detect zero-variance distribution"
    
    def test_custom_thresholds(self):
        """Allow custom WARNING and CRITICAL thresholds."""
        np.random.seed(42)
        
        reference = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production = pd.DataFrame({feat: np.random.normal(50, 10, 200) for feat in ALL_FEATURES})
        production['battery_mean'] = np.random.normal(54, 10, 200)  # KS ~ 0.25
        
        ks_results = compute_ks_statistics(reference, production)
        lifecycle_drift = detect_lifecycle_drift(ks_results)
        
        # With strict thresholds (0.15, 0.25), should be CRITICAL
        status_strict, _ = classify_drift_status(
            ks_results, lifecycle_drift, threshold_warning=0.15, threshold_critical=0.25
        )
        assert status_strict == 'CRITICAL', "Should be CRITICAL with strict thresholds"
        
        # With lenient thresholds (0.3, 0.5), should be OK
        status_lenient, _ = classify_drift_status(
            ks_results, lifecycle_drift, threshold_warning=0.3, threshold_critical=0.5
        )
        assert status_lenient == 'OK', "Should be OK with lenient thresholds"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
