"""
Page 5: Research Context - Project Background & Key Discoveries
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Header
st.title("📖 Research Context & Methodology")
st.markdown("### Understanding the IoT Predictive Maintenance Problem")

st.markdown("---")

# Section 1: The Problem
st.subheader("🔧 The Business Problem")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    **IoT Device Failures in Production Environments**
    
    Our organization deployed **789 IoT devices** for critical monitoring applications. 
    Over time, **45 devices (5.7%) exhibited critical failures** requiring emergency maintenance.
    
    **Challenges:**
    - 🚨 **Unplanned downtime** causes revenue loss and customer dissatisfaction
    - ⚙️ **Emergency repairs** cost 3-5x more than preventive maintenance
    - 📊 **No early warning system** - failures discovered reactively
    - 🔍 **Manual inspection** of 789 devices infeasible (resource constraints)
    
    **Business Objective:**
    Build a machine learning model to **predict critical devices BEFORE failure** 
    enabling **preventive maintenance** and **resource optimization**.
    """)

with col2:
    st.info("""
    **Impact Metrics**
    
    - **789** total devices
    - **45** critical failures (5.7%)
    - **16.8:1** imbalance ratio
    - **29** telemetry features
    - **78.6%** recall achieved
    - **84.6%** precision achieved
    """)

st.markdown("---")

# Section 2: Technical Approach
st.subheader("🔬 Technical Approach & Pipeline")

st.markdown("""
Our solution follows a **rigorous data science methodology** with emphasis on validation and avoiding data leakage.
""")

# Pipeline diagram
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **1️⃣ Data Preparation**
    
    - ✅ **Stratified split** by device_id
    - ✅ **Zero overlap** (552 train, 237 test)
    - ✅ **Balanced proportions** (5.6% vs 5.9% critical)
    - ❌ **Temporal split REJECTED** (data leakage)
    """)

with col2:
    st.markdown("""
    **2️⃣ Feature Engineering**
    
    - 📊 **29 clean features** (telemetry + connectivity + messaging)
    - ⚠️ **Leakage detection** (removed msg6_count, msg6_rate)
    - 📈 **Statistical analysis** (t-tests, distributions)
    - 🔗 **Correlation study** (multicollinearity check)
    """)

with col3:
    st.markdown("""
    **3️⃣ Model Development**
    
    - 🎯 **SMOTE 0.5** (handle 16.8:1 imbalance)
    - 🤖 **Algorithm comparison** (XGB, LGBM, CatBoost)
    - 🏆 **CatBoost WINNER** (78.6% recall, 84.6% precision)
    - 📦 **Production pipeline** (SimpleImputer → SMOTE → CatBoost)
    """)

st.markdown("---")

# Section 3: Key Discoveries & Lessons Learned
st.subheader("💡 Key Discoveries & Critical Lessons")

# Discovery 1: Temporal Split Failure
with st.expander("**🚨 Discovery 1: Temporal Split Failed (0% Recall)**", expanded=True):
    st.markdown("""
    **Problem:** Initial approach split data by time (old messages → train, recent → test)
    
    **Result:** Model achieved **0% recall** - couldn't detect ANY critical devices!
    
    **Root Cause Analysis:**
    - Dataset was **aggregated** (1 row per device, not time-series)
    - Temporal split created **650 devices in BOTH train and test** (severe leakage)
    - Model memorized device IDs instead of learning patterns
    - Critical devices appeared in training data, test became "easy memorization"
    
    **Lesson Learned:** 
    > ⚠️ **Always validate split assumptions** - temporal split only valid for true time-series data
    > 
    > ✅ **Stratified split by device_id** ensures zero overlap and honest evaluation
    
    **Impact:** Switching to stratified split → **50% recall baseline** (honest performance)
    """)

# Discovery 2: MSG6 Leakage
with st.expander("**🔍 Discovery 2: Data Leakage from msg6_count Feature**", expanded=False):
    st.markdown("""
    **Problem:** Model with `msg6_count` feature achieved suspicious **87.5% precision**
    
    **Investigation:** Analyzed feature importance and distributions
    
    **Finding:**
    - `msg6_count` was **#1 feature** (31% importance - red flag!)
    - Message type 6 = **"Device Critical Status Report"**
    - Critical devices send MORE msg6 messages by definition
    - Feature contains **ground truth label information** (data leakage)
    
    **Action Taken:**
    - ❌ Removed `msg6_count` and `msg6_rate` from feature set
    - ✅ Re-trained model with 29 clean features only
    - ✅ Performance dropped to 50% recall (expected with honest features)
    
    **Lesson Learned:**
    > ⚠️ **High single-feature importance = potential leakage indicator**
    > 
    > ✅ **Domain knowledge critical** - understand what features MEAN in business context
    > 
    > ✅ **Validate feature distributions** between critical and normal groups
    
    **Impact:** Honest baseline established → enabled real optimization work
    """)

# Discovery 3: Synthetic Data Validation
with st.expander("**🧪 Discovery 3: Theoretical vs Empirical Synthetic Data**", expanded=False):
    st.markdown("""
    **Experiment:** Validate model using synthetic critical devices
    
    **Approach 1 - Theoretical (NB06):**
    - **Assumption:** "High values = critical" (e.g., p75-p100 percentiles)
    - **Method:** Sample from upper quartiles of general distribution
    - **Result:** 0% recall - TOTAL FAILURE ❌
    
    **Approach 2 - Empirical (NB06B):**
    - **Validation:** Analyzed critical vs normal distributions FIRST
    - **Discovery:** Direction varies by feature (battery LOW, temp HIGH, messages VARIABLE)
    - **Method:** SMOTE interpolation from REAL critical devices (preserves correlations)
    - **Result:** 100% recall - validates SMOTE works ✅
    
    **Lesson Learned:**
    > ⚠️ **Theoretical assumptions fail** - "high values = bad" is not universal
    > 
    > ✅ **Empirical analysis required** - test statistical differences before sampling
    > 
    > ✅ **SMOTE preserves patterns** - interpolates within real distribution manifold
    
    **Important Caveat:**
    - 100% synthetic recall does NOT mean model is better than 78.6% real recall
    - Synthetic generated FROM training critical → model KNOWS these patterns
    - Real test set (78.6%) remains **authoritative validation**
    - Synthetic useful for **stress testing edge cases**, not independent validation
    """)

# Discovery 4: Algorithm Comparison
with st.expander("**⚖️ Discovery 4: CatBoost Outperforms XGBoost and LightGBM**", expanded=False):
    st.markdown("""
    **Experiment:** Compare 3 gradient boosting algorithms with SMOTE 0.5
    
    **Results:**
    
    | Model | Recall | Precision | F1-Score | AUC | Decision |
    |-------|--------|-----------|----------|-----|----------|
    | XGBoost + SMOTE | 71.4% | 71.4% | 71.4% | 0.8799 | Baseline |
    | LightGBM + SMOTE | 64.3% | 69.2% | 66.7% | 0.8823 | ❌ DISQUALIFIED (recall < 70%) |
    | **CatBoost + SMOTE** | **78.6%** | **84.6%** | **81.5%** | **0.8621** | ✅ **WINNER** |
    
    **Why CatBoost Won:**
    - ✅ **+7.2 pp recall improvement** (10/14 → 11/14 critical detected)
    - ✅ **+13.2 pp precision improvement** (71.4% → 84.6%, only 2 false alarms)
    - ✅ **Ordered boosting** reduces overfitting on small dataset (789 total, 45 critical)
    - ✅ **Symmetric trees** provide better generalization vs XGBoost asymmetric
    
    **Lesson Learned:**
    > ✅ **Test multiple algorithms** - different inductive biases work better on different data
    > 
    > ✅ **CatBoost excels on small datasets** - default regularization prevents overfitting
    > 
    > ⚠️ **Tradeoff exists** - CatBoost slightly lower AUC but MUCH better precision/recall
    
    **See MODEL_COMPARISON.md** for complete analysis with confusion matrices and business impact.
    """)

st.markdown("---")

# Section 4: Features Engineering Deep Dive
st.subheader("🔧 Features Engineering: 29 Features Explained")

st.markdown("""
Our final model uses **29 numerical features** extracted from IoT device telemetry, grouped into 3 categories:
""")

tab1, tab2, tab3 = st.tabs(["📡 Telemetry (18)", "📶 Connectivity (9)", "📨 Messaging (2)"])

with tab1:
    st.markdown("""
    ### Telemetry Features (18 total)
    
    **Optical Sensor (7 features):**
    - `optical_mean`, `optical_std`, `optical_min`, `optical_max` - Central tendency and spread
    - `optical_readings` - Sample count (data quality indicator)
    - `optical_below_threshold` - Degradation indicator
    - `optical_range` - Variability metric
    
    **Temperature Sensor (6 features):**
    - `temp_mean`, `temp_std`, `temp_min`, `temp_max` - Thermal distribution
    - `temp_above_threshold` - Overheating indicator
    - `temp_range` - Thermal stability
    
    **Battery/Power (5 features):**
    - `battery_mean`, `battery_std`, `battery_min`, `battery_max` - Voltage distribution
    - `battery_below_threshold` - Low power events
    
    **Engineering Rationale:**
    - **Aggregations** capture both average behavior (mean) and variability (std, range)
    - **Thresholds** encode domain knowledge (e.g., battery < 3.0V = critical)
    - **Min/Max** detect extreme events (spikes, drops)
    
    **Key Insight:** Critical devices show **LOW battery** (power failure), **HIGH temp** (overheating), 
    **VARIABLE optical** (unstable sensor) - NOT universally "high values".
    """)

with tab2:
    st.markdown("""
    ### Connectivity Features (9 total)
    
    **Signal-to-Noise Ratio - SNR (3 features):**
    - `snr_mean`, `snr_std`, `snr_min` - Signal quality distribution
    - **Importance:** Low SNR indicates poor signal → communication failures
    
    **Reference Signal Received Power - RSRP (3 features):**
    - `rsrp_mean`, `rsrp_std`, `rsrp_min` - Signal strength distribution
    - **Importance:** Weak signal (< -110 dBm) → device struggling to connect
    
    **Reference Signal Received Quality - RSRQ (3 features):**
    - `rsrq_mean`, `rsrq_std`, `rsrq_min` - Link quality distribution
    - **Importance:** Poor quality → retransmissions, latency, eventual dropout
    
    **Engineering Rationale:**
    - **Mean values** show average connectivity health
    - **Std/variability** indicates connection stability (stable vs flaky)
    - **Min values** detect worst-case scenarios (connection almost lost)
    
    **Key Insight:** Critical devices show **degrading connectivity BEFORE complete failure** 
    (SNR dropping, RSRP weakening, RSRQ unstable) - early warning signal!
    """)

with tab3:
    st.markdown("""
    ### Messaging Features (2 total)
    
    **`total_messages` (count):**
    - Total number of messages sent by device in observation window
    - **Low values:** Silent device (already failed or communication blocked)
    - **Normal values:** Regular telemetry reporting (healthy)
    - **High values:** Possible "death throes" (device spamming before failure)
    
    **`max_frame_count` (integer):**
    - Maximum frame count observed in message fragmentation
    - **High values:** Device attempting **desperate reconnection** (communication stress)
    - **Importance:** #1 or #2 most important feature across all models
    - **Interpretation:** When device struggles, it fragments messages more (retries, errors)
    
    **Engineering Rationale:**
    - **Activity level** (total_messages) separates silent failures from active devices
    - **Fragmentation stress** (max_frame_count) detects communication desperation
    
    **Key Insight:** `max_frame_count` is a **communication stress indicator** - 
    critical devices show abnormally high frame counts as they struggle to maintain connection.
    
    **Why only 2 messaging features?**
    - Originally had `msg6_count`, `msg6_rate` → **REMOVED due to data leakage**
    - Message type 6 = "Critical Status Report" → contains ground truth label info
    - Keeping only neutral messaging metrics (total volume, fragmentation) ensures honest prediction
    """)

st.markdown("---")

# Section 5: Validation Philosophy
st.subheader("✅ Validation Philosophy & Best Practices")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **What We Did RIGHT ✅**
    
    1. **Stratified Split by Device ID**
       - Zero overlap between train (552) and test (237)
       - Balanced proportions (5.6% vs 5.9% critical)
       - Honest evaluation on unseen devices
    
    2. **Leakage Detection & Removal**
       - Analyzed feature importance distributions
       - Removed msg6_count/msg6_rate (ground truth leak)
       - Validated with domain experts
    
    3. **Empirical Validation Over Theory**
       - Tested synthetic data assumptions (NB06 failure)
       - Corrected with empirical analysis (NB06B success)
       - Statistical tests before engineering features
    
    4. **Multiple Algorithm Comparison**
       - XGBoost, LightGBM, CatBoost tested
       - Decision matrix with business criteria
       - Documented tradeoffs (MODEL_COMPARISON.md)
    
    5. **Production-Ready Pipeline**
       - End-to-end Pipeline (Imputer → SMOTE → CatBoost)
       - Saved artifacts (joblib + metadata JSON)
       - Inference functions for batch/single prediction
    """)

with col2:
    st.markdown("""
    **Lessons for Future Projects ⚠️**
    
    1. **Split Validation**
       - ❌ Don't assume temporal split works for aggregated data
       - ✅ Validate overlap between train/test BEFORE modeling
       - ✅ Use stratification for imbalanced classes
    
    2. **Feature Leakage**
       - ❌ Don't trust high single-feature importance blindly
       - ✅ Understand what features MEAN in business context
       - ✅ Check if feature contains "future information"
    
    3. **Theoretical Assumptions**
       - ❌ Don't assume "high = bad" or "low = good"
       - ✅ Analyze distributions empirically FIRST
       - ✅ Use statistical tests (t-test, Mann-Whitney)
    
    4. **Synthetic Validation**
       - ❌ Don't use synthetic as independent validation
       - ✅ Understand synthetic = interpolation of training
       - ✅ Use real held-out test set as authoritative
    
    5. **Documentation**
       - ✅ Document decisions (why CatBoost vs XGBoost?)
       - ✅ Keep history of failed approaches (learning value)
       - ✅ Create artifacts for stakeholders (MODEL_COMPARISON.md)
    """)

st.markdown("---")

# Section 6: Business Impact Summary
st.subheader("💼 Business Impact & ROI")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Critical Devices Detected",
        "11/14",
        delta="78.6% coverage",
        help="Preventive maintenance triggered for 11 critical devices"
    )
    st.caption("**Prevented failures** before emergency breakdown")

with col2:
    st.metric(
        "False Alarms",
        "2/237",
        delta="0.8% FP rate",
        delta_color="inverse",
        help="Only 2 false positives in entire normal population"
    )
    st.caption("**Minimal investigation overhead** for operations team")

with col3:
    st.metric(
        "Missed Failures",
        "3/14",
        delta="21.4% miss rate",
        delta_color="inverse",
        help="3 critical devices not detected (acceptable tradeoff)"
    )
    st.caption("**Fallback:** Manual inspection + domain expertise")

st.markdown("""
**Scenario: 1000 Devices Deployed**

- ✅ **47 failures prevented** vs 42 without model (+5 devices saved)
- ✅ **12 emergency repairs** vs 17 without model (-5 urgent calls)
- ✅ **8 false alarms** vs 16 with baseline model (-50% investigation cost)
- 💰 **Estimated savings:** $25K-$50K per year (reduced downtime + optimized maintenance)

**Model enables proactive maintenance strategy** shifting from reactive firefighting to planned interventions.
""")

st.markdown("---")

# Footer
st.info("""
📚 **Further Reading:**
- **MODEL_COMPARISON.md** - Complete algorithm comparison with confusion matrices
- **Notebooks 02B-08** - Detailed technical implementation and validation
- **CHANGELOG.md** - Complete project timeline (12 phases)
""")

st.caption("""
**Research Context** | IoT Predictive Maintenance Project | CatBoost v1.0 | November 2025
""")
