# Feature Engineering Temporal - Roadmap for Causal Features

**Document Purpose:** Technical guide for next-generation model with temporal features that enable causal inference. Provides concrete recommendations for data collection, feature design, and validation approaches to eliminate lifecycle confounding and quantify prediction horizon.

**Target Audience:** Data scientists, data engineers, IoT platform developers

**Prerequisites:** 
- Read `docs/TEMPORAL_LIMITATIONS.md` to understand current model limitations
- Access to raw sensor timeseries data (not just aggregated statistics)

**Last Updated:** November 11, 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Model Limitations Recap](#current-model-limitations-recap)
3. [Data Requirements for Temporal Features](#data-requirements-for-temporal-features)
4. [Priority 1: Lifecycle Phase Separation](#priority-1-lifecycle-phase-separation)
5. [Priority 2: Time-Windowed Features](#priority-2-time-windowed-features)
6. [Priority 3: Trend and Degradation Features](#priority-3-trend-and-degradation-features)
7. [Priority 4: Delta and Rate Features](#priority-4-delta-and-rate-features)
8. [Priority 5: Temporal Metadata Features](#priority-5-temporal-metadata-features)
9. [Implementation Examples](#implementation-examples)
10. [Validation Approaches](#validation-approaches)
11. [Expected Impact](#expected-impact)
12. [Migration Path](#migration-path)

---

## Executive Summary

### The Problem with Current Features

Current model uses **lifecycle-aggregated features** (1-row per device):

```python
# Current dataset (problematic)
device_12345 = {
    'optical_mean': 300,     # Average over lab (1200) + inactive (0) + production (800) = meaningless
    'battery_mean': 3.63,    # Mixture of full (4.0V) + discharged (3.7V) + degraded (3.2V) = confounded
    'optical_std': 450,      # High because of phase mixing, NOT gradual degradation
}
```

**Problems:**
- ❌ Cannot distinguish causal (before-failure) from simultaneous (at-failure) patterns
- ❌ Lifecycle phases (lab→inactive→production) confound sensor physics
- ❌ No temporal precedence (X observed BEFORE Y)
- ❌ Cannot quantify prediction horizon (30 days before failure vs 1 day before)

### The Solution: Temporal Feature Engineering

**Next-generation model uses time-windowed, phase-separated, trend features:**

```python
# Next-gen dataset (causal)
device_12345_at_t_minus_30d_before_failure = {
    # Production-only features (eliminate lab/inactive confounding)
    'battery_mean_production_only': 3.35,     # Only production period data
    'optical_mean_production_only': 750,      # No lab/inactive mixing
    
    # Time-windowed features (causal precedence)
    'battery_mean_last_30d': 3.25,            # Observable 30 days BEFORE failure
    'optical_mean_last_7d': 650,              # Short-term window
    
    # Trend features (degradation rate)
    'battery_trend_30d': -0.015,              # V/day decline rate (causal!)
    'optical_trend_30d': -5.2,                # Degradation slope
    
    # Delta features (change over time)
    'delta_battery_30d': -0.45,               # Change from t-30d to t-0
    'delta_optical_7d': -150,                 # Short-term change
    
    # Rate features (normalized degradation)
    'battery_degradation_rate': 0.013,        # %/day normalized by initial value
    
    # Temporal metadata (context)
    'days_since_activation': 90,              # How long in production
    'days_inactive_total': 80,                # Total inactive time (confounding indicator)
}
```

**Benefits:**
- ✅ **Causal inference:** Trends observable 30 days BEFORE failure
- ✅ **Lifecycle separation:** Production-only features eliminate confounding
- ✅ **Quantifiable prediction horizon:** Can validate "predicts X days in advance"
- ✅ **Robust generalization:** Degradation physics generalizes, deployment artifacts don't

### Priorities

**PRIORITY 1 (CRITICAL): Lifecycle Phase Separation**
- Collect metadata: `lab_test_start`, `activation_timestamp`, `inactive_periods`
- Create production-only features: `battery_mean_production_only`
- **Impact:** Eliminates deployment pattern confounding (direct-deploy vs lab-tested)

**PRIORITY 2 (HIGH): Time-Windowed Features**
- Calculate features over fixed windows: `battery_mean_last_30d`, `optical_mean_last_7d`
- **Impact:** Enables causal precedence validation (observable BEFORE failure)

**PRIORITY 3 (HIGH): Trend Features**
- Fit linear regression to sensor values over time: `battery_trend_30d = slope`
- **Impact:** Directly captures degradation rate (physics), not snapshots

**PRIORITY 4 (MEDIUM): Delta and Rate Features**
- Calculate change over time: `delta_battery_30d = battery_t0 - battery_t-30d`
- **Impact:** Normalizes for different baselines (battery supplier changes)

**PRIORITY 5 (LOW): Temporal Metadata**
- Add lifecycle context: `days_since_activation`, `num_reactivations`
- **Impact:** Enables lifecycle-aware modeling (control for confounders)

---

## Current Model Limitations Recap

### Aggregation Over Entire Lifecycle

**Current dataset structure:**

```
Device ID: 12345
First message: 2024-01-01 (lab testing)
Inactive period: 2024-01-10 to 2024-04-01 (80 days)
Production start: 2024-04-01
Failure: 2024-05-01

Features calculated over ALL messages (2024-01-01 to 2024-05-01):
optical_mean = mean(optical_values[all timestamps])
battery_mean = mean(battery_values[all timestamps])
```

**Problem:** Features aggregate:
1. **Lab testing period:** Controlled environment, not representative of production
2. **Inactive period:** Device off/disconnected, sensor readings meaningless (zeros, last known value, or NaN)
3. **Production period:** Real-world operation
4. **At-failure period:** Likely includes sensor state at failure moment (simultaneous, not causal)

**Example:**
- Lab (10 days): optical=1200, battery=4.0V
- Inactive (80 days): optical=0 (dark), battery=3.7V (slow discharge)
- Production (30 days): optical=800→600 (degrading), battery=3.3→3.0V (degrading)

**Aggregated features:**
```python
optical_mean = (1200*10 + 0*80 + 700*30) / 120 = 275  # Dominated by inactive zeros
battery_mean = (4.0*10 + 3.7*80 + 3.15*30) / 120 = 3.62  # Mixture of all phases
```

**Why this is bad:**
- `optical_mean=275` does NOT represent production behavior (should be ~700)
- `battery_mean=3.62` does NOT represent degradation (should be 3.0V at failure)
- Model learns "low optical_mean = critical" which confounds inactive period with actual failure

### Temporal Causality Impossibility

Without temporal windowing:

**Cannot distinguish:**
- **Causal:** "Battery declined from 4.0V to 3.0V over 30 days BEFORE failure" (predictive)
- **Simultaneous:** "Battery was 3.0V AT failure moment" (descriptive, not predictive)
- **Confounded:** "Battery average 3.62V across all lifecycle phases" (meaningless)

**Current model may have learned:** "battery_mean < 3.7V = critical"

**What we WANT model to learn:** "battery_trend_30d < -0.01 V/day = critical" (degradation rate)

**Difference:**
- First pattern FAILS on new battery batches (supplier change, nominal voltage 3.85V)
- Second pattern GENERALIZES (degradation physics invariant to baseline voltage)

---

## Data Requirements for Temporal Features

### Raw Timeseries Data

**Minimum requirements:**

```python
# Raw sensor readings (one row per message)
sensor_timeseries = {
    'device_id': str,
    'timestamp': datetime,  # CRITICAL - must have timestamps
    'optical_value': float,
    'temperature_value': float,
    'battery_voltage': float,
    'snr': float,
    'rsrp': float,
    'rsrq': float,
    'message_count': int,
    'frame_count': int
}
```

**Example:**
```
device_id,timestamp,optical_value,temperature_value,battery_voltage,snr,rsrp,rsrq
12345,2024-01-01 08:00:00,1205,22.3,4.02,15.2,-85.1,-10.2
12345,2024-01-01 08:15:00,1198,22.5,4.01,14.8,-85.5,-10.4
12345,2024-01-01 08:30:00,1210,22.1,4.02,15.5,-84.8,-10.1
...
12345,2024-05-01 12:00:00,450,28.7,2.95,8.2,-105.3,-15.8  # Near failure
```

**Data frequency:**
- Minimum: 1 message per day (coarse, but usable)
- Recommended: 4-8 messages per day (hourly sampling during active periods)
- Ideal: Message-driven (whenever sensor has update), typically 10-50 messages/day

**Storage requirements:**
- 100 devices × 120 days × 10 messages/day × 10 features × 8 bytes = ~9.6 MB (negligible)
- Scaling to 10,000 devices = ~960 MB (still manageable)

### Lifecycle Metadata

**Required fields:**

```python
device_metadata = {
    'device_id': str,
    
    # Lab testing period (if applicable)
    'lab_test_start_timestamp': datetime | None,
    'lab_test_end_timestamp': datetime | None,
    
    # Production activation
    'activation_timestamp': datetime,  # CRITICAL - when device entered production
    'first_production_message_timestamp': datetime,
    
    # Inactive periods (optional but highly recommended)
    'inactive_periods': [
        {'start': datetime, 'end': datetime, 'reason': str},
        ...
    ],
    
    # Failure information
    'failure_timestamp': datetime | None,  # When device failed (for training labels)
    'failure_type': str | None,  # 'critical', 'warning', 'operational'
    
    # Hardware/deployment metadata
    'sensor_batch': str,
    'firmware_version': str,
    'deployment_pattern': str,  # 'lab_tested', 'direct_deploy', 'reactivated'
}
```

**Example:**
```json
{
    "device_id": "12345",
    "lab_test_start_timestamp": "2024-01-01T08:00:00Z",
    "lab_test_end_timestamp": "2024-01-10T17:00:00Z",
    "activation_timestamp": "2024-04-01T09:00:00Z",
    "inactive_periods": [
        {
            "start": "2024-01-10T17:00:00Z",
            "end": "2024-04-01T09:00:00Z",
            "reason": "storage_before_deployment"
        }
    ],
    "failure_timestamp": "2024-05-01T14:23:15Z",
    "failure_type": "critical",
    "sensor_batch": "LOT_2024_Q1",
    "firmware_version": "v2.3.1",
    "deployment_pattern": "lab_tested_inactive_production"
}
```

### Failure Labels with Time Context

**Enhanced failure labeling:**

Instead of binary `is_critical` label, provide:

```python
failure_labels = {
    'device_id': str,
    'is_critical': bool,
    'failure_timestamp': datetime,  # When failure occurred
    'failure_detected_timestamp': datetime,  # When failure was detected (may differ)
    'failure_severity': str,  # 'critical', 'major', 'minor'
    'failure_mode': str,  # 'battery_depleted', 'optical_sensor_failed', 'connectivity_lost', etc.
}
```

**Why this matters:**

Enables validation of prediction horizon:
- Calculate features at `failure_timestamp - 30 days`
- Check if model could predict failure 30 days in advance
- Measure: "What % of failures are predictable 30 days before? 7 days before?"

---

## Priority 1: Lifecycle Phase Separation

### Objective

**Eliminate confounding** from mixing lab testing, inactive periods, and production operation.

### Implementation

**Step 1: Detect Lifecycle Phases**

```python
import pandas as pd

def detect_lifecycle_phases(timeseries_df, metadata):
    """
    Classify each message into lifecycle phase.
    
    Args:
        timeseries_df: Raw sensor readings with timestamps
        metadata: Device metadata with lab_test_start, activation_timestamp, etc.
    
    Returns:
        timeseries_df with added 'lifecycle_phase' column
    """
    df = timeseries_df.copy()
    
    # Initialize phase column
    df['lifecycle_phase'] = 'unknown'
    
    # Lab testing period
    if metadata.get('lab_test_start_timestamp') and metadata.get('lab_test_end_timestamp'):
        lab_mask = (
            (df['timestamp'] >= metadata['lab_test_start_timestamp']) &
            (df['timestamp'] <= metadata['lab_test_end_timestamp'])
        )
        df.loc[lab_mask, 'lifecycle_phase'] = 'lab_testing'
    
    # Production period
    if metadata.get('activation_timestamp'):
        production_mask = df['timestamp'] >= metadata['activation_timestamp']
        df.loc[production_mask, 'lifecycle_phase'] = 'production'
    
    # Inactive periods
    for inactive in metadata.get('inactive_periods', []):
        inactive_mask = (
            (df['timestamp'] >= inactive['start']) &
            (df['timestamp'] <= inactive['end'])
        )
        df.loc[inactive_mask, 'lifecycle_phase'] = 'inactive'
    
    return df
```

**Step 2: Calculate Production-Only Features**

```python
def calculate_production_only_features(timeseries_df):
    """
    Calculate aggregated features ONLY over production period.
    
    This eliminates lab testing and inactive period confounding.
    """
    # Filter to production messages only
    production_df = timeseries_df[timeseries_df['lifecycle_phase'] == 'production']
    
    if len(production_df) == 0:
        # No production data available
        return None
    
    features = {
        # Optical sensor (production only)
        'optical_mean_production': production_df['optical_value'].mean(),
        'optical_std_production': production_df['optical_value'].std(),
        'optical_min_production': production_df['optical_value'].min(),
        'optical_max_production': production_df['optical_value'].max(),
        'optical_range_production': production_df['optical_value'].max() - production_df['optical_value'].min(),
        
        # Temperature (production only)
        'temp_mean_production': production_df['temperature_value'].mean(),
        'temp_std_production': production_df['temperature_value'].std(),
        'temp_min_production': production_df['temperature_value'].min(),
        'temp_max_production': production_df['temperature_value'].max(),
        
        # Battery (production only)
        'battery_mean_production': production_df['battery_voltage'].mean(),
        'battery_std_production': production_df['battery_voltage'].std(),
        'battery_min_production': production_df['battery_voltage'].min(),
        'battery_max_production': production_df['battery_voltage'].max(),
        
        # Connectivity (production only)
        'snr_mean_production': production_df['snr'].mean(),
        'rsrp_mean_production': production_df['rsrp'].mean(),
        'rsrq_mean_production': production_df['rsrq'].mean(),
        
        # Metadata
        'production_duration_days': (production_df['timestamp'].max() - production_df['timestamp'].min()).days,
        'production_message_count': len(production_df)
    }
    
    return features
```

**Impact:**

**Before (lifecycle-aggregated):**
```python
# Device with lab→inactive→production pattern
device_features_old = {
    'optical_mean': 300,  # Mixture of lab(1200) + inactive(0) + production(700) = confounded
    'battery_mean': 3.62  # Mixture = confounded
}
# Model learns: "optical_mean < 500 = critical" (actually learning inactive period indicator)
```

**After (production-only):**
```python
# Same device, production-only features
device_features_new = {
    'optical_mean_production': 700,  # Only production data, no lab/inactive
    'battery_mean_production': 3.15  # Only production data
}
# Model learns: "optical_mean_production < 750 = critical" (actually sensor degradation)
```

**Generalization test:**

**Scenario:** Direct-deploy device (no lab testing, no inactive period)

**Old model (lifecycle-aggregated):**
- Direct-deploy device: optical_mean=750 (entire lifecycle = production)
- Model predicts: NON-CRITICAL (learned "optical_mean < 500" from lab→inactive→production pattern)
- **WRONG:** Device with optical=750 in production is actually degraded

**New model (production-only):**
- Direct-deploy device: optical_mean_production=750
- Model predicts: CRITICAL (learned "optical_mean_production < 900" from production physics)
- **CORRECT:** Generalizes across deployment patterns

---

## Priority 2: Time-Windowed Features

### Objective

**Enable causal precedence:** Calculate features over fixed time windows BEFORE failure, not entire history.

### Implementation

**Time Windows to Calculate:**

```python
TIME_WINDOWS = [
    7,   # Last 7 days (short-term patterns)
    14,  # Last 14 days
    30,  # Last 30 days (medium-term trends)
    60,  # Last 60 days (long-term context, optional)
]
```

**Feature Calculation:**

```python
def calculate_windowed_features(timeseries_df, observation_timestamp, windows=[7, 14, 30]):
    """
    Calculate features over time windows ending at observation_timestamp.
    
    Args:
        timeseries_df: Sensor readings (already filtered to production period)
        observation_timestamp: Point in time to make prediction (e.g., failure - 30 days)
        windows: List of window sizes in days
    
    Returns:
        Dictionary of windowed features
    """
    features = {}
    
    for window_days in windows:
        window_start = observation_timestamp - pd.Timedelta(days=window_days)
        window_end = observation_timestamp
        
        # Filter to window
        window_df = timeseries_df[
            (timeseries_df['timestamp'] >= window_start) &
            (timeseries_df['timestamp'] < window_end)
        ]
        
        if len(window_df) == 0:
            # No data in this window (device may have been inactive)
            continue
        
        # Calculate features for this window
        features[f'battery_mean_{window_days}d'] = window_df['battery_voltage'].mean()
        features[f'battery_std_{window_days}d'] = window_df['battery_voltage'].std()
        features[f'battery_min_{window_days}d'] = window_df['battery_voltage'].min()
        
        features[f'optical_mean_{window_days}d'] = window_df['optical_value'].mean()
        features[f'optical_std_{window_days}d'] = window_df['optical_value'].std()
        
        features[f'temp_mean_{window_days}d'] = window_df['temperature_value'].mean()
        features[f'temp_max_{window_days}d'] = window_df['temperature_value'].max()
        
        features[f'snr_mean_{window_days}d'] = window_df['snr'].mean()
        features[f'rsrp_mean_{window_days}d'] = window_df['rsrp'].mean()
        features[f'rsrq_mean_{window_days}d'] = window_df['rsrq'].mean()
        
        # Message activity in window
        features[f'message_count_{window_days}d'] = len(window_df)
    
    return features
```

**Training Dataset Construction:**

```python
def build_training_dataset_with_windows(devices_metadata, sensor_timeseries):
    """
    Build training dataset with time-windowed features.
    
    For CRITICAL devices: Calculate features at failure_timestamp - 30 days
    For HEALTHY devices: Calculate features at random observation point
    """
    training_data = []
    
    for device in devices_metadata:
        device_id = device['device_id']
        device_timeseries = sensor_timeseries[sensor_timeseries['device_id'] == device_id]
        
        # Filter to production period only
        production_timeseries = device_timeseries[device_timeseries['lifecycle_phase'] == 'production']
        
        if device['is_critical']:
            # Critical device: observe 30 days BEFORE failure
            observation_timestamp = device['failure_timestamp'] - pd.Timedelta(days=30)
        else:
            # Healthy device: observe at random point (or last known timestamp)
            observation_timestamp = production_timeseries['timestamp'].max()
        
        # Calculate windowed features
        features = calculate_windowed_features(
            production_timeseries,
            observation_timestamp,
            windows=[7, 14, 30]
        )
        
        features['device_id'] = device_id
        features['is_critical'] = device['is_critical']
        features['observation_timestamp'] = observation_timestamp
        
        training_data.append(features)
    
    return pd.DataFrame(training_data)
```

**Impact:**

**Temporal Precedence Validation:**

Now we can validate: "Can model predict failure 30 days in advance?"

```python
# Training: Calculate features at failure - 30 days
critical_device_features_at_t_minus_30d = calculate_windowed_features(
    production_timeseries,
    observation_timestamp=failure_timestamp - pd.Timedelta(days=30),
    windows=[7, 14, 30]
)
# Features observable 30 days BEFORE failure

# Prediction: If model achieves 75% recall on these features,
# it PROVES model can predict 30 days in advance (causal, not simultaneous)
```

**Prediction Horizon Quantification:**

Test model at different observation points:

```python
prediction_horizons = []

for horizon_days in [1, 7, 14, 30, 60]:
    # Calculate features at failure - horizon_days
    features = calculate_windowed_features(
        production_timeseries,
        observation_timestamp=failure_timestamp - pd.Timedelta(days=horizon_days),
        windows=[7, 14, 30]
    )
    
    # Predict
    prediction = model.predict(features)
    
    prediction_horizons.append({
        'horizon_days': horizon_days,
        'correct': prediction == is_critical
    })

# Analyze: At what horizon does recall drop?
# Example result: Recall 80% at 30 days, 85% at 14 days, 90% at 7 days, 95% at 1 day
# Conclusion: Model can reliably predict 30 days in advance
```

---

## Priority 3: Trend and Degradation Features

### Objective

**Capture degradation dynamics:** Fit linear regression to sensor values over time, extract slope (degradation rate).

### Implementation

**Trend Feature Calculation:**

```python
from scipy.stats import linregress

def calculate_trend_features(timeseries_df, observation_timestamp, windows=[7, 30]):
    """
    Calculate trend (slope) of sensor values over time windows.
    
    Trend = degradation rate (e.g., battery declines -0.015 V/day)
    """
    features = {}
    
    for window_days in windows:
        window_start = observation_timestamp - pd.Timedelta(days=window_days)
        window_df = timeseries_df[
            (timeseries_df['timestamp'] >= window_start) &
            (timeseries_df['timestamp'] < observation_timestamp)
        ]
        
        if len(window_df) < 3:
            # Need at least 3 points for meaningful regression
            continue
        
        # Convert timestamps to days since window_start
        window_df['days'] = (window_df['timestamp'] - window_start).dt.total_seconds() / (24 * 3600)
        
        # Battery voltage trend
        if window_df['battery_voltage'].notna().sum() >= 3:
            slope_battery, intercept, r_value, p_value, std_err = linregress(
                window_df['days'],
                window_df['battery_voltage']
            )
            features[f'battery_trend_{window_days}d'] = slope_battery  # V/day
            features[f'battery_trend_r2_{window_days}d'] = r_value ** 2  # R² goodness of fit
        
        # Optical sensor trend
        if window_df['optical_value'].notna().sum() >= 3:
            slope_optical, _, r_value, _, _ = linregress(
                window_df['days'],
                window_df['optical_value']
            )
            features[f'optical_trend_{window_days}d'] = slope_optical  # units/day
            features[f'optical_trend_r2_{window_days}d'] = r_value ** 2
        
        # Temperature trend
        if window_df['temperature_value'].notna().sum() >= 3:
            slope_temp, _, r_value, _, _ = linregress(
                window_df['days'],
                window_df['temperature_value']
            )
            features[f'temp_trend_{window_days}d'] = slope_temp  # °C/day
            features[f'temp_trend_r2_{window_days}d'] = r_value ** 2
        
        # RSRP trend (connectivity degradation)
        if window_df['rsrp'].notna().sum() >= 3:
            slope_rsrp, _, r_value, _, _ = linregress(
                window_df['days'],
                window_df['rsrp']
            )
            features[f'rsrp_trend_{window_days}d'] = slope_rsrp  # dBm/day
            features[f'rsrp_trend_r2_{window_days}d'] = r_value ** 2
    
    return features
```

**Interpretation:**

```python
# Example: Critical device
features = {
    'battery_trend_30d': -0.015,  # Battery declining 0.015 V/day
    'battery_trend_r2_30d': 0.92,  # Strong linear trend (R²=0.92)
    'optical_trend_30d': -8.5,     # Optical sensor declining 8.5 units/day
    'rsrp_trend_30d': -0.3,        # Connectivity degrading 0.3 dBm/day
}

# Model learns: "battery_trend_30d < -0.01 V/day = critical"
# This is CAUSAL: Degradation rate predicts failure
```

**Why Trends Generalize:**

**Scenario: New battery batch with different baseline voltage**

**Old model (mean-based):**
```python
# Training data: Battery supplier A, nominal 3.7V
# Learned: "battery_mean < 3.3V = critical"

# Production: Battery supplier B, nominal 3.85V
# Healthy device: battery_mean = 3.65V
# Prediction: CRITICAL (FALSE POSITIVE) because 3.65 < 3.3 in old model threshold
```

**New model (trend-based):**
```python
# Training data: Learned "battery_trend_30d < -0.01 V/day = critical"
# (degradation rate, not absolute value)

# Production: Battery supplier B, nominal 3.85V
# Healthy device: battery_mean = 3.65V, battery_trend_30d = -0.002 V/day (stable)
# Prediction: NON-CRITICAL (CORRECT) because trend is gradual, not rapid degradation
```

**Impact:** Model generalizes across hardware batches because degradation RATE is physics (invariant), not baseline value (supplier-dependent).

---

## Priority 4: Delta and Rate Features

### Objective

**Normalize for different baselines:** Calculate change over time (delta) and percentage change (rate).

### Implementation

**Delta Features:**

```python
def calculate_delta_features(timeseries_df, observation_timestamp, windows=[7, 30]):
    """
    Calculate change in sensor values over time windows.
    
    Delta = value_at_end - value_at_start
    """
    features = {}
    
    for window_days in windows:
        window_start = observation_timestamp - pd.Timedelta(days=window_days)
        window_df = timeseries_df[
            (timeseries_df['timestamp'] >= window_start) &
            (timeseries_df['timestamp'] < observation_timestamp)
        ]
        
        if len(window_df) < 2:
            continue
        
        # Get first and last values in window
        first_row = window_df.iloc[0]
        last_row = window_df.iloc[-1]
        
        # Battery voltage change
        delta_battery = last_row['battery_voltage'] - first_row['battery_voltage']
        features[f'delta_battery_{window_days}d'] = delta_battery  # Volts
        
        # Optical sensor change
        delta_optical = last_row['optical_value'] - first_row['optical_value']
        features[f'delta_optical_{window_days}d'] = delta_optical
        
        # RSRP change (connectivity)
        delta_rsrp = last_row['rsrp'] - first_row['rsrp']
        features[f'delta_rsrp_{window_days}d'] = delta_rsrp  # dBm
    
    return features
```

**Rate Features (Percentage Change):**

```python
def calculate_rate_features(timeseries_df, observation_timestamp, windows=[7, 30]):
    """
    Calculate percentage change (rate) over time windows.
    
    Rate = (value_end - value_start) / value_start * 100 / window_days
    """
    features = {}
    
    for window_days in windows:
        window_start = observation_timestamp - pd.Timedelta(days=window_days)
        window_df = timeseries_df[
            (timeseries_df['timestamp'] >= window_start) &
            (timeseries_df['timestamp'] < observation_timestamp)
        ]
        
        if len(window_df) < 2:
            continue
        
        first_row = window_df.iloc[0]
        last_row = window_df.iloc[-1]
        
        # Battery degradation rate (%/day)
        if first_row['battery_voltage'] > 0:
            battery_rate = (
                (last_row['battery_voltage'] - first_row['battery_voltage']) 
                / first_row['battery_voltage'] 
                * 100 
                / window_days
            )
            features[f'battery_degradation_rate_{window_days}d'] = battery_rate  # %/day
        
        # Optical sensor degradation rate
        if first_row['optical_value'] > 0:
            optical_rate = (
                (last_row['optical_value'] - first_row['optical_value']) 
                / first_row['optical_value'] 
                * 100 
                / window_days
            )
            features[f'optical_degradation_rate_{window_days}d'] = optical_rate  # %/day
    
    return features
```

**Impact:**

**Rate features normalize for different baselines:**

```python
# Device A: Battery 4.0V → 3.7V over 30 days
delta_battery_30d = 3.7 - 4.0 = -0.3 V
battery_degradation_rate_30d = (-0.3 / 4.0) * 100 / 30 = -0.25 %/day

# Device B: Battery 3.85V → 3.55V over 30 days (different supplier, lower baseline)
delta_battery_30d = 3.55 - 3.85 = -0.3 V  # SAME absolute change
battery_degradation_rate_30d = (-0.3 / 3.85) * 100 / 30 = -0.26 %/day  # SIMILAR rate

# Model learns: "battery_degradation_rate < -0.2 %/day = critical"
# Generalizes across battery suppliers (different baselines, same physics)
```

---

## Priority 5: Temporal Metadata Features

### Objective

**Provide lifecycle context:** Add metadata features about device history, activity patterns, reactivations.

### Implementation

```python
def calculate_temporal_metadata(timeseries_df, metadata, observation_timestamp):
    """
    Calculate temporal metadata features.
    """
    features = {}
    
    # Time since activation
    if metadata.get('activation_timestamp'):
        features['days_since_activation'] = (
            observation_timestamp - metadata['activation_timestamp']
        ).days
    
    # Total inactive time
    inactive_days = 0
    for inactive in metadata.get('inactive_periods', []):
        inactive_days += (inactive['end'] - inactive['start']).days
    features['days_inactive_total'] = inactive_days
    
    # Number of inactive periods (reactivation count)
    features['num_inactive_periods'] = len(metadata.get('inactive_periods', []))
    
    # Time since last reactivation
    if metadata.get('inactive_periods'):
        last_reactivation = max(period['end'] for period in metadata['inactive_periods'])
        features['days_since_last_reactivation'] = (observation_timestamp - last_reactivation).days
    else:
        features['days_since_last_reactivation'] = None
    
    # Production duration (active time only)
    production_df = timeseries_df[timeseries_df['lifecycle_phase'] == 'production']
    if len(production_df) > 0:
        features['production_duration_days'] = (
            production_df['timestamp'].max() - production_df['timestamp'].min()
        ).days
    
    # Message frequency (messages per day in production)
    if features.get('production_duration_days', 0) > 0:
        features['message_frequency_per_day'] = len(production_df) / features['production_duration_days']
    
    # Lab testing duration (if applicable)
    if metadata.get('lab_test_start_timestamp') and metadata.get('lab_test_end_timestamp'):
        features['lab_test_duration_days'] = (
            metadata['lab_test_end_timestamp'] - metadata['lab_test_start_timestamp']
        ).days
    
    return features
```

**Use Cases:**

**1. Control for confounders:**

```python
# Model can learn: "If num_inactive_periods > 2, weight variability features less"
# (high variability may be lifecycle artifact, not sensor degradation)
```

**2. Lifecycle-aware predictions:**

```python
# Model can learn: "If days_since_activation < 7, device may still be settling (lower threshold)"
# (new devices may have higher variability during burn-in period)
```

**3. Deployment pattern detection:**

```python
# Automatically infer deployment pattern from metadata:
if device_features['lab_test_duration_days'] > 0 and device_features['days_inactive_total'] > 30:
    deployment_pattern = 'lab_tested_inactive_production'
elif device_features['days_inactive_total'] == 0 and device_features['days_since_activation'] > 30:
    deployment_pattern = 'direct_deploy_always_active'
else:
    deployment_pattern = 'unknown'
```

---

## Implementation Examples

### Complete Feature Engineering Pipeline

```python
# scripts/build_temporal_features.py
"""
Build next-generation training dataset with temporal features.

Usage:
    python scripts/build_temporal_features.py \\
        --sensor-data data/sensor_timeseries.csv \\
        --metadata data/device_metadata.json \\
        --output data/training_temporal_features.csv
"""

import pandas as pd
import json
from pathlib import Path

def build_temporal_features_dataset(
    sensor_timeseries_path,
    metadata_path,
    output_path,
    prediction_horizon_days=30
):
    """
    Build complete training dataset with temporal features.
    
    Args:
        sensor_timeseries_path: Raw sensor readings CSV
        metadata_path: Device metadata JSON
        output_path: Output CSV path
        prediction_horizon_days: Calculate features X days before failure
    
    Returns:
        DataFrame with temporal features
    """
    # Load data
    print("Loading sensor timeseries...")
    sensor_df = pd.read_csv(sensor_timeseries_path, parse_dates=['timestamp'])
    
    print("Loading device metadata...")
    with open(metadata_path) as f:
        metadata_list = json.load(f)
    
    training_data = []
    
    for metadata in metadata_list:
        device_id = metadata['device_id']
        print(f"Processing device {device_id}...")
        
        # Get device timeseries
        device_timeseries = sensor_df[sensor_df['device_id'] == device_id].copy()
        
        # Detect lifecycle phases
        device_timeseries = detect_lifecycle_phases(device_timeseries, metadata)
        
        # Filter to production period
        production_timeseries = device_timeseries[
            device_timeseries['lifecycle_phase'] == 'production'
        ]
        
        if len(production_timeseries) == 0:
            print(f"  ⚠️  No production data for {device_id}, skipping")
            continue
        
        # Determine observation timestamp
        if metadata.get('is_critical') and metadata.get('failure_timestamp'):
            # Critical device: observe BEFORE failure
            observation_timestamp = pd.Timestamp(metadata['failure_timestamp']) - pd.Timedelta(days=prediction_horizon_days)
        else:
            # Healthy device: observe at latest available data
            observation_timestamp = production_timeseries['timestamp'].max()
        
        # Calculate all feature types
        features = {}
        
        # 1. Production-only aggregated features
        features.update(calculate_production_only_features(production_timeseries))
        
        # 2. Time-windowed features
        features.update(calculate_windowed_features(
            production_timeseries,
            observation_timestamp,
            windows=[7, 14, 30]
        ))
        
        # 3. Trend features
        features.update(calculate_trend_features(
            production_timeseries,
            observation_timestamp,
            windows=[7, 30]
        ))
        
        # 4. Delta and rate features
        features.update(calculate_delta_features(
            production_timeseries,
            observation_timestamp,
            windows=[7, 30]
        ))
        features.update(calculate_rate_features(
            production_timeseries,
            observation_timestamp,
            windows=[7, 30]
        ))
        
        # 5. Temporal metadata
        features.update(calculate_temporal_metadata(
            device_timeseries,
            metadata,
            observation_timestamp
        ))
        
        # Add label and metadata
        features['device_id'] = device_id
        features['is_critical'] = metadata.get('is_critical', 0)
        features['observation_timestamp'] = observation_timestamp
        features['prediction_horizon_days'] = prediction_horizon_days
        
        training_data.append(features)
    
    # Create DataFrame
    df = pd.DataFrame(training_data)
    
    # Save
    df.to_csv(output_path, index=False)
    print(f"\n✅ Saved {len(df)} devices to {output_path}")
    print(f"   Features: {len(df.columns)} columns")
    print(f"   Critical devices: {df['is_critical'].sum()} ({df['is_critical'].mean():.1%})")
    
    return df

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sensor-data', required=True)
    parser.add_argument('--metadata', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--prediction-horizon', type=int, default=30)
    args = parser.parse_args()
    
    build_temporal_features_dataset(
        args.sensor_data,
        args.metadata,
        args.output,
        args.prediction_horizon
    )
```

---

## Validation Approaches

### Temporal Holdout Validation

**Validate prediction horizon:**

```python
# Test: Can model predict 30 days in advance?

# Training set: Features at failure - 30 days
train_df = build_temporal_features_dataset(
    sensor_data, metadata, prediction_horizon_days=30
)

# Test set: Features at different horizons
test_horizons = []
for horizon in [1, 7, 14, 30, 60]:
    test_df = build_temporal_features_dataset(
        sensor_data, metadata_test, prediction_horizon_days=horizon
    )
    
    # Train model on 30-day horizon data
    model.fit(train_df.drop(['is_critical', 'device_id'], axis=1), train_df['is_critical'])
    
    # Test on this horizon
    predictions = model.predict(test_df.drop(['is_critical', 'device_id'], axis=1))
    recall = recall_score(test_df['is_critical'], predictions)
    
    test_horizons.append({'horizon_days': horizon, 'recall': recall})

# Analyze results
# Expected: Recall stable across horizons (30-60d) = causal patterns learned
# If recall drops dramatically at 60d = model only captures short-term patterns
```

### Feature Ablation Study

**Identify most important feature types:**

```python
# Baseline: All features
all_features_recall = evaluate_model(train_df, test_df, features='all')

# Ablation: Remove production-only features
features_no_production = [col for col in train_df.columns if 'production' not in col]
no_production_recall = evaluate_model(train_df, test_df, features=features_no_production)

# Ablation: Remove trend features
features_no_trend = [col for col in train_df.columns if 'trend' not in col]
no_trend_recall = evaluate_model(train_df, test_df, features=features_no_trend)

# Ablation: Remove delta/rate features
features_no_delta = [col for col in train_df.columns if 'delta' not in col and 'rate' not in col]
no_delta_recall = evaluate_model(train_df, test_df, features=features_no_delta)

# Analysis:
# If removing production-only features drops recall 20%: Lifecycle confounding was major issue
# If removing trend features drops recall 15%: Degradation dynamics critical for prediction
# If removing delta/rate drops recall <5%: Baseline normalization less important
```

---

## Expected Impact

### Performance Improvements

**Quantitative expectations:**

| Metric | Current Model (Lifecycle-Aggregated) | Next-Gen Model (Temporal Features) |
|--------|--------------------------------------|-------------------------------------|
| **Recall (Overall)** | 78.6% | **85-90%** (fewer false negatives from confounding) |
| **Precision (Overall)** | 84.6% | **88-92%** (fewer false positives from deployment artifacts) |
| **Recall (Direct-Deploy)** | ~55% (FAILS) | **75-80%** (generalizes without lifecycle confounding) |
| **Recall (Lab-Tested)** | ~79% (OK) | **85-90%** (improved with trends) |
| **Prediction Horizon** | Unknown (possibly 0-7 days) | **Validated 30 days** |
| **Generalization (New Hardware)** | FAILS (learns absolute values) | **Robust** (learns degradation rates) |

### Qualitative Benefits

**1. Causal Interpretability:**

```python
# Current model (black box):
"Device predicted critical because optical_mean=300"
# Why? Is 300 low? High? Relative to what?

# Next-gen model (interpretable):
"Device predicted critical because:
- battery_trend_30d = -0.018 V/day (rapid degradation)
- optical_degradation_rate_30d = -1.2%/day (sensor failing)
- rsrp_trend_30d = -0.5 dBm/day (connectivity degrading)"
# Clear causal story: Device is degrading rapidly across multiple sensors
```

**2. Regime-Independent Deployment:**

```python
# Current: Conditional deployment based on deployment pattern
if deployment_pattern == 'lab_tested':
    use_model = True
else:
    use_model = False  # Baseline for direct-deploy

# Next-gen: Universal deployment
use_model = True  # Works for ALL deployment patterns (no confounding)
```

**3. Quantified Prediction Horizon:**

```python
# Current: Unknown prediction horizon (may only detect at-failure)
"Model predicts failures (unknown how far in advance)"

# Next-gen: Validated prediction horizon
"Model predicts failures 30 days in advance with 85% recall"
# Actionable: Gives operations team 30-day window to intervene
```

---

## Migration Path

### Phase 1: Data Collection (Months 1-3)

**Goal:** Collect raw timeseries data and lifecycle metadata

**Actions:**
1. Instrument IoT platform to log raw sensor readings with timestamps
2. Collect activation_timestamp, lab_test_start/end, inactive_periods for each device
3. Enrich failure labels with failure_timestamp
4. Target: 1000+ devices with complete timeseries (minimum 500 devices, 50+ critical failures)

**Validation:** Check data completeness (>95% devices have timestamps, >90% have lifecycle metadata)

### Phase 2: Feature Engineering (Month 4)

**Goal:** Implement temporal feature pipeline

**Actions:**
1. Implement lifecycle phase detection
2. Implement production-only features
3. Implement time-windowed, trend, delta, rate features
4. Build training dataset with prediction_horizon=30 days
5. Validate feature distribution (check for NaN, outliers, correlated features)

**Output:** `data/training_temporal_features.csv` with 100+ features per device

### Phase 3: Model Training and Validation (Month 5)

**Goal:** Train next-gen model, validate performance

**Actions:**
1. Train RandomForest/XGBoost on temporal features
2. Temporal holdout validation (test at 7, 14, 30, 60 day horizons)
3. Feature ablation study (quantify impact of each feature type)
4. Compare to current model (A/B test on hold-out set)

**Success criteria:** 
- Recall ≥ 85% at 30-day prediction horizon
- Performance NOT degraded on direct-deploy stratum (vs current model)

### Phase 4: Shadow Mode Deployment (Months 6-7)

**Goal:** Deploy next-gen model in shadow mode, validate in production

**Actions:**
1. Deploy next-gen model alongside current model (both in shadow mode)
2. Collect predictions for 60 days
3. Compare: Current model vs next-gen model performance on same production data
4. Drift monitoring (check if temporal features stable over time)

**Decision:** Proceed to Phase 5 if next-gen model ≥ current model + 5% recall

### Phase 5: Gradual Rollout (Months 8-10)

**Goal:** Replace current model with next-gen model

**Actions:**
1. Month 8: 50% next-gen, 50% current model
2. Month 9: 80% next-gen, 20% current model
3. Month 10: 100% next-gen model
4. Monitor performance continuously, rollback if recall < 80%

**Success:** Next-gen model becomes production model

---

**Document version:** 1.0  
**Last updated:** 2025-11-11  
**Review cadence:** Quarterly or after data collection milestones  
**Next review:** 2026-02-11 (or after Phase 1 completion)
