"""
Pytest Configuration and Shared Fixtures
Common fixtures and configuration for all test modules
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_device_data():
    """
    Create sample device data with all 29 required features
    Simulates realistic IoT sensor telemetry data
    """
    np.random.seed(42)
    n_devices = 50
    
    data = {
        # Optical features (7)
        'optical_mean': np.random.uniform(800, 1200, n_devices),
        'optical_std': np.random.uniform(50, 150, n_devices),
        'optical_min': np.random.uniform(600, 900, n_devices),
        'optical_max': np.random.uniform(1000, 1500, n_devices),
        'optical_readings': np.random.randint(100, 1000, n_devices),
        'optical_below_threshold': np.random.randint(0, 50, n_devices),
        'optical_range': np.random.uniform(200, 600, n_devices),
        
        # Temperature features (6)
        'temp_mean': np.random.uniform(20, 40, n_devices),
        'temp_std': np.random.uniform(2, 10, n_devices),
        'temp_min': np.random.uniform(15, 25, n_devices),
        'temp_max': np.random.uniform(35, 50, n_devices),
        'temp_above_threshold': np.random.randint(0, 20, n_devices),
        'temp_range': np.random.uniform(10, 30, n_devices),
        
        # Battery features (5)
        'battery_mean': np.random.uniform(3.0, 3.8, n_devices),
        'battery_std': np.random.uniform(0.1, 0.5, n_devices),
        'battery_min': np.random.uniform(2.5, 3.2, n_devices),
        'battery_max': np.random.uniform(3.5, 4.0, n_devices),
        'battery_below_threshold': np.random.randint(0, 10, n_devices),
        
        # SNR features (3)
        'snr_mean': np.random.uniform(5, 25, n_devices),
        'snr_std': np.random.uniform(1, 5, n_devices),
        'snr_min': np.random.uniform(0, 15, n_devices),
        
        # RSRP features (3)
        'rsrp_mean': np.random.uniform(-120, -80, n_devices),
        'rsrp_std': np.random.uniform(2, 10, n_devices),
        'rsrp_min': np.random.uniform(-130, -90, n_devices),
        
        # RSRQ features (3)
        'rsrq_mean': np.random.uniform(-20, -5, n_devices),
        'rsrq_std': np.random.uniform(1, 5, n_devices),
        'rsrq_min': np.random.uniform(-25, -10, n_devices),
        
        # Message features (2)
        'total_messages': np.random.randint(100, 2000, n_devices),
        'max_frame_count': np.random.randint(1, 100, n_devices)
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def critical_device_indices():
    """
    Return indices of 'critical' devices in sample data
    Simulates known critical devices for testing
    """
    # Assume 10% of devices are critical (5 out of 50)
    return [2, 8, 15, 23, 41]


@pytest.fixture
def sample_predictions():
    """
    Create sample prediction probabilities and labels
    Simulates model output
    """
    np.random.seed(42)
    n_devices = 50
    
    # Generate probabilities (skewed toward non-critical)
    probabilities = np.random.beta(2, 5, n_devices)
    
    # Binary predictions (threshold 0.5)
    predictions = (probabilities > 0.5).astype(int)
    
    return {
        'probabilities': probabilities,
        'predictions': predictions,
        'threshold': 0.5
    }


@pytest.fixture
def temp_data_dir(tmp_path):
    """
    Create temporary directory structure for test data
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    return {
        'root': tmp_path,
        'data': data_dir,
        'models': models_dir,
        'logs': logs_dir
    }


@pytest.fixture
def mock_streamlit():
    """
    Mock Streamlit functions to prevent import errors in tests
    """
    from unittest.mock import MagicMock
    
    mock_st = MagicMock()
    mock_st.cache_resource = lambda x: x  # No-op decorator
    mock_st.error = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.info = MagicMock()
    mock_st.success = MagicMock()
    
    return mock_st


# Test configuration
def pytest_configure(config):
    """
    Custom pytest configuration
    """
    # Add custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
