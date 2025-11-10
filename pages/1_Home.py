"""
Page 1: Home - Project Overview and Key Metrics
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.model_loader import load_metadata
from utils.translations import get_text, get_language_from_session

# Get language
lang = get_language_from_session(st.session_state)

# Load metadata
try:
    metadata = load_metadata()
    metrics = metadata.get('performance', {})
except:
    metrics = {
        'recall': 0.786,
        'precision': 0.846,
        'f1_score': 0.815,
        'roc_auc': 0.8621
    }

# Header
st.title(get_text('home', 'title', lang))
st.markdown(f"### {get_text('home', 'subtitle', lang)}")

st.markdown("---")

# Headline Metrics
st.subheader(get_text('home', 'performance_title', lang))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label=f"**{get_text('home', 'recall_label', lang)}**",
        value=f"{metrics.get('recall', 0.786):.1%}",
        delta="+28.6% vs baseline",
        help=get_text('home', 'recall_help', lang)
    )

with col2:
    st.metric(
        label=f"**{get_text('home', 'precision_label', lang)}**",
        value=f"{metrics.get('precision', 0.846):.1%}",
        delta="+4.6% vs target (80%)",
        help=get_text('home', 'precision_help', lang)
    )

with col3:
    st.metric(
        label=f"**{get_text('home', 'f1_label', lang)}**",
        value=f"{metrics.get('f1_score', 0.815):.1%}",
        delta="Balanced performance" if lang == 'en' else "Performance balanceada",
        help=get_text('home', 'f1_help', lang)
    )

with col4:
    st.metric(
        label=f"**{get_text('home', 'auc_label', lang)}**",
        value=f"{metrics.get('roc_auc', 0.8621):.4f}",
        delta="Excellent discrimination" if lang == 'en' else "Excelente discriminação",
        help=get_text('home', 'auc_help', lang)
    )

st.markdown("---")

# Project Story
st.subheader("📖 Project Journey: From 0% to 78.6% Recall")

with st.expander("**Phase 1: Temporal Split (REJECTED)** ❌", expanded=False):
    st.markdown("""
    - **Approach:** Split by date (old messages → train, recent → test)
    - **Result:** 0% recall - model couldn't detect ANY critical devices
    - **Problem:** Data leakage (650 devices in BOTH train and test)
    - **Lesson:** Dataset was aggregated (1 row/device), temporal split invalid
    """)

with st.expander("**Phase 2: Stratified Split (VALIDATED)** ✅", expanded=False):
    st.markdown("""
    - **Approach:** Split by device_id with stratification (31 critical train, 14 test)
    - **Result:** 50% recall, 87.5% precision - HONEST baseline
    - **Discovery:** Removed msg6_count/msg6_rate features (data leakage!)
    - **Validation:** Zero overlap, balanced proportions, clean features
    """)

with st.expander("**Phase 3: SMOTE Optimization** 🚀", expanded=True):
    st.markdown("""
    - **Approach:** SMOTE 0.5 strategy to balance class imbalance (16.8:1 ratio)
    - **Result:** 71.4% recall with XGBoost (+21.4% improvement)
    - **Improvement:** Detected 10/14 critical devices (+3 vs baseline)
    - **Tradeoff:** Precision dropped to 71.4% (acceptable for critical detection)
    """)

with st.expander("**Phase 4: Algorithm Optimization (FINAL)** 🏆", expanded=True):
    st.markdown("""
    - **Approach:** Tested XGBoost, LightGBM, CatBoost with SMOTE
    - **Winner:** CatBoost achieved 78.6% recall, 84.6% precision
    - **Final Result:** 11/14 critical devices detected, only 2 false alarms (0.8% FP rate)
    - **Business Value:** Prevents 78.6% of failures with minimal investigation overhead
    """)

st.markdown("---")

# Business Value
st.subheader("💼 Business Impact")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **✅ What the Model DOES:**
    - Detects **11 out of 14** critical devices (78.6% coverage)
    - Only **2 false positives** in 237 devices (0.8% investigation overhead)
    - **Balanced approach:** High recall + High precision
    - **Actionable insights:** Probability scores for risk prioritization
    """)

with col2:
    st.markdown("""
    **⚠️ Important Limitations:**
    - **Miss rate:** 3 of 14 critical devices not detected (21.4%)
    - **Requires human validation:** ML predictions support decisions, don't replace experts
    - **Historical training:** Model learns from past patterns (2025 data)
    - **Fallback needed:** Combine with domain knowledge and manual inspection
    """)

st.markdown("---")

# Navigation Guide
st.subheader("🗺️ How to Use This Application")

st.markdown("""
1. **📤 Batch Upload:** Upload CSV with device features → Get predictions for all devices → Download results
2. **🔍 Single Prediction:** Enter features for ONE device → Get instant risk assessment → See feature contributions
3. **📊 Model Insights:** Explore feature importance → Confusion matrix → Synthetic data testing → Performance metrics
""")

st.info("👉 Use the sidebar navigation to explore different sections of the application.")

st.markdown("---")

# Footer
st.caption("**Model:** CatBoost + SMOTE 0.5 | **Training:** 552 devices (31 critical) | **Test:** 237 devices (14 critical) | **Date:** November 7, 2025")
