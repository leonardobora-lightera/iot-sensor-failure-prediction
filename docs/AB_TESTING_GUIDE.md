# A/B Testing Guide - Model Validation in Production

**Document Purpose:** Practical guide for validating IoT sensor failure prediction model in production using stratified A/B testing methodology. Ensures model performs reliably across different deployment patterns, hardware configurations, and environments before full deployment.

**Target Audience:** ML Engineers, DevOps, Product Managers deploying model to production

**Prerequisites:** Read `docs/TEMPORAL_LIMITATIONS.md` to understand model validity regime constraints

**Last Updated:** November 11, 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Why A/B Testing is Critical](#why-ab-testing-is-critical)
3. [Deployment Strategy Overview](#deployment-strategy-overview)
4. [Phase 1: Shadow Mode (30-60 days)](#phase-1-shadow-mode-30-60-days)
5. [Phase 2: Metrics Validation](#phase-2-metrics-validation)
6. [Phase 3: Stratified A/B Test](#phase-3-stratified-ab-test)
7. [Phase 4: Gradual Rollout](#phase-4-gradual-rollout)
8. [Regime-Specific Deployment](#regime-specific-deployment)
9. [Monitoring and Alerting](#monitoring-and-alerting)
10. [Rollback Procedures](#rollback-procedures)
11. [Appendix A: Metrics Calculation](#appendix-a-metrics-calculation)
12. [Appendix B: Example Code](#appendix-b-example-code)

---

## Executive Summary

### The Problem

Current model achieved **78.6% recall** and **84.6% precision** on test set, but test set may not represent production diversity:

- Different deployment patterns (lab-tested vs direct-deploy)
- Different hardware batches (sensor lots, firmware versions)
- Different environments (geographic regions, climates)
- Different operational contexts (customer types, use cases)

**Deploying blindly risks catastrophic failures** (false negatives missing critical devices) in underrepresented scenarios.

### The Solution

**4-phase stratified validation:**

1. **Shadow Mode** (30-60 days): Collect predictions without acting, build ground truth dataset
2. **Metrics Validation**: Calculate recall/precision per stratum (deployment pattern, hardware, environment)
3. **Stratified A/B Test**: Deploy model only to validated strata, baseline for others
4. **Gradual Rollout**: Expand to 100% in validated strata, conditional deployment elsewhere

### Success Criteria

Model is **approved for production deployment** to a stratum if:

- ✅ Recall ≥ 75% (maximum 25% false negative rate)
- ✅ Precision ≥ 80% (maximum 20% false positive rate)
- ✅ Performance NOT more than 10% below overall average
- ✅ Sample size ≥ 50 devices in stratum (statistical power)
- ✅ At least 5 critical failures observed in stratum (class balance)

If stratum FAILS criteria:
- ❌ DO NOT deploy model to that stratum
- ❌ Use baseline approach (manual inspection, rule-based heuristics)
- ❌ Collect more data, retrain model, or develop stratum-specific model

---

## Why A/B Testing is Critical

### Test Set Limitations

**Test set validation (78.6% recall, 84.6% precision) proves:**
- ✅ Model learned patterns that generalize within test distribution
- ✅ Model better than random (baseline ~6% prevalence)

**Test set validation does NOT prove:**
- ❌ Model generalizes to deployment patterns underrepresented in training (e.g., direct-deploy devices)
- ❌ Model generalizes to new hardware batches (e.g., different battery supplier)
- ❌ Model generalizes to different environments (e.g., tropical vs temperate climate)
- ❌ Model learned causal patterns (sensor physics) vs simultaneous patterns (at-failure symptoms)

### Real-World Risks

**Without A/B testing, you CANNOT detect:**

**Risk 1: Deployment Pattern Overfitting**
- Training data: 90% lab-tested devices (lab→inactive→production lifecycle)
- Production: 60% direct-deploy devices (no lab testing, always active)
- **Model fails on direct-deploy:** Recall drops to 40% because learned "high optical_std = inactive period = critical" (artifact), not "optical degradation = critical" (physics)

**Risk 2: Hardware Batch Shift**
- Training data: Battery supplier A, nominal voltage 3.7V
- Production: Battery supplier B, nominal voltage 3.85V (different chemistry)
- **Model produces false positives:** Healthy devices with battery_mean=3.65V flagged as critical because model learned "battery_mean < 3.7V = critical" from training

**Risk 3: Environmental Shift**
- Training data: Temperate climate, temp_mean=22°C
- Production deployment: Tropical region, temp_mean=32°C
- **Model miscalibrated:** Temp↔battery correlation different at higher temperatures, prediction unreliable

**Risk 4: Silent Degradation**
- Model performs well initially (validated strata)
- Deployment expands to new customer segment
- Performance degrades gradually over months
- **No alert until catastrophic failures accumulate**

### A/B Testing Benefits

**What A/B testing provides:**

1. **Quantified performance per stratum** - Know exactly where model works and where it fails
2. **Safe deployment** - Start with small subset, expand only if validated
3. **Early detection of failures** - Catch issues before full deployment
4. **Data-driven decisions** - Deploy based on evidence, not assumptions
5. **Continuous learning** - Collect ground truth for model improvement
6. **Regulatory compliance** - Auditable validation process for high-stakes domains

---

## Deployment Strategy Overview

### 4-Phase Approach

```
Phase 1: Shadow Mode (30-60 days)
├── Collect predictions WITHOUT acting
├── Build ground truth dataset (actual device failures)
├── No impact on operations (safe)
└── Output: Baseline performance metrics

Phase 2: Metrics Validation (1 week)
├── Calculate recall/precision per stratum
├── Identify validated strata (meet success criteria)
├── Identify failed strata (below criteria)
└── Output: Deployment decision matrix

Phase 3: Stratified A/B Test (30-60 days)
├── Deploy model to validated strata only
├── Baseline approach for failed strata
├── Monitor performance continuously
└── Output: Production performance validation

Phase 4: Gradual Rollout (ongoing)
├── Expand to 100% in validated strata
├── Recalibrate or retrain for failed strata
├── Continuous drift monitoring
└── Output: Full production deployment
```

### Timeline

**Minimum timeline:** 60-120 days from start to full deployment

- Days 0-60: Shadow mode
- Days 60-67: Metrics validation and decision
- Days 67-127: Stratified A/B test
- Days 127+: Gradual rollout and monitoring

**Do NOT rush this process.** False negatives (missed critical failures) have high cost.

### Resources Required

**Data collection:**
- Prediction logging infrastructure
- Ground truth failure tracking (operational monitoring integration)
- Device metadata (deployment pattern, hardware batch, environment)

**Analysis:**
- Data scientist (stratification, metrics calculation, statistical power analysis)
- Domain expert (interpret failure modes, validate thresholds)

**Infrastructure:**
- Conditional deployment system (route devices to model vs baseline based on stratum)
- Monitoring dashboards (real-time performance tracking per stratum)
- Alerting system (detect performance degradation)

---

## Phase 1: Shadow Mode (30-60 days)

### Objective

Collect model predictions WITHOUT acting on them, build ground truth dataset of actual device failures.

### Setup

**1. Prediction Logging**

Log every prediction to database/data lake:

```python
# models/inference.py
import logging
import json
from datetime import datetime

def predict_with_logging(device_features, device_metadata):
    """Run inference and log prediction for shadow mode."""
    
    # Run model inference
    prediction = model.predict(device_features)
    probability = model.predict_proba(device_features)[:, 1]
    
    # Log prediction
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'device_id': device_metadata['device_id'],
        'prediction': int(prediction[0]),
        'probability': float(probability[0]),
        'features': device_features.to_dict(orient='records')[0],
        'metadata': device_metadata,
        'model_version': 'v1.0.0',
        'deployment_mode': 'shadow'
    }
    
    # Store to database/data lake
    logger.info(json.dumps(log_entry))
    # OR: db.predictions.insert_one(log_entry)
    # OR: kinesis.put_record(Data=json.dumps(log_entry))
    
    # IMPORTANT: Do NOT act on prediction in shadow mode
    return None  # Return None to indicate no action taken
```

**2. Ground Truth Collection**

Track actual device failures:

```python
# monitoring/failure_tracker.py
def log_device_failure(device_id, failure_timestamp, failure_type):
    """Log actual device failure for ground truth."""
    
    failure_entry = {
        'device_id': device_id,
        'failure_timestamp': failure_timestamp,
        'failure_type': failure_type,  # 'critical', 'warning', 'operational'
        'ground_truth': 1  # Critical failure
    }
    
    # Store to database
    db.failures.insert_one(failure_entry)
```

**3. Metadata Enrichment**

Collect device metadata for stratification:

```python
# Required metadata fields
device_metadata = {
    'device_id': str,
    'deployment_pattern': str,  # 'lab_tested', 'direct_deploy', 'reactivated'
    'sensor_batch': str,  # Manufacturing lot
    'firmware_version': str,  # e.g., 'v2.3.1'
    'geographic_region': str,  # e.g., 'North America', 'Europe', 'Asia'
    'climate_zone': str,  # e.g., 'temperate', 'tropical', 'arid'
    'customer_type': str,  # e.g., 'enterprise', 'consumer'
    'activation_date': datetime,
    'last_message_timestamp': datetime
}
```

### Execution

**Week 1-2: Infrastructure Setup**
- Deploy prediction logging
- Integrate failure tracking with operational monitoring
- Validate data pipeline (check logs arriving correctly)

**Week 3-8: Data Collection**
- Predict on ALL production devices
- Log predictions (do NOT act)
- Continue using current baseline approach for decision-making
- Track failures as they occur

**Week 9: Data Quality Check**
- Verify ≥ 500 devices with predictions
- Verify ≥ 30 critical failures observed
- Check metadata completeness (>95% devices have required fields)

### Success Criteria for Phase 1

✅ **Minimum sample size:** 500 devices with predictions  
✅ **Minimum failures:** 30 critical failures observed  
✅ **Metadata coverage:** >95% devices have deployment_pattern, sensor_batch, firmware_version  
✅ **Time window:** At least 30 days (captures temporal patterns)  
✅ **Baseline performance:** Current approach still operational (no disruption)

If criteria NOT met: Extend shadow mode until sufficient data collected.

---

## Phase 2: Metrics Validation

### Objective

Calculate model performance per stratum, identify which strata meet success criteria for deployment.

### Stratification Strategy

**Primary Strata: Deployment Pattern** (CRITICAL for lifecycle confounding)

```python
strata_deployment = {
    'lab_tested_inactive_production': devices with lab testing + inactive period + production,
    'direct_deploy_always_active': devices shipped directly, no lab testing, always active,
    'reactivated': devices with multiple inactive → active cycles,
    'unknown': deployment pattern not determinable from metadata
}
```

**Secondary Strata: Hardware Batch** (if sufficient sample size)

```python
strata_hardware = {
    'batch_A': sensor_batch in ['LOT_2024_Q1', 'LOT_2024_Q2'],
    'batch_B': sensor_batch in ['LOT_2024_Q3', 'LOT_2024_Q4'],
    'batch_C': sensor_batch in ['LOT_2025_Q1'],
}
```

**Tertiary Strata: Environment** (if sufficient sample size)

```python
strata_environment = {
    'temperate': climate_zone == 'temperate',
    'tropical': climate_zone == 'tropical',
    'arid': climate_zone == 'arid',
}
```

### Metrics Calculation

For each stratum, calculate:

**1. Confusion Matrix**

```python
import pandas as pd
from sklearn.metrics import recall_score, precision_score, confusion_matrix

# Load shadow mode data
predictions = pd.read_sql("SELECT * FROM predictions WHERE deployment_mode='shadow'", con=db)
failures = pd.read_sql("SELECT device_id, ground_truth FROM failures", con=db)

# Merge predictions with ground truth
# Assume device is critical if it failed within 7 days of prediction
df = predictions.merge(failures, on='device_id', how='left')
df['ground_truth'] = df['ground_truth'].fillna(0)  # Devices that didn't fail = healthy

# Calculate metrics per stratum
for stratum in strata_deployment:
    stratum_devices = df[df['deployment_pattern'] == stratum]
    
    if len(stratum_devices) < 50:
        print(f"⚠️ Stratum {stratum}: insufficient sample size ({len(stratum_devices)} < 50)")
        continue
    
    # Confusion matrix
    y_true = stratum_devices['ground_truth']
    y_pred = stratum_devices['prediction']
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    recall = recall_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    
    print(f"\n{stratum}:")
    print(f"  Sample size: {len(stratum_devices)} devices")
    print(f"  Critical failures: {sum(y_true)} ({sum(y_true)/len(y_true)*100:.1f}%)")
    print(f"  Recall: {recall:.1%} (TP={tp}/{tp+fn})")
    print(f"  Precision: {precision:.1%} (TP={tp}/{tp+fp})")
    print(f"  Confusion matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
```

**2. Performance vs Overall Average**

```python
# Overall performance (all devices)
overall_recall = recall_score(df['ground_truth'], df['prediction'])
overall_precision = precision_score(df['ground_truth'], df['prediction'])

# Per stratum comparison
for stratum in strata_deployment:
    stratum_devices = df[df['deployment_pattern'] == stratum]
    stratum_recall = recall_score(stratum_devices['ground_truth'], stratum_devices['prediction'])
    
    delta_recall = (stratum_recall - overall_recall) / overall_recall * 100
    
    if delta_recall < -10:
        print(f"❌ {stratum}: Recall {delta_recall:.1f}% below average (FAILED)")
    else:
        print(f"✅ {stratum}: Recall {delta_recall:.1f}% vs average (OK)")
```

### Decision Matrix

Classify each stratum:

| Stratum | Sample Size | Recall | Precision | Delta vs Avg | **Decision** |
|---------|-------------|--------|-----------|--------------|--------------|
| lab_tested | 350 | 79% | 86% | +0.4% | ✅ **DEPLOY** |
| direct_deploy | 120 | 55% | 78% | -23.6% | ❌ **REJECT** |
| reactivated | 80 | 85% | 82% | +6.4% | ✅ **DEPLOY** |
| unknown | 50 | 70% | 75% | -8.6% | ⚠️ **CAUTION** (borderline) |

**Action:**
- ✅ Deploy model to `lab_tested` and `reactivated` strata
- ❌ Do NOT deploy to `direct_deploy` (use baseline instead)
- ⚠️ For `unknown`: Use model with higher probability threshold (e.g., >0.7 instead of >0.5)

### Output: Deployment Configuration

```python
# config/deployment_strata.yaml
approved_strata:
  - deployment_pattern: lab_tested_inactive_production
    min_probability: 0.5
    enabled: true
  
  - deployment_pattern: reactivated
    min_probability: 0.5
    enabled: true

rejected_strata:
  - deployment_pattern: direct_deploy_always_active
    reason: "Recall 55% < 75% threshold. Use baseline approach."
    enabled: false

cautionary_strata:
  - deployment_pattern: unknown
    min_probability: 0.7  # Higher threshold due to borderline performance
    enabled: true
    monitoring_frequency: daily
```

---

## Phase 3: Stratified A/B Test

### Objective

Deploy model to validated strata, continue baseline for rejected strata, monitor performance continuously.

### A/B Split Design

**NOT a 50/50 random split.** Use **stratum-based routing**:

**Group A: Model**
- Devices in approved strata (lab_tested, reactivated)
- Model makes predictions, system acts on them

**Group B: Baseline**
- Devices in rejected strata (direct_deploy)
- Current baseline approach (manual inspection, rule-based heuristics)

**Group C: Cautionary (Model with High Threshold)**
- Devices in borderline strata (unknown)
- Model predicts, but only act if probability > 0.7

### Implementation

```python
# models/conditional_deployment.py
import yaml

# Load deployment configuration
with open('config/deployment_strata.yaml') as f:
    deployment_config = yaml.safe_load(f)

def route_device(device_metadata):
    """Determine whether to use model or baseline for this device."""
    
    deployment_pattern = device_metadata.get('deployment_pattern', 'unknown')
    
    # Check approved strata
    for stratum in deployment_config['approved_strata']:
        if deployment_pattern == stratum['deployment_pattern']:
            return {
                'use_model': True,
                'min_probability': stratum['min_probability'],
                'group': 'A_model'
            }
    
    # Check rejected strata
    for stratum in deployment_config['rejected_strata']:
        if deployment_pattern == stratum['deployment_pattern']:
            return {
                'use_model': False,
                'reason': stratum['reason'],
                'group': 'B_baseline'
            }
    
    # Check cautionary strata
    for stratum in deployment_config['cautionary_strata']:
        if deployment_pattern == stratum['deployment_pattern']:
            return {
                'use_model': True,
                'min_probability': stratum['min_probability'],
                'group': 'C_cautionary'
            }
    
    # Default: use baseline for unknown patterns (conservative)
    return {
        'use_model': False,
        'reason': 'Deployment pattern not validated',
        'group': 'B_baseline'
    }

# Usage in inference pipeline
def make_decision(device_features, device_metadata):
    """Make critical/non-critical decision using model or baseline."""
    
    routing = route_device(device_metadata)
    
    if routing['use_model']:
        # Use model
        probability = model.predict_proba(device_features)[:, 1][0]
        
        if probability >= routing['min_probability']:
            decision = 'critical'
            confidence = probability
            method = 'model'
        else:
            decision = 'non_critical'
            confidence = 1 - probability
            method = 'model'
    else:
        # Use baseline approach
        decision, confidence = baseline_heuristic(device_features)
        method = 'baseline'
    
    # Log decision for monitoring
    log_decision(device_metadata['device_id'], decision, confidence, method, routing['group'])
    
    return decision, confidence, method
```

### Monitoring During A/B Test

**Daily dashboards:**

```sql
-- Performance by group (A/B/C)
SELECT 
    ab_group,
    COUNT(*) as total_devices,
    SUM(CASE WHEN ground_truth=1 THEN 1 ELSE 0 END) as actual_critical,
    SUM(CASE WHEN prediction=1 THEN 1 ELSE 0 END) as predicted_critical,
    SUM(CASE WHEN ground_truth=1 AND prediction=1 THEN 1 ELSE 0 END) as true_positives,
    SUM(CASE WHEN ground_truth=1 AND prediction=0 THEN 1 ELSE 0 END) as false_negatives
FROM ab_test_results
WHERE test_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY ab_group
```

**Alert thresholds:**

- ❌ **CRITICAL:** Any false negative in Group A with catastrophic consequence → immediate review
- ⚠️ **WARNING:** Recall in Group A drops >5% below shadow mode baseline → investigate
- ⚠️ **WARNING:** Precision in Group A drops >10% below shadow mode → check for false positive surge

### Duration

**Minimum 30 days, target 60 days** to:
- Accumulate sufficient failures (statistical power)
- Capture temporal patterns (weekly cycles, seasonal effects)
- Validate model stability over time

### Success Criteria for Phase 3

✅ **Group A (model) recall ≥ 75%** in production (confirms shadow mode findings)  
✅ **Group A precision ≥ 80%** in production  
✅ **No catastrophic failures** (false negatives with severe consequence)  
✅ **Drift monitoring shows KS < 0.2** (distribution stable)  
✅ **Group B (baseline) performance NOT significantly better** than Group A (model adds value)

If criteria MET: Proceed to Phase 4 (gradual rollout)  
If criteria NOT MET: Rollback, investigate root cause, retrain model

---

## Phase 4: Gradual Rollout

### Objective

Expand model deployment to 100% of validated strata, maintain conditional deployment for rejected strata.

### Rollout Schedule

**Week 1-2: 80% in Approved Strata**

```python
# Randomly assign 20% of approved stratum devices to baseline for ongoing A/B
if device in approved_stratum:
    if random.random() < 0.8:
        use_model = True  # 80%
    else:
        use_model = False  # 20% control group
```

**Week 3-4: 90% in Approved Strata**

Increase to 90% model, 10% baseline control.

**Week 5+: 100% in Approved Strata**

Full deployment to approved strata. Maintain small control group (5%) for ongoing monitoring.

### Ongoing Deployment Strategy

**Approved Strata (lab_tested, reactivated):**
- ✅ 95% use model
- ✅ 5% use baseline (control group for performance monitoring)

**Rejected Strata (direct_deploy):**
- ❌ 100% use baseline
- 📊 Continue collecting shadow mode predictions
- 🔄 Quarterly review: retrain model with new data, re-evaluate

**Cautionary Strata (unknown):**
- ⚠️ 100% use model with high threshold (probability > 0.7)
- 📊 Monitor performance closely (daily drift checks)

**New Strata (emerge over time):**
- ❌ Default to baseline (conservative)
- 🔍 Collect shadow mode predictions for 30 days
- 📊 Validate performance before enabling model

### Continuous Monitoring (Ongoing)

**Weekly:**
- Run drift_monitor.py on past week's data
- Check recall/precision per stratum (confirm no degradation)
- Review false negatives (any catastrophic failures missed?)

**Monthly:**
- Full performance report by stratum
- Update deployment configuration if strata performance changes
- Retrain model if drift sustained >4 weeks

**Quarterly:**
- Re-evaluate rejected strata (has new data improved model?)
- Test model on new strata (hardware batches, firmware versions)
- Update documentation and deployment guide

---

## Regime-Specific Deployment

### Conditional Routing Logic

```python
def should_use_model_v2(device_metadata, latest_drift_report):
    """Enhanced decision logic with drift monitoring integration."""
    
    # Check 1: Drift status (global)
    if latest_drift_report['overall_status'] == 'CRITICAL':
        return False, "CRITICAL drift detected - model disabled globally"
    
    # Check 2: Deployment pattern (stratum)
    deployment_pattern = device_metadata.get('deployment_pattern', 'unknown')
    
    if deployment_pattern in ['lab_tested_inactive_production', 'reactivated']:
        # Approved stratum
        min_prob = 0.5
        use_model = True
    elif deployment_pattern == 'direct_deploy_always_active':
        # Rejected stratum
        return False, "Deployment pattern not validated (direct_deploy)"
    elif deployment_pattern == 'unknown':
        # Cautionary stratum
        min_prob = 0.7
        use_model = True
    else:
        # Unknown pattern - conservative
        return False, f"Deployment pattern '{deployment_pattern}' not recognized"
    
    # Check 3: Hardware batch
    sensor_batch = device_metadata.get('sensor_batch')
    if sensor_batch not in VALIDATED_BATCHES:
        return False, f"Sensor batch '{sensor_batch}' not validated"
    
    # Check 4: Firmware version
    firmware_version = device_metadata.get('firmware_version')
    if firmware_version not in VALIDATED_FIRMWARE:
        return False, f"Firmware '{firmware_version}' not validated"
    
    # Check 5: Warning drift - increase threshold
    if latest_drift_report['overall_status'] == 'WARNING':
        min_prob = max(min_prob, 0.7)  # Stricter threshold during drift warning
    
    # All checks passed
    return True, f"Approved for stratum {deployment_pattern}, min_prob={min_prob}"
```

### Fallback Strategy

When model NOT used (rejected stratum, drift critical, etc.), use:

**Rule-Based Heuristics:**

```python
def baseline_heuristic(device_features):
    """Conservative rule-based critical device detection."""
    
    # Rule 1: Battery critically low
    if device_features['battery_mean'] < 3.1:
        return 'critical', 0.9
    
    # Rule 2: Optical sensor degraded + battery low
    if device_features['optical_mean'] < -10 and device_features['battery_mean'] < 3.3:
        return 'critical', 0.85
    
    # Rule 3: Connectivity severely degraded
    if device_features['rsrp_mean'] < -120 and device_features['rsrq_mean'] < -15:
        return 'critical', 0.8
    
    # Rule 4: Multiple sensors showing extreme values
    extreme_count = sum([
        device_features['optical_min'] < -20,
        device_features['temp_max'] > 70,
        device_features['battery_min'] < 2.9,
        device_features['snr_mean'] < -5
    ])
    
    if extreme_count >= 2:
        return 'critical', 0.75
    
    # Default: non-critical
    return 'non_critical', 0.6
```

**Manual Inspection Queue:**

For high-value devices or uncertain cases:

```python
if routing['use_model'] == False and device_metadata['customer_tier'] == 'enterprise':
    # Route to human expert for manual review
    queue_for_manual_inspection(device_metadata['device_id'], reason=routing['reason'])
```

---

## Monitoring and Alerting

### Key Metrics to Track

**Performance Metrics (Per Stratum):**

```python
# Daily aggregation
metrics_dashboard = {
    'stratum': deployment_pattern,
    'date': date,
    'total_devices': count,
    'predicted_critical': sum(predictions == 1),
    'actual_critical': sum(ground_truth == 1),
    'recall': TP / (TP + FN),
    'precision': TP / (TP + FP),
    'false_negatives': FN,
    'false_positives': FP,
    'avg_probability': mean(probabilities),
    'model_usage_rate': count(method='model') / total_devices
}
```

**Drift Metrics:**

```python
# Weekly drift monitoring
drift_dashboard = {
    'week': week_number,
    'max_ks_statistic': max(ks_statistics),
    'critical_features': [feat for feat in features if ks[feat] > 0.4],
    'warning_features': [feat for feat in features if 0.2 <= ks[feat] < 0.4],
    'lifecycle_drift_detected': bool,
    'overall_status': 'OK' | 'WARNING' | 'CRITICAL'
}
```

### Alert Conditions

**CRITICAL (Immediate Response):**

- ❌ Recall drops below 70% in any approved stratum
- ❌ Any false negative with catastrophic consequence (device failure caused injury, significant financial loss)
- ❌ Drift status = CRITICAL (KS > 0.4)
- ❌ Model availability < 95% (system failures)

**WARNING (Investigate Within 24h):**

- ⚠️ Recall drops 5-10% below baseline in approved stratum
- ⚠️ Precision drops >15% (surge in false positives)
- ⚠️ Drift status = WARNING (0.2 < KS < 0.4)
- ⚠️ False negative rate in Group A > false negative rate in Group B (baseline outperforming model)

**INFO (Review in Weekly Meeting):**

- ℹ️ New deployment pattern observed (not in current strata)
- ℹ️ New hardware batch or firmware version deployed
- ℹ️ Prediction rate changes >10% (e.g., 6% → 7%)

### Alerting Channels

```yaml
# config/alerting.yaml
alerts:
  critical:
    channels:
      - pagerduty: data-science-oncall
      - slack: "#ml-incidents"
      - email: ml-team@company.com
    escalation: 15min
  
  warning:
    channels:
      - slack: "#ml-monitoring"
      - email: ml-team@company.com
    escalation: 24h
  
  info:
    channels:
      - slack: "#ml-monitoring"
    escalation: none
```

---

## Rollback Procedures

### Trigger Conditions

**Immediate Rollback (Disable Model):**

1. Recall < 70% for 3 consecutive days in approved stratum
2. Catastrophic false negative (severity level 1 incident)
3. Drift CRITICAL sustained >48 hours
4. Model technical failure (prediction errors, NaN outputs)

**Gradual Rollback (Reduce Model Usage):**

1. Recall drops 5-10% below baseline (reduce from 100% → 50% → 0%)
2. Precision drops >20% (reduce model usage until false positive rate acceptable)
3. Drift WARNING sustained >7 days (enter cautionary mode with higher threshold)

### Rollback Execution

**Step 1: Disable Model**

```python
# Update deployment configuration
deployment_config['global_override'] = {
    'enabled': False,
    'reason': 'Recall dropped to 68% in lab_tested stratum',
    'effective_timestamp': datetime.utcnow(),
    'rollback_initiated_by': 'oncall_engineer_name'
}

# Save configuration (will be picked up by next deployment)
with open('config/deployment_strata.yaml', 'w') as f:
    yaml.dump(deployment_config, f)
```

**Step 2: Notify Stakeholders**

```python
# Send alert
send_alert(
    level='CRITICAL',
    message='Model rollback initiated due to performance degradation',
    details={
        'reason': 'Recall dropped to 68%',
        'affected_strata': ['lab_tested_inactive_production'],
        'action': 'Model disabled, baseline approach activated'
    }
)
```

**Step 3: Revert to Baseline**

All devices now use baseline heuristic approach (rule-based + manual inspection).

**Step 4: Root Cause Analysis**

```python
# Analysis checklist
root_cause_analysis = {
    'drift_detected': check_drift_report(),  # Is distribution shifting?
    'data_quality_issues': check_data_pipeline(),  # Are features correct?
    'ground_truth_accuracy': validate_labels(),  # Are failure labels correct?
    'model_degradation': check_model_version(),  # Was model updated?
    'system_bugs': check_logs_for_errors(),  # Any technical failures?
}
```

**Step 5: Remediation**

Depending on root cause:

- **Drift:** Retrain model with recent production data
- **Data quality:** Fix data pipeline, re-run predictions
- **Ground truth:** Re-label data, recalculate metrics
- **Model bug:** Rollback to previous model version
- **System bug:** Fix code, redeploy with testing

**Step 6: Re-validation**

Before re-enabling model:
- Run shadow mode for 14 days minimum
- Validate recall/precision meet criteria
- Get sign-off from data science lead

### Post-Rollback Review

**Required documentation:**

1. **Incident timeline:** When degradation started, when detected, when rolled back
2. **Root cause:** What caused performance degradation
3. **Impact:** How many false negatives occurred during degradation period
4. **Remediation:** What was done to fix the issue
5. **Prevention:** What changes prevent recurrence (e.g., better alerting, stricter thresholds)

---

## Appendix A: Metrics Calculation

### Recall (Sensitivity)

**Definition:** Percentage of actual critical devices correctly identified.

```
Recall = TP / (TP + FN)
```

Where:
- TP (True Positives): Critical devices correctly predicted as critical
- FN (False Negatives): Critical devices incorrectly predicted as non-critical

**Example:**
- 14 critical devices in test set
- Model predicts 11 as critical, misses 3
- Recall = 11 / (11 + 3) = 78.6%

**Business Impact:** False negatives = missed failures = potential safety/financial risks

**Target:** ≥ 75% (maximum 25% false negative rate acceptable)

### Precision (Positive Predictive Value)

**Definition:** Percentage of predicted critical devices that are actually critical.

```
Precision = TP / (TP + FP)
```

Where:
- TP (True Positives): Critical devices correctly predicted as critical
- FP (False Positives): Non-critical devices incorrectly predicted as critical

**Example:**
- Model predicts 13 devices as critical
- 11 are actually critical, 2 are false alarms
- Precision = 11 / (11 + 2) = 84.6%

**Business Impact:** False positives = unnecessary interventions = wasted resources, customer annoyance

**Target:** ≥ 80% (maximum 20% false positive rate acceptable)

### F1 Score (Harmonic Mean)

**Definition:** Balanced metric combining recall and precision.

```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

**Example:**
- Recall = 78.6%, Precision = 84.6%
- F1 = 2 * (0.846 * 0.786) / (0.846 + 0.786) = 81.5%

**Use case:** Overall model quality assessment, useful when class imbalance present

### Statistical Power

**Minimum sample size per stratum:**

For 80% statistical power to detect 10% performance difference:

```python
from statsmodels.stats.power import zt_ind_solve_power

# Parameters
effect_size = 0.1  # 10% difference in recall
alpha = 0.05  # Significance level
power = 0.8  # Statistical power

# Calculate required sample size
n = zt_ind_solve_power(effect_size=effect_size, alpha=alpha, power=power)
# Result: n ≈ 50 devices per stratum
```

**Guideline:** 
- Minimum 50 devices per stratum for stratified analysis
- Minimum 5 critical failures per stratum for recall calculation

---

## Appendix B: Example Code

### Complete A/B Test Analysis Script

```python
# scripts/ab_test_analysis.py
"""
A/B Test Performance Analysis - Stratified by Deployment Pattern

Usage:
    python scripts/ab_test_analysis.py \\
        --start-date 2025-10-01 \\
        --end-date 2025-11-11 \\
        --output reports/ab_test/
"""

import pandas as pd
import numpy as np
from sklearn.metrics import recall_score, precision_score, confusion_matrix, f1_score
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

def load_ab_test_data(start_date, end_date):
    """Load predictions and ground truth from database."""
    query = f"""
    SELECT 
        p.device_id,
        p.prediction,
        p.probability,
        p.deployment_pattern,
        p.ab_group,
        COALESCE(f.ground_truth, 0) as ground_truth
    FROM predictions p
    LEFT JOIN failures f ON p.device_id = f.device_id
    WHERE p.prediction_date >= '{start_date}'
      AND p.prediction_date <= '{end_date}'
      AND p.deployment_mode = 'ab_test'
    """
    # df = pd.read_sql(query, con=database_connection)
    # For demo, load from CSV:
    df = pd.read_csv('data/ab_test_results.csv')
    return df

def analyze_stratum(df, stratum_name, stratum_filter):
    """Calculate metrics for one stratum."""
    stratum_df = df[stratum_filter]
    
    if len(stratum_df) < 50:
        return {
            'stratum': stratum_name,
            'sample_size': len(stratum_df),
            'status': 'INSUFFICIENT_DATA',
            'message': f'Only {len(stratum_df)} devices, need ≥50'
        }
    
    y_true = stratum_df['ground_truth']
    y_pred = stratum_df['prediction']
    
    if y_true.sum() < 5:
        return {
            'stratum': stratum_name,
            'sample_size': len(stratum_df),
            'critical_count': int(y_true.sum()),
            'status': 'INSUFFICIENT_FAILURES',
            'message': f'Only {y_true.sum()} failures, need ≥5'
        }
    
    # Calculate metrics
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    recall = recall_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    # Determine status
    if recall >= 0.75 and precision >= 0.80:
        status = 'APPROVED'
    elif recall < 0.75:
        status = 'REJECTED_LOW_RECALL'
    elif precision < 0.80:
        status = 'REJECTED_LOW_PRECISION'
    else:
        status = 'APPROVED'
    
    return {
        'stratum': stratum_name,
        'sample_size': len(stratum_df),
        'critical_count': int(y_true.sum()),
        'prevalence': f"{y_true.mean():.1%}",
        'recall': recall,
        'precision': precision,
        'f1_score': f1,
        'TP': int(tp),
        'FP': int(fp),
        'FN': int(fn),
        'TN': int(tn),
        'status': status
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', required=True)
    parser.add_argument('--end-date', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    # Load data
    print(f"Loading A/B test data from {args.start_date} to {args.end_date}...")
    df = load_ab_test_data(args.start_date, args.end_date)
    print(f"Loaded {len(df)} devices")
    
    # Analyze by deployment pattern
    strata = {
        'lab_tested': df['deployment_pattern'] == 'lab_tested_inactive_production',
        'direct_deploy': df['deployment_pattern'] == 'direct_deploy_always_active',
        'reactivated': df['deployment_pattern'] == 'reactivated',
        'unknown': df['deployment_pattern'] == 'unknown'
    }
    
    results = []
    for stratum_name, stratum_filter in strata.items():
        result = analyze_stratum(df, stratum_name, stratum_filter)
        results.append(result)
        print(f"\n{stratum_name}: {result['status']}")
        if result.get('recall'):
            print(f"  Recall: {result['recall']:.1%}, Precision: {result['precision']:.1%}")
    
    # Save results
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_dir / 'stratum_analysis.csv', index=False)
    
    print(f"\n✅ Analysis complete. Results saved to {output_dir}")

if __name__ == '__main__':
    main()
```

---

**Document version:** 1.0  
**Last updated:** 2025-11-11  
**Review cadence:** After each A/B test cycle  
**Next review:** After Phase 3 completion
