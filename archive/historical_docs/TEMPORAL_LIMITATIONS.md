# TEMPORAL LIMITATIONS - Model Validity Regime Documentation

**Document Purpose:** Honest technical documentation of temporal and lifecycle limitations in current model training data, their implications for predictive causality, generalization risks, and mitigation strategies.

**Audience:** Technical stakeholders, data scientists, ML engineers, product managers deploying this model in production.

**Last Updated:** November 11, 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Dataset Structure Analysis](#dataset-structure-analysis)
3. [Lifecycle Phases Confounding](#lifecycle-phases-confounding)
4. [Temporal Causality Impossibility](#temporal-causality-impossibility)
5. [Deployment Pattern Learning Risk](#deployment-pattern-learning-risk)
6. [Generalization Risks](#generalization-risks)
7. [Model Validity Regime](#model-validity-regime)
8. [Mitigation Strategies](#mitigation-strategies)
9. [Recommendations for Future Work](#recommendations-for-future-work)

---

## Executive Summary

### Core Issue

The current IoT sensor failure prediction model achieves **78.6% recall** and **84.6% precision** on test data, but has **fundamental limitations** in temporal causality due to dataset structure. Features are aggregated over the **entire lifecycle** of each device (including lab testing, inactive periods, and production), making it **mathematically impossible** to distinguish:

- **Causal patterns** (sensor degradation observable 30+ days BEFORE failure)
- **Simultaneous patterns** (sensor state AT THE MOMENT of failure)

### Why This Matters

If the model learned simultaneous correlations (e.g., "battery=3.0V when device fails") rather than causal patterns (e.g., "battery degradation trend over 30 days predicts failure"), it will:

- ✅ Perform well on test set (similar devices, similar deployment patterns)
- ❌ **Fail catastrophically** on new device batches, different environments, or different deployment workflows
- ❌ **Not generalize** to "sensors it has never observed" (user's primary concern)

### Lifecycle Confounding (CRITICAL)

Dataset aggregation includes **three distinct phases** mixed together:

1. **Lab testing period:** Device tested before deployment (controlled environment, artificial workloads)
2. **Inactive period:** Device powered off or disconnected (weeks/months between lab and production)
3. **Production period:** Device active at customer site (real-world conditions)

**Example:**
- Device tested in lab days 0-10: optical_mean = 1200, battery = 4.0V
- Inactive days 10-90: optical_mean = 0 (dark), battery = 3.7V (slow discharge)
- Production days 90-120: optical_mean = 800, battery = 3.2V (degrading)
- **Failure at day 120**

**Aggregated features seen by model:**
```python
optical_mean = (1200*10 + 0*80 + 800*30) / 120 = 300  # Meaningless average across phases
optical_std = 450  # High variability due to phase mixing, NOT gradual degradation
battery_mean = 3.63V  # Mixture of lab, inactive, production
```

**Risk:** Model may learn "high optical_std = device had inactive period = critical device" (organizational artifact) instead of "optical degradation trend = sensor failing" (physical causality).

### Model Validity Regime

This model is **VALID and RELIABLE** for:

- ✅ Devices with **similar deployment pattern** to training data (lab → inactive → production)
- ✅ Devices from **same sensor batches** and firmware versions
- ✅ Operational **environments similar** to training distribution

This model is **UNRELIABLE** for:

- ❌ Direct-deploy devices (no lab testing phase)
- ❌ Always-active devices (no inactive periods)
- ❌ New sensor batches or firmware updates
- ❌ Different environmental conditions (temperature, humidity, deployment locations)

### Recommended Deployment Strategy

**DO NOT** deploy this model blindly to all devices. Instead:

1. **Drift Monitoring** (scripts/drift_monitor.py): Detect when production data exits valid regime
2. **Stratified A/B Testing** (docs/A/B_TESTING_GUIDE.md): Validate performance per deployment pattern
3. **Conditional Deployment**: Use model only for device types matching training regime
4. **Continuous Monitoring**: Track performance by deployment pattern, retrain when drift detected

---

## Dataset Structure Analysis

### Aggregation Granularity

**Dataset:** `device_features_test_stratified.csv` and training equivalent

**Structure:** 1 row per device (237 test devices, 14 critical)

**Features:** 29 aggregated statistics per device
- Optical sensor: `optical_mean`, `optical_std`, `optical_min`, `optical_max`, `optical_range`, `optical_above_threshold`, `optical_below_threshold`
- Temperature: `temp_mean`, `temp_std`, `temp_min`, `temp_max`, `temp_range`, `temp_above_threshold`
- Battery: `battery_mean`, `battery_std`, `battery_min`, `battery_max`, `battery_range`
- Connectivity: `snr_mean`, `snr_std`, `snr_min`, `rsrp_mean`, `rsrp_std`, `rsrp_min`, `rsrq_mean`, `rsrq_std`, `rsrq_min`
- Messages: `total_messages`, `max_frame_count`

### Temporal Aggregation Window

**CRITICAL FINDING:**

Features are calculated over the **ENTIRE device history** from first activation to last observation (confirmed by user). This includes:

- **Lab testing period** (if applicable): Device tested in controlled environment before shipping
- **Inactive periods**: Device powered off or disconnected (e.g., in transit, storage, between deployments)
- **Production period**: Device active at customer site
- **At-failure period**: Likely includes sensor state at or very close to failure moment

**Mathematical representation:**
```python
# Feature calculation (current dataset)
optical_mean = mean(optical_values[t=0 to t=failure])  # Entire lifecycle
optical_std = std(optical_values[t=0 to t=failure])

# What we NEED for causal inference (not available)
optical_mean_30d_before = mean(optical_values[t=failure-30d to t=failure-1d])  # Predictive window
optical_trend_30d = slope(optical_values[t=failure-30d to t=failure-1d])  # Degradation rate
```

**Consequence:** Cannot determine if `optical_mean=500` represents:
- Stable value 500 maintained for 90 days before sudden failure (causal)
- Average of varying values that only dropped to 500 in final day before failure (simultaneous)
- Mixture of lab testing (1200) + inactive (0) + production (800) (confounded)

### Missing Temporal Information

The dataset does **NOT** include:
- ❌ Timestamps for individual sensor readings
- ❌ Temporal windows for aggregations (first_timestamp, last_timestamp)
- ❌ Time-to-failure for each device
- ❌ Lifecycle phase labels (is_lab_testing, is_inactive, is_production)
- ❌ Activation/reactivation timestamps
- ❌ Deployment metadata (direct_deploy vs lab_tested)

**What IS available:**
- ✅ Aggregated statistics (mean, std, min, max, range)
- ✅ Threshold counts (above/below, implies temporal frequency indirectly)
- ✅ Total message count (proxy for activity level)

---

## Lifecycle Phases Confounding

### Problem Statement

Aggregating features over **heterogeneous lifecycle phases** introduces a **confounding variable** that may dominate the signal the model learns.

### Typical Device Lifecycle

**Scenario A: Lab-Tested Device (common in training data)**

| Phase | Duration | Optical | Battery | Activity |
|-------|----------|---------|---------|----------|
| Lab Testing | 10 days | 1200 (bright) | 4.0V (full) | High messages |
| Inactive | 80 days | 0 (dark) | 3.7V (slow discharge) | Zero messages |
| Production | 30 days | 800 → 400 | 3.2V → 3.0V (degrading) | Medium messages |
| **Failure** | Day 120 | - | - | - |

**Aggregated features:**
```python
optical_mean = 300  # Dominated by 80-day inactive period at zero
optical_std = 450   # HIGH variability from phase mixing
battery_mean = 3.63V  # Mixture of all phases
total_messages = 3000  # Mostly from lab + production
```

**Scenario B: Direct-Deploy Device (rare in training data?)**

| Phase | Duration | Optical | Battery | Activity |
|-------|----------|---------|---------|----------|
| Production | 120 days | 900 → 600 (gradual) | 4.0V → 3.4V (gradual) | Consistent messages |
| **Failure** | Day 120 | - | - | - |

**Aggregated features:**
```python
optical_mean = 750  # Stable degradation, no phase mixing
optical_std = 150   # LOW variability, smooth degradation
battery_mean = 3.7V  # Gradual decline
total_messages = 12000  # Consistent activity
```

### Confounding Hypothesis

**If critical devices are more likely to have Scenario A pattern** (lab tested, long inactive period, short production before failure), **the model may learn:**

- ❌ "High optical_std = critical" (because critical devices had lab→inactive→production mixing)
- ❌ "Low total_messages = critical" (because critical devices were inactive longer)
- ❌ "High battery_range = critical" (because critical devices had full battery in lab, degraded in production)

**Instead of learning:**
- ✅ "Optical degradation trend = critical" (physical sensor failure)
- ✅ "Battery voltage decline rate = critical" (power system failure)
- ✅ "Connectivity RSRP decreasing = critical" (antenna degradation)

### Evidence For Confounding

**Supporting evidence:**
1. **Negative optical_mean values** in data (-13.71, -5.62): Suggests preprocessing/normalization already applied, possibly Z-score. Negative Z-score = below population mean. Devices with long inactive periods (optical=0) would have very low optical_mean after aggregation.

2. **High std features are important** (based on 29 features including std for optical, temp, battery, SNR, RSRP, RSRQ): Variability may be capturing lifecycle phase mixing, not gradual degradation.

3. **Correlation optical↔SNR positive** (r > 0.3): Devices with low optical (inactive?) also have low SNR (disconnected?). This supports lifecycle confounding hypothesis.

4. **78.6% recall, not 100%:** 3 out of 14 critical devices were missed (false negatives). Possibly these had different lifecycle patterns (e.g., direct deploy) not well-represented in training.

### Evidence Against Confounding

**Mitigating factors:**
1. **Threshold features** (optical_above_threshold, temp_above_threshold): These count frequency, which implies some temporal information (% of time above/below threshold during lifecycle).

2. **Connectivity degradation is slow:** RSRP/RSRQ decline over weeks due to antenna corrosion or component failure, not instantaneous. Model likely learned this gradual process.

3. **Variability features may capture gradual processes:** Even with phase mixing, `battery_std` can distinguish "stable battery over time" (healthy) from "high variance battery" (unstable power, degrading).

4. **Critical devices show variability, not uniform extremes:** If model only learned "at-failure symptoms", all critical devices would have similar extreme values. But data shows variability in critical devices' features.

### Conclusion on Confounding

**Confounding is REAL but PARTIAL:**
- Model likely learned MIXTURE of physical patterns (gradual degradation) AND lifecycle patterns (deployment artifacts)
- Cannot determine percentage split without experiments (see A/B Testing Guide)
- Risk increases for devices with deployment patterns different from training distribution

---

## Temporal Causality Impossibility

### Philosophical Foundation

**Causal inference requires temporal precedence:** To claim "X causes Y", we must observe X occurring BEFORE Y.

**Prediction requires causal patterns:** A predictive model must learn patterns observable BEFORE failure, not AT failure.

### The Fundamental Problem

With 1-row-per-device aggregation over entire lifecycle including at-failure period:

**Scenario:** Device fails at t=120 days
- `battery_mean` calculated over t=0 to t=120
- t=120 reading: battery=2.8V (at-failure symptom)
- This value IS INCLUDED in `battery_mean` calculation

**Mathematical impossibility:**

Given only `battery_mean=3.2V`, we CANNOT determine:
- Option A: Battery was 3.2V for entire 120 days, then sudden failure (causal pattern unclear)
- Option B: Battery degraded gradually 4.0V→3.0V over 120 days, mean=3.2V (causal pattern: degradation predicts failure)
- Option C: Battery was 4.0V for 100 days, crashed to 2.8V in final 20 days, mean=3.2V (simultaneous pattern: crash coincides with failure)
- Option D: Battery was 4.0V in lab (10d), 3.7V inactive (80d), 3.0V production (30d), mean=3.2V (confounded)

**All four scenarios produce identical aggregate feature `battery_mean=3.2V`.**

### Causal vs Simultaneous Learning Table

| Aspect | Causal Patterns Learned | Simultaneous Patterns Learned |
|--------|------------------------|-------------------------------|
| **What model knows** | Sensor behavior 30-60 days BEFORE failure | Sensor state AT failure moment |
| **Example pattern** | "Battery degradation trend -0.02V/day predicts failure" | "Battery=3.0V at failure" |
| **Test set performance** | 78.6% recall ✓ | 78.6% recall ✓ (identical) |
| **New device batch** | Generalizes ✓ (degradation physics invariant) | **FAILS** ❌ (new batch has different voltage baseline) |
| **Different environment** | Generalizes ✓ (degradation rate scales) | **FAILS** ❌ (different temp affects voltage differently) |
| **Firmware update** | Generalizes ✓ (hardware physics unchanged) | **FAILS** ❌ (firmware changes reporting, thresholds) |
| **Temporal drift** | Robust ✓ (physical laws stable) | **Fragile** ❌ (context-dependent correlations) |
| **Direct-deploy devices** | Generalizes ✓ | **FAILS** ❌ (learned lifecycle artifact, not present) |

### Why Test Set Performance Doesn't Prove Causality

**Test set validation shows:** Model achieves 78.6% recall on held-out devices

**What this proves:** Model learned SOME patterns that generalize within test distribution

**What this does NOT prove:**
- ❌ Patterns are causal (temporal precedence)
- ❌ Model will generalize to new distributions
- ❌ Model learned sensor physics vs deployment artifacts

**Analogy:** A model trained on "ice cream sales predict drowning deaths" will have perfect in-distribution accuracy (both correlate with summer), but zero causal understanding. It fails when deployed in winter beach town.

### Implications for Prediction Horizon

**Question:** Can this model predict failures X days in advance?

**Answer:** **UNKNOWN** with current data. We cannot validate prediction horizon because:

1. Features aggregate entire history including at-failure period
2. No timestamp data to separate "30 days before" from "1 day before"
3. Test set may achieve 78.6% recall by detecting at-failure symptoms, not predictive signals

**Conservative assumption:** Model may only reliably detect failures at or very close to failure moment (reactive, not predictive).

**Optimistic interpretation:** Variability and threshold features may capture gradual processes observable weeks before failure.

**Truth:** Likely somewhere in between, but quantifying prediction horizon requires temporal validation experiments (see Recommendations).

---

## Deployment Pattern Learning Risk

### Organizational Artifacts vs Physical Causality

**Physical causality (what we want model to learn):**
- Battery voltage decline → component degradation → failure
- Optical sensor output drop → LED degradation → failure
- RSRP/RSRQ deterioration → antenna corrosion → connectivity failure

**Organizational artifacts (what model may have learned):**
- Lab tested devices → often problematic from manufacturing → higher failure rate
- Long inactive periods → devices in troubled deployments → higher failure rate
- Low message count → devices poorly configured → higher failure rate

### Deployment Heterogeneity

**Training data likely contains specific deployment patterns:**

**Pattern 1: Enterprise deployment (hypothetical)**
- All devices lab tested before shipping
- Deployed in batches, some stored (inactive) before installation
- Firmware version X
- Geographic region A (climate, infrastructure)

**Pattern 2: Direct-to-consumer (hypothetical, possibly underrepresented)**
- No lab testing, shipped directly to end users
- Activated immediately upon receipt
- Firmware version Y
- Geographic region B

**Risk:** If training data is 90% Pattern 1, model optimizes for Pattern 1 characteristics, fails on Pattern 2.

### Generalization Failure Modes

**Failure Mode 1: New Deployment Workflow**

Company changes deployment process:
- OLD: All devices lab tested (training regime)
- NEW: Direct deploy to reduce costs

**Result:** Model sees devices with:
- Low optical_std (no phase mixing)
- High total_messages (always active)
- Different battery_mean baseline

**Drift detection triggers:** KS statistic > 0.4 on optical_std, total_messages distributions

**Model performance:** Recall may drop to 40-50% because learned patterns don't transfer

**Failure Mode 2: New Sensor Batch**

Hardware vendor changes battery supplier:
- OLD: Battery nominal voltage 3.7V (training data)
- NEW: Battery nominal voltage 3.85V (different chemistry)

**Result:** Model sees battery_mean=3.65V and classifies as critical (learned "battery_mean < 3.7V = critical" from training distribution), but device is healthy.

**Drift detection triggers:** KS statistic > 0.3 on battery_mean distribution

**Model performance:** Precision drops (false positives on healthy devices with new battery baseline)

**Failure Mode 3: Environmental Change**

Deployment to new geographic region:
- OLD: Temperate climate, temp_mean=22°C (training)
- NEW: Tropical climate, temp_mean=32°C

**Result:** Model sees temp_mean=32°C, but temp↔battery correlation changes (higher heat accelerates degradation differently), model miscalibrated.

**Drift detection triggers:** KS statistic > 0.4 on temp_mean, temp_std distributions

**Model performance:** Recall/precision both affected unpredictably

---

## Generalization Risks

### Taxonomy of Distribution Shift

**1. Deployment Pattern Shift** (HIGH RISK)
- Change in lifecycle phases (lab→inactive→production vs direct deploy)
- Affects: optical_std, battery_range, total_messages, all variability features
- Detectability: HIGH (drift monitor will catch distribution changes)
- Impact: Severe (model may have learned deployment artifacts heavily)

**2. Hardware Shift** (MEDIUM-HIGH RISK)
- New sensor batches, firmware updates, component supplier changes
- Affects: Absolute value features (optical_mean, battery_mean, RSRP/RSRQ baselines)
- Detectability: MEDIUM (drift monitor catches feature shifts, but may not distinguish "new hardware" from "more failures")
- Impact: Moderate to severe (depends on magnitude of hardware change)

**3. Environmental Shift** (MEDIUM RISK)
- Geographic region, climate, installation conditions
- Affects: temp_mean, temp_std, correlations (e.g., temp↔battery)
- Detectability: MEDIUM (drift monitor catches temp distribution change)
- Impact: Moderate (correlations may shift, but physics still underlying)

**4. Temporal Drift** (LOW-MEDIUM RISK)
- Aging of entire deployed fleet, seasonal variations
- Affects: Slow shifts in all features over months/years
- Detectability: LOW initially (gradual drift may stay below thresholds), HIGH eventually
- Impact: Slow degradation of performance over time

### Quantifying Risks

**Without temporal validation experiments, we CANNOT quantify:**
- How much did model learn causal patterns (robust to shift) vs simultaneous patterns (fragile)?
- Which features capture sensor physics (generalizable) vs deployment artifacts (context-specific)?
- What percentage of 78.6% recall comes from predictive signals vs at-failure detection?

**Recommended approach:** **Assume pessimistic scenario** (model learned significant deployment artifacts) and design deployment strategy defensively:

1. **Drift monitoring** (assume model fragile to distribution shift)
2. **Stratified validation** (test performance per deployment pattern)
3. **Conditional deployment** (use model only in validated regimes)
4. **Continuous monitoring** (detect performance degradation early)

---

## Model Validity Regime

### Regime Definition

This model is **validated and reliable** for devices matching the following characteristics:

**Lifecycle Pattern:**
- ✅ Lab tested before deployment (similar to training data)
- ✅ Possible inactive period between lab and production (weeks to months)
- ✅ Activated in production environment
- ✅ Similar message frequency patterns to training distribution

**Hardware Configuration:**
- ✅ Sensor batch and firmware version represented in training data
- ✅ Battery chemistry/supplier matching training data
- ✅ Optical sensor LED/photodiode from same manufacturing lots

**Environmental Conditions:**
- ✅ Operating temperature range similar to training distribution (likely -10°C to +40°C based on temp_mean values)
- ✅ Deployment environment (indoor vs outdoor, humidity, etc.) matching training
- ✅ Geographic region with similar infrastructure (connectivity quality)

**Operational Characteristics:**
- ✅ Message sending patterns within training distribution
- ✅ Data collection frequency similar to training (affects aggregation statistics)

### Out-of-Regime Detection

**Automatic detection via drift_monitor.py:**

Model is **OUT OF VALID REGIME** if:
- ❌ KS statistic > 0.2 on ANY of 29 features (WARNING level)
- ❌ KS statistic > 0.4 on ANY of 29 features (CRITICAL level)
- ❌ Lifecycle pattern drift detected (total_messages, variability distributions)

**Manual detection criteria:**

Model should NOT be used if:
- ❌ Deployment workflow changed (e.g., no more lab testing)
- ❌ New sensor hardware batch deployed
- ❌ Firmware update without revalidation
- ❌ Deployment to new geographic region/climate
- ❌ Performance metrics degrade >10% below baseline (78.6% recall, 84.6% precision)

### Regime-Specific Deployment Strategy

**Scenario 1: In-Regime Deployment**
- Deployment pattern matches training (lab→inactive→production)
- Hardware/firmware validated
- Environment similar to training

**Action:**
- ✅ Use model with confidence
- ✅ Monitor drift weekly
- ✅ Report predictions with probability scores
- ✅ Track performance metrics monthly

**Scenario 2: Partial Out-of-Regime**
- Some distribution shift detected (0.2 < KS < 0.4)
- New deployment pattern but hardware/environment unchanged

**Action:**
- ⚠️ Use model with CAUTION
- ⚠️ Increase monitoring frequency (daily drift checks)
- ⚠️ Require probability > 0.7 for critical classification (stricter threshold)
- ⚠️ Shadow mode: collect predictions but don't act, validate performance for 30-60 days

**Scenario 3: Critical Out-of-Regime**
- Major distribution shift (KS > 0.4)
- New hardware batch or firmware
- Different deployment workflow

**Action:**
- ❌ DO NOT use model
- ❌ Revert to baseline approach (manual inspection, rule-based heuristics)
- ❌ Collect new data in production
- ❌ Retrain model or recalibrate thresholds before using

---

## Mitigation Strategies

### Strategy 1: Drift Monitoring (CRITICAL - Implement Immediately)

**Tool:** `scripts/drift_monitor.py`

**Purpose:** Detect when production data distribution shifts away from training distribution, indicating model may be operating outside valid regime.

**Method:** Kolmogorov-Smirnov test comparing production batch vs training reference distribution for each of 29 features.

**Thresholds:**
- KS < 0.2: ✅ Within valid regime
- 0.2 ≤ KS < 0.4: ⚠️ WARNING - increased monitoring, consider shadow mode
- KS ≥ 0.4: ❌ CRITICAL - do not use model, investigate root cause

**Lifecycle Pattern Drift Detection (ENHANCED):**
- Monitor total_messages distribution (proxy for activity level, inactive periods)
- Monitor variability distributions (optical_std, temp_std, battery_std) - high variability = lifecycle phase mixing
- Threshold: KS > 0.3 on lifecycle proxies = deployment pattern changed

**Operational workflow:**
1. Collect production data batch (e.g., weekly, 100-500 devices)
2. Run `drift_monitor.py --reference data/device_features_train.csv --production data/production_batch_2025W45.csv`
3. Review JSON report and CDF plots
4. If WARNING/CRITICAL, escalate to data science team
5. Decision: continue using model, enter shadow mode, or disable model

**Implementation:**
```bash
# Weekly cron job
python scripts/drift_monitor.py \
  --reference data/device_features_train.csv \
  --production data/production_weekly/batch_$(date +%Y_W%U).csv \
  --output reports/drift_weekly/ \
  --threshold-warning 0.2 \
  --threshold-critical 0.4
```

### Strategy 2: Stratified A/B Testing (IMPORTANT - Before Full Deployment)

**Tool:** `docs/A/B_TESTING_GUIDE.md`

**Purpose:** Validate model performance across different deployment patterns, environments, hardware configurations BEFORE trusting predictions.

**Method:** Deploy model in shadow mode (collect predictions without acting) for 30-60 days, stratify analysis by deployment characteristics.

**Strata to test:**
1. **Deployment pattern:** Lab-tested vs direct-deploy vs reactivated
2. **Hardware batch:** Sensor manufacturing lot A vs B vs C
3. **Environment:** Geographic region, climate zone
4. **Firmware:** Version X vs Y

**Success criteria:**
- Recall ≥ 75% in ALL strata (not just overall)
- Precision ≥ 80% in ALL strata
- No stratum with performance <10% below overall average

**Failure handling:**
- If stratum X fails criteria: DO NOT deploy model to devices matching stratum X
- Use conditional deployment (only deploy to validated strata)

**Implementation phases:**
1. **Shadow mode** (30-60 days): Collect predictions, don't act
2. **Metrics validation**: Calculate recall/precision per stratum
3. **Conditional A/B**: Deploy to validated strata only, baseline for others
4. **Gradual rollout**: Expand to more strata as validated

### Strategy 3: Conditional Deployment (OPERATIONAL BEST PRACTICE)

**Purpose:** Use model ONLY for device types where it has been validated, preventing out-of-regime failures.

**Implementation:** Device metadata-based routing

```python
def should_use_model(device_metadata, drift_report):
    """Determine if model is valid for this device."""
    
    # Check 1: Deployment pattern
    deployment_pattern = infer_deployment_pattern(device_metadata)
    if deployment_pattern not in ['lab_tested_inactive_production', 'reactivated']:
        return False, "Deployment pattern not in validated regime"
    
    # Check 2: Hardware configuration
    if device_metadata['sensor_batch'] not in VALIDATED_BATCHES:
        return False, "Sensor batch not validated"
    
    if device_metadata['firmware_version'] not in VALIDATED_FIRMWARE:
        return False, "Firmware version not validated"
    
    # Check 3: Drift status
    if drift_report['max_ks_statistic'] > 0.4:
        return False, "CRITICAL drift detected"
    
    if drift_report['max_ks_statistic'] > 0.2:
        return True, "WARNING drift - use with caution, high probability threshold"
    
    # All checks passed
    return True, "Within validated regime"

# Usage in inference pipeline
use_model, reason = should_use_model(device_metadata, latest_drift_report)

if use_model:
    prediction = model.predict(device_features)
    # Act on prediction
else:
    logger.warning(f"Model not used for device {device_id}: {reason}")
    # Revert to baseline approach (manual inspection, heuristics)
```

**Device metadata required:**
- `deployment_pattern`: lab_tested, direct_deploy, reactivated, etc.
- `sensor_batch`: Manufacturing lot identifier
- `firmware_version`: Firmware version string
- `geographic_region`: Deployment location
- `activation_date`: When device entered production

**Fallback strategy when model not used:**
- Rule-based heuristics (e.g., "if battery_mean < 3.1V AND optical_mean < 400 → flag critical")
- Manual inspection queue
- Conservative flagging (over-predict critical to avoid false negatives)

### Strategy 4: Continuous Performance Monitoring

**Purpose:** Detect silent performance degradation in production before catastrophic failures.

**Metrics to track:**
- **Prediction rate:** % of devices classified as critical (expect ~6-8% based on training prevalence)
- **False positive rate:** Devices flagged critical but operated normally >30 days (requires ground truth collection)
- **False negative rate:** Devices NOT flagged but failed within 7 days (CRITICAL SAFETY metric)
- **Confidence distribution:** Average prediction probability (detect calibration drift)

**Ground truth collection:**
- Log all predictions with timestamp
- Track device failures (requires operational monitoring integration)
- Match predictions to actual outcomes with 7-day, 30-day windows
- Calculate recall/precision monthly

**Alert thresholds:**
- ❌ Recall drops >10% below baseline (78.6% → <70%): CRITICAL
- ⚠️ Precision drops >15% below baseline (84.6% → <72%): WARNING
- ⚠️ Prediction rate changes >20% (6% → >7.2% or <4.8%): Distribution shift
- ❌ Any false negative with catastrophic consequence: INCIDENT

**Response:**
1. If metric degrades: Investigate root cause (drift? deployment pattern change? hardware update?)
2. If drift confirmed: Retrain model with recent production data
3. If deployment pattern changed: Recalibrate thresholds or conditionally disable model
4. If catastrophic false negative: Immediate review, adjust decision threshold to favor recall over precision

### Strategy 5: Model Retraining Cadence

**Purpose:** Keep model updated with evolving sensor fleet, deployment patterns, failure modes.

**Triggers for retraining:**
1. **Scheduled:** Every 6 months (minimum cadence)
2. **Drift-triggered:** KS > 0.3 sustained for >4 weeks
3. **Performance-triggered:** Recall or precision drops >10% below baseline
4. **Business-triggered:** New hardware batch, firmware update, major deployment change

**Retraining process:**
1. Collect production data from past 6-12 months
2. Label devices with ground truth failures (requires operational monitoring)
3. Combine with original training data (weighted, or train on recent only)
4. Retrain model, validate on holdout production data
5. Compare performance to current model (A/B test new vs old)
6. Deploy new model if performance ≥ current model

**Data requirements for retraining:**
- Minimum 500 devices (maintain statistical power)
- Minimum 30 critical failures (maintain class balance)
- Ground truth labels (requires failure tracking)
- Temporal metadata if available (enables temporal feature engineering)

---

## Recommendations for Future Work

### Priority 1: Temporal Feature Engineering (HIGH IMPACT)

**Goal:** Eliminate lifecycle confounding and enable causal inference by separating lifecycle phases and creating time-windowed features.

**See:** `docs/FEATURE_ENGINEERING_TEMPORAL.md` for detailed implementation guide.

**Key recommendations:**

**1. Lifecycle Phase Separation**

Collect metadata:
- `lab_test_start_timestamp`, `lab_test_end_timestamp`
- `activation_timestamp` (production start)
- `inactive_periods` (timestamps when device offline)

Create phase-specific features:
```python
# Filter to production period only (eliminate lab/inactive confounding)
production_data = sensor_data[
    (timestamp >= activation_timestamp) &
    (message_count > 0)  # Active periods only
]

# Features over production period ONLY
features = {
    'battery_mean_production': production_data['battery'].mean(),
    'optical_std_production': production_data['optical'].std(),
    'temp_max_production': production_data['temp'].max(),
    # ... for all 29 features
}
```

**2. Temporal Windows (Causal Features)**

Create time-windowed aggregations:
```python
# Assuming we have timestamp data
features_temporal = {
    # Last 30 days before observation (predictive window)
    'battery_mean_30d': production_data[-30d:]['battery'].mean(),
    'optical_mean_30d': production_data[-30d:]['optical'].mean(),
    
    # Last 7 days (short-term trends)
    'battery_mean_7d': production_data[-7d:]['battery'].mean(),
    
    # Trend features (degradation rate)
    'battery_trend_30d': linregress(days, production_data[-30d:]['battery']).slope,
    'optical_trend_30d': linregress(days, production_data[-30d:]['optical']).slope,
    
    # Delta features (change over time)
    'delta_battery_30d': production_data[-1d]['battery'] - production_data[-30d]['battery'],
    'delta_optical_7d': production_data[-1d]['optical'] - production_data[-7d]['optical'],
}
```

**3. Activity Detection**

Create lifecycle metadata features:
```python
# Detect inactive periods (0 messages for >7 days)
inactive_periods = detect_inactive_periods(sensor_data, threshold_days=7)

features_lifecycle = {
    'days_inactive_total': sum(inactive_periods),
    'num_inactive_periods': len(inactive_periods),
    'reactivation_count': count_transitions(inactive → active),
    'days_since_last_reactivation': current_date - last_reactivation_date,
    'production_duration_days': current_date - activation_timestamp,
}
```

**Impact:**
- ✅ Eliminates lifecycle confounding (production-only features)
- ✅ Enables causal inference (trends observable BEFORE failure)
- ✅ Improves generalization (robust to deployment pattern changes)
- ✅ Quantifies prediction horizon (can validate "X days before failure")

### Priority 2: Temporal Validation Experiments (MEDIUM IMPACT)

**Goal:** Quantify how much model learned causal vs simultaneous patterns, validate prediction horizon.

**Approach 1: Temporal Holdout (if timestamps available)**

If historical data has timestamps:
1. For each device, create features at t-30d, t-15d, t-7d, t-1d before failure (or last observation for healthy devices)
2. Evaluate model on each temporal window
3. **If causal:** Recall should be similar at t-30d and t-1d (degradation observable early)
4. **If simultaneous:** Recall should increase dramatically from t-30d to t-1d (only detectable close to failure)

**Approach 2: Feature Ablation**

Test model performance removing different feature types:
1. Baseline: All 29 features → 78.6% recall
2. Remove variability features (std, range): If recall drops >20%, model heavily relies on lifecycle confounding
3. Remove threshold features: If recall drops <5%, model doesn't use temporal frequency information
4. Remove connectivity features: If recall drops >15%, connectivity degradation is strong causal signal

**Approach 3: Manufacturer/Environment Stratification**

If metadata available (sensor batch, deployment location):
1. Train on sensor batch A, test on batch B (hardware shift)
2. Train on region X, test on region Y (environmental shift)
3. **If causal:** Performance should transfer (physics generalizes)
4. **If simultaneous:** Performance should degrade (context-specific correlations)

**Expected outcome:**
- Quantify % of recall from causal patterns (generalizable) vs simultaneous patterns (fragile)
- Identify which features are most causal (optical_trend_30d) vs most simultaneous (optical_min)
- Inform feature selection for next model iteration

### Priority 3: Enhanced Drift Detection (MEDIUM IMPACT)

**Goal:** Improve drift monitoring with lifecycle-aware and causal-aware drift metrics.

**Enhancement 1: Lifecycle Pattern Drift**

Already planned in drift_monitor.py (Thought 7):
- Monitor total_messages distribution (activity level)
- Monitor optical_std, temp_std, battery_std (phase mixing indicators)
- Alert if deployment pattern changes (e.g., no more lab testing)

**Enhancement 2: Correlation Drift**

Monitor feature correlations (not just distributions):
```python
# Training reference
corr_train = training_data[['temp_mean', 'battery_mean']].corr()

# Production batch
corr_prod = production_data[['temp_mean', 'battery_mean']].corr()

# Correlation drift (Frobenius norm distance)
corr_drift = np.linalg.norm(corr_train - corr_prod, ord='fro')

# Alert if correlations change (physics relationships shifting)
if corr_drift > 0.3:
    alert("Correlation structure changed - environmental or hardware shift")
```

**Enhancement 3: Model Confidence Drift**

Monitor prediction probability distributions:
```python
# Training reference (if available from validation set)
proba_critical_train = model.predict_proba(validation_set)[:, 1]

# Production batch
proba_critical_prod = model.predict_proba(production_batch)[:, 1]

# Confidence drift (KS test on probability distributions)
ks_confidence = ks_2samp(proba_critical_train, proba_critical_prod)

# Alert if model is more/less confident than training (calibration drift)
if ks_confidence.statistic > 0.3:
    alert("Model confidence distribution changed - recalibration may be needed")
```

### Priority 4: Active Learning for Edge Cases (LOW-MEDIUM IMPACT)

**Goal:** Improve model on underrepresented deployment patterns without full retraining.

**Approach:**
1. Identify devices where model is uncertain (0.4 < probability < 0.6)
2. Prioritize these for manual inspection and ground truth labeling
3. Collect edge cases (direct-deploy, new hardware, different environments)
4. Retrain model with weighted sampling (oversample edge cases)

**Implementation:**
```python
# In production inference
predictions = model.predict_proba(production_batch)
uncertain_devices = production_batch[
    (predictions[:, 1] > 0.4) & (predictions[:, 1] < 0.6)
]

# Flag for human review
for device in uncertain_devices:
    queue_for_manual_inspection(device)
    # Later, after ground truth known:
    add_to_retraining_pool(device, ground_truth_label, weight=3.0)
```

**Impact:**
- Improves model on edge cases (direct-deploy, new environments)
- Reduces false negatives/positives in uncertain regime
- Expands model validity regime over time

---

## Appendix A: Glossary

**Terms used in this document:**

- **Causal pattern:** Sensor behavior observable BEFORE failure that causally predicts failure (e.g., battery degradation trend)
- **Simultaneous pattern:** Sensor state AT failure moment that correlates with failure but doesn't predict it (e.g., battery=3.0V at failure)
- **Lifecycle phases:** Distinct periods in device history (lab testing, inactive, production) with different operational characteristics
- **Confounding variable:** Factor correlated with both features and target that creates spurious correlation (e.g., deployment pattern affects both feature distributions and failure rate)
- **Deployment pattern:** Workflow for deploying devices (lab→inactive→production vs direct-deploy vs always-active)
- **Distribution shift:** Change in feature distributions between training and production data
- **Drift:** Gradual change in feature distributions or model performance over time
- **Kolmogorov-Smirnov (KS) test:** Statistical test measuring maximum difference between two cumulative distribution functions
- **Model validity regime:** Set of conditions (deployment pattern, hardware, environment) under which model performance is validated
- **Out-of-regime:** Production scenario not represented in training data, where model performance may degrade
- **Prediction horizon:** Time interval between prediction and failure (e.g., "30 days before failure")
- **Shadow mode:** Deployment phase where model makes predictions but doesn't act, used for validation
- **Temporal causality:** Requirement that cause precedes effect in time, essential for predictive modeling

---

## Appendix B: Contact and Escalation

**For questions about this document:**
- Data Science Team: [contact info]
- Model owner: [name]

**Escalation scenarios:**

**CRITICAL drift (KS > 0.4):**
1. Immediately disable model in production
2. Alert data science team
3. Investigate root cause (deployment change? hardware update?)
4. Do not re-enable until validated

**Performance degradation (Recall < 70%):**
1. Enter shadow mode (collect predictions, don't act)
2. Analyze false negatives (which failure modes being missed?)
3. Collect ground truth data
4. Retrain or recalibrate model

**Catastrophic false negative (missed critical failure with severe consequence):**
1. Incident response protocol
2. Immediate review of recent predictions for similar devices
3. Adjust decision threshold to favor recall (accept more false positives)
4. Root cause analysis of why device not flagged

---

**Document version:** 1.0  
**Last updated:** 2025-11-11  
**Review cadence:** Quarterly or after major model updates  
**Next review:** 2026-02-11
