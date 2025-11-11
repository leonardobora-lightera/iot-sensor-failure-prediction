# 🧪 Test Suite - IoT Sensor Failure Prediction

Comprehensive unit tests for `utils/` modules ensuring code quality, reliability, and maintainability.

## 📋 Test Coverage

### **1. Model Loader Tests** (`test_model_loader.py`)
- ✅ `load_pipeline()`: Success, file not found, default path, corrupted file
- ✅ `load_metadata()`: Success, file not found, invalid JSON, feature importance format
- **Coverage Target**: 90%+

### **2. Preprocessing Tests** (`test_preprocessing.py`)
- ✅ `validate_features()`: Complete features, missing features, extra columns
- ✅ `check_feature_types()`: Numeric conversion, non-convertible strings, preservation
- ✅ `get_missing_stats()`: No missing, partial missing, extreme missing (>90%)
- ✅ `prepare_for_prediction()`: Feature extraction, type conversion, order preservation
- **Coverage Target**: 85%+

### **3. Visualization Tests** (`test_visualization.py`)
- ✅ `plot_feature_importance()`: Figure creation, top_n filtering, sorting
- ✅ `plot_confusion_matrix()`: Correct values, labels, zero handling
- ✅ `plot_probability_distribution()`: With/without predictions, threshold line
- ✅ `plot_roc_curve()`: Two traces (ROC + diagonal), AUC in legend
- ✅ `create_metric_gauge()`: Color thresholds (excellent/good/poor), value display
- **Coverage Target**: 75%+

---

## 🚀 Running Tests

### **Install Dependencies**
```powershell
# Install production dependencies first
pip install -r requirements.txt

# Install development/testing dependencies
pip install -r requirements-dev.txt
```

### **Run All Tests**
```powershell
# Run all tests with coverage report
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_preprocessing.py

# Run specific test class
pytest tests/test_preprocessing.py::TestValidateFeatures

# Run specific test function
pytest tests/test_preprocessing.py::TestValidateFeatures::test_validate_features_complete
```

### **Run Tests by Marker**
```powershell
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

### **Coverage Reports**
```powershell
# Generate coverage report (terminal)
pytest --cov=utils --cov=models --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=utils --cov=models --cov-report=html

# Open HTML report (Windows)
start tests/coverage_html/index.html
```

---

## 📊 Test Results Summary

### **Expected Metrics** (Target)
| Metric | Target | Status |
|--------|--------|--------|
| **Total Coverage** | 80%+ | ⏳ Pending |
| **Model Loader** | 90%+ | ⏳ Pending |
| **Preprocessing** | 85%+ | ⏳ Pending |
| **Visualization** | 75%+ | ⏳ Pending |
| **Total Tests** | 50+ | ✅ 63 tests |
| **Test Duration** | <30s | ⏳ Pending |

### **Test Breakdown**
- `test_model_loader.py`: **10 tests** (load_pipeline 4, load_metadata 6)
- `test_preprocessing.py`: **31 tests** (features 4, validation 4, types 5, missing 4, prepare 6, constants 3)
- `test_visualization.py`: **22 tests** (feature importance 5, confusion matrix 5, probability 4, ROC 5, gauge 7, integration 1)

---

## 🛠️ Test Fixtures

### **Shared Fixtures** (`conftest.py`)
- `sample_device_data`: 50 devices with all 29 features (realistic telemetry)
- `critical_device_indices`: Known critical devices [2, 8, 15, 23, 41]
- `sample_predictions`: Mock model output (probabilities, predictions, threshold)
- `temp_data_dir`: Temporary directory structure (data/, models/, logs/)
- `mock_streamlit`: Mock Streamlit functions (prevents import errors)

---

## ⚠️ Known Issues & Workarounds

### **Import Errors (Expected)**
- **Lint errors** for `joblib` and `plotly` imports are **expected** during development
- These are resolved when running tests (dependencies installed via `requirements-dev.txt`)
- Streamlit functions are **mocked** in tests (no GUI needed)

### **Coverage Gaps**
- `display_missing_info()`: Streamlit UI function (hard to test, low priority)
- Streamlit decorators (`@st.cache_resource`): Mocked in tests, not counted in coverage

---

## 📝 Writing New Tests

### **Template Structure**
```python
import pytest
from utils.your_module import your_function

class TestYourFunction:
    """Test suite for your_function"""
    
    @pytest.fixture
    def sample_data(self):
        """Create test data"""
        return {"key": "value"}
    
    def test_success_case(self, sample_data):
        """Test normal operation"""
        result = your_function(sample_data)
        assert result is not None
    
    def test_error_handling(self):
        """Test error conditions"""
        with pytest.raises(ValueError):
            your_function(None)
```

### **Best Practices**
1. **Arrange-Act-Assert**: Setup → Execute → Verify
2. **Mock Streamlit**: Use `with patch('module.st.function'):`
3. **Fixtures**: Reuse test data via `@pytest.fixture`
4. **Descriptive Names**: `test_validate_features_missing_columns` (clear intent)
5. **Edge Cases**: Test empty inputs, NaN, extreme values

---

## 🎯 Next Steps (After Task 1)

1. **Run Tests Locally**: `pytest -v` (verify all 63 tests pass)
2. **Check Coverage**: `pytest --cov` (ensure 80%+ target)
3. **Fix Failures**: Address any test failures or assertion errors
4. **Commit**: Git commit with message "✅ Task 1: Unit tests complete (63 tests, 80%+ coverage)"
5. **Task 2**: Integration tests (`test_inference_pipeline.py`)

---

## 📚 References
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-cov Plugin](https://pytest-cov.readthedocs.io/)
- [Streamlit Testing Best Practices](https://docs.streamlit.io/develop/concepts/app-testing)
