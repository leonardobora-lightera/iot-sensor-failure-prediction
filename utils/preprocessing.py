"""
Data Preprocessing and Validation
Feature validation, type checking, missing value handling for CSV uploads
"""
import streamlit as st
import pandas as pd
import numpy as np


# 29 required features for model (based on NB08 pipeline)
REQUIRED_FEATURES = [
    # Telemetry (12 features)
    'optical_mean', 'optical_std', 'optical_min', 'optical_max',
    'optical_readings', 'optical_below_threshold', 'optical_range',
    'temp_mean', 'temp_std', 'temp_min', 'temp_max', 
    'temp_above_threshold', 'temp_range',
    'battery_mean', 'battery_std', 'battery_min', 'battery_max',
    'battery_below_threshold',
    # Connectivity (9 features)
    'snr_mean', 'snr_std', 'snr_min',
    'rsrp_mean', 'rsrp_std', 'rsrp_min',
    'rsrq_mean', 'rsrq_std', 'rsrq_min',
    # Messages (2 features)
    'total_messages', 'max_frame_count'
]


def validate_features(df: pd.DataFrame, show_warnings: bool = True) -> tuple[bool, list]:
    """
    Validate that DataFrame has all required features
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe to validate
    show_warnings : bool, default True
        Whether to display Streamlit warnings
    
    Returns
    -------
    is_valid : bool
        True if all features present
    missing : list
        List of missing feature names
    """
    missing_features = set(REQUIRED_FEATURES) - set(df.columns)
    
    if missing_features:
        if show_warnings:
            st.error(f"❌ Missing {len(missing_features)} required features:")
            st.code(", ".join(sorted(missing_features)))
        return False, list(missing_features)
    
    return True, []


def check_feature_types(df: pd.DataFrame, show_info: bool = True) -> pd.DataFrame:
    """
    Check and convert feature types to numeric
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    show_info : bool, default True
        Whether to display conversion info
    
    Returns
    -------
    df : pd.DataFrame
        DataFrame with converted types
    """
    df = df.copy()
    non_numeric = []
    
    for feature in REQUIRED_FEATURES:
        if feature in df.columns:
            if not pd.api.types.is_numeric_dtype(df[feature]):
                non_numeric.append(feature)
                try:
                    df[feature] = pd.to_numeric(df[feature], errors='coerce')
                except:
                    pass
    
    if non_numeric and show_info:
        st.info(f"ℹ️ Converted {len(non_numeric)} features to numeric: {', '.join(non_numeric[:5])}")
    
    return df


def get_missing_stats(df: pd.DataFrame) -> dict:
    """
    Calculate missing value statistics
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    
    Returns
    -------
    stats : dict
        Missing value statistics (count, percentage per feature)
    """
    missing_count = df[REQUIRED_FEATURES].isnull().sum()
    missing_pct = (missing_count / len(df) * 100).round(1)
    
    stats = {
        'total_missing': missing_count.sum(),
        'features_with_missing': (missing_count > 0).sum(),
        'by_feature': pd.DataFrame({
            'count': missing_count,
            'percentage': missing_pct
        }).sort_values('count', ascending=False)
    }
    
    return stats


def display_missing_info(df: pd.DataFrame):
    """
    Display missing value information in Streamlit
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    """
    stats = get_missing_stats(df)
    
    if stats['total_missing'] == 0:
        st.success("✅ No missing values detected")
        return
    
    st.warning(f"⚠️ Found {stats['total_missing']:,} missing values across {stats['features_with_missing']} features")
    
    with st.expander("📊 Missing Values by Feature"):
        missing_df = stats['by_feature'][stats['by_feature']['count'] > 0]
        st.dataframe(missing_df, use_container_width=True)
        st.info("ℹ️ Pipeline includes SimpleImputer (median strategy) - missing values will be handled automatically")


def prepare_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for model prediction
    
    Extracts only required features in correct order, validates types
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe (may have extra columns like device_id)
    
    Returns
    -------
    features_df : pd.DataFrame
        Clean DataFrame with 29 features only
    """
    # Extract required features only
    features_df = df[REQUIRED_FEATURES].copy()
    
    # Convert to numeric (pipeline expects float64)
    features_df = check_feature_types(features_df, show_info=False)
    
    return features_df
