"""
Page 2: Batch Upload - CSV Processing and Bulk Predictions
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.model_loader import load_pipeline
from utils.preprocessing import (
    validate_features, 
    check_feature_types,
    display_missing_info,
    prepare_for_prediction,
    REQUIRED_FEATURES
)

# Header
st.title("📤 Batch Upload - Bulk Device Prediction")
st.markdown("Upload a CSV file with device features to get predictions for multiple devices at once.")

st.markdown("---")

# Instructions
with st.expander("📋 **CSV Format Requirements**", expanded=True):
    st.markdown(f"""
    Your CSV must contain **29 required features**:
    
    **Telemetry Features (18):**
    - `optical_*`: mean, std, min, max, readings, below_threshold, range
    - `temp_*`: mean, std, min, max, above_threshold, range
    - `battery_*`: mean, std, min, max, below_threshold
    
    **Connectivity Features (9):**
    - `snr_*`: mean, std, min
    - `rsrp_*`: mean, std, min
    - `rsrq_*`: mean, std, min
    
    **Messaging Features (2):**
    - `total_messages`, `max_frame_count`
    
    **Optional columns:** `device_id` (for identification, not used in prediction)
    
    **Missing values:** OK - model has built-in imputation (median strategy)
    """)
    
    # Download example template
    if st.button("📥 Download Example CSV Template"):
        # Create example DataFrame with required features
        example_data = {feature: [0.0] for feature in REQUIRED_FEATURES}
        example_data['device_id'] = ['DEVICE_001']
        example_df = pd.DataFrame(example_data)
        
        csv = example_df.to_csv(index=False)
        st.download_button(
            label="💾 Download template.csv",
            data=csv,
            file_name="device_features_template.csv",
            mime="text/csv"
        )

st.markdown("---")

# File Upload
uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type="csv",
    help="CSV with device features (one row per device)"
)

if uploaded_file is not None:
    # Read CSV
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded {len(df)} devices from CSV")
        
        # Show first few rows
        with st.expander("👀 Preview Data (first 5 rows)"):
            st.dataframe(df.head(), use_container_width=True)
        
        # Validate features
        is_valid, missing = validate_features(df)
        
        if not is_valid:
            st.error(f"❌ Cannot proceed - {len(missing)} required features missing")
            st.stop()
        
        # Check types
        df = check_feature_types(df)
        
        # Show missing value info
        display_missing_info(df)
        
        st.markdown("---")
        
        # Prediction button
        if st.button("🚀 Generate Predictions", type="primary"):
            with st.spinner("Running CatBoost pipeline..."):
                # Load model
                try:
                    model = load_pipeline()
                except Exception as e:
                    st.error(f"❌ Error loading model: {e}")
                    st.stop()
                
                # Prepare features
                features_df = prepare_for_prediction(df)
                
                # Predict
                try:
                    predictions = model.predict(features_df)
                    probabilities = model.predict_proba(features_df)[:, 1]
                    
                    # Add results to dataframe
                    results_df = df.copy()
                    results_df['prediction'] = predictions
                    results_df['probability'] = probabilities
                    results_df['risk_level'] = pd.cut(
                        probabilities,
                        bins=[0, 0.3, 0.7, 1.0],
                        labels=['Low', 'Medium', 'High']
                    )
                    results_df['verdict'] = results_df['prediction'].map({
                        0: 'NORMAL',
                        1: 'CRITICAL'
                    })
                    
                    # Store in session state
                    st.session_state['batch_results'] = results_df
                    
                    st.success(f"✅ Predictions complete for {len(results_df)} devices!")
                    
                except Exception as e:
                    st.error(f"❌ Prediction error: {e}")
                    st.stop()
    
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
        st.stop()

# Display results if available
if 'batch_results' in st.session_state:
    results_df = st.session_state['batch_results']
    
    st.markdown("---")
    st.subheader("📊 Prediction Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    critical_count = (results_df['prediction'] == 1).sum()
    normal_count = (results_df['prediction'] == 0).sum()
    high_risk_count = (results_df['risk_level'] == 'High').sum()
    avg_prob = results_df['probability'].mean()
    
    with col1:
        st.metric("Total Devices", len(results_df))
    with col2:
        st.metric("Critical Predicted", critical_count, delta=f"{critical_count/len(results_df):.1%}")
    with col3:
        st.metric("Normal Predicted", normal_count, delta=f"{normal_count/len(results_df):.1%}")
    with col4:
        st.metric("Avg Probability", f"{avg_prob:.1%}")
    
    st.markdown("---")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        filter_verdict = st.multiselect(
            "Filter by Verdict",
            options=['NORMAL', 'CRITICAL'],
            default=['NORMAL', 'CRITICAL']
        )
    
    with col2:
        filter_risk = st.multiselect(
            "Filter by Risk Level",
            options=['Low', 'Medium', 'High'],
            default=['Low', 'Medium', 'High']
        )
    
    # Apply filters
    filtered_df = results_df[
        (results_df['verdict'].isin(filter_verdict)) &
        (results_df['risk_level'].isin(filter_risk))
    ]
    
    # Sort options
    sort_col = st.selectbox(
        "Sort by",
        options=['probability', 'device_id'] if 'device_id' in filtered_df.columns else ['probability'],
        index=0
    )
    sort_order = st.radio("Order", options=['Descending', 'Ascending'], horizontal=True)
    
    filtered_df = filtered_df.sort_values(
        by=sort_col,
        ascending=(sort_order == 'Ascending')
    )
    
    # Display table
    st.dataframe(
        filtered_df[['device_id', 'prediction', 'probability', 'risk_level', 'verdict']] if 'device_id' in filtered_df.columns else filtered_df[['prediction', 'probability', 'risk_level', 'verdict']],
        use_container_width=True,
        height=400
    )
    
    # Download results
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="💾 Download Results as CSV",
        data=csv,
        file_name="predictions_results.csv",
        mime="text/csv",
        type="primary"
    )
    
    # Top critical devices
    if critical_count > 0:
        st.markdown("---")
        st.subheader("⚠️ Top 10 High-Risk Critical Devices")
        
        critical_df = results_df[results_df['prediction'] == 1].sort_values('probability', ascending=False).head(10)
        
        st.dataframe(
            critical_df[['device_id', 'probability', 'risk_level']] if 'device_id' in critical_df.columns else critical_df[['probability', 'risk_level']],
            use_container_width=True
        )

st.markdown("---")
st.caption("💡 **Tip:** Download results to Excel/Google Sheets for further analysis and reporting.")
