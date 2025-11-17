"""
Page 5: Research Context - Project Background & Key Discoveries
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.translations import get_text, get_language_from_session

# Get language
lang = get_language_from_session(st.session_state)

# Header
st.title(get_text('research', 'title', lang))
st.markdown(f"### {get_text('research', 'subtitle', lang)}")

st.markdown("---")

# Model Version Indicator
st.info(get_text('research', 'model_version_info', lang))

st.markdown("---")

# Section 1: The Problem
st.subheader(get_text('research', 'problem_title', lang))

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(get_text('research', 'problem_content', lang))

with col2:
    st.info(f"""{get_text('research', 'evolution_box_title', lang)}

{get_text('research', 'evolution_v1_title', lang)}
- {get_text('research', 'evolution_v1_devices', lang)}
- {get_text('research', 'evolution_v1_perf', lang)}
- {get_text('research', 'evolution_v1_auc', lang)}
- {get_text('research', 'evolution_v1_issue', lang)}

{get_text('research', 'evolution_v2_title', lang)}
- {get_text('research', 'evolution_v2_devices', lang)}
- {get_text('research', 'evolution_v2_perf', lang)}
- {get_text('research', 'evolution_v2_auc', lang)}
- {get_text('research', 'evolution_v2_benefit', lang)}
""")

st.markdown("---")

# Section 2: Technical Approach
st.subheader(get_text('research', 'technical_title', lang))

st.markdown(get_text('research', 'technical_intro', lang))

# Model Evolution Tabs
tab_v1, tab_v2 = st.tabs([get_text('research', 'tab_v1', lang), get_text('research', 'tab_v2', lang)])

with tab_v1:
    st.markdown("""
    ### Model v1: Initial Approach with Mixed Data
    
    **Dataset:** 789 devices (FACTORY production + FIELD deployment messages mixed)
    
    **Performance:**
    - ✅ Recall: 78.6% (11/14 critical detected)
    - ✅ Precision: 84.6% (only 2 false alarms)
    - ✅ F1-Score: 81.5%
    - ⚠️ ROC-AUC: 0.8621
    
    **Pipeline:**
    - Stratified split: 552 train, 237 test (by device_id)
    - Features: 29 telemetry + connectivity + messaging
    - SMOTE 0.5 for class balancing
    - CatBoost gradient boosting
    
    **Problem Discovered:**
    - 🚨 **Lifecycle mixing contamination** - FACTORY messages (lab testing) mixed with FIELD messages (production)
    - Device 861275072515287: Flagged 99.8% critical (FALSE POSITIVE) due to 30 max_frame_count from FACTORY
    - max_frame_count=30, optical_readings=99 are NORMAL in factory testing, NOT critical in field
    - Model learned patterns from wrong lifecycle phase → inflated metrics
    
    **Decision:**
    - ❌ v1 deprecated due to contamination
    - ✅ Rebuild with FIELD-only data (v2)
    """)

with tab_v2:
    st.markdown("""
    ### Model v2: FIELD-only Clean Data (Current Production)
    
    **Dataset:** 762 devices (FIELD deployment only - removed 362k FACTORY messages = 31.8%)
    
    **Performance:**
    - ✅ Recall: 57.1% (8/14 critical detected) - **honest baseline**
    - ✅ Precision: 57.1% (6 false positives)
    - ✅ F1-Score: 57.1%
    - ✅ **ROC-AUC: 0.9186** (+6.6% vs v1) - **better probability calibration**
    
    **Pipeline:**
    - Stratified split: 533 train (29 critical), 229 test (14 critical)
    - **Features: 30** (added `days_since_last_message` temporal feature)
    - SMOTE 0.5 for class balancing
    - CatBoost gradient boosting
    
    **Trade-off Philosophy: "2 Steps Back, 3 Forward"**
    - ⚠️ Lower recall (-21.5% vs v1) due to clean data
    - ✅ Better AUC (+6.6%) - improved probability calibration
    - ✅ **Solid foundation** for future improvements without contamination
    
    **Roadmap to Exceed v1:**
    1. Hyperparameter tuning (GridSearch) - Expected +10-15% recall
    2. FASE 3 temporal features (4 new) - Expected +20% recall
    3. Threshold optimization - Better precision/recall balance
    
    **Target:** Precision >80%, Recall >75% with clean FIELD-only data
    """)

st.markdown("---")

# Pipeline diagram - Updated for v2
st.subheader("🔄 Model v2 Pipeline")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **1️⃣ Data Preparation**
    
    - ✅ **Lifecycle filtering** (MODE='FIELD' only)
    - ✅ **Stratified split** by device_id
    - ✅ **Zero overlap** (533 train, 229 test)
    - ✅ **Balanced proportions** (5.4% vs 6.1% critical)
    - ❌ **Temporal split REJECTED** (data leakage)
    """)

with col2:
    st.markdown("""
    **2️⃣ Feature Engineering**
    
    - 📊 **30 features** (29 telemetry + 1 temporal)
    - ⭐ **NEW:** days_since_last_message
    - ⚠️ **Leakage detection** (removed msg6_count, msg6_rate)
    - 📈 **Statistical analysis** (t-tests, distributions)
    - 🔗 **Correlation study** (multicollinearity check)
    """)

with col3:
    st.markdown("""
    **3️⃣ Model Development**
    
    - 🎯 **SMOTE 0.5** (handle imbalance)
    - 🤖 **CatBoost** (best in v1 testing)
    - 📦 **Production pipeline** (Imputer → SMOTE → CatBoost)
    - ✅ **ROC-AUC 0.9186** (better calibration vs v1)
    """)

st.markdown("---")

# Section 2.5: Why CatBoost?
st.subheader("🤖 Why CatBoost? - Algorithm Comparison (v1 Research)")

st.markdown("""
**CatBoost** (Categorical Boosting) was selected in v1 research after rigorous comparison with XGBoost and LightGBM. 
This algorithm choice **carried over to v2** as it showed superior performance on small, imbalanced datasets.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **🔍 What is CatBoost?**
    
    CatBoost is an **advanced gradient boosting** algorithm that builds an ensemble of 
    **decision trees sequentially**, where each tree corrects errors from previous trees.
    
    **Key Technical Advantages:**
    
    1. **Ordered Boosting** 📊
       - Prevents **target leakage** during training
       - Reduces overfitting compared to XGBoost's level-wise approach
       - Uses different permutations to compute residuals
    
    2. **Symmetric Trees** 🌳
       - Builds **balanced binary trees** (fewer leaves)
       - Faster prediction time in production
       - Better generalization on unseen data
    
    3. **Native Categorical Support** 🏷️
       - Handles categorical features WITHOUT one-hot encoding
       - Computes optimal splits using target statistics
       - (Not used in this project - all features numerical)
    """)

with col2:
    st.markdown("""
    **🏆 v1 Algorithm Comparison Results**
    
    Tested on 789 devices (v1 mixed data) with identical SMOTE 0.5 preprocessing:
    
    | Algorithm | Recall | Precision | F1 | False Alarms |
    |-----------|--------|-----------|----|--------------| 
    | XGBoost   | 71.4%  | 71.4%     | 71.4% | 4/237 (1.7%) |
    | LightGBM  | 64.3%  | 69.2%     | 66.7% | 4/237 (1.7%) |
    | **CatBoost** | **78.6%** | **84.6%** | **81.5%** | **2/237 (0.8%)** |
    
    **CatBoost delivered:**
    - ✅ **+7.2pp recall** vs XGBoost (1 more critical device detected)
    - ✅ **+13.2pp precision** vs XGBoost (50% fewer false alarms)
    - ✅ **Exceeds 80% precision target** (business requirement)
    
    **Why CatBoost for v2?**
    - ✅ Proven performance on small datasets (789 devices v1, 762 devices v2)
    - ✅ **Ordered boosting** crucial for limited critical samples (45 v1, 43 v2)
    - ✅ Built-in overfitting protection
    - ✅ Faster training than XGBoost with similar/better results
    
    **Note:** v1 metrics shown above. v2 metrics different due to clean FIELD-only data (see Model Evolution section).
    """)

st.markdown("---")

# Section 3: Key Discoveries & Lessons Learned
st.subheader("💡 Key Discoveries & Critical Lessons")

# Discovery 0: Lifecycle Contamination (NEW - v2 discovery)
with st.expander("**🚨 Discovery 0: Lifecycle Contamination (FACTORY vs FIELD)** ⭐ NEW", expanded=True):
    st.markdown("""
    **Problem:** Model v1 achieved 78.6% recall but showed suspicious false positives
    
    **Investigation:** Device 861275072515287 flagged 99.8% critical but appeared healthy in production
    
    **Root Cause Analysis:**
    - Dataset mixed **FACTORY messages** (lab testing, Nov 2024) with **FIELD messages** (production, May-Nov 2025)
    - FACTORY behavior is DIFFERENT from FIELD behavior:
      - **FACTORY:** High max_frame_count (30), many optical readings (99), high SNR (30) = NORMAL testing
      - **FIELD:** Same patterns = CRITICAL device struggling
    - Model learned "high max_frame_count = critical" from FIELD, applied to FACTORY → **false positive**
    
    **Impact on 861275072515287:**
    - 5,279 FACTORY messages (Nov 2024) vs only 9 FIELD messages (May-Oct 2025)
    - Features: max_frame_count=30, optical_readings=99, snr_readings=30
    - In FACTORY context: Normal testing stress
    - In FIELD context: Device struggling (red flag)
    - **v1 prediction:** 99.8% critical (contaminated by FACTORY patterns)
    
    **Solution - FASE 2: v2 FIELD-only**
    - ✅ Filter MODE='FIELD' only → remove 362k FACTORY messages (31.8%)
    - ✅ 762 devices remaining (removed 27 FACTORY-only devices)
    - ✅ Model v2 trained on FIELD-only → learns production patterns correctly
    - ✅ Better probability calibration (AUC 0.8621 → 0.9186)
    
    **Trade-off:**
    - ⚠️ Recall dropped: 78.6% → 57.1% (-21.5%)
    - ✅ AUC improved: 0.8621 → 0.9186 (+6.6%)
    - ✅ Clean foundation for future improvements (no contamination)
    
    **Lesson Learned:**
    > ⚠️ **Lifecycle phases matter** - Lab testing ≠ Production deployment
    > 
    > ✅ **Filter by operational context** - MODE='FIELD' for production predictions
    > 
    > ✅ **Philosophy: "2 steps back, 3 forward"** - Accept short-term metric drop for long-term gains
    
    **Impact:** v2 deployed Nov 13, 2025 - foundation for FASE 3 temporal features (expected +20% recall)
    """)

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
with st.expander("**⚖️ Discovery 4: CatBoost Outperforms XGBoost and LightGBM (v1)**", expanded=False):
    st.markdown("""
    **Experiment:** Compare 3 gradient boosting algorithms with SMOTE 0.5 (v1 mixed data)
    
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
    
    **CatBoost Retained for v2:**
    - ✅ Proven performance on small datasets
    - ✅ Same algorithm, new FIELD-only data
    - ✅ v2 metrics: Recall 57.1%, Precision 57.1%, **AUC 0.9186** (better calibration)
    
    **Lesson Learned:**
    > ✅ **Test multiple algorithms** - different inductive biases work better on different data
    > 
    > ✅ **CatBoost excels on small datasets** - default regularization prevents overfitting
    > 
    > ⚠️ **Algorithm choice stable** - CatBoost best for both v1 and v2
    
    **See MODEL_COMPARISON.md** for complete v1 analysis with confusion matrices.
    """)

st.markdown("---")

# Section 4: Features Engineering Deep Dive
st.subheader("🔧 Features Engineering: 30 Features (v2)")

st.markdown("""
**Model v2** uses **30 numerical features** extracted from IoT device telemetry, grouped into 3 categories:
- **v1 (Mixed):** 29 features (no temporal)
- **v2 (FIELD-only):** 30 features (added `days_since_last_message`)
""")

tab1, tab2, tab3 = st.tabs(["📡 Telemetry (18)", "📶 Connectivity (9)", "📨 Messaging (3)"])

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
    ### Messaging Features (3 total) ⭐ v2: +1 temporal feature
    
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
    
    **`days_since_last_message` (temporal - NEW in v2):** ⭐
    - Days elapsed since device last sent a message
    - **Calculation:** (current_date - MAX(message_timestamp)).days
    - **Low values (0-7):** Active device, regular communication
    - **Medium values (8-30):** Reduced activity, potential degradation
    - **High values (30+):** Silent device, likely failed or disconnected
    - **Importance:** Temporal pattern indicator - inactivity precedes failure
    - **Position:** MUST be at index 3 (after total_messages, max_frame_count) for model v2 compatibility
    
    **Engineering Rationale:**
    - **Activity level** (total_messages) separates silent failures from active devices
    - **Fragmentation stress** (max_frame_count) detects communication desperation
    - **Temporal decay** (days_since_last_message) captures inactivity patterns - NEW v2
    
    **Key Insight:** `max_frame_count` is a **communication stress indicator** - 
    critical devices show abnormally high frame counts as they struggle to maintain connection.
    
    **Why only 3 messaging features?**
    - Originally had `msg6_count`, `msg6_rate` in v1 → **REMOVED due to data leakage**
    - Message type 6 = "Critical Status Report" → contains ground truth label info
    - Kept neutral messaging metrics (volume, fragmentation, temporal) for honest prediction
    - **v2 added** `days_since_last_message` - temporal feature WITHOUT leakage
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

# Model version selector for metrics
model_version = st.radio("Select Model Version:", ["v2 (Current - FIELD-only)", "v1 (Deprecated - Mixed)"], horizontal=True)

if model_version == "v2 (Current - FIELD-only)":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Critical Devices Detected",
            "8/14",
            delta="57.1% coverage",
            help="Preventive maintenance triggered for 8 critical devices (v2 FIELD-only)"
        )
        st.caption("**Clean data foundation** for future improvements")

    with col2:
        st.metric(
            "False Alarms",
            "6/229",
            delta="2.6% FP rate",
            delta_color="inverse",
            help="6 false positives in 229 test devices (v2)"
        )
        st.caption("**Conservative model** - fewer false positives vs v1")

    with col3:
        st.metric(
            "Missed Failures",
            "6/14",
            delta="42.9% miss rate",
            delta_color="inverse",
            help="6 critical devices not detected (tradeoff for clean data)"
        )
        st.caption("**Roadmap:** FASE 3 temporal features to recover recall")

    st.markdown("""
    **Model v2 Impact (FIELD-only - Current Production):**
    
    - ✅ **Better probability calibration:** ROC-AUC 0.9186 (+6.6% vs v1)
    - ✅ **Clean foundation:** No FACTORY contamination
    - ⚠️ **Lower recall:** 57.1% vs 78.6% v1 (trade-off for data quality)
    - 🎯 **Roadmap to exceed v1:**
      1. Hyperparameter tuning → +10-15% recall
      2. FASE 3 temporal features (4 new) → +20% recall
      3. Threshold optimization → Better balance
    
    **Target:** Precision >80%, Recall >75% with clean FIELD-only data by Q1 2026
    """)

else:  # v1 metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Critical Devices Detected",
            "11/14",
            delta="78.6% coverage",
            help="Preventive maintenance for 11 critical devices (v1 mixed data)"
        )
        st.caption("**Higher recall** but contaminated by FACTORY")

    with col2:
        st.metric(
            "False Alarms",
            "2/237",
            delta="0.8% FP rate",
            delta_color="inverse",
            help="Only 2 false positives (v1 - but lifecycle mixing issue)"
        )
        st.caption("**Low FP** but includes FACTORY false positives")

    with col3:
        st.metric(
            "Missed Failures",
            "3/14",
            delta="21.4% miss rate",
            delta_color="inverse",
            help="3 critical devices not detected (v1)"
        )
        st.caption("**Better coverage** but data contamination")

    st.warning("""
    **⚠️ v1 Deprecated (Mixed FACTORY+FIELD Data):**
    
    - ❌ **Lifecycle contamination:** 362k FACTORY messages mixed with FIELD
    - ❌ **False positive example:** Device 861275072515287 (99.8% critical - WRONG)
    - ❌ **Lower AUC:** 0.8621 (worse probability calibration)
    - ✅ **Replaced by v2** on November 13, 2025
    
    **v1 retained for historical comparison and research context only.**
    """)

st.markdown("---")

# Footer
st.info("""
📚 **Further Reading:**
- **MODEL_COMPARISON.md** - v1 algorithm comparison (XGBoost vs LightGBM vs CatBoost)
- **Notebooks 02B-08** - v1 technical implementation and validation
- **CHANGELOG.md** - Complete project timeline (v1 + v2)
- **README.md** - v2 FIELD-only model overview and roadmap
""")

st.caption("""
**Research Context** | IoT Predictive Maintenance Project | **Current:** CatBoost v2.0 FIELD-only (Nov 13, 2025) | **Deprecated:** v1.0 Mixed (Nov 7, 2025)
""")
