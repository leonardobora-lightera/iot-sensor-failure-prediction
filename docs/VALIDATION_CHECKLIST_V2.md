# Validation Checklist - Model v2 FIELD-only Streamlit App

**Date:** November 14, 2025  
**Model Version:** v2.0 FIELD-only (November 13, 2025)  
**Validator:** Leonardo Costa  
**Objective:** Ensure Streamlit app reflects 100% of model v2 updates (functionality, texts, research context)

---

## 🎯 Validation Scope

### Core Requirements
- ✅ Model v2 PKL loaded correctly (`catboost_pipeline_v2_field_only.pkl`)
- ✅ Metadata v2 loaded (`catboost_pipeline_v2_metadata.json`)
- ✅ 30 features supported (including `days_since_last_message`)
- ✅ Metrics displayed: Recall 57.1%, Precision 57.1%, AUC 0.9186
- ✅ All text references updated from v1 (Mixed) to v2 (FIELD-only)

---

## 📄 Page-by-Page Validation

### ✅ streamlit_app.py (Main Entry)
**Status:** [ ] Local | [ ] Cloud

| Item | Expected | Result | Status |
|------|----------|--------|--------|
| Sidebar: Model Version | "v2.0 FIELD-only" | | [ ] PASS / [ ] FAIL |
| Sidebar: Training Date | "2025-11-13" | | [ ] PASS / [ ] FAIL |
| Sidebar: Algorithm | "CatBoost + SMOTE" | | [ ] PASS / [ ] FAIL |
| Sidebar: Recall Metric | "57.1%" with "-21.5% vs v1" | | [ ] PASS / [ ] FAIL |
| Sidebar: Precision Metric | "57.1%" with "-27.5% vs v1" | | [ ] PASS / [ ] FAIL |
| Sidebar: ROC-AUC Metric | "0.9186" with "+6.6% vs v1" | | [ ] PASS / [ ] FAIL |
| Navigation: 5 Pages | Home, Batch Upload, Single Predict, Insights, Research | | [ ] PASS / [ ] FAIL |
| Language Selector | English/Português working | | [ ] PASS / [ ] FAIL |

**Issues Found:**
- 

---

### ✅ Page 1: Home
**Status:** [ ] Local | [ ] Cloud

| Item | Expected | Result | Status |
|------|----------|--------|--------|
| Title | "IoT Critical Device Prediction" | | [ ] PASS / [ ] FAIL |
| Performance Metrics | Recall 57.1%, Precision 57.1%, F1 57.1%, AUC 0.9186 | | [ ] PASS / [ ] FAIL |
| Deltas | Recall -21.5% (red), Precision -27.5% (red), F1 -24.4% (red), AUC +6.6% (green) | | [ ] PASS / [ ] FAIL |
| Model Evolution Section | 3 expanders: v1 Mixed, v2 FIELD-only, Roadmap "3 Steps Forward" | | [ ] PASS / [ ] FAIL |
| Business Impact | "8 out of 14 critical detected (57.1%)" | | [ ] PASS / [ ] FAIL |
| Limitations Section | "Miss rate: 6 of 14", "No hyperparameter tuning", "Missing temporal features" | | [ ] PASS / [ ] FAIL |
| Footer | "533 train (29 critical) | 229 test (14 critical) | November 13, 2025" | | [ ] PASS / [ ] FAIL |

**Issues Found:**
- 

---

### ✅ Page 2: Batch Upload
**Status:** [ ] Local | [ ] Cloud

| Item | Expected | Result | Status |
|------|----------|--------|--------|
| Title | "Batch Upload" | | [ ] PASS / [ ] FAIL |
| CSV Format Docs | "30 required features (Model v2)" | | [ ] PASS / [ ] FAIL |
| Messaging Features | "Messaging (3)" with days_since_last_message listed | | [ ] PASS / [ ] FAIL |
| CSV Upload | Accepts CSV with 30 features + device_id (31 columns) | | [ ] PASS / [ ] FAIL |
| Validation | Shows error if <30 features, accepts if =30 features | | [ ] PASS / [ ] FAIL |
| Results Table | Displays device_id, probability, risk_level | | [ ] PASS / [ ] FAIL |
| Download CSV | Allows download of results | | [ ] PASS / [ ] FAIL |

**Test CSV:** `payload_aws_BORA_transformed_v2.csv` (640 devices, 31 columns)

**Issues Found:**
- 

---

### ✅ Page 3: Single Prediction
**Status:** [ ] Local | [ ] Cloud

| Item | Expected | Result | Status |
|------|----------|--------|--------|
| Title | "Single Prediction" | | [ ] PASS / [ ] FAIL |
| Form Tabs | Telemetry (18), Connectivity (9), Messaging (3) | | [ ] PASS / [ ] FAIL |
| Messaging Tab Columns | 3 columns (total_messages, max_frame_count, days_since_last_message) | | [ ] PASS / [ ] FAIL |
| days_since_last_message Input | Field present with ⭐ marker, default 0.0, help text | | [ ] PASS / [ ] FAIL |
| Prediction Button | "Predict Critical Risk" button works | | [ ] PASS / [ ] FAIL |
| Results Display | Shows probability, risk level, confidence bar | | [ ] PASS / [ ] FAIL |
| Feature Order | 30 features submitted in correct order (days_since at position 3) | | [ ] PASS / [ ] FAIL |

**Test Case 1:** Normal device (all features moderate)
**Test Case 2:** Critical device (battery_min=2.0, temp_max=45, days_since=60)

**Issues Found:**
- 

---

### ✅ Page 4: Model Insights
**Status:** [ ] Local | [ ] Cloud

| Item | Expected | Result | Status |
|------|----------|--------|--------|
| Title | "Model Insights" | | [ ] PASS / [ ] FAIL |
| Performance Metrics | Recall 57.1%, Precision 57.1%, AUC 0.9186 | | [ ] PASS / [ ] FAIL |
| Confusion Matrix | TP=8, FN=6, FP=6, TN=209 (total 229 test devices) | | [ ] PASS / [ ] FAIL |
| Business Metrics | "8/14 critical detected", "6 missed", "6 false alarms" | | [ ] PASS / [ ] FAIL |
| Help Text | Mentions "v2 FIELD-only" context | | [ ] PASS / [ ] FAIL |
| Feature Importance | (If available) Shows top features with days_since_last_message | | [ ] PASS / [ ] FAIL |

**Issues Found:**
- 

---

### ✅ Page 5: Research Context
**Status:** [ ] Local | [ ] Cloud

| Item | Expected | Result | Status |
|------|----------|--------|--------|
| Version Indicator | "📊 Current Model: v2.0 FIELD-only (November 13, 2025)" | | [ ] PASS / [ ] FAIL |
| Impact Metrics Box | Shows v1 and v2 metrics side by side | | [ ] PASS / [ ] FAIL |
| Model Evolution Section | Tabs: "v1: Mixed FACTORY+FIELD" and "v2: FIELD-only Clean Data" | | [ ] PASS / [ ] FAIL |
| Discovery 0 (NEW) | "🚨 Discovery 0: Lifecycle Contamination" expanded by default | | [ ] PASS / [ ] FAIL |
| Device 861275072515287 | Mentioned as false positive example in Discovery 0 | | [ ] PASS / [ ] FAIL |
| Features Section | "30 Features (v2)" - Tab 3: "Messaging (3)" with days_since_last_message ⭐ | | [ ] PASS / [ ] FAIL |
| Business Impact Selector | Radio: "v2 (Current - FIELD-only)" / "v1 (Deprecated - Mixed)" | | [ ] PASS / [ ] FAIL |
| v2 Business Metrics | 8/14 detected, 6 false alarms, 6 missed (when v2 selected) | | [ ] PASS / [ ] FAIL |
| Footer | "Current: CatBoost v2.0 FIELD-only (Nov 13, 2025) | Deprecated: v1.0 Mixed (Nov 7, 2025)" | | [ ] PASS / [ ] FAIL |

**Issues Found:**
- 

---

## 🧪 Functional Testing

### Model Loading
| Test | Expected | Result | Status |
|------|----------|--------|--------|
| Load PKL | `catboost_pipeline_v2_field_only.pkl` loads without error | | [ ] PASS / [ ] FAIL |
| Load Metadata | `catboost_pipeline_v2_metadata.json` loads without error | | [ ] PASS / [ ] FAIL |
| Feature Count | Pipeline expects exactly 30 features | | [ ] PASS / [ ] FAIL |
| Feature Order | days_since_last_message at position 3 | | [ ] PASS / [ ] FAIL |

### Predictions
| Test | Input | Expected Output | Result | Status |
|------|-------|-----------------|--------|--------|
| Normal Device | All moderate values | Probability <30% | | [ ] PASS / [ ] FAIL |
| Critical Device | battery_min=2.0, temp_max=45, days_since=90 | Probability >50% | | [ ] PASS / [ ] FAIL |
| Batch Upload | payload_aws_BORA_transformed_v2.csv (640 devices) | 3 critical detected (0.5%) | | [ ] PASS / [ ] FAIL |
| Missing Feature | CSV with 29 features (missing days_since) | Error message | | [ ] PASS / [ ] FAIL |

---

## 🌐 Streamlit Cloud Deployment

### Deployment Status
| Item | Expected | Result | Status |
|------|----------|--------|--------|
| URL Accessible | https://iot-sensor-failure-prediction.streamlit.app loads | | [ ] PASS / [ ] FAIL |
| No Console Errors | Browser console clean (no 404, 500 errors) | | [ ] PASS / [ ] FAIL |
| Python 3.13 Import Fix | sys.path fix working (no KeyError: 'utils') | | [ ] PASS / [ ] FAIL |
| All Pages Load | 5 pages navigate without crashes | | [ ] PASS / [ ] FAIL |
| Model File Present | PKL file loaded (no "File not found" error) | | [ ] PASS / [ ] FAIL |

---

## 📝 Text Consistency Check

### References to v1 (Should be contextualized as historical)
- [ ] All "78.6% recall" references marked as "v1 (deprecated)" or in historical context
- [ ] All "789 devices" references marked as "v1 dataset" or historical
- [ ] All "552 train / 237 test" references marked as "v1 split" or historical

### References to v2 (Should be current/primary)
- [ ] "57.1% recall" shown as current model performance
- [ ] "762 devices FIELD-only" shown as current dataset
- [ ] "533 train / 229 test" shown as current split
- [ ] "30 features" mentioned consistently (not 29)
- [ ] "days_since_last_message" documented as new temporal feature

---

## 🐛 Known Issues / Bugs Found

### Critical (Blocks Usage)
- None expected (all critical bugs fixed in commits 7347676, 7c89e55, f1aaf1a)

### Medium (Affects UX)
- 

### Low (Minor Issues)
- 

---

## ✅ Final Sign-Off

**Local Testing Completed:** [ ] YES / [ ] NO  
**Cloud Testing Completed:** [ ] YES / [ ] NO  
**All Critical Items Passing:** [ ] YES / [ ] NO  
**Ready for Production:** [ ] YES / [ ] NO  

**Overall Assessment:**
- 

**Next Steps:**
1. 
2. 
3. 

---

**Validation Completed By:** Leonardo Costa  
**Date:** _______________  
**Signature:** _______________
