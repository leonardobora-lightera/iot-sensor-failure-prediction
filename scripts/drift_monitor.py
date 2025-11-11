"""
Drift Monitor - Distribution Shift Detection for IoT Sensor Failure Model

This script detects distribution shifts between training and production data using
Kolmogorov-Smirnov statistical tests. It identifies when the model is operating
outside its validated regime due to:
1. Feature distribution drift (sensor values changing)
2. Lifecycle pattern drift (deployment workflow changing)

Usage:
    python scripts/drift_monitor.py \\
        --reference data/device_features_train.csv \\
        --production data/production_batch_2025W45.csv \\
        --output reports/drift_weekly/ \\
        --threshold-warning 0.2 \\
        --threshold-critical 0.4

Output:
    - JSON report with KS statistics per feature
    - CDF plots showing distribution differences
    - Lifecycle pattern drift alerts
    - Overall drift status (OK, WARNING, CRITICAL)

Author: Data Science Team
Last Updated: 2025-11-11
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


# Feature groups for lifecycle pattern detection
LIFECYCLE_PROXY_FEATURES = {
    'activity_level': ['total_messages', 'max_frame_count'],
    'variability': ['optical_std', 'temp_std', 'battery_std', 'snr_std', 'rsrp_std', 'rsrq_std']
}

# All 29 features to monitor
ALL_FEATURES = [
    # Messages (2)
    'total_messages', 'max_frame_count',
    # Optical (7)
    'optical_mean', 'optical_std', 'optical_min', 'optical_max', 'optical_range',
    'optical_above_threshold', 'optical_below_threshold',
    # Temperature (6)
    'temp_mean', 'temp_std', 'temp_min', 'temp_max', 'temp_range', 'temp_above_threshold',
    # Battery (5)
    'battery_mean', 'battery_std', 'battery_min', 'battery_max', 'battery_range',
    # SNR (3)
    'snr_mean', 'snr_std', 'snr_min',
    # RSRP (3)
    'rsrp_mean', 'rsrp_std', 'rsrp_min',
    # RSRQ (3)
    'rsrq_mean', 'rsrq_std', 'rsrq_min'
]


def load_data(filepath: str) -> pd.DataFrame:
    """Load device features CSV file."""
    df = pd.read_csv(filepath)
    
    # Validate required features present
    missing_features = set(ALL_FEATURES) - set(df.columns)
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")
    
    return df[ALL_FEATURES]


def compute_ks_statistics(
    reference: pd.DataFrame,
    production: pd.DataFrame
) -> Dict[str, Dict]:
    """
    Compute Kolmogorov-Smirnov test for each feature.
    
    Args:
        reference: Training/reference data (DataFrame with 29 features)
        production: Production batch data (DataFrame with 29 features)
    
    Returns:
        Dictionary mapping feature name to KS test results:
        {
            'feature_name': {
                'ks_statistic': float,
                'p_value': float,
                'reference_mean': float,
                'production_mean': float,
                'reference_std': float,
                'production_std': float
            }
        }
    """
    results = {}
    
    for feature in ALL_FEATURES:
        # Drop NaN values for comparison
        ref_data = reference[feature].dropna()
        prod_data = production[feature].dropna()
        
        if len(ref_data) == 0 or len(prod_data) == 0:
            results[feature] = {
                'ks_statistic': np.nan,
                'p_value': np.nan,
                'reference_mean': np.nan,
                'production_mean': np.nan,
                'reference_std': np.nan,
                'production_std': np.nan,
                'error': 'Insufficient data after removing NaN'
            }
            continue
        
        # Kolmogorov-Smirnov test
        ks_result = stats.ks_2samp(ref_data, prod_data)
        
        results[feature] = {
            'ks_statistic': float(ks_result.statistic),
            'p_value': float(ks_result.pvalue),
            'reference_mean': float(ref_data.mean()),
            'production_mean': float(prod_data.mean()),
            'reference_std': float(ref_data.std()),
            'production_std': float(prod_data.std()),
            'reference_n': int(len(ref_data)),
            'production_n': int(len(prod_data))
        }
    
    return results


def detect_lifecycle_drift(ks_results: Dict[str, Dict]) -> Dict[str, any]:
    """
    Detect changes in lifecycle patterns using proxy features.
    
    High drift in activity_level (total_messages) suggests deployment pattern changed
    (e.g., direct deploy vs lab-tested).
    
    High drift in variability features suggests lifecycle phase mixing changed
    (e.g., more/less inactive periods).
    
    Args:
        ks_results: KS statistics for all features
    
    Returns:
        Dictionary with lifecycle drift detection results:
        {
            'lifecycle_drift_detected': bool,
            'activity_drift': float (max KS among activity features),
            'variability_drift': float (max KS among variability features),
            'details': {...}
        }
    """
    # Activity level drift (proxy for inactive periods)
    activity_ks = [
        ks_results[feat]['ks_statistic']
        for feat in LIFECYCLE_PROXY_FEATURES['activity_level']
        if not np.isnan(ks_results[feat]['ks_statistic'])
    ]
    activity_drift = max(activity_ks) if activity_ks else np.nan
    
    # Variability drift (proxy for lifecycle phase mixing)
    variability_ks = [
        ks_results[feat]['ks_statistic']
        for feat in LIFECYCLE_PROXY_FEATURES['variability']
        if not np.isnan(ks_results[feat]['ks_statistic'])
    ]
    variability_drift = max(variability_ks) if variability_ks else np.nan
    
    # Overall lifecycle drift score
    lifecycle_drift_score = max(
        activity_drift if not np.isnan(activity_drift) else 0,
        variability_drift if not np.isnan(variability_drift) else 0
    )
    
    # Detection threshold: 0.3 for lifecycle pattern change
    detected = lifecycle_drift_score > 0.3
    
    return {
        'lifecycle_drift_detected': detected,
        'lifecycle_drift_score': float(lifecycle_drift_score),
        'activity_drift': float(activity_drift) if not np.isnan(activity_drift) else None,
        'variability_drift': float(variability_drift) if not np.isnan(variability_drift) else None,
        'interpretation': (
            "Deployment pattern likely CHANGED (e.g., lab-tested → direct-deploy)" 
            if detected else 
            "Deployment pattern appears STABLE"
        ),
        'details': {
            'activity_features': {
                feat: ks_results[feat]['ks_statistic']
                for feat in LIFECYCLE_PROXY_FEATURES['activity_level']
            },
            'variability_features': {
                feat: ks_results[feat]['ks_statistic']
                for feat in LIFECYCLE_PROXY_FEATURES['variability']
            }
        }
    }


def classify_drift_status(
    ks_results: Dict[str, Dict],
    lifecycle_drift: Dict,
    threshold_warning: float = 0.2,
    threshold_critical: float = 0.4
) -> Tuple[str, List[str]]:
    """
    Classify overall drift status based on KS statistics and thresholds.
    
    Args:
        ks_results: KS statistics for all features
        lifecycle_drift: Lifecycle drift detection results
        threshold_warning: KS threshold for WARNING level (default 0.2)
        threshold_critical: KS threshold for CRITICAL level (default 0.4)
    
    Returns:
        Tuple of (status, alerts):
        - status: 'OK', 'WARNING', or 'CRITICAL'
        - alerts: List of alert messages
    """
    alerts = []
    max_ks = 0.0
    critical_features = []
    warning_features = []
    
    # Check each feature
    for feature, result in ks_results.items():
        ks_stat = result['ks_statistic']
        if np.isnan(ks_stat):
            continue
        
        max_ks = max(max_ks, ks_stat)
        
        if ks_stat >= threshold_critical:
            critical_features.append(feature)
            alerts.append(
                f"CRITICAL drift on {feature}: KS={ks_stat:.3f} "
                f"(ref_mean={result['reference_mean']:.2f}, "
                f"prod_mean={result['production_mean']:.2f})"
            )
        elif ks_stat >= threshold_warning:
            warning_features.append(feature)
            alerts.append(
                f"WARNING drift on {feature}: KS={ks_stat:.3f} "
                f"(ref_mean={result['reference_mean']:.2f}, "
                f"prod_mean={result['production_mean']:.2f})"
            )
    
    # Check lifecycle drift
    if lifecycle_drift['lifecycle_drift_detected']:
        alerts.append(
            f"LIFECYCLE PATTERN DRIFT detected: score={lifecycle_drift['lifecycle_drift_score']:.3f}. "
            f"{lifecycle_drift['interpretation']}"
        )
    
    # Determine overall status
    if critical_features or lifecycle_drift['lifecycle_drift_detected']:
        status = 'CRITICAL'
    elif warning_features:
        status = 'WARNING'
    else:
        status = 'OK'
    
    return status, alerts


def plot_feature_cdfs(
    reference: pd.DataFrame,
    production: pd.DataFrame,
    ks_results: Dict[str, Dict],
    output_dir: Path,
    top_n: int = 10
):
    """
    Plot cumulative distribution functions (CDFs) for features with highest drift.
    
    Args:
        reference: Training/reference data
        production: Production batch data
        ks_results: KS statistics
        output_dir: Directory to save plots
        top_n: Number of top-drift features to plot
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sort features by KS statistic (highest drift first)
    sorted_features = sorted(
        [(feat, res['ks_statistic']) for feat, res in ks_results.items()],
        key=lambda x: x[1] if not np.isnan(x[1]) else 0,
        reverse=True
    )[:top_n]
    
    # Create subplot grid
    n_plots = len(sorted_features)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()
    
    for idx, (feature, ks_stat) in enumerate(sorted_features):
        ax = axes[idx]
        
        # Get data
        ref_data = reference[feature].dropna().values
        prod_data = production[feature].dropna().values
        
        # Sort for CDF
        ref_sorted = np.sort(ref_data)
        prod_sorted = np.sort(prod_data)
        
        # Compute CDFs
        ref_cdf = np.arange(1, len(ref_sorted) + 1) / len(ref_sorted)
        prod_cdf = np.arange(1, len(prod_sorted) + 1) / len(prod_sorted)
        
        # Plot
        ax.plot(ref_sorted, ref_cdf, label='Reference (training)', linewidth=2, alpha=0.8)
        ax.plot(prod_sorted, prod_cdf, label='Production', linewidth=2, alpha=0.8)
        
        ax.set_xlabel(feature)
        ax.set_ylabel('Cumulative Probability')
        ax.set_title(f'{feature}\nKS={ks_stat:.3f}')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for idx in range(len(sorted_features), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'top_drift_features_cdf.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ CDF plots saved to {output_dir / 'top_drift_features_cdf.png'}")


def save_report(
    ks_results: Dict[str, Dict],
    lifecycle_drift: Dict,
    status: str,
    alerts: List[str],
    output_dir: Path
):
    """Save drift detection report as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        'overall_status': status,
        'alerts': alerts,
        'max_ks_statistic': max(
            (res['ks_statistic'] for res in ks_results.values() if not np.isnan(res['ks_statistic'])),
            default=0.0
        ),
        'lifecycle_drift': lifecycle_drift,
        'feature_drift': ks_results,
        'summary': {
            'total_features': len(ALL_FEATURES),
            'critical_features': sum(
                1 for res in ks_results.values() 
                if not np.isnan(res['ks_statistic']) and res['ks_statistic'] >= 0.4
            ),
            'warning_features': sum(
                1 for res in ks_results.values() 
                if not np.isnan(res['ks_statistic']) and 0.2 <= res['ks_statistic'] < 0.4
            ),
            'ok_features': sum(
                1 for res in ks_results.values() 
                if not np.isnan(res['ks_statistic']) and res['ks_statistic'] < 0.2
            )
        }
    }
    
    report_path = output_dir / 'drift_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Drift report saved to {report_path}")
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description='Detect distribution drift in IoT sensor failure model data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Weekly drift monitoring
  python scripts/drift_monitor.py \\
      --reference data/device_features_train.csv \\
      --production data/production_batch_2025W45.csv \\
      --output reports/drift_weekly/

  # Custom thresholds
  python scripts/drift_monitor.py \\
      --reference data/device_features_train.csv \\
      --production data/production_batch_2025W45.csv \\
      --output reports/drift_weekly/ \\
      --threshold-warning 0.15 \\
      --threshold-critical 0.35
        """
    )
    
    parser.add_argument(
        '--reference',
        required=True,
        help='Path to reference/training data CSV'
    )
    parser.add_argument(
        '--production',
        required=True,
        help='Path to production batch data CSV'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output directory for reports and plots'
    )
    parser.add_argument(
        '--threshold-warning',
        type=float,
        default=0.2,
        help='KS statistic threshold for WARNING level (default: 0.2)'
    )
    parser.add_argument(
        '--threshold-critical',
        type=float,
        default=0.4,
        help='KS statistic threshold for CRITICAL level (default: 0.4)'
    )
    parser.add_argument(
        '--top-n',
        type=int,
        default=10,
        help='Number of top-drift features to plot (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Load data
    print(f"📂 Loading reference data from {args.reference}...")
    reference_data = load_data(args.reference)
    print(f"   ✓ Loaded {len(reference_data)} reference devices")
    
    print(f"📂 Loading production data from {args.production}...")
    production_data = load_data(args.production)
    print(f"   ✓ Loaded {len(production_data)} production devices")
    
    # Compute KS statistics
    print("📊 Computing Kolmogorov-Smirnov statistics...")
    ks_results = compute_ks_statistics(reference_data, production_data)
    print(f"   ✓ Computed KS statistics for {len(ALL_FEATURES)} features")
    
    # Detect lifecycle drift
    print("🔍 Detecting lifecycle pattern drift...")
    lifecycle_drift = detect_lifecycle_drift(ks_results)
    print(f"   ✓ Lifecycle drift detected: {lifecycle_drift['lifecycle_drift_detected']}")
    
    # Classify drift status
    print("⚠️  Classifying drift status...")
    status, alerts = classify_drift_status(
        ks_results,
        lifecycle_drift,
        args.threshold_warning,
        args.threshold_critical
    )
    
    # Print status
    print("\n" + "=" * 80)
    print(f"DRIFT STATUS: {status}")
    print("=" * 80)
    
    if alerts:
        print("\nALERTS:")
        for alert in alerts:
            print(f"  • {alert}")
    else:
        print("\n✅ No drift detected. Production data matches training distribution.")
    
    print(f"\nMax KS statistic: {max((res['ks_statistic'] for res in ks_results.values() if not np.isnan(res['ks_statistic'])), default=0.0):.3f}")
    print("=" * 80 + "\n")
    
    # Save outputs
    output_dir = Path(args.output)
    
    print("💾 Saving drift report...")
    save_report(ks_results, lifecycle_drift, status, alerts, output_dir)
    
    print("📈 Generating CDF plots...")
    plot_feature_cdfs(
        reference_data,
        production_data,
        ks_results,
        output_dir,
        top_n=args.top_n
    )
    
    print("\n✅ Drift monitoring complete!")
    
    # Exit with appropriate code
    if status == 'CRITICAL':
        print("❌ CRITICAL drift detected - model should NOT be used")
        sys.exit(2)
    elif status == 'WARNING':
        print("⚠️  WARNING drift detected - use model with caution")
        sys.exit(1)
    else:
        print("✅ OK - model operating within valid regime")
        sys.exit(0)


if __name__ == '__main__':
    main()
