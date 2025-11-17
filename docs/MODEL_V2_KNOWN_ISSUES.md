# Model v2 FIELD-only - Known Issues & Limitations

**Document Version:** 1.0  
**Date:** November 14, 2025  
**Model Version:** CatBoost v2.0 FIELD-only  
**Status:** 🟡 **PRODUCTION DEPLOYMENT WITH ACKNOWLEDGED LIMITATIONS**

---

## 📋 Executive Summary

This document provides transparency about known limitations, edge cases, and areas for improvement in the IoT Sensor Failure Prediction Model v2. While the model has been scientifically validated (see MODEL_V2_VALIDATION_REPORT.md), stakeholders should be aware of these constraints when interpreting predictions and planning maintenance operations.

**Key Takeaway:** Model v2 is a **significant improvement** over v1 (contamination removed, temporal features added), but operates with **57.1% precision/recall** at baseline threshold 0.50. This means **~43% miss rate** - almost half of critical devices may not be detected.

---

## 🎯 Performance Limitations

### 1. Miss Rate: 42.9% (6 out of 14 critical devices)

**Issue:** Model fails to detect approximately **43% of critical devices** in test set

**Evidence:**
- Test set: 229 devices (14 critical, 215 normal)
- True Positives: 8 devices (57.1% detected)
- False Negatives: 6 devices (42.9% MISSED)
- Source: `metrics_discrepancy_investigation.py` (Nov 14, 2025)

**Impact:**
- **High-risk devices may go undetected** until catastrophic failure
- Maintenance teams cannot rely solely on model alerts
- Manual monitoring still required for critical infrastructure

**Root Causes:**
1. **Small dataset:** Only 46 critical devices in training (762 total)
2. **Class imbalance:** 6% critical vs 94% normal (even after SMOTE)
3. **Feature limitations:** 30 telemetry features may not capture all failure modes
4. **No hyperparameter tuning:** Default CatBoost parameters used

**Mitigation Strategies:**
- ✅ **FASE 3:** Add advanced temporal features (expected +20% recall → ~77%)
- ⚙️ **Hyperparameter tuning:** GridSearchCV on depth/iterations (expected +10-15% recall)
- 📊 **Data collection:** Gather more critical device examples (target 100+ samples)
- 🔍 **Ensemble methods:** Combine multiple models to reduce miss rate

**Recommendation for Stakeholders:**
- Use model as **early warning system**, NOT as sole decision criterion
- Implement **tiered monitoring:** Model alerts + periodic manual checks
- Prioritize **high-probability detections** (>80%) for immediate action
- Schedule **routine maintenance** for devices flagged at 50-80% probability

---

### 2. Baseline Precision/Recall: 57.1%

**Issue:** At default threshold 0.50, model achieves **57.1% precision AND 57.1% recall**

**Confusion Matrix (Threshold 0.50):**
```
┌─────────────────────────────┐
│  True Positive  (TP):    8  │  ← Correctly detected critical
│  False Positive (FP):    6  │  ← False alarms (unnecessary maintenance)
│  False Negative (FN):    6  │  ← Missed failures (high risk!)
│  True Negative  (TN):  209  │  ← Correctly identified normal
└─────────────────────────────┘
```

**Interpretation:**
- **Precision 57.1%:** Out of 14 devices flagged as critical, only 8 are actually critical (6 false alarms)
- **Recall 57.1%:** Out of 14 actual critical devices, only 8 are detected (6 missed)
- **F1-Score 0.571:** Balanced but low performance

**Impact:**
- **6 false positives** → Wasted maintenance resources (43% false alarm rate)
- **6 false negatives** → Undetected failures (43% miss rate)
- Business must **accept trade-off** between false alarms and missed failures

**Threshold Adjustment Trade-offs:**

| Threshold | Precision | Recall | False Positives | False Negatives | Use Case |
|-----------|-----------|--------|-----------------|-----------------|----------|
| **0.50** (baseline) | 57.1% | 57.1% | 6 devices | 6 devices | Balanced (default) |
| **0.60-0.70** | 🔺 Higher | ➡️ Same | 🔻 Fewer | ➡️ Same | Reduce false alarms |
| **0.40** | 🔻 Lower | 🔺 Higher | 🔺 More | 🔻 Fewer | Maximize detection (critical infra) |

**Note:** Threshold adjustment on 789 mixed dataset showed 90.9% precision at 0.60, but this was NOT reproducible on pure 762 FIELD-only test set. **Do not use 83.3% precision as reference** - it's artificially inflated by dataset contamination.

---

### 3. Metrics Discrepancy (Resolved)

**Issue:** Initial threshold experiment reported **83.3% precision** but true baseline is **57.1%**

**Cause Identified (Nov 14, 2025):**
- Threshold experiment used **789 devices (mixed FIELD + FACTORY)**
- Model v2 trained on **762 devices (FIELD-only)** - 27 FACTORY removed
- Feature `days_since_last_message` was **imputed as 0** in mixed dataset (didn't exist in v1)
- FACTORY devices are easier to classify (lab testing signatures) → inflated precision

**Proof:**
```python
# Threshold experiment (789 mixed)
Precision: 83.3%  |  Recall: 71.4%  |  Dataset: device_features_with_telemetry.csv

# Metrics investigation (762 FIELD-only - CORRECT)
Precision: 57.1%  |  Recall: 57.1%  |  Dataset: device_features_with_telemetry_field_only.csv
```

**Resolution:**
- ✅ **Correct baseline:** 57.1% precision / 57.1% recall
- ✅ **Discrepancy explained:** Dataset difference (27 FACTORY devices)
- ✅ **Documentation updated:** Validation report and metadata corrected

**Lesson Learned:**
- Always validate metrics on **EXACT training/test split**
- Dataset composition (FIELD vs FACTORY) significantly impacts performance
- Feature imputation can mask true model behavior

---

## 🔍 Feature & Model Limitations

### 4. Signal Variance Ambiguity

**Issue:** Signal features (`rsrp_std`, `snr_std`) are highly important (#5, #11 rank) but may flag **environmental issues** instead of **device degradation**

**Evidence:**
- Device 861275072514504: **rsrp_std z-score +4.94σ** (EXTREME outlier)
  - Signal highly unstable BUT hardware healthy (battery, temp, optical all normal)
  - **Could be:** Antenna obstruction, network handover, cell tower switching
  - **Or could be:** Early-stage degradation (connectivity fails before hardware)
  
- Device 861275072341072: **rsrq_min z-score -3.65σ**
  - Historical signal quality dip BUT device operational (regular hourly msgs)
  - CSV shows battery 3.33-3.44V, temp 15-33°C (normal ranges)
  - **Likely:** Environmental false positive

**Impact:**
- **Cannot distinguish** device fault vs environmental/network issues
- Signal variance may trigger alerts for **external factors** (not device health)
- Maintenance teams may investigate healthy devices in poor signal areas

**Root Cause:**
- Signal metrics (`rsrp`, `rsrq`, `snr`) measure **network quality**, not device health
- Variance could indicate:
  1. Device modem degradation (antenna, RF circuitry failure) ← **DEVICE ISSUE**
  2. Physical obstruction (debris, ice, vegetation growth) ← **ENVIRONMENTAL**
  3. Network changes (tower maintenance, handover issues) ← **NETWORK ISSUE**
  4. Mobility (device vibration, movement) ← **INSTALLATION ISSUE**

**Pending Investigation:**
- **Ground truth validation** needed to determine correlation
- If signal variance outliers **do NOT** correlate with failures → consider removing/de-weighting features
- If **DO** correlate → model may have **predictive capability** (early warning system)

**Temporary Mitigation:**
- For devices flagged ONLY by signal variance (like 861275072514504):
  1. Check installation environment (antenna visibility, obstructions)
  2. Verify network coverage maps (weak signal areas)
  3. Monitor for 30-60 days post-detection (predictive test)
  4. Prioritize devices with **multi-dimensional outliers** (signal + battery + temp)

---

### 5. No Hyperparameter Tuning

**Issue:** Model uses **default CatBoost parameters** - no optimization performed

**Current Configuration:**
```python
CatBoostClassifier(
    iterations=100,      # Default (could test 200, 300)
    depth=6,             # Default (could test 4, 8, 10)
    learning_rate=0.1,   # Default (could test 0.05, 0.15)
    random_state=42
)
```

**Impact:**
- Model may be **under-optimized** for this specific dataset
- Potential performance gains left on table (~10-15% recall improvement)
- Trade-off between overfitting and generalization not explored

**Why Not Tuned:**
- FASE 2 focused on **data quality** (FACTORY removal) not model optimization
- GridSearchCV is computationally expensive (small team, limited resources)
- Baseline performance (57.1%) deemed **acceptable for v2 release**

**Recommendation for FASE 3:**
```python
# Proposed hyperparameter search space
param_grid = {
    'classifier__iterations': [100, 200, 300],
    'classifier__depth': [4, 6, 8, 10],
    'classifier__learning_rate': [0.05, 0.1, 0.15],
    'classifier__l2_leaf_reg': [1, 3, 5, 7]
}

# Expected improvement: +10-15% recall
# New baseline: 57% → ~67-72% recall
```

---

### 6. Small Dataset Size

**Issue:** Only **762 devices** total, with just **46 critical** (6% class imbalance)

**Breakdown:**
- Total devices: 762 (FIELD-only)
- Critical: 46 (6.0%)
- Normal: 716 (94.0%)
- Train set: 533 devices (32 critical)
- Test set: 229 devices (14 critical)

**Impact:**
- **Limited generalization:** Model may not capture rare failure modes
- **Overfitting risk:** Small sample size increases variance
- **Class imbalance:** SMOTE helps but can't fully compensate
- **Test set uncertainty:** Only 14 critical devices in test (high variance in metrics)

**Industry Comparison:**
- **Ideal dataset:** 1,000+ devices, 100+ critical samples
- **Current dataset:** 762 devices, 46 critical samples ← **BELOW IDEAL**

**Data Collection Recommendations:**
1. **Expand FIELD dataset:** Target 1,500 devices (100+ critical)
2. **Time-series extension:** Wait 3-6 months for natural failures to occur
3. **Active learning:** Prioritize labeling high-uncertainty predictions
4. **Cross-validation:** Use 5-fold CV to maximize training data utilization

---

### 7. Temporal Feature Limitations

**Issue:** Only **1 temporal feature** (`days_since_last_message`) - limited time-based context

**Current State:**
- `days_since_last_message`: Rank #8/30 (4.73% importance) ← Useful but basic
- No deployment age tracking
- No activity trend analysis
- No degradation rate calculations

**Missing Temporal Features (FASE 3):**
```python
# Planned additions
'deployment_age'          # Days since first message (device lifetime)
'last_active_period'      # Days of recent activity (engagement)
'msg_last_7days'          # Message count last 7 days (trend)
'msg_last_30days'         # Message count last 30 days (activity level)
'optical_delta'           # Change in optical readings over time
'battery_delta'           # Battery degradation rate
'temp_trend'              # Temperature trend (increasing = overheating)
```

**Expected Impact:**
- **+20% recall improvement** (57% → ~77%)
- Better capture of **degradation patterns** (slow failures vs sudden failures)
- Distinguish **inactive** devices (potential failures) vs **decommissioned** devices

---

## ⚠️ Edge Cases & Known Failure Modes

### 8. Borderline Probability Devices (50-70%)

**Issue:** Devices with probabilities near threshold are **high uncertainty**

**Example:**
- Device 861275072341072: **59.8% probability** (just above 50% threshold)
  - Only 1 outlier (rsrq_min z-score -3.65σ)
  - CSV shows healthy operation (battery, temp normal)
  - **Verdict:** Likely false positive

**Recommendation:**
- Probabilities **50-70%:** LOW CONFIDENCE - monitor but don't prioritize
- Probabilities **70-85%:** MODERATE CONFIDENCE - schedule inspection within 30 days
- Probabilities **>85%:** HIGH CONFIDENCE - immediate action required

**Threshold Sensitivity:**
- Small changes in threshold (0.50 → 0.55) can flip classification
- Use **probability score** directly, not just binary critical/normal

---

### 9. Devices with Single Outliers

**Issue:** Devices flagged by only 1 feature may be **false positives** or **environmental issues**

**Pattern:**
- Device 861275072341072: 1 outlier (rsrq_min) → **FALSE POSITIVE**
- Device 861275072514504: 2 outliers (rsrp_std, snr_std) → **UNCERTAIN**
- Device 866207059671895: 12 outliers (temp, battery, optical, signal) → **LEGITIMATE**

**Decision Matrix:**
```
Outlier Count | Probability | Action
0-1 outliers  | <70%        | Monitor only (likely FP)
2-4 outliers  | 70-85%      | Inspect within 30 days
5+ outliers   | >85%        | CRITICAL - immediate maintenance
```

---

### 10. FACTORY Data Contamination (Resolved in v2)

**Issue (Historical):** v1 included 362,343 FACTORY messages (31.8% of data) causing false positives

**Example:**
- Device 861275072515287 flagged as critical in v1
- Investigation revealed **lab testing messages** (battery 0.0V, optical max values)
- Device was NOT deployed yet - contamination from pre-deployment testing

**Resolution in v2:**
- ✅ All FACTORY messages removed (MODE='FIELD' filter)
- ✅ 27 FACTORY-only devices excluded from training
- ✅ Dataset purified to 762 FIELD-only devices

**Status:** ✅ **RESOLVED** - v2 is clean

---

## 🔄 Comparison: v1 vs v2 Trade-offs

| Metric | v1 (Mixed) | v2 (FIELD-only) | Change | Interpretation |
|--------|------------|-----------------|--------|----------------|
| **Dataset Size** | 789 devices | 762 devices | -27 | FACTORY removed |
| **Critical Devices** | 46 | 46 | 0 | Same ground truth |
| **Features** | 29 | 30 | +1 | Added `days_since_last_message` |
| **AUC** | 0.8621 | 0.9186 | **+6.6%** | ✅ Better discrimination |
| **Recall** | 78.6% | 57.1% | **-21.5%** | ⚠️ Misses more failures |
| **Precision** | ? | 57.1% | ? | Unknown v1 baseline |
| **False Positives** | HIGH | MODERATE | ✅ Reduced | Lifecycle contamination fixed |

**Key Insight:**
- v2 traded **-21.5% recall** for **+6.6% AUC** and **contamination removal**
- v1 detected more failures BUT had **systematic false positives** (FACTORY data)
- v2 is **more reliable** (fewer false alarms) but **more conservative** (misses borderline cases)

**Decision Rationale:**
- **Quality over quantity:** Better to miss some failures than flood maintenance with false alarms
- **Trust building:** v1 false positives eroded user trust in model
- **FASE 3 recovery:** Temporal features expected to recover lost recall (+20% → ~77%)

---

## 📈 Roadmap: Planned Improvements

### Short-Term (Next 30 Days)

1. **Ground Truth Validation** ⏳ (BLOCKED - awaiting Enzo)
   - Validate 3 critical devices against STI Dashboard
   - Determine if signal variance correlates with failures
   - Refine feature weights based on operational data

2. **Threshold Optimization** 🔧
   - If ground truth confirms high FP rate → increase threshold to 0.60
   - If confirms high miss rate → decrease threshold to 0.40
   - Create **tiered alert system** (LOW/MEDIUM/HIGH confidence)

3. **Documentation** 📝
   - Share Known Issues with stakeholders
   - Update Streamlit app with threshold recommendations
   - Create user guide for interpreting probabilities

### Medium-Term (FASE 3 - Next 60-90 Days)

4. **Advanced Temporal Features** 🚀
   - Add 7 time-based features (deployment_age, activity_trends, delta calculations)
   - Expected: **+20% recall** (57% → ~77%)
   - Reduce miss rate from 43% to ~23%

5. **Hyperparameter Tuning** ⚙️
   - GridSearchCV on CatBoost parameters
   - Expected: **+10-15% recall** (cumulative ~87-92% with FASE 3)
   - Test ensemble methods (CatBoost + XGBoost + LightGBM)

6. **Data Expansion** 📊
   - Collect 6 more months of operational data
   - Target 1,500 devices (100+ critical samples)
   - Retrain with larger, more diverse dataset

### Long-Term (Next 6-12 Months)

7. **Real-Time Monitoring** 📡
   - Integrate with live telemetry stream
   - Generate alerts within 1 hour of anomaly detection
   - Deploy edge computing for on-device inference

8. **Explainability Dashboard** 🔍
   - SHAP values for each prediction
   - Feature contribution breakdown per device
   - "Why was this device flagged?" transparency

9. **Continuous Learning** 🔄
   - Auto-retrain monthly with new labeled data
   - A/B testing of model versions
   - Feedback loop from maintenance teams

---

## ✅ Acceptance Criteria for Production

**Model v2 is approved for production deployment IF:**

- ✅ **Baseline performance understood:** 57.1% precision/recall acknowledged by stakeholders
- ✅ **Miss rate acceptable:** Business accepts 43% miss rate (supplemented by manual checks)
- ✅ **False positive rate acceptable:** 43% false alarm rate acceptable for maintenance capacity
- ✅ **Contamination removed:** FACTORY data excluded (Discovery 0 validated)
- ✅ **Scientific validation:** 3 experiments completed (devices, features, threshold)
- ⏳ **Ground truth pending:** Awaiting operational validation from Enzo

**Deployment Recommendations:**

1. **Use as early warning system** - NOT sole decision criterion
2. **Tiered alerts:** HIGH (>85%), MEDIUM (70-85%), LOW (50-70%)
3. **Multi-dimensional checks:** Prioritize devices with 5+ outliers
4. **Manual review:** Inspect signal-only outliers for environmental issues
5. **Monitoring period:** 30-60 day observation for 70-85% probability devices
6. **Feedback collection:** Track maintenance outcomes to refine model

---

## 📞 Support & Escalation

**Model Owner:** Leonardo Costa (Data Science Team)  
**Stakeholder Contact:** Enzo (STI Dashboard - Operational Validation)  
**Documentation:** 
- `docs/MODEL_V2_VALIDATION_REPORT.md` (Technical validation)
- `docs/PLANO_ACAO_FIX_FALSOS_POSITIVOS.md` (FASE 2 planning)
- `CHANGELOG.md` (Discovery 0 - Lifecycle contamination)

**Issue Reporting:**
- False positives: Report device ID + operational evidence (STI logs, CSV messages)
- False negatives: Report failed device ID + failure timestamp
- Feature requests: FASE 3 planning backlog

---

## 🏷️ Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-14 | Initial release - Known issues documented post-validation |

**Last Updated:** November 14, 2025  
**Next Review:** After ground truth validation (Enzo feedback)
