"""
IoT Critical Device Prediction - Streamlit App
Multi-page application for CatBoost model deployment
"""
import streamlit as st
from datetime import datetime
import pytz
from utils.translations import get_text, get_language_from_session

# Page config
st.set_page_config(
    page_title="IoT Critical Device Prediction",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize language in session state
if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

# Language selector in sidebar (at top)
language_options = ['English', 'Português (BR)']
st.session_state['language'] = st.sidebar.selectbox(
    '🌍 ' + ('Language' if st.session_state['language'] == 'English' else 'Idioma'),
    language_options,
    index=language_options.index(st.session_state['language'])
)

# Get language code
lang = get_language_from_session(st.session_state)

st.sidebar.markdown("---")

# Define pages
home_page = st.Page("pages/1_Home.py", title="Home", icon="🏠", default=True)
batch_page = st.Page("pages/2_Batch_Upload.py", title="Batch Upload", icon="📤")
single_page = st.Page("pages/3_Single_Predict.py", title="Single Prediction", icon="🔍")
insights_page = st.Page("pages/4_Insights.py", title="Model Insights", icon="📊")
research_page = st.Page("pages/5_Research_Context.py", title="Research Context", icon="📖")

# Navigation
pg = st.navigation([home_page, batch_page, single_page, insights_page, research_page])

# Sidebar info
st.sidebar.title(get_text('sidebar', 'title', lang))
st.sidebar.markdown("---")
st.sidebar.markdown(f"**{get_text('sidebar', 'model_version', lang)}:** v2.0 FIELD-only")
st.sidebar.markdown(f"**{get_text('sidebar', 'training_date', lang)}:** 2025-11-13")
st.sidebar.markdown(f"**{get_text('sidebar', 'algorithm', lang)}:** CatBoost + SMOTE")
st.sidebar.markdown("---")

# Key metrics in sidebar
st.sidebar.metric(
    get_text('sidebar', 'recall', lang), 
    "57.1%", 
    f"-21.5% vs v1 (clean data)"
)
st.sidebar.metric(
    get_text('sidebar', 'precision', lang), 
    "57.1%", 
    f"-27.5% vs v1"
)
st.sidebar.metric("ROC-AUC", "0.9186", "+6.6% vs v1")

st.sidebar.markdown("---")

# Current timestamp (Brazil timezone)
tz_br = pytz.timezone('America/Sao_Paulo')
now = datetime.now(tz_br)
st.sidebar.caption(f"📅 {now.strftime('%d/%m/%Y %H:%M')}")

st.sidebar.markdown("---")

# GitHub Repository Link
st.sidebar.markdown("### 📂 Code Repository")
st.sidebar.markdown("[🔗 View on GitHub](https://github.com/leonardobora-lightera/iot-sensor-failure-prediction)")

# Run selected page
pg.run()
