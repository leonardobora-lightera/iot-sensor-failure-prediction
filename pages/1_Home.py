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
    # Default to v2 metrics if metadata not found
    metrics = {
        'recall': 0.571,
        'precision': 0.571,
        'f1_score': 0.571,
        'roc_auc': 0.9186
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
        value=f"{metrics.get('roc_auc', 0.9186):.4f}",
        delta="+6.6% vs v1" if lang == 'en' else "+6.6% vs v1",
        help=get_text('home', 'auc_help', lang)
    )

st.markdown("---")

# Project Evolution
st.subheader("📖 Model Evolution: v1 (Mixed) → v2 (FIELD-only)")

with st.expander("**v1: Mixed FACTORY+FIELD Data** ⚠️", expanded=False):
    st.markdown("""
    - **Dataset:** 789 devices (lab + production mixed)
    - **Performance:** Recall 78.6%, Precision 84.6%, AUC 0.8621
    - **Problem:** Lifecycle mixing contaminates production patterns
    """)

with st.expander("**v2: Production-Only (FIELD) Data** ✅", expanded=True):
    st.markdown("""
    - **Dataset:** 762 devices (FIELD-only, removed 362k FACTORY messages)
    - **Performance:** Recall 57.1%, Precision 57.1%, **AUC 0.9186** (+6.6%)
    - **Advantage:** Clean data, better probability calibration
    - **Philosophy:** "2 steps back, 3 forward" - solid foundation for improvements
    """)

with st.expander("**Roadmap: '3 Steps Forward'** 🎯", expanded=False):
    st.markdown("""
    **Current trade-off:** -21.5% recall vs v1, but cleaner foundation
    
    **Path to exceed v1:**
    1. **Hyperparameter Tuning** (GridSearch CatBoost) - Expected +10-15% recall
    2. **Temporal Features (FASE 3)** - 4 new features - Expected +20% recall  
    3. **Threshold Calibration** - Optimize decision boundary
    
    **Target:** Precision >80%, Recall >75% with production-only data
    """)

st.markdown("---")

# Business Value
st.subheader("💼 Model v2 Impact")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **✅ What the Model v2 DOES:**
    - Detects **8 out of 14** critical devices (57.1% coverage)
    - **Clean data:** FIELD-only (removed 362k FACTORY messages)
    - **Better calibration:** AUC 0.9186 (+6.6% vs v1)
    - **Actionable insights:** Probability scores for risk prioritization
    """)

with col2:
    st.markdown("""
    **⚠️ Current Limitations:**
    - **Miss rate:** 6 of 14 critical devices not detected (42.9%)
    - **No hyperparameter tuning yet** (expected +10-15% recall improvement)
    - **Missing temporal features** (FASE 3 - expected +20% recall)
    - **Requires human validation:** ML predictions support decisions, don't replace experts
    """)

st.markdown("---")

# Navigation Guide
st.subheader("🗺️ How to Use This Application")

st.markdown("""
1. **📤 Batch Upload:** Upload CSV with device features → Get predictions for all devices → Download results
2. **🔍 Single Prediction:** Enter features for ONE device → Get instant risk assessment → See feature contributions
3. **📊 Model Insights:** Explore feature importance → Confusion matrix → Performance metrics
""")

st.info("👉 Use the sidebar navigation to explore different sections of the application.")

st.markdown("---")

# Footer
st.caption("**Model v2:** CatBoost + SMOTE 0.5 (FIELD-only) | **Training:** 533 devices (29 critical) | **Test:** 229 devices (14 critical) | **Date:** November 13, 2025")
