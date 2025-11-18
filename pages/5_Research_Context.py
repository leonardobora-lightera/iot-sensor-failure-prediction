"""
Page 5: Research Context - Project Background & Key Discoveries
Reorganized with tabs for better UX (Nov 18, 2025)
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

# Main tabs for better organization
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔬 Research Journey",
    "🔍 Discovery 0", 
    "📊 Model Evolution",
    "💡 Sensor Health Guide",
    "🎨 Visual Diagrams"
])

# ============================================================================
# TAB 1: RESEARCH JOURNEY
# ============================================================================
with tab1:
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
    
    # Pipeline diagram - Updated for v2
    st.markdown("---")
    st.markdown("### 🔄 Model v2 Pipeline")
    
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
    
    # Section: Why CatBoost?
    st.markdown("### 🤖 Why CatBoost? - Algorithm Comparison (v1 Research)")
    
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
        
        **Note:** v1 metrics shown above. v2 metrics different due to clean FIELD-only data (see Model Evolution tab).
        """)

# ============================================================================
# TAB 2: DISCOVERY 0 (CONTAMINATION)
# ============================================================================
with tab2:
    st.markdown("## 🚨 Discovery 0: Lifecycle Contamination (FACTORY vs FIELD)")
    
    st.warning("""
    **Critical Discovery:** Model v1 achieved 78.6% recall but had a fundamental data contamination issue 
    that inflated performance metrics and created false positives in production.
    """)
    
    st.markdown("""
    ### 🔍 The Investigation
    
    **Problem:** Model v1 achieved 78.6% recall but showed suspicious false positives
    
    **Trigger:** Device `861275072515287` flagged 99.8% critical but appeared healthy in production
    
    **Root Cause Analysis:**
    - Dataset mixed **FACTORY messages** (lab testing, Nov 2024) with **FIELD messages** (production, May-Nov 2025)
    - FACTORY behavior is DIFFERENT from FIELD behavior:
      - **FACTORY:** High max_frame_count (30), many optical readings (99), high SNR (30) = NORMAL testing
      - **FIELD:** Same patterns = CRITICAL device struggling
    - Model learned "high max_frame_count = critical" from FIELD, applied to FACTORY → **false positive**
    
    ### 📊 Impact on Device 861275072515287
    
    - **5,279 FACTORY messages** (Nov 2024) vs only **9 FIELD messages** (May-Oct 2025)
    - Features: `max_frame_count=30`, `optical_readings=99`, `snr_readings=30`
    - In FACTORY context: Normal testing stress
    - In FIELD context: Device struggling (red flag)
    - **v1 prediction:** 99.8% critical (contaminated by FACTORY patterns)
    
    ### ✅ Solution - FASE 2: v2 FIELD-only
    
    - ✅ Filter `MODE='FIELD'` only → remove 362k FACTORY messages (31.8%)
    - ✅ 762 devices remaining (removed 27 FACTORY-only devices)
    - ✅ Model v2 trained on FIELD-only → learns production patterns correctly
    - ✅ Better probability calibration (AUC 0.8621 → 0.9186)
    
    ### ⚖️ Trade-off: "2 Steps Back, 3 Forward"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Recall Change", "-21.5%", delta="78.6% → 57.1%", delta_color="inverse")
        st.caption("⚠️ Short-term metric drop")
    
    with col2:
        st.metric("AUC Improvement", "+6.6%", delta="0.8621 → 0.9186")
        st.caption("✅ Better probability calibration")
    
    st.info("""
    ### 💡 Lesson Learned
    
    > ⚠️ **Lifecycle phases matter** - Lab testing ≠ Production deployment
    > 
    > ✅ **Filter by operational context** - MODE='FIELD' for production predictions
    > 
    > ✅ **Philosophy: "2 steps back, 3 forward"** - Accept short-term metric drop for long-term gains
    
    **Impact:** v2 deployed Nov 13, 2025 - foundation for FASE 3 temporal features (expected +20% recall)
    """)

# ============================================================================
# TAB 3: MODEL EVOLUTION
# ============================================================================
with tab3:
    st.markdown("## 📊 Model Evolution: v1 → v2")
    
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
    
    # Features Engineering Deep Dive
    st.markdown("## 🔧 Features Engineering: 30 Features (v2)")
    
    st.markdown("""
    **Model v2** uses **30 numerical features** extracted from IoT device telemetry, grouped into 3 categories:
    - **v1 (Mixed):** 29 features (no temporal)
    - **v2 (FIELD-only):** 30 features (added `days_since_last_message`)
    """)
    
    tab_tel, tab_conn, tab_msg = st.tabs(["📡 Telemetry (18)", "📶 Connectivity (9)", "📨 Messaging (3)"])
    
    with tab_tel:
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
    
    with tab_conn:
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
    
    with tab_msg:
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
    
    # Other Discoveries
    st.markdown("## 💡 Key Discoveries & Lessons Learned")
    
    with st.expander("**🚨 Discovery 1: Temporal Split Failed (0% Recall)**", expanded=False):
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
    
    with st.expander("**⚖️ Discovery 3: CatBoost Outperforms XGBoost and LightGBM (v1)**", expanded=False):
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
    
    # Business Impact Summary
    st.markdown("## 💼 Business Impact & ROI")
    
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

# ============================================================================
# TAB 4: SENSOR HEALTH GUIDE
# ============================================================================
with tab4:
    st.markdown("## 💡 Sensor Health Guide: Top 5 Critical Indicators")
    
    st.info("""
    **Educational Guide:** These are the most important indicators for detecting failing IoT devices, 
    ranked by feature importance from the CatBoost model v2.
    """)
    
    st.markdown("---")
    
    # Top 5 Indicators
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 1️⃣ Optical Sensor Degradation
        **Feature:** `optical_below_threshold`  
        **Importance:** 7.0% (Rank #1-2)
        
        **What it measures:**
        - Percentage of optical readings below acceptable threshold
        - Indicates sensor degradation or contamination
        
        **Why it matters:**
        - High values (>50%) = Sensor failing or obstructed
        - Early warning sign before complete sensor failure
        - Critical for devices relying on optical measurements
        
        **Reference Ranges:**
        - ✅ **Normal:** < 20% below threshold
        - ⚠️ **Atenção:** 20-50% below threshold
        - 🚨 **Crítico:** > 50% below threshold
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ Battery Power Level
        **Feature:** `battery_mean`  
        **Importance:** 6.6% (Rank #2-3)
        
        **What it measures:**
        - Average battery voltage over observation period
        - Power supply stability indicator
        
        **Why it matters:**
        - Low battery (< 3.0V) = Device shutting down soon
        - Power failures cause communication loss
        - Predictable failure mode (gradual decline)
        
        **Reference Ranges:**
        - ✅ **Normal:** > 3.5V average
        - ⚠️ **Atenção:** 3.0-3.5V average
        - 🚨 **Crítico:** < 3.0V average
        """)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        ### 3️⃣ Activity Level
        **Feature:** `total_messages`  
        **Importance:** 6.6% (Rank #2-3)
        
        **What it measures:**
        - Total number of messages sent in observation window
        - Communication activity indicator
        
        **Why it matters:**
        - Silent devices (<10 messages) = Already failed
        - Spam devices (>500 messages) = Desperation mode
        - Normal activity (50-200) = Healthy communication
        
        **Reference Ranges:**
        - ✅ **Normal:** 50-300 messages
        - ⚠️ **Atenção:** 10-50 or 300-500 messages
        - 🚨 **Crítico:** < 10 or > 500 messages
        """)
    
    with col4:
        st.markdown("""
        ### 4️⃣ Communication Stress
        **Feature:** `max_frame_count`  
        **Importance:** 5.3% (Rank #4-5)
        
        **What it measures:**
        - Maximum frame count in message fragmentation
        - Retransmission and reconnection attempts
        
        **Why it matters:**
        - High frame count (>20) = Desperate reconnection
        - Indicates poor signal or device malfunction
        - Precedes complete communication failure
        
        **Reference Ranges:**
        - ✅ **Normal:** < 10 max frame count
        - ⚠️ **Atenção:** 10-20 max frame count
        - 🚨 **Crítico:** > 20 max frame count
        """)
    
    st.markdown("---")
    
    col5, col6 = st.columns([1, 1])
    
    with col5:
        st.markdown("""
        ### 5️⃣ Signal Instability
        **Feature:** `rsrp_std`  
        **Importance:** 5.2% (Rank #4-5)
        
        **What it measures:**
        - Standard deviation of RSRP (signal strength)
        - Signal stability vs fluctuation
        
        **Why it matters:**
        - High std (>10 dBm) = Unstable connection
        - Flaky signal causes retransmissions
        - Precedes dropout and device isolation
        
        **Reference Ranges:**
        - ✅ **Normal:** < 5 dBm std
        - ⚠️ **Atenção:** 5-10 dBm std
        - 🚨 **Crítico:** > 10 dBm std
        """)
    
    with col6:
        st.info("""
        ### 🎯 How to Use This Guide
        
        **For Operations:**
        1. Monitor these 5 indicators across device fleet
        2. Flag devices with 2+ indicators in "Crítico" range
        3. Schedule preventive maintenance before failure
        
        **For Analysis:**
        1. Compare critical vs operational device profiles
        2. Identify failure patterns (battery vs connectivity)
        3. Optimize sensor placement and configuration
        
        **For Development:**
        1. FASE 3 temporal features to track trends
        2. Early warning thresholds (7-14 days advance)
        3. Automated alert system integration
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 📊 Reference Ranges Summary Table
    
    | Indicator | Normal ✅ | Atenção ⚠️ | Crítico 🚨 |
    |-----------|----------|-----------|----------|
    | **optical_below_threshold** | < 20% | 20-50% | > 50% |
    | **battery_mean** | > 3.5V | 3.0-3.5V | < 3.0V |
    | **total_messages** | 50-300 | 10-50 or 300-500 | < 10 or > 500 |
    | **max_frame_count** | < 10 | 10-20 | > 20 |
    | **rsrp_std** | < 5 dBm | 5-10 dBm | > 10 dBm |
    
    **Note:** These ranges are empirical estimates from v2 FIELD-only dataset (762 devices, 43 critical). 
    Validate with domain experts and adjust based on specific deployment context.
    """)

# ============================================================================
# TAB 5: VISUAL DIAGRAMS
# ============================================================================
with tab5:
    st.markdown("## 🎨 Visual Diagrams: Research Journey & Roadmap")
    
    st.info("""
    **Interactive Diagrams:** Click edit links to view full-size diagrams in Mermaid Chart Playground.  
    Use these diagrams in presentations, documentation, or stakeholder reports.
    """)
    
    st.markdown("---")
    
    # Diagram 1: Pipeline
    st.markdown("### 1️⃣ Model v2.0 Pipeline")
    st.markdown("""
    End-to-end machine learning pipeline from data input to validated MVP.
    
    [🎨 Edit Diagram 1 - Pipeline](https://mermaidchart.com/play?utm_source=mermaid_mcp_server&utm_medium=remote_server&utm_campaign=vscode#pako:eNp1U8mO2zAM_RVBQAsUmNE2OxAUsN3ZATKLk6ZoMUCRaGzBliRIchsY-fdeOXHTGToXQ-b67Yf-AW62sBlEeh-sPgpo6DxDoJ6v5P9e6N9fv_yC_eNW90e6bbl3U_H_rO71tW4O4_2b9a8m_nbdTWB_P4KVwpl-vIddbUkrqrgvp28zqBOA6fRegRQJ3cMQussnCPPfoTMQ-r3haOjewiXvRnew7I3r3Qy5v_j-6z9__7i9H4xceT-dDOe9sTuctifTcTscTOvdNLh8-_XxavOC5wH7KhP89-9gc7nszLp1keUfv_x4WQV3s3N3fg7T1V95lE8KrrtTl_NdIV2WOpHzbE0WRGIL8hy-ZFC3S8qAIOkJaYdY64MR3exw-jBGkiVhUSHO_2TkxkmqkMUcNJkJFB8nMKNji-lTSg5iXjDzVwIlsZkHE7SbRYZ-Yd7p56kFspmDJAvBv26h2jJKN3bgjKHlA0kgOlhJXBqFnpY85lIfYrOL6rM8Y0OAyDMW0TYs5UQSVa5bov8U0qTyV68f05xfQ9MmbUiGA2BOgpB_zCMF34VB3q-7gV9rZk5YqcQ_fT_0vRoW5c5i0j6IyEkmECT7FPxJo9dHaqI-EnQFA-zpSed-zeh_mVVVMSMc7IlP4j-D3O5-UVGHnXAoCK6RE5KmCJ-zlM7Jtk3vbQbsbRMx6xyIGE5xBttMWrbVLx3zVN3Nyn4_2m1NKVoTstXP-4p87lEGcdQ8_6t77aVQJjhfKEkYJgIgXgjNQv0I3P_FYgJtRBe7hU0GZZbXyJ-U_o7fmj0l0qYo1WIJLhHWlFtN3G5TdOZ5ItXG6w9xfLCYpzJlLBBbRscu5L-7r3fewt6wIZNbP2WfyJMr7Kvi9tXJ4Nhr9dz-Aw7PMwY)
    
    **Pipeline Stages:**
    - **Data Input:** 762 FIELD-only devices
    - **Imputation:** SimpleImputer with median strategy
    - **Split:** Stratified 70/30 by device_id (533 train, 229 test)
    - **Balancing:** SMOTE 0.5 (~250 samples per class)
    - **Training:** CatBoost (100 iterations, depth 6, lr 0.1)
    - **Validation:** Recall 57.1%, Precision 57.1%, AUC 0.9186
    - **Result:** MVP/POC Validated
    """)
    
    st.code("""
flowchart TD
    A[Data Input<br/>762 devices FIELD-only] --> B[SimpleImputer median]
    B --> C[Stratified Split<br/>70/30: 533 train, 229 test]
    C --> D[SMOTE 0.5<br/>Balanced ~250/class]
    D --> E[CatBoost<br/>100 iterations, depth 6, lr 0.1]
    E --> F[Predictions]
    F --> G[Metrics<br/>Recall 57.1%, Precision 57.1%, AUC 0.9186]
    G --> H[Model v2.0<br/>MVP/POC Validated]
    """, language="mermaid")
    
    st.markdown("---")
    
    # Diagram 2: Discovery 0
    st.markdown("### 2️⃣ Discovery 0: Contamination Investigation")
    st.markdown("""
    Root cause analysis of v1 false positives and strategic pivot to v2 FIELD-only.
    
    [🎨 Edit Diagram 2 - Discovery 0](https://mermaidchart.com/play?utm_source=mermaid_mcp_server&utm_medium=remote_server&utm_campaign=vscode#pako:eNqNVctu2zAQ_JWFD01QwJIVv4ogKGC7SQ-JX_EhbQAhXdmEKZEgKTcxjF79l36D0UMvPfTQW36j_Yrt0pQluwmQixUl7pAcznBmdvdgAO-AG2HI3pBHbRTMrSdU5Kvj-O86_vvvn_9gfD61vSPdttw7Eb9_ldy_GHgEzucQJxiQI8tTi3sQ-jS6SlA8OttG1-oQYu16OjJcE_QyK9VgiClGPF4gq2r3-vsQYEoJiucnBcVTZSuYlYPEj6ID2Ou3e5tlzZjzKwGLBH15awUBFYSnmCy3Zr8-ffv98z0UjTtl-tB0B_aJaZ3Cbnl05EcCYcoFlTTF6jtYikJSuS8pZ-fadTpVk5xVh-nu70bYG37uOyfT8pyxJv0FZXm9gJimnKfN4F6Z13MNz3xsDWBqndhepWiieKgPVQIRKlR5Q4kcKe_76-s7sOMMH5wVnCLGs0P1yMRqCGSxMPI1BnCBMqFEnP0D9PltCfRoBQmeXdEomDnFG44sczzscBYtK4IRqskHvvDP6swwBvm0E3yFRM4yfo75xBx45vCOi8S5-r7ljU6LOOELKjBogK1ZFO7Rd2KFdN3KPnr3EE6NsTU0PMueVP7p6TW-zaGleqND3b22thktXWt3K6Uce9Aynw8O4KC9r_V7cNCryTjiTPkBzn2BMmEISrUVILvwGcH1ZHs1ehqYk5ExGZjH5qQarYeLmCdqtKFwa7YgjdGuwXKaO50qp2KXPYedW0VcGX1tjmsrEzDF-hodPoDuJjxsgJf5Ofq0PyixFmlcqrtX1R-fTGFqu1YmrTV53BB9LUMmXxnwBPsUxQquBL5MdW32XC1WJkZjtqplPtMIheBMqOu1w3cYm67rTVz1dpzJjWEyb1YL4V1QdknZvR4cKhvCs6s-UqaCQzgqPP6Y4aCgEUWlbP3UJdqRpCElYNM5T-oxL-BExH6iapYN5kKuI1zeihBSZaPb2An1MOinb65HIqMMw33yoJ5RaF4ZJeQjr0dn5xdx0scfsl-XKx-vO3NhN8R6KBP0f2XrkJUdBweh1whvvNnLUxDoXS7ZVnuEd958Ax0BIAI)
    
    **Investigation Flow:**
    - **Trigger:** Device 861275072515287 flagged 99.8% critical (false positive)
    - **Discovery:** 39% FACTORY messages in device data (179 FACTORY + 281 FIELD)
    - **Validation:** Dataset-wide scan → 31.8% total contamination (362k FACTORY msgs)
    - **Decision:** Rebuild with FIELD-only vs Keep v1 78.6%
    - **Action:** Filter FACTORY, retrain v2.0
    - **Result:** Recall 57.1% (-21.5%), AUC 0.9186 (+6.6%), clean foundation
    - **Lesson:** Data Quality > Model Complexity, Critical Thinking > Perfect Metrics
    """)
    
    st.markdown("---")
    
    # Diagram 3: Research Journey
    st.markdown("### 3️⃣ Research Journey: 7 Phases")
    st.markdown("""
    Complete research methodology from hypothesis through v2.1 enhancement to MVP positioning.
    
    [🎨 Edit Diagram 3 - Research Journey](https://mermaidchart.com/play?utm_source=mermaid_mcp_server&utm_medium=remote_server&utm_campaign=vscode#pako:eNp1VMFu00AQ_ZWhqKhVlVA7JE2LKDKJSwxpHGxTqQoVctfjdKmza3m3RlHDkRsSEuKEQMCdD-B7-AH4BNZ27NpC5GArOzNvnt-82esNwgPcONgII_6aXPiJhLHzgoH6uVL925r9-frxB4xOp7Y3Ml3LvRPJ--fJ3cOBz-B4DHGCASWyPLW4B6FPo6sExcOzbWi1DiHVrqcjwzVBL7NSDYaYYsTjBbKqdq-_DwGmlKB4UzAonipbwawcJH4UHcBev93bLGvGnF8KmCfoy1srCKggPMVkuTX79enb75_voWjcKdOHljuwT0znFHbLoyM_EghTLqikKVbfwVIUks59STk7267TqZrkrDpau78JR8bAs53TsppwJv0FZXn1CmKacrnW4F6Z43qO4ZmPrQFMrRPbq2RNFA_1oUogQoUqb0iRI-V9f315B3ac4YOxgkvEePZUPTKxGgJZLIx8iQEsUCaUiLN_gD6_LYEerSDB8ysaBTOneMORZY6HLc6iZUUwQjX5wJf-WZ1ZxiCfdoKvkMhZxs8xn5gDzxzecJE4V9-3vNFpESd8QQUGDbA1i8I9-taskK5b2Udv78KJMbaGhmfZk8o_Pb3Gtzm0VG94qLvX1jahpWvtbqWUYw9axvPBAey297V-D3Z6NRlHnCk_wLkvMKIMQam2AmQXPiO4nmyvRk8DczIyJgPz2JxUo_VwEfNEjTZUbs0WpDHaNVhOc6dT5VTscuaws6uIK6OvzXFtZQKmWF-jwwfQ3YSHDfAyP0ef8IMSZ5HGpbp7Zf3xyRSmtmtl0lqTxw3R1zLk8pUCN7BPUazgSuDLVNdmz9ViZWI0Zqta5nONUAjOhLpePnyHsem69sRVb8OZ3Bgm82a1EN4FZZeUzevBobIhPLvyI2UqOITjwuP1DAcFjSgqZeunLlFHkoaUgEPnPKnHvMRnIvYTVbNsMBdyGWFxK0JIlY1uYyfUw6AevbkciowwDPfJvXpGsXlllJBzUo-Wzi_ipI89sl-PKx-vW2thN8R6KBP2f2Vrscu2HeyG3Xo8396KUxDoTU7ZRjfCG2_-AsePB-M)
    
    **Journey Phases:**
    1. **Hypothesis:** Can ML predict IoT failures?
    2. **v1 Development:** 789 devices, 78.6% recall (looks great!)
    3. **Discovery 0:** 31.8% FACTORY contamination found
    4. **Strategic Pivot:** Rebuild FIELD-only vs Keep v1 inflated metrics
    5. **v2.0 Validation:** 762 FIELD-only, 57.1% honest baseline
    6. **v2.1 Enhancement:** +3 temporal features, +0.1% recall (insufficient)
    7. **MVP Positioning:** Keep v2.0, honest 57.1%, FASE 3 roadmap
    
    **Key Lessons:**
    - ✅ Critical Thinking
    - ✅ Data Quality > Metrics
    - ✅ Resilience (accept -21.5% for clean foundation)
    - ✅ Scientific Rigor
    - ✅ Transparency (honest baseline > inflated metrics)
    """)
    
    st.markdown("---")
    
    # Diagram 4: FASE 3 Roadmap
    st.markdown("### 4️⃣ FASE 3 Roadmap: From 57.1% MVP to 85%+ Production")
    st.markdown("""
    Four parallel improvement tracks to achieve production-ready performance with clean FIELD-only data.
    
    [🎨 Edit Diagram 4 - FASE 3 Roadmap](https://mermaidchart.com/play?utm_source=mermaid_mcp_server&utm_medium=remote_server&utm_campaign=vscode#pako:eNqFVd1u40QUfpWjoiJQN4t_t60RK3ljt0RqfuS4hZWJosl4nAw7saPxJFVY7SU3XIC0iAsQEuIJuOV59gXgETiOYzduHRFFo-T8fGfmO39vT2gWsxPnJBHZPV0QqSD0vkkBP2OF_z6J_v3jx7_gyh37YEIwdL2-O_pYqM9n8rOXVzJbgn3-XD-F_t0IVAYX9ukZjGQWr6niWTr5tIQ6AIRO5yUoSegbHaF_eQ9h8Rt0B0K_PxoG7g1c-W54G_jjSaubEX347dd__v5p72g48OXrkR-M3MDt-6EfQHg76A2u251NjPnzD3tX0wHPDfFlIfhfj9zBuDcctLtZ0Yffv997WQc3vXNvegjx4Fee5fNKd32qRzFbiWy7ZKmakjmr2Av5kkHOU8qAIOkJaYdY64MR3exw-jBGkiVhUSHO_2TkxkmqkMUcNJkJFB8nMKNji-lTSg5iXjDzVwIlsZkHE7SbRYZ-Yd7p56kFspmDJAvBv26h2jJKN3bgjKHlA0kgOlhJXBqFnpY85lIfYrOL6rM8Y0OAyDMW0TYs5UQSVa5bov8U0qTyV68f05xfQ9MmbUiGA2BOgpB_zCMF34VB3q-7gV9rZk5YqcQ_fT_0vRoW5c5i0j6IyEkmECT7FPxJo9dHaqI-EnQFA-zpSed-zeh_mVVVMSMc7IlP4j-D3O5-UVGHnXAoCK6RE5KmCJ-zlM7Jtk3vbQbsbRMx6xyIGE5xBttMWrbVLx3zVN3Nyn4_2m1NKVoTstXP-4p87lEGcdQ8_6t77aVQJjhfKEkYJgIgXgjNQv0I3P_FYgJtRBe7hU0GZZbXyJ-U_o7fmj0l0qYo1WIJLhHWlFtN3G5TdOZ5ItXG6w9xfLCYpzJlLBBbRscu5L-7r3fewt6wIZNbP2WfyJMr7Kvi9tXJ4Nhr9dz-Aw7PMwY)
    
    **Improvement Tracks:**
    
    **Track 1: Temporal Features (+20% recall projected)**
    - `deployment_age` - Time since activation
    - `activity_trends` - 7-day avg degradation
    - `degradation_delta` - Change rate analysis
    - Focus: Early vs late stage failure patterns
    
    **Track 2: Hyperparameter Tuning (+10-15% recall projected)**
    - GridSearchCV: depth 4-10, iterations 50-200
    - Learning rate: 0.03, 0.05, 0.1, 0.15
    - L2 regularization tuning
    - Focus: Overfitting prevention
    
    **Track 3: Dataset Expansion (reduce variance)**
    - Sample 100+ FAILED devices
    - Balance with OPERATIONAL count
    - Achieve 95% statistical confidence
    - Focus: Generalization
    
    **Track 4: Temporal Validation (deployment readiness)**
    - Time-based split: Train < 2025-01-01, Test >= 2025-01-01
    - Monitor model drift
    - Real-world validation
    
    **Target:** Recall ≥ 85%, Precision ≥ 80%, Clean FIELD-only data
    **Outcome:** Production ready with human oversight, 5-10% false alarms acceptable
    """)

# Footer
st.markdown("---")
st.info("""
📚 **Further Reading:**
- **MODEL_COMPARISON.md** - v1 algorithm comparison (XGBoost vs LightGBM vs CatBoost)
- **Notebooks 02B-08** - v1 technical implementation and validation
- **CHANGELOG.md** - Complete project timeline (v1 + v2)
- **README.md** - v2 FIELD-only model overview and roadmap
""")

st.caption("""
**Research Context** | IoT Predictive Maintenance Project | **Current:** CatBoost v2.0 FIELD-only (Nov 13, 2025) | **Reorganized:** Tab-based UX (Nov 18, 2025)
""")
