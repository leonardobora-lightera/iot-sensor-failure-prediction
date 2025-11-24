"""
Page 3: Single Prediction - Individual Device Assessment
"""
import streamlit as st
import pandas as pd
import sys
# Header
st.title(get_text('single', 'title', lang))
st.markdown(get_text('single', 'subtitle', lang))

st.markdown("---")

# Load model and metadata
try:
    model = load_pipeline()
    metadata = load_metadata()
    feature_importance = metadata.get('feature_importance', {})
except Exception as e:
    st.error(f"❌ Error loading model: {e}")
    st.stop()

# Form for feature input
with st.form("prediction_form"):
    st.subheader(get_text('single', 'form_title', lang))
    
    # Group features by category
    tab1, tab2, tab3 = st.tabs([
        get_text('single', 'tab_telemetry', lang), 
        get_text('single', 'tab_connectivity', lang), 
        get_text('single', 'tab_messaging', lang)
    ])
    
    features = {}
    
    with tab1:
        st.markdown(f"**{get_text('single', 'optical_title', lang)}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            features['optical_mean'] = st.number_input("optical_mean", value=50.0, format="%.2f")
            features['optical_std'] = st.number_input("optical_std", value=10.0, format="%.2f")
            features['optical_min'] = st.number_input("optical_min", value=30.0, format="%.2f")
        with col2:
            features['optical_max'] = st.number_input("optical_max", value=70.0, format="%.2f")
            features['optical_readings'] = st.number_input("optical_readings", value=100.0, format="%.1f")
            features['optical_below_threshold'] = st.number_input("optical_below_threshold", value=5.0, format="%.1f")
        with col3:
            features['optical_range'] = st.number_input("optical_range", value=40.0, format="%.2f")
        
        st.markdown(f"**{get_text('single', 'temp_title', lang)}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            features['temp_mean'] = st.number_input("temp_mean (°C)", value=25.0, format="%.2f", key="temp_mean")
            features['temp_std'] = st.number_input("temp_std", value=5.0, format="%.2f")
        with col2:
            features['temp_min'] = st.number_input("temp_min (°C)", value=15.0, format="%.2f", key="temp_min")
            features['temp_max'] = st.number_input("temp_max (°C)", value=35.0, format="%.2f", key="temp_max")
        with col3:
            features['temp_above_threshold'] = st.number_input("temp_above_threshold", value=2.0, format="%.1f")
            features['temp_range'] = st.number_input("temp_range", value=20.0, format="%.2f")
        
        st.markdown(f"**{get_text('single', 'battery_title', lang)}**")
        col1, col2 = st.columns(2)
        with col1:
            features['battery_mean'] = st.number_input("battery_mean (V)", value=3.3, format="%.2f", key="bat_mean")
            features['battery_std'] = st.number_input("battery_std", value=0.1, format="%.3f")
            features['battery_min'] = st.number_input("battery_min (V)", value=3.0, format="%.2f", key="bat_min")
        with col2:
            features['battery_max'] = st.number_input("battery_max (V)", value=3.5, format="%.2f", key="bat_max")
            features['battery_below_threshold'] = st.number_input("battery_below_threshold", value=0.0, format="%.1f")
    
    with tab2:
        st.markdown(f"**{get_text('single', 'snr_title', lang)}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            features['snr_mean'] = st.number_input("snr_mean (dB)", value=10.0, format="%.2f", key="snr_mean")
        with col2:
            features['snr_std'] = st.number_input("snr_std", value=2.0, format="%.2f")
        with col3:
            features['snr_min'] = st.number_input("snr_min (dB)", value=5.0, format="%.2f", key="snr_min")
        
        st.markdown(f"**{get_text('single', 'rsrp_title', lang)}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            features['rsrp_mean'] = st.number_input("rsrp_mean (dBm)", value=-100.0, format="%.2f", key="rsrp_mean")
        with col2:
            features['rsrp_std'] = st.number_input("rsrp_std", value=5.0, format="%.2f")
        with col3:
            features['rsrp_min'] = st.number_input("rsrp_min (dBm)", value=-110.0, format="%.2f", key="rsrp_min")
        
        st.markdown(f"**{get_text('single', 'rsrq_title', lang)}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            features['rsrq_mean'] = st.number_input("rsrq_mean (dB)", value=-10.0, format="%.2f", key="rsrq_mean")
        with col2:
            features['rsrq_std'] = st.number_input("rsrq_std", value=2.0, format="%.2f")
        with col3:
            features['rsrq_min'] = st.number_input("rsrq_min (dB)", value=-15.0, format="%.2f", key="rsrq_min")
    
    with tab3:
        st.markdown(f"**{get_text('single', 'messaging_title', lang)}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            features['total_messages'] = st.number_input(
                "total_messages",
                value=100.0,
                format="%.0f",
                help="Total number of messages sent by device"
            )
        with col2:
            features['max_frame_count'] = st.number_input(
                "max_frame_count",
                value=50.0,
                format="%.0f",
                help="Maximum frame count observed (communication stress indicator)"
            )
        with col3:
            # Automatic calculation for days_since_last_message
            st.markdown(f"**{get_text('single', 'messaging_date_title', lang) if lang == 'pt-br' else 'Last Message Date'}**")
            last_msg_date = st.date_input(
                "Select date",
                value=datetime.now().date(),
                label_visibility="collapsed"
            )
            
            # Calculate days difference
            days_diff = (datetime.now().date() - last_msg_date).days
            if days_diff < 0:
                days_diff = 0
            
            features['days_since_last_message'] = st.number_input(
                "days_since_last_message ⭐",
                value=float(days_diff),
                format="%.1f",
                disabled=True,
                help="Automatically calculated from date: Days since device last sent a message"
            )
    
    # Submit button
    submitted = st.form_submit_button(get_text('single', 'predict_button', lang), type="primary")

# Process prediction
if submitted:
    st.markdown("---")
    st.subheader(get_text('single', 'result_title', lang))
    
    # Create DataFrame from features
    features_df = pd.DataFrame([features])
    
    # Predict
    try:
        prediction = model.predict(features_df)[0]
        probability = model.predict_proba(features_df)[0, 1]
        
        # Determine risk level
        if probability < 0.3:
            risk_level = "Low"
            risk_color = "green"
        elif probability < 0.7:
            risk_level = "Medium"
            risk_color = "orange"
        else:
            risk_level = "High"
            risk_color = "red"
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Verdict",
                "🚨 CRITICAL" if prediction == 1 else "✅ NORMAL",
                delta=None
            )
        
        with col2:
            st.metric(
                "Failure Probability",
                f"{probability:.1%}",
                delta=f"{(probability - 0.5):.1%} vs threshold"
            )
        
        with col3:
            st.metric(
                "Risk Level",
                f"{risk_level}",
                delta=None
            )
        
        # Gauge chart
        st.markdown("### 📊 Probability Gauge")
        fig = create_metric_gauge(
            value=probability,
            title="Failure Probability",
            threshold_good=0.3,
            threshold_excellent=0.7
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation
        st.markdown("---")
        st.markdown("### 💡 Interpretation")
        
        if prediction == 1:
            st.error(f"""
            **⚠️ CRITICAL DEVICE DETECTED**
            
            This device shows **{probability:.1%}** probability of critical failure based on {len(features)} input features.
            
            **Risk Level:** {risk_level}
            
            **Recommended Actions:**
            - ✅ Schedule immediate inspection
            - ✅ Review telemetry history (optical, temperature, battery trends)
            - ✅ Check connectivity metrics (signal strength, message volume)
            - ✅ Consider preventive replacement if high-value application
            """)
        else:
            st.success(f"""
            **✅ NORMAL DEVICE**
            
            This device shows **{probability:.1%}** probability of critical failure - below the 50% threshold.
            
            **Risk Level:** {risk_level}
            
            **Recommended Actions:**
            - ✅ Continue normal monitoring schedule
            - ✅ Track probability trend over time
            - ℹ️ Review if probability increases above 30% (Medium risk)
            """)
        
        # Feature contributions (top 5 most important features in this prediction)
        st.markdown("---")
        st.markdown("### 🔍 Top Contributing Features")
        
        if feature_importance:
            # Get top 5 features by importance
            top_features = sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            for feat_name, importance in top_features:
                if feat_name in features:
                    feat_value = features[feat_name]
                    st.markdown(f"- **{feat_name}**: {feat_value:.2f} (importance: {importance:.1%})")
        
    except Exception as e:
        st.error(f"❌ Prediction error: {e}")
        st.exception(e)

st.markdown("---")
st.caption("💡 **Tip:** Model v2 learns from 30 features (including days_since_last_message) - ensure all values are accurate for best predictions.")
