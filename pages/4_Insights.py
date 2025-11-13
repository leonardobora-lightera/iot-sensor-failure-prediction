"""
Page 4: Model Insights - Performance Metrics and Visualizations
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.model_loader import load_pipeline, load_metadata
from utils.visualization import (
    plot_feature_importance,
    plot_confusion_matrix,
    plot_probability_distribution
)
from utils.translations import get_text, get_language_from_session

# Get language
lang = get_language_from_session(st.session_state)

# Header
st.title(get_text('insights', 'title', lang))
st.markdown(get_text('insights', 'subtitle', lang))

st.markdown("---")

# Load metadata
try:
    metadata = load_metadata()
except:
    st.warning("⚠️ Metadata file not found - using default values")
    metadata = {}

# Extract metadata components
features_list = metadata.get('features', [])
performance = metadata.get('performance', {})
confusion_matrix_data = metadata.get('confusion_matrix', {})
# Fix: Use 'feature_importance_top5' array from metadata
feature_importance_top5 = metadata.get('feature_importance_top5', [])
hyperparameters = metadata.get('hyperparameters', {})

# Section 1: Model Performance Overview
st.subheader("📈 Model Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    recall = performance.get('recall', 0.571)
    st.metric("Recall", f"{recall:.1%}", help="8/14 critical devices detected (v2 FIELD-only)")

with col2:
    precision = performance.get('precision', 0.571)
    st.metric("Precision", f"{precision:.1%}", help="57.1% of critical predictions correct")

with col3:
    f1 = performance.get('f1_score', 0.571)
    st.metric("F1-Score", f"{f1:.1%}", help="Harmonic mean of precision and recall")

with col4:
    auc = performance.get('roc_auc', 0.9186)
    st.metric("ROC-AUC", f"{auc:.4f}", help="Area under ROC curve (+6.6% vs v1)")

# Business Metrics
st.markdown("### 💼 Business Impact Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    tp = confusion_matrix_data.get('TP', 8)  # v2: 8 true positives
    fn = confusion_matrix_data.get('FN', 6)  # v2: 6 false negatives
    total_critical = tp + fn
    st.metric(
        "Critical Detected",
        f"{tp}/{total_critical}",
        delta=f"{tp/total_critical:.1%} coverage"
    )

with col2:
    fp = confusion_matrix_data.get('FP', 6)  # v2: 6 false positives
    total_devices = 229  # v2: 229 test devices
    st.metric(
        "False Alarms",
        f"{fp}/{total_devices}",
        delta=f"{fp/total_devices:.1%} FP rate",
        delta_color="inverse"
    )

with col3:
    tn = confusion_matrix_data.get('TN', 209)  # v2: 209 true negatives
    total_normal = tn + fp
    st.metric(
        "Normal Correctly ID'd",
        f"{tn}/{total_normal}",
        delta=f"{tn/total_normal:.1%} specificity"
    )

st.markdown("---")

# Section 2: Confusion Matrix
st.subheader("🔢 Confusion Matrix")

col1, col2 = st.columns([1, 1])

with col1:
    # Confusion matrix heatmap
    tp = confusion_matrix_data.get('TP', 11)
    fp = confusion_matrix_data.get('FP', 2)
    fn = confusion_matrix_data.get('FN', 3)
    tn = confusion_matrix_data.get('TN', 221)
    
    fig_cm = plot_confusion_matrix(tn, fp, fn, tp)
    st.plotly_chart(fig_cm, use_container_width=True)

with col2:
    st.markdown("### Interpretation")
    st.markdown(f"""
    **True Positives (TP):** {tp}  
    Critical devices correctly identified ✅
    
    **False Positives (FP):** {fp}  
    Normal devices misclassified as critical ⚠️
    
    **False Negatives (FN):** {fn}  
    Critical devices missed ❌
    
    **True Negatives (TN):** {tn}  
    Normal devices correctly identified ✅
    
    ---
    
    **Miss Rate:** {fn}/{tp+fn} = {fn/(tp+fn):.1%}  
    **False Alarm Rate:** {fp}/{tn+fp} = {fp/(tn+fp):.1%}
    """)

st.markdown("---")

# Section 3: Feature Importance
st.subheader("🎯 Feature Importance Analysis")

if feature_importance_top5:
    # Convert array to DataFrame
    importance_df = pd.DataFrame(feature_importance_top5)
    
    # Plot
    fig_importance = plot_feature_importance(importance_df, top_n=len(importance_df))
    st.plotly_chart(fig_importance, use_container_width=True)
    
    # Top 5 interpretation
    st.markdown("### 🏆 Top 5 Most Important Features")
    
    for idx, row in importance_df.iterrows():
        feat_name = row['feature']
        importance = row['importance']
        
        # Feature interpretation
        if 'max_frame_count' in feat_name:
            interpretation = "Communication stress indicator - devices attempting desperate reconnection"
        elif 'total_messages' in feat_name:
            interpretation = "Activity level - silent devices may be failing"
        elif 'optical' in feat_name:
            interpretation = "Optical sensor health - environmental or power-related failures"
        elif 'temp' in feat_name:
            interpretation = "Temperature patterns - overheating or environmental stress"
        elif 'battery' in feat_name:
            interpretation = "Power supply health - voltage instability"
        elif 'snr' in feat_name or 'rsrp' in feat_name or 'rsrq' in feat_name:
            interpretation = "Connectivity quality - signal degradation before failure"
        else:
            interpretation = "Telemetry indicator"
        
        st.markdown(f"**{idx+1}. {feat_name}** ({importance:.1f}%): {interpretation}")
    
    # Distribution check
    st.markdown("---")
    st.markdown("### ✅ Feature Importance Health Check")
    
    top_feature_pct = importance_df.iloc[0]['importance']
    
    if top_feature_pct > 80:
        st.error(f"⚠️ **Potential Issue:** Top feature has {top_feature_pct:.1f}% importance (>80% indicates possible data leakage)")
    elif top_feature_pct > 60:
        st.warning(f"⚠️ **Watch:** Top feature has {top_feature_pct:.1f}% importance (high concentration, verify not leakage)")
    else:
        st.success(f"✅ **Healthy Distribution:** Top feature has {top_feature_pct:.1f}% importance (<60%, well-distributed)")

else:
    st.info("ℹ️ Feature importance data not available in metadata")

st.markdown("---")

# Section 4: Synthetic Data Testing
st.subheader("🧪 Synthetic Data Validation")

st.markdown("""
**Experiment:** Testing model on 30 synthetic critical devices generated using SMOTE (empirical approach).

**Context:** Notebook 06B created synthetic samples by interpolating between REAL critical devices from training set.
""")

# Load synthetic data
try:
    synthetic_path = Path(__file__).parent.parent / "data" / "synthetic_critical_empirical.csv"
    synthetic_df = pd.read_csv(synthetic_path)
    
    st.success(f"✅ Loaded {len(synthetic_df)} synthetic critical devices")
    
    # Show sample
    with st.expander("👀 Preview Synthetic Data (first 5)"):
        st.dataframe(synthetic_df.head(), use_container_width=True)
    
    # Test model on synthetic
    if st.button("🧪 Test Model on Synthetic Data"):
        with st.spinner("Running predictions on synthetic data..."):
            try:
                model = load_pipeline()
                
                # Extract features (29 columns, exclude metadata)
                feature_cols = [col for col in synthetic_df.columns if col in features_list or col.startswith(('optical', 'temp', 'battery', 'snr', 'rsrp', 'rsrq', 'total', 'max'))]
                features_df = synthetic_df[feature_cols]
                
                predictions = model.predict(features_df)
                probabilities = model.predict_proba(features_df)[:, 1]
                
                # Calculate metrics
                synthetic_recall = predictions.sum() / len(predictions)
                avg_prob = probabilities.mean()
                high_conf = (probabilities > 0.7).sum()
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Synthetic Recall", f"{synthetic_recall:.1%}")
                with col2:
                    st.metric("Avg Probability", f"{avg_prob:.1%}")
                with col3:
                    st.metric("High Confidence (>70%)", f"{high_conf}/{len(predictions)}")
                
                # Plot probability distribution
                fig_prob = plot_probability_distribution(probabilities, predictions)
                st.plotly_chart(fig_prob, use_container_width=True)
                
                # Interpretation
                st.markdown("---")
                st.markdown("### 📊 Results Interpretation")
                
                if synthetic_recall == 1.0:
                    st.warning(f"""
                    **⚠️ 100% Synthetic Recall - TOO HIGH!**
                    
                    All 30 synthetic samples classified as CRITICAL with average probability {avg_prob:.1%}.
                    
                    **What this means:**
                    - ✅ SMOTE successfully preserves correlations (generates realistic samples)
                    - ✅ Model recognizes patterns learned from training critical devices
                    - ⚠️ BUT: 100% indicates **memorization** not generalization
                    
                    **Why 100% is suspicious:**
                    - Synthetic generated FROM training critical (31 samples) via SMOTE interpolation
                    - Model trained on those exact 31 critical patterns
                    - Synthetic are BY DEFINITION within training manifold
                    - Real test set has only 78.6% recall (harder patterns not in training)
                    
                    **Conclusion:**
                    - Test set REAL critical (78.6% recall) remains **authoritative validation**
                    - Synthetic useful for **stress testing edge cases**, NOT independent validation
                    - 100% proves SMOTE works, NOT that model is better than 78.6%
                    """)
                elif synthetic_recall >= 0.6:
                    st.success(f"""
                    **✅ Realistic Synthetic Recall ({synthetic_recall:.1%})**
                    
                    Synthetic validation shows realistic performance, suggesting model learns general patterns
                    rather than memorizing specific training samples.
                    """)
                else:
                    st.info(f"""
                    **ℹ️ Low Synthetic Recall ({synthetic_recall:.1%})**
                    
                    Model may not recognize synthetic samples generated by SMOTE, which could indicate:
                    - Synthetic samples are out-of-distribution
                    - Model requires more diverse critical samples for training
                    """)
                
                # Comparison with NB06
                st.markdown("---")
                st.markdown("### 📈 Comparison: Theoretical vs Empirical Approach")
                
                comparison_data = {
                    'Approach': ['NB06 (Theoretical)', 'NB06B (Empirical)'],
                    'Recall': ['0%', f'{synthetic_recall:.1%}'],
                    'Method': [
                        'Assumed "high values = critical" without validation',
                        'Analyzed critical vs normal distributions, used SMOTE interpolation'
                    ],
                    'Lesson': [
                        'Theory failed - sampling not validated',
                        'Empirical analysis >>> theoretical assumptions'
                    ]
                }
                
                st.table(pd.DataFrame(comparison_data))
                
            except Exception as e:
                st.error(f"❌ Error testing synthetic data: {e}")
                st.exception(e)

except FileNotFoundError:
    st.warning("⚠️ Synthetic data file not found (data/synthetic_critical_empirical.csv)")
except Exception as e:
    st.warning(f"⚠️ Could not load synthetic data: {e}")

st.markdown("---")

# Section 5: Model Metadata
st.subheader("⚙️ Model Configuration")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Algorithm Details")
    st.markdown(f"""
    - **Algorithm:** CatBoost Classifier
    - **Version:** v1.0
    - **Training Date:** 2025-11-07
    - **Pipeline:** SimpleImputer → SMOTE → CatBoost
    """)
    
    if hyperparameters:
        st.markdown("### Hyperparameters")
        for param, value in hyperparameters.items():
            st.markdown(f"- **{param}:** {value}")

with col2:
    st.markdown("### Dataset Summary")
    st.markdown(f"""
    - **Total Devices:** 789
    - **Train Set:** 552 devices (31 critical, 5.6%)
    - **Test Set:** 237 devices (14 critical, 5.9%)
    - **Features:** {len(features_list) if features_list else 29}
    - **Class Imbalance:** 16.8:1 (normal:critical)
    """)
    
    st.markdown("### Performance Summary")
    st.markdown(f"""
    - **Detection:** {tp}/{tp+fn} critical devices
    - **False Alarms:** {fp}/{tn+fp} of normal devices
    - **Balanced Accuracy:** {((tp/(tp+fn) + tn/(tn+fp))/2):.1%}
    """)

st.markdown("---")
st.caption("💡 **Note:** All metrics calculated on held-out test set (237 devices, zero overlap with training).")
