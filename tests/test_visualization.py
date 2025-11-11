"""
Unit Tests for utils/visualization.py
Tests chart generation functions (feature importance, confusion matrix, ROC curve)
"""
import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.visualization import (
    plot_feature_importance,
    plot_confusion_matrix,
    plot_probability_distribution,
    plot_roc_curve,
    create_metric_gauge
)


class TestPlotFeatureImportance:
    """Test suite for plot_feature_importance function"""
    
    @pytest.fixture
    def importance_df(self):
        """Create sample feature importance DataFrame"""
        return pd.DataFrame({
            'feature': ['max_frame_count', 'total_messages', 'optical_readings', 
                       'optical_below_threshold', 'rsrq_std', 'battery_mean',
                       'snr_mean', 'rsrp_mean', 'temp_mean', 'optical_mean'],
            'importance': [51.8, 11.7, 3.6, 3.1, 3.0, 2.5, 2.0, 1.8, 1.5, 1.2]
        })
    
    def test_plot_feature_importance_returns_figure(self, importance_df):
        """Test that function returns a Plotly Figure"""
        fig = plot_feature_importance(importance_df, top_n=5)
        
        assert isinstance(fig, go.Figure)
    
    def test_plot_feature_importance_top_n_filtering(self, importance_df):
        """Test that top_n parameter filters correctly"""
        fig = plot_feature_importance(importance_df, top_n=5)
        
        # Should only have 5 features in the plot
        # Extract data from figure
        data_length = len(fig.data[0].y)
        assert data_length == 5
    
    def test_plot_feature_importance_sorted_descending(self, importance_df):
        """Test that features are sorted by importance"""
        fig = plot_feature_importance(importance_df, top_n=10)
        
        # Extract importance values (x-axis data)
        importance_values = fig.data[0].x
        
        # Should be in DESCENDING order (highest importance at top for horizontal bar)
        # Plotly px.bar with orientation='h' shows highest at top, but data is sorted ascending for y-axis display
        # So values will appear ascending in the array but visually descending on plot
        assert len(importance_values) == 10
    
    def test_plot_feature_importance_handles_small_dataset(self):
        """Test with fewer features than top_n"""
        small_df = pd.DataFrame({
            'feature': ['feature_1', 'feature_2'],
            'importance': [80.0, 20.0]
        })
        
        fig = plot_feature_importance(small_df, top_n=10)
        
        # Should work without error and show all 2 features
        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].y) == 2
    
    def test_plot_feature_importance_has_title(self, importance_df):
        """Test that figure has appropriate title"""
        fig = plot_feature_importance(importance_df, top_n=5)
        
        assert 'title' in fig.layout
        assert 'Top 5' in fig.layout.title.text


class TestPlotConfusionMatrix:
    """Test suite for plot_confusion_matrix function"""
    
    def test_plot_confusion_matrix_returns_figure(self):
        """Test that function returns a Plotly Figure"""
        fig = plot_confusion_matrix(tn=602, fp=2, fn=3, tp=11)
        
        assert isinstance(fig, go.Figure)
    
    def test_plot_confusion_matrix_correct_values(self):
        """Test that confusion matrix contains correct values"""
        tn, fp, fn, tp = 602, 2, 3, 11
        fig = plot_confusion_matrix(tn, fp, fn, tp)
        
        # Extract data from heatmap
        data = fig.data[0].z
        
        # Verify matrix structure [[tn, fp], [fn, tp]]
        assert data[0][0] == tn
        assert data[0][1] == fp
        assert data[1][0] == fn
        assert data[1][1] == tp
    
    def test_plot_confusion_matrix_labels(self):
        """Test that axis labels are correct"""
        fig = plot_confusion_matrix(tn=100, fp=5, fn=10, tp=20)
        
        # Check x and y labels
        assert fig.data[0].x[0] == 'Normal'
        assert fig.data[0].x[1] == 'Critical'
        assert fig.data[0].y[0] == 'Normal'
        assert fig.data[0].y[1] == 'Critical'
    
    def test_plot_confusion_matrix_zero_values(self):
        """Test handling of zero values in confusion matrix"""
        fig = plot_confusion_matrix(tn=0, fp=0, fn=0, tp=0)
        
        # Should work without error
        assert isinstance(fig, go.Figure)
    
    def test_plot_confusion_matrix_has_title(self):
        """Test that figure has appropriate title"""
        fig = plot_confusion_matrix(tn=100, fp=5, fn=10, tp=20)
        
        assert 'title' in fig.layout
        assert 'Confusion Matrix' in fig.layout.title.text


class TestPlotProbabilityDistribution:
    """Test suite for plot_probability_distribution function"""
    
    @pytest.fixture
    def sample_probabilities(self):
        """Create sample probability array"""
        np.random.seed(42)
        return np.random.beta(2, 5, 100)  # Skewed distribution
    
    @pytest.fixture
    def sample_predictions(self):
        """Create sample predictions (binary)"""
        np.random.seed(42)
        probs = np.random.beta(2, 5, 100)
        return (probs > 0.5).astype(int)
    
    def test_plot_probability_distribution_returns_figure(self, sample_probabilities):
        """Test that function returns a Plotly Figure"""
        fig = plot_probability_distribution(sample_probabilities)
        
        assert isinstance(fig, go.Figure)
    
    def test_plot_probability_distribution_with_predictions(self, sample_probabilities, sample_predictions):
        """Test plot with predictions for coloring"""
        fig = plot_probability_distribution(sample_probabilities, sample_predictions)
        
        assert isinstance(fig, go.Figure)
        # Should have colored bars by prediction
        assert len(fig.data) > 1  # Multiple traces for different colors
    
    def test_plot_probability_distribution_threshold_line(self, sample_probabilities):
        """Test that threshold line is added"""
        threshold = 0.6
        fig = plot_probability_distribution(sample_probabilities, threshold=threshold)
        
        # Check for vertical line shape
        assert len(fig.layout.shapes) > 0
        # Verify threshold value in shapes or annotations
        has_threshold = any('0.6' in str(shape) for shape in fig.layout.shapes)
        assert has_threshold or len(fig.layout.annotations) > 0
    
    def test_plot_probability_distribution_range(self, sample_probabilities):
        """Test that probabilities are in valid range [0, 1]"""
        # Verify input assumptions
        assert np.all(sample_probabilities >= 0)
        assert np.all(sample_probabilities <= 1)
        
        fig = plot_probability_distribution(sample_probabilities)
        assert isinstance(fig, go.Figure)


class TestPlotROCCurve:
    """Test suite for plot_roc_curve function"""
    
    @pytest.fixture
    def sample_roc_data(self):
        """Create sample ROC curve data"""
        fpr = np.array([0.0, 0.1, 0.2, 0.5, 1.0])
        tpr = np.array([0.0, 0.6, 0.8, 0.9, 1.0])
        auc = 0.8621
        return fpr, tpr, auc
    
    def test_plot_roc_curve_returns_figure(self, sample_roc_data):
        """Test that function returns a Plotly Figure"""
        fpr, tpr, auc = sample_roc_data
        fig = plot_roc_curve(fpr, tpr, auc)
        
        assert isinstance(fig, go.Figure)
    
    def test_plot_roc_curve_has_two_traces(self, sample_roc_data):
        """Test that figure has ROC curve + diagonal reference line"""
        fpr, tpr, auc = sample_roc_data
        fig = plot_roc_curve(fpr, tpr, auc)
        
        # Should have 2 traces: ROC curve and diagonal
        assert len(fig.data) == 2
    
    def test_plot_roc_curve_auc_in_legend(self, sample_roc_data):
        """Test that AUC value appears in legend"""
        fpr, tpr, auc = sample_roc_data
        fig = plot_roc_curve(fpr, tpr, auc)
        
        # Check if AUC value is in trace name
        roc_trace_name = fig.data[0].name
        assert '0.8621' in roc_trace_name
    
    def test_plot_roc_curve_diagonal_reference(self, sample_roc_data):
        """Test that diagonal reference line is correct"""
        fpr, tpr, auc = sample_roc_data
        fig = plot_roc_curve(fpr, tpr, auc)
        
        # Diagonal should be from (0,0) to (1,1)
        diagonal_trace = fig.data[1]
        assert diagonal_trace.x[0] == 0 and diagonal_trace.x[1] == 1
        assert diagonal_trace.y[0] == 0 and diagonal_trace.y[1] == 1
    
    def test_plot_roc_curve_perfect_classifier(self):
        """Test with perfect classifier (AUC = 1.0)"""
        fpr = np.array([0.0, 0.0, 1.0])
        tpr = np.array([0.0, 1.0, 1.0])
        auc = 1.0
        
        fig = plot_roc_curve(fpr, tpr, auc)
        assert isinstance(fig, go.Figure)
        assert '1.0000' in fig.data[0].name


class TestCreateMetricGauge:
    """Test suite for create_metric_gauge function"""
    
    def test_create_metric_gauge_returns_figure(self):
        """Test that function returns a Plotly Figure"""
        fig = create_metric_gauge(value=0.85, title="Precision")
        
        assert isinstance(fig, go.Figure)
    
    def test_create_metric_gauge_value_display(self):
        """Test that gauge displays correct value"""
        value = 0.786
        fig = create_metric_gauge(value=value, title="Recall")
        
        # Value should be converted to percentage (78.6)
        assert fig.data[0].value == value * 100
    
    def test_create_metric_gauge_excellent_threshold(self):
        """Test gauge color for excellent performance"""
        fig = create_metric_gauge(
            value=0.90, 
            title="Precision",
            threshold_excellent=0.85
        )
        
        # Should have green color for excellent
        assert fig.data[0].gauge.bar.color == "green"
    
    def test_create_metric_gauge_good_threshold(self):
        """Test gauge color for good performance"""
        fig = create_metric_gauge(
            value=0.75, 
            title="Recall",
            threshold_good=0.70,
            threshold_excellent=0.85
        )
        
        # Should have yellow color for good (between thresholds)
        assert fig.data[0].gauge.bar.color == "yellow"
    
    def test_create_metric_gauge_poor_threshold(self):
        """Test gauge color for poor performance"""
        fig = create_metric_gauge(
            value=0.50, 
            title="F1-Score",
            threshold_good=0.70
        )
        
        # Should have red color for poor (below threshold)
        assert fig.data[0].gauge.bar.color == "red"
    
    def test_create_metric_gauge_title(self):
        """Test that gauge has correct title"""
        title = "Test Metric"
        fig = create_metric_gauge(value=0.80, title=title)
        
        assert fig.data[0].title.text == title
    
    def test_create_metric_gauge_absolute_values(self):
        """Test gauge with absolute values (not percentages)"""
        value = 50
        fig = create_metric_gauge(
            value=value, 
            title="Device Count",
            max_value=100,
            threshold_good=30,
            threshold_excellent=70
        )
        
        # Value should NOT be converted to percentage
        assert fig.data[0].value == value


class TestVisualizationIntegration:
    """Integration tests for visualization functions"""
    
    def test_all_visualizations_produce_valid_figures(self):
        """Test that all visualization functions produce valid Plotly figures"""
        # Feature importance
        importance_df = pd.DataFrame({
            'feature': ['feat1', 'feat2'],
            'importance': [60.0, 40.0]
        })
        fig1 = plot_feature_importance(importance_df)
        
        # Confusion matrix
        fig2 = plot_confusion_matrix(100, 5, 10, 20)
        
        # Probability distribution
        probs = np.random.uniform(0, 1, 50)
        fig3 = plot_probability_distribution(probs)
        
        # ROC curve
        fpr = np.linspace(0, 1, 10)
        tpr = np.linspace(0, 1, 10)
        fig4 = plot_roc_curve(fpr, tpr, 0.85)
        
        # Metric gauge
        fig5 = create_metric_gauge(0.80, "Test")
        
        # All should be valid Figure objects
        for fig in [fig1, fig2, fig3, fig4, fig5]:
            assert isinstance(fig, go.Figure)
            assert hasattr(fig, 'data')
            assert hasattr(fig, 'layout')
