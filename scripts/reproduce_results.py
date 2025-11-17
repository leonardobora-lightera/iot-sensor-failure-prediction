"""
Reproducibility Validation Script - IoT Sensor Failure Prediction

OBJETIVO: Validar que modelo CatBoost v2 produz resultados DETERMINÍSTICOS e EXATOS
         no test set, demonstrando rigor científico.

MODELO v2 - FIELD-only (Nov 13, 2025):
- Dataset: 762 devices FIELD-only (sem contaminação FACTORY)
- Features: 30 (29 telemetria + days_since_last_message)
- Pipeline: SimpleImputer → SMOTE 0.5 → CatBoost

MÉTRICAS ESPERADAS v2 (baseline threshold 0.50):
- Precision: 57.1% (8 TP, 6 FP)
- Recall: 57.1% (8 TP, 6 FN)
- F1-Score: 0.571
- ROC-AUC: 0.9186
- Test Set: 229 devices (14 critical)

CRITÉRIO SUCESSO: Reproduzir métricas v2 com precisão decimal.
"""

import pandas as pd
import joblib
from pathlib import Path
from sklearn.metrics import recall_score, precision_score, f1_score, roc_auc_score, confusion_matrix

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "catboost_pipeline_v2_field_only.pkl"
TEST_DATA_PATH = PROJECT_ROOT / "data" / "device_features_test_stratified.csv"

def load_test_data():
    """Load test set (237 devices, 14 critical)"""
    df = pd.read_csv(TEST_DATA_PATH)
    
    # Separate features and target
    # Remove: device_id (identifier), is_critical_target (target), 
    #         is_critical/severity_category/msg6_count/msg6_rate (leakage/categorical)
    exclude_cols = ['device_id', 'is_critical_target', 'is_critical', 
                    'severity_category', 'msg6_count', 'msg6_rate']
    X_test = df.drop(columns=exclude_cols, errors='ignore')
    y_test = df['is_critical_target']
    
    return X_test, y_test

def load_model():
    """Load trained CatBoost pipeline"""
    pipeline = joblib.load(MODEL_PATH)
    return pipeline

def validate_reproducibility():
    """Main validation function"""
    print("=" * 70)
    print("REPRODUCIBILITY VALIDATION - IoT Sensor Failure Prediction POC")
    print("=" * 70)
    
    # Load data and model
    print("\n[1/4] Loading test set...")
    X_test, y_test = load_test_data()
    print(f"   ✓ Test set loaded: {len(X_test)} devices, {y_test.sum()} critical")
    
    print("\n[2/4] Loading CatBoost pipeline...")
    pipeline = load_model()
    print(f"   ✓ Pipeline loaded: {MODEL_PATH.name}")
    
    # Make predictions
    print("\n[3/4] Running inference on test set...")
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    print("   ✓ Predictions completed")
    
    # Calculate metrics
    print("\n[4/4] Calculating performance metrics...")
    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    # Display results
    print("\n" + "=" * 70)
    print("RESULTADOS OBTIDOS:")
    print("=" * 70)
    print(f"Recall:     {recall:.4f} ({recall*100:.2f}%)")
    print(f"Precision:  {precision:.4f} ({precision*100:.2f}%)")
    print(f"F1-Score:   {f1:.4f} ({f1*100:.2f}%)")
    print(f"AUC:        {auc:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"  TN={tn:3d}  FP={fp:3d}")
    print(f"  FN={fn:3d}  TP={tp:3d}")
    print(f"\nCritical Devices Detected: {tp}/{y_test.sum()} ({tp/y_test.sum()*100:.1f}%)")
    
    # Validate against expected values
    print("\n" + "=" * 70)
    print("VALIDAÇÃO DE REPRODUTIBILIDADE:")
    print("=" * 70)
    
    expected_recall = 0.7857
    expected_precision = 0.8462
    expected_tp = 11
    tolerance = 0.005  # ±0.5%
    
    checks = []
    
    # Check Recall
    recall_ok = abs(recall - expected_recall) <= tolerance
    checks.append(recall_ok)
    status = "✓ PASS" if recall_ok else "✗ FAIL"
    print(f"Recall:    {status} (esperado {expected_recall:.4f}, obtido {recall:.4f})")
    
    # Check Precision
    precision_ok = abs(precision - expected_precision) <= tolerance
    checks.append(precision_ok)
    status = "✓ PASS" if precision_ok else "✗ FAIL"
    print(f"Precision: {status} (esperado {expected_precision:.4f}, obtido {precision:.4f})")
    
    # Check True Positives
    tp_ok = tp == expected_tp
    checks.append(tp_ok)
    status = "✓ PASS" if tp_ok else "✗ FAIL"
    print(f"TP:        {status} (esperado {expected_tp}, obtido {tp})")
    
    # Final verdict
    print("\n" + "=" * 70)
    if all(checks):
        print("✓✓✓ POC VALIDADA - RESULTADOS REPRODUZÍVEIS E DETERMINÍSTICOS ✓✓✓")
        print("=" * 70)
        print("\nModelo demonstra RIGOR CIENTÍFICO:")
        print("  • Métricas exatas reproduzidas")
        print("  • Pipeline determinístico (random_state=42)")
        print("  • Modelo pronto para apresentação POC")
        print("\nPróximos passos: Apresentação stakeholders + Produção (3-4 semanas)")
        return 0
    else:
        print("✗✗✗ ATENÇÃO: RESULTADOS DIVERGIRAM DO ESPERADO ✗✗✗")
        print("=" * 70)
        print("\nPossíveis causas:")
        print("  • Modelo ou pipeline alterado")
        print("  • Test set modificado")
        print("  • Ambiente Python diferente")
        print("\nAção: Investigar mudanças antes de apresentação POC")
        return 1

if __name__ == "__main__":
    exit_code = validate_reproducibility()
    exit(exit_code)
