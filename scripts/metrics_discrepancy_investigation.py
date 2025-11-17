"""
Metrics Discrepancy Investigation
=====================================

OBJETIVO:
Reproduzir EXATAMENTE o test set usado no treinamento do modelo v2 para confirmar
se as métricas baseline são 57.1% (metadata) ou 83.3% (threshold experiment).

HIPÓTESE:
A discrepância pode ser causada por:
1. Dataset diferente (789 mixed vs 762 FIELD-only)
2. Feature days_since_last_message ausente no dataset original (imputado como 0)
3. Split diferente (random_state ou stratify)

ESTRATÉGIA:
1. Carregar device_features_with_telemetry_field_only.csv (762 devices)
2. Adicionar labels is_critical do arquivo original
3. Reproduzir split EXATO (test_size=0.3, random_state=42, stratify=y)
4. Calcular métricas com threshold 0.50
5. Comparar com metadata (57.1%) e threshold experiment (83.3%)

Author: Leonardo Costa
Date: 2025-11-14
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report
)
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / 'models' / 'catboost_pipeline_v2_field_only.pkl'
FIELD_ONLY_PATH = BASE_DIR / 'data' / 'device_features_with_telemetry_field_only.csv'
ORIGINAL_PATH = BASE_DIR / 'data' / 'device_features_with_telemetry.csv'
OUTPUT_DIR = BASE_DIR / 'analysis'

# Constants
RANDOM_STATE = 42
TEST_SIZE = 0.30
THRESHOLD = 0.50  # Baseline threshold

# Feature order (must match model training)
FEATURES_ORDER = [
    'total_messages', 'max_frame_count', 'days_since_last_message',
    'optical_mean', 'optical_std', 'optical_min', 'optical_max', 
    'optical_readings', 'optical_range', 'optical_below_threshold',
    'temp_mean', 'temp_std', 'temp_min', 'temp_max', 
    'temp_range', 'temp_above_threshold',
    'battery_mean', 'battery_std', 'battery_min', 'battery_max', 
    'battery_below_threshold',
    'snr_mean', 'snr_std', 'snr_min',
    'rsrp_mean', 'rsrp_std', 'rsrp_min',
    'rsrq_mean', 'rsrq_std', 'rsrq_min'
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_field_only_with_labels():
    """
    Carrega dataset FIELD-only e adiciona labels do arquivo original
    
    Returns:
        pd.DataFrame: Dataset FIELD-only com labels (762 devices)
    """
    print("\n" + "="*80)
    print("LOADING DATASETS")
    print("="*80)
    
    # Load FIELD-only dataset
    print(f"\n📂 Loading FIELD-only dataset: {FIELD_ONLY_PATH.name}")
    df_field = pd.read_csv(FIELD_ONLY_PATH)
    print(f"   ├─ Shape: {df_field.shape}")
    print(f"   ├─ Devices: {len(df_field)}")
    print(f"   └─ Columns: {df_field.columns.tolist()}")
    
    # Load original dataset with labels
    print(f"\n📂 Loading original dataset with labels: {ORIGINAL_PATH.name}")
    df_original = pd.read_csv(ORIGINAL_PATH)
    print(f"   ├─ Shape: {df_original.shape}")
    print(f"   ├─ Devices: {len(df_original)}")
    print(f"   └─ Has is_critical: {'is_critical' in df_original.columns}")
    
    # Merge labels
    print(f"\n🔗 Merging labels from original to FIELD-only...")
    df_field_with_labels = df_field.merge(
        df_original[['device_id', 'is_critical']], 
        on='device_id', 
        how='left'
    )
    
    # Check for missing labels
    missing_labels = df_field_with_labels['is_critical'].isna().sum()
    if missing_labels > 0:
        print(f"   ⚠️  WARNING: {missing_labels} devices without labels (will be dropped)")
        df_field_with_labels = df_field_with_labels.dropna(subset=['is_critical'])
    
    # Label distribution
    critical_count = df_field_with_labels['is_critical'].sum()
    normal_count = len(df_field_with_labels) - critical_count
    
    print(f"\n✅ Final dataset:")
    print(f"   ├─ Total devices: {len(df_field_with_labels)}")
    print(f"   ├─ Critical: {critical_count} ({critical_count/len(df_field_with_labels)*100:.1f}%)")
    print(f"   └─ Normal: {normal_count} ({normal_count/len(df_field_with_labels)*100:.1f}%)")
    
    return df_field_with_labels

def prepare_features(df):
    """
    Prepara features na ordem correta para o modelo
    
    Args:
        df (pd.DataFrame): Dataset com features
        
    Returns:
        tuple: (X, y) arrays prontos para modelo
    """
    print("\n" + "="*80)
    print("PREPARING FEATURES")
    print("="*80)
    
    # Check for missing features
    missing_features = [f for f in FEATURES_ORDER if f not in df.columns]
    if missing_features:
        print(f"\n⚠️  WARNING: Missing features: {missing_features}")
        print(f"   These will be IMPUTED with 0 (model's SimpleImputer will handle)")
        for feat in missing_features:
            df[feat] = 0
    
    # Select features in correct order
    X = df[FEATURES_ORDER].values
    y = df['is_critical'].values
    
    print(f"\n✅ Features prepared:")
    print(f"   ├─ X shape: {X.shape}")
    print(f"   ├─ y shape: {y.shape}")
    print(f"   ├─ Features count: {len(FEATURES_ORDER)}")
    print(f"   └─ Critical rate: {y.mean()*100:.1f}%")
    
    return X, y

def reproduce_train_test_split(X, y):
    """
    Reproduz EXATAMENTE o split usado no treinamento
    
    Args:
        X (np.array): Features
        y (np.array): Labels
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    print("\n" + "="*80)
    print("REPRODUCING TRAIN/TEST SPLIT")
    print("="*80)
    
    print(f"\n⚙️  Split configuration:")
    print(f"   ├─ test_size: {TEST_SIZE}")
    print(f"   ├─ random_state: {RANDOM_STATE}")
    print(f"   └─ stratify: True (maintains class balance)")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=TEST_SIZE, 
        random_state=RANDOM_STATE, 
        stratify=y
    )
    
    print(f"\n✅ Split results:")
    print(f"   TRAIN:")
    print(f"   ├─ Size: {len(X_train)} devices ({len(X_train)/len(X)*100:.1f}%)")
    print(f"   ├─ Critical: {y_train.sum()} ({y_train.sum()/len(y_train)*100:.1f}%)")
    print(f"   └─ Normal: {len(y_train) - y_train.sum()}")
    print(f"\n   TEST:")
    print(f"   ├─ Size: {len(X_test)} devices ({len(X_test)/len(X)*100:.1f}%)")
    print(f"   ├─ Critical: {y_test.sum()} ({y_test.sum()/len(y_test)*100:.1f}%)")
    print(f"   └─ Normal: {len(y_test) - y_test.sum()}")
    
    return X_train, X_test, y_train, y_test

def load_model_and_predict(X_test):
    """
    Carrega modelo v2 e gera predições
    
    Args:
        X_test (np.array): Test features
        
    Returns:
        np.array: Probabilities for positive class
    """
    print("\n" + "="*80)
    print("LOADING MODEL & GENERATING PREDICTIONS")
    print("="*80)
    
    print(f"\n📦 Loading model: {MODEL_PATH.name}")
    model = joblib.load(MODEL_PATH)
    
    print(f"   ├─ Model type: {type(model).__name__}")
    print(f"   └─ Pipeline steps: {[name for name, _ in model.steps]}")
    
    print(f"\n🎯 Generating predictions for {len(X_test)} test devices...")
    y_proba = model.predict_proba(X_test)[:, 1]
    
    print(f"   ├─ Probability range: [{y_proba.min():.3f}, {y_proba.max():.3f}]")
    print(f"   ├─ Mean probability: {y_proba.mean():.3f}")
    print(f"   └─ Median probability: {np.median(y_proba):.3f}")
    
    return y_proba

def calculate_metrics(y_test, y_proba, threshold=0.50):
    """
    Calcula métricas para threshold especificado
    
    Args:
        y_test (np.array): True labels
        y_proba (np.array): Predicted probabilities
        threshold (float): Classification threshold
        
    Returns:
        dict: Metrics dictionary
    """
    print("\n" + "="*80)
    print(f"CALCULATING METRICS (Threshold: {threshold})")
    print("="*80)
    
    # Convert probabilities to predictions
    y_pred = (y_proba >= threshold).astype(int)
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    
    # Calculate metrics
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    # Results
    metrics = {
        'threshold': threshold,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'tn': tn,
        'predicted_critical': tp + fp,
        'actual_critical': tp + fn
    }
    
    print(f"\n📊 CONFUSION MATRIX:")
    print(f"   ┌─────────────────────────────┐")
    print(f"   │  True Positive  (TP): {tp:>4}  │")
    print(f"   │  False Positive (FP): {fp:>4}  │")
    print(f"   │  False Negative (FN): {fn:>4}  │")
    print(f"   │  True Negative  (TN): {tn:>4}  │")
    print(f"   └─────────────────────────────┘")
    
    print(f"\n📈 PERFORMANCE METRICS:")
    print(f"   ┌─────────────────────────────────┐")
    print(f"   │  Precision: {precision*100:>5.1f}%           │")
    print(f"   │  Recall:    {recall*100:>5.1f}%           │")
    print(f"   │  F1-Score:  {f1:>5.3f}            │")
    print(f"   └─────────────────────────────────┘")
    
    print(f"\n🎯 DETECTION SUMMARY:")
    print(f"   ├─ Predicted Critical: {tp + fp} devices")
    print(f"   ├─ Actual Critical:    {tp + fn} devices")
    print(f"   ├─ Correctly Detected: {tp} devices ({tp/(tp+fn)*100:.1f}%)")
    print(f"   └─ Missed:             {fn} devices ({fn/(tp+fn)*100:.1f}%)")
    
    return metrics

def compare_with_metadata_and_experiment(metrics):
    """
    Compara resultados com metadata e threshold experiment
    
    Args:
        metrics (dict): Calculated metrics
    """
    print("\n" + "="*80)
    print("COMPARISON WITH PREVIOUS RESULTS")
    print("="*80)
    
    # Reference values
    metadata_precision = 0.571  # 57.1%
    metadata_recall = 0.571     # 57.1%
    experiment_precision = 0.833  # 83.3%
    experiment_recall = 0.714     # 71.4%
    
    # Calculate differences
    diff_metadata_prec = (metrics['precision'] - metadata_precision) * 100
    diff_metadata_rec = (metrics['recall'] - metadata_recall) * 100
    diff_exp_prec = (metrics['precision'] - experiment_precision) * 100
    diff_exp_rec = (metrics['recall'] - experiment_recall) * 100
    
    print("\n📋 REFERENCE COMPARISON:")
    print("\n   1️⃣  MODEL METADATA (catboost_pipeline_v2_metadata.json):")
    print(f"      ├─ Precision: 57.1%")
    print(f"      ├─ Recall:    57.1%")
    print(f"      └─ Difference: {diff_metadata_prec:+.1f}pp precision, {diff_metadata_rec:+.1f}pp recall")
    
    print("\n   2️⃣  THRESHOLD EXPERIMENT (Nov 14 - 789 devices mixed):")
    print(f"      ├─ Precision: 83.3%")
    print(f"      ├─ Recall:    71.4%")
    print(f"      └─ Difference: {diff_exp_prec:+.1f}pp precision, {diff_exp_rec:+.1f}pp recall")
    
    print("\n   3️⃣  THIS INVESTIGATION (762 devices FIELD-only):")
    print(f"      ├─ Precision: {metrics['precision']*100:.1f}%")
    print(f"      └─ Recall:    {metrics['recall']*100:.1f}%")
    
    # Determine conclusion
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    if abs(metrics['precision'] - metadata_precision) < 0.05:
        print("\n✅ MATCHES METADATA (~57.1%)")
        print("   └─ Discrepância no threshold experiment foi causada por dataset diferente")
        print("      (789 mixed vs 762 FIELD-only)")
    elif abs(metrics['precision'] - experiment_precision) < 0.05:
        print("\n⚠️  MATCHES THRESHOLD EXPERIMENT (~83.3%)")
        print("   └─ Metadata está INCORRETO - modelo performa MELHOR que reportado")
        print("      Possível causa: Metadata foi calculado em subset diferente")
    else:
        print("\n❓ RESULTADO INTERMEDIÁRIO")
        print("   └─ Métricas não correspondem nem ao metadata nem ao experiment")
        print("      Investigação adicional necessária")
    
    return diff_metadata_prec, diff_exp_prec

def save_results(metrics, df_field):
    """
    Salva resultados da investigação
    
    Args:
        metrics (dict): Calculated metrics
        df_field (pd.DataFrame): Dataset used
    """
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    
    # Create results dataframe
    results = pd.DataFrame([{
        'investigation_date': '2025-11-14',
        'dataset': 'device_features_with_telemetry_field_only.csv',
        'total_devices': len(df_field),
        'test_size': int(len(df_field) * TEST_SIZE),
        'threshold': metrics['threshold'],
        'precision': f"{metrics['precision']*100:.1f}%",
        'recall': f"{metrics['recall']*100:.1f}%",
        'f1_score': f"{metrics['f1_score']:.3f}",
        'tp': metrics['tp'],
        'fp': metrics['fp'],
        'fn': metrics['fn'],
        'tn': metrics['tn']
    }])
    
    output_path = OUTPUT_DIR / 'metrics_discrepancy_investigation.csv'
    results.to_csv(output_path, index=False)
    print(f"\n💾 Results saved: {output_path}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution flow"""
    
    print("\n" + "="*80)
    print("METRICS DISCREPANCY INVESTIGATION")
    print("="*80)
    print("\n🎯 OBJETIVO: Reproduzir EXATO test set v2 para confirmar baseline metrics")
    print("   ├─ Metadata reporta:     57.1% precision / 57.1% recall")
    print("   ├─ Experiment observou:  83.3% precision / 71.4% recall")
    print("   └─ Discrepância:        +26.2pp precision")
    
    # Step 1: Load FIELD-only dataset with labels
    df_field = load_field_only_with_labels()
    
    # Step 2: Prepare features
    X, y = prepare_features(df_field)
    
    # Step 3: Reproduce train/test split
    X_train, X_test, y_train, y_test = reproduce_train_test_split(X, y)
    
    # Step 4: Load model and predict
    y_proba = load_model_and_predict(X_test)
    
    # Step 5: Calculate metrics
    metrics = calculate_metrics(y_test, y_proba, threshold=THRESHOLD)
    
    # Step 6: Compare with previous results
    compare_with_metadata_and_experiment(metrics)
    
    # Step 7: Save results
    save_results(metrics, df_field)
    
    print("\n" + "="*80)
    print("✅ INVESTIGATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
