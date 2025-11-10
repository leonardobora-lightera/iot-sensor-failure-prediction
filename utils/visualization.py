"""
Visualization Templates with Plotly
Chart templates for feature importance, confusion matrix, distributions
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def plot_feature_importance(importance_df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """
    Create horizontal bar chart for feature importance
    
    Parameters
    ----------
    importance_df : pd.DataFrame
        DataFrame with 'feature' and 'importance' columns
    top_n : int, default 15
        Number of top features to display
    
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Interactive bar chart
    """
    # Sort and get top N
    df_sorted = importance_df.nlargest(top_n, 'importance')
    
    fig = px.bar(
        df_sorted,
        x='importance',
        y='feature',
        orientation='h',
        title=f'Top {top_n} Feature Importance',
        labels={'importance': 'Importance (%)', 'feature': 'Feature'},
        color='importance',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    return fig


def plot_confusion_matrix(tn: int, fp: int, fn: int, tp: int) -> go.Figure:
    """
    Create confusion matrix heatmap
    
    Parameters
    ----------
    tn, fp, fn, tp : int
        Confusion matrix values (True Neg, False Pos, False Neg, True Pos)
    
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Interactive heatmap
    """
    cm = np.array([[tn, fp], [fn, tp]])
    
    fig = px.imshow(
        cm,
        labels=dict(x="Predicted", y="Actual", color="Count"),
        x=['Normal', 'Critical'],
        y=['Normal', 'Critical'],
        text_auto=True,
        color_continuous_scale='RdYlGn',
        title='Confusion Matrix (Test Set)'
    )
    
    fig.update_layout(height=400)
    
    return fig


def plot_probability_distribution(probabilities: np.ndarray, 
                                  predictions: np.ndarray = None,
                                  threshold: float = 0.5) -> go.Figure:
    """
    Create histogram of prediction probabilities
    
    Parameters
    ----------
    probabilities : np.ndarray
        Predicted probabilities (0-1)
    predictions : np.ndarray, optional
        Binary predictions (0/1) for coloring
    threshold : float, default 0.5
        Decision threshold line
    
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Interactive histogram
    """
    if predictions is not None:
        df = pd.DataFrame({
            'probability': probabilities,
            'prediction': ['Critical' if p == 1 else 'Normal' for p in predictions]
        })
        
        fig = px.histogram(
            df,
            x='probability',
            color='prediction',
            nbins=30,
            title='Prediction Probability Distribution',
            labels={'probability': 'Probability of Critical', 'count': 'Count'},
            color_discrete_map={'Normal': 'lightblue', 'Critical': 'salmon'}
        )
    else:
        fig = px.histogram(
            x=probabilities,
            nbins=30,
            title='Prediction Probability Distribution',
            labels={'x': 'Probability of Critical', 'count': 'Count'}
        )
    
    # Add threshold line
    fig.add_vline(
        x=threshold, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Threshold ({threshold})"
    )
    
    fig.update_layout(height=400)
    
    return fig


def plot_roc_curve(fpr: np.ndarray, tpr: np.ndarray, auc: float) -> go.Figure:
    """
    Create ROC curve plot
    
    Parameters
    ----------
    fpr : np.ndarray
        False positive rates
    tpr : np.ndarray
        True positive rates
    auc : float
        Area under curve
    
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Interactive ROC curve
    """
    fig = go.Figure()
    
    # ROC curve
    fig.add_trace(go.Scatter(
        x=fpr,
        y=tpr,
        mode='lines',
        name=f'ROC Curve (AUC = {auc:.4f})',
        line=dict(color='blue', width=2)
    ))
    
    # Diagonal reference line
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode='lines',
        name='Random Classifier',
        line=dict(color='gray', dash='dash')
    ))
    
    fig.update_layout(
        title='ROC Curve',
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        height=500,
        width=500,
        yaxis=dict(scaleanchor="x", scaleratio=1),
        xaxis=dict(constrain='domain')
    )
    
    return fig


def create_metric_gauge(value: float, title: str, 
                       max_value: float = 1.0,
                       threshold_good: float = 0.7,
                       threshold_excellent: float = 0.85) -> go.Figure:
    """
    Create gauge chart for single metric
    
    Parameters
    ----------
    value : float
        Metric value (0-1 or 0-100)
    title : str
        Metric name
    max_value : float, default 1.0
        Maximum value (1.0 for percentages, 100 for absolute)
    threshold_good : float, default 0.7
        Threshold for "good" performance
    threshold_excellent : float, default 0.85
        Threshold for "excellent" performance
    
    Returns
    -------
    fig : plotly.graph_objects.Figure
        Interactive gauge
    """
    # Determine color based on thresholds
    if value >= threshold_excellent:
        color = "green"
    elif value >= threshold_good:
        color = "yellow"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value * 100 if max_value == 1.0 else value,
        title={'text': title},
        delta={'reference': threshold_good * 100 if max_value == 1.0 else threshold_good},
        gauge={
            'axis': {'range': [None, max_value * 100 if max_value == 1.0 else max_value]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, threshold_good * 100 if max_value == 1.0 else threshold_good], 'color': "lightgray"},
                {'range': [threshold_good * 100 if max_value == 1.0 else threshold_good, 
                          threshold_excellent * 100 if max_value == 1.0 else threshold_excellent], 'color': "lightyellow"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 100 if max_value == 1.0 else max_value
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig
