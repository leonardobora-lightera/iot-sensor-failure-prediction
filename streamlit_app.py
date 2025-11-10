"""
IoT Critical Device Prediction - Streamlit App
Multi-page application for CatBoost model deployment
"""
import streamlit as st
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
st.sidebar.markdown(f"**{get_text('sidebar', 'model_version', lang)}:** v1.0")
st.sidebar.markdown(f"**{get_text('sidebar', 'training_date', lang)}:** 2025-11-07")
st.sidebar.markdown(f"**{get_text('sidebar', 'algorithm', lang)}:** CatBoost + SMOTE")
st.sidebar.markdown("---")

# Key metrics in sidebar
st.sidebar.metric(
    get_text('sidebar', 'recall', lang), 
    "78.6%", 
    f"+28.6% {get_text('sidebar', 'recall_delta', lang)}"
)
st.sidebar.metric(
    get_text('sidebar', 'precision', lang), 
    "84.6%", 
    f"+4.6% {get_text('sidebar', 'precision_delta', lang)}"
)
st.sidebar.metric(get_text('sidebar', 'f1_score', lang), "81.5%")

# Run selected page
pg.run()
