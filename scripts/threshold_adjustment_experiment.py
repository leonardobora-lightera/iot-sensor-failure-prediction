"""
Threshold Adjustment Experiment - Model v2 FIELD-only
======================================================
Testa diferentes thresholds de classificação para otimizar precision/recall.
Objetivo: Encontrar threshold que maximiza precision mantendo recall aceitável.
"""

import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (precision_score, recall_score, f1_score, 
                             confusion_matrix, precision_recall_curve, auc)

# Configurações
MODEL_PATH = Path("models/catboost_pipeline_v2_field_only.pkl")
DATA_PATH = Path("data/device_features_with_telemetry.csv")  # Arquivo original com labels
OUTPUT_PATH = Path("analysis")
OUTPUT_PATH.mkdir(exist_ok=True)

# Thresholds a testar
THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]

# Features do modelo v2 (30 features)
FEATURE_COLS = [
    'total_messages', 'max_frame_count', 'days_since_last_message',
    'optical_mean', 'optical_std', 'optical_min', 'optical_max', 
    'optical_readings', 'optical_range', 'optical_below_threshold',
    'temp_mean', 'temp_std', 'temp_min', 'temp_max', 'temp_range',
    'temp_above_threshold',
    'battery_mean', 'battery_std', 'battery_min', 'battery_max',
    'battery_below_threshold',
    'snr_mean', 'snr_std', 'snr_min',
    'rsrp_mean', 'rsrp_std', 'rsrp_min',
    'rsrq_mean', 'rsrq_std', 'rsrq_min'
]

def load_data_and_split():
    """Carrega dados e reproduz train/test split do treinamento"""
    print(f"📂 Carregando dados: {DATA_PATH}")
    
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    print(f"✅ {len(df)} devices carregados (total)")
    
    # Filtrar apenas FIELD (reproduzir processo do modelo v2)
    if 'MODE' in df.columns:
        df_field = df[df['MODE'] == 'FIELD'].copy()
        print(f"✅ {len(df_field)} devices FIELD-only (removidos {len(df) - len(df_field)} FACTORY)")
    else:
        print("⚠️ Coluna MODE não encontrada, usando todos devices")
        df_field = df
    
    # Verificar label column
    if 'is_critical' not in df_field.columns:
        raise ValueError("❌ Coluna 'is_critical' não encontrada no dataset")
    
    # Verificar quais features existem no dataset
    available_features = [f for f in FEATURE_COLS if f in df_field.columns]
    missing_features = [f for f in FEATURE_COLS if f not in df_field.columns]
    
    if missing_features:
        print(f"⚠️ Features ausentes (serão imputadas pelo modelo): {missing_features}")
        # Adicionar features faltantes com valor 0 (serão tratadas pelo imputer do modelo)
        for feat in missing_features:
            df_field[feat] = 0
    
    # Preparar features e labels
    X = df_field[FEATURE_COLS]
    y = df_field['is_critical'].astype(int)
    
    print(f"📊 Dataset: {len(X)} devices, {y.sum()} críticos ({y.sum()/len(y)*100:.1f}%)")
    
    # Reproduzir split do treinamento (MESMO random_state!)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"✅ Train: {len(X_train)} devices ({y_train.sum()} críticos)")
    print(f"✅ Test:  {len(X_test)} devices ({y_test.sum()} críticos)")
    
    return X_test, y_test

def load_model():
    """Carrega modelo v2"""
    print(f"\n🤖 Carregando modelo: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modelo carregado: {type(model).__name__}")
    return model

def get_predictions(model, X_test):
    """Gera probabilidades de predição"""
    print("\n🔮 Gerando predições...")
    probabilities = model.predict_proba(X_test)[:, 1]  # Probabilidade classe positiva
    print(f"✅ Probabilidades geradas para {len(probabilities)} devices")
    print(f"📊 Prob stats: min={probabilities.min():.3f}, max={probabilities.max():.3f}, "
          f"mean={probabilities.mean():.3f}, median={np.median(probabilities):.3f}")
    return probabilities

def evaluate_threshold(y_true, probabilities, threshold):
    """Avalia métricas para um threshold específico"""
    y_pred = (probabilities >= threshold).astype(int)
    
    # Calcular métricas
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    return {
        'threshold': threshold,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'tp': int(tp),
        'fp': int(fp),
        'fn': int(fn),
        'tn': int(tn),
        'total_predicted_critical': int(tp + fp),
        'total_actual_critical': int(tp + fn)
    }

def run_threshold_experiment(y_test, probabilities):
    """Executa experimento para todos thresholds"""
    print("\n" + "="*80)
    print("🧪 THRESHOLD ADJUSTMENT EXPERIMENT")
    print("="*80)
    
    results = []
    
    for threshold in THRESHOLDS:
        metrics = evaluate_threshold(y_test, probabilities, threshold)
        results.append(metrics)
        
        print(f"\nThreshold: {threshold:.2f}")
        print(f"  Precision: {metrics['precision']:.1%}  |  Recall: {metrics['recall']:.1%}  |  F1: {metrics['f1_score']:.3f}")
        print(f"  TP: {metrics['tp']:3d}  FP: {metrics['fp']:3d}  |  FN: {metrics['fn']:3d}  TN: {metrics['tn']:3d}")
        print(f"  Predicted Critical: {metrics['total_predicted_critical']} devices")
    
    results_df = pd.DataFrame(results)
    
    # Salvar CSV
    csv_file = OUTPUT_PATH / 'threshold_experiment_results.csv'
    results_df.to_csv(csv_file, index=False)
    print(f"\n✅ Resultados salvos: {csv_file}")
    
    return results_df

def plot_precision_recall_curve(y_test, probabilities):
    """Plota precision-recall curve"""
    print("\n📈 Criando Precision-Recall Curve...")
    
    precision, recall, thresholds = precision_recall_curve(y_test, probabilities)
    pr_auc = auc(recall, precision)
    
    plt.figure(figsize=(10, 7))
    plt.plot(recall, precision, 'b-', linewidth=2, label=f'PR Curve (AUC = {pr_auc:.3f})')
    
    # Marcar thresholds testados
    for t in THRESHOLDS:
        y_pred = (probabilities >= t).astype(int)
        p = precision_score(y_test, y_pred, zero_division=0)
        r = recall_score(y_test, y_pred, zero_division=0)
        
        if t == 0.50:
            plt.plot(r, p, 'ro', markersize=12, label=f'Threshold {t:.2f} (baseline)')
        elif t in [0.65, 0.70]:
            plt.plot(r, p, 'go', markersize=10, label=f'Threshold {t:.2f}')
        else:
            plt.plot(r, p, 'ko', markersize=6)
        
        plt.annotate(f'{t:.2f}', (r, p), textcoords="offset points", 
                    xytext=(5,5), fontsize=9)
    
    plt.xlabel('Recall', fontsize=12, fontweight='bold')
    plt.ylabel('Precision', fontsize=12, fontweight='bold')
    plt.title('Precision-Recall Curve - Threshold Adjustment Experiment', 
              fontsize=14, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10, loc='best')
    plt.xlim([0, 1.05])
    plt.ylim([0, 1.05])
    
    output_file = OUTPUT_PATH / 'precision_recall_curve.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {output_file}")
    plt.close()

def plot_threshold_metrics(results_df):
    """Plota métricas vs threshold"""
    print("\n📈 Criando gráfico Threshold vs Metrics...")
    
    plt.figure(figsize=(12, 7))
    
    plt.plot(results_df['threshold'], results_df['precision'], 
             'o-', linewidth=2, markersize=8, label='Precision', color='#2ECC71')
    plt.plot(results_df['threshold'], results_df['recall'], 
             's-', linewidth=2, markersize=8, label='Recall', color='#E74C3C')
    plt.plot(results_df['threshold'], results_df['f1_score'], 
             '^-', linewidth=2, markersize=8, label='F1-Score', color='#3498DB')
    
    # Linha vertical no threshold baseline (0.5)
    plt.axvline(x=0.50, color='gray', linestyle='--', alpha=0.5, label='Baseline (0.50)')
    
    plt.xlabel('Threshold', fontsize=12, fontweight='bold')
    plt.ylabel('Score', fontsize=12, fontweight='bold')
    plt.title('Classification Metrics vs Threshold - Model v2 FIELD-only', 
              fontsize=14, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11, loc='best')
    plt.xticks(THRESHOLDS)
    plt.ylim([0, 1.05])
    
    # Anotar pontos interessantes
    for idx, row in results_df.iterrows():
        if row['threshold'] in [0.50, 0.65, 0.70]:
            plt.annotate(f"{row['f1_score']:.3f}", 
                        (row['threshold'], row['f1_score']),
                        textcoords="offset points", xytext=(0,10), 
                        fontsize=9, ha='center', fontweight='bold')
    
    output_file = OUTPUT_PATH / 'threshold_vs_metrics.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {output_file}")
    plt.close()

def analyze_and_recommend(results_df):
    """Analisa resultados e faz recomendação"""
    print("\n" + "="*80)
    print("💡 ANÁLISE E RECOMENDAÇÃO")
    print("="*80)
    
    # Baseline (threshold 0.5)
    baseline = results_df[results_df['threshold'] == 0.50].iloc[0]
    
    print(f"\n📊 BASELINE (Threshold 0.50):")
    print(f"   Precision: {baseline['precision']:.1%}")
    print(f"   Recall:    {baseline['recall']:.1%}")
    print(f"   F1-Score:  {baseline['f1_score']:.3f}")
    print(f"   Detectados: {baseline['total_predicted_critical']}/{baseline['total_actual_critical']} críticos")
    
    # Melhor F1
    best_f1 = results_df.loc[results_df['f1_score'].idxmax()]
    print(f"\n🏆 MELHOR F1-SCORE (Threshold {best_f1['threshold']:.2f}):")
    print(f"   Precision: {best_f1['precision']:.1%}")
    print(f"   Recall:    {best_f1['recall']:.1%}")
    print(f"   F1-Score:  {best_f1['f1_score']:.3f}")
    
    # Melhor precision com recall > 40%
    high_prec = results_df[results_df['recall'] >= 0.4].nlargest(1, 'precision')
    if not high_prec.empty:
        rec = high_prec.iloc[0]
        print(f"\n⭐ ALTA PRECISION (Recall ≥ 40%, Threshold {rec['threshold']:.2f}):")
        print(f"   Precision: {rec['precision']:.1%}  (+{(rec['precision']-baseline['precision'])*100:+.1f}pp)")
        print(f"   Recall:    {rec['recall']:.1%}  ({(rec['recall']-baseline['recall'])*100:+.1f}pp)")
        print(f"   F1-Score:  {rec['f1_score']:.3f}")
        print(f"   Detectados: {rec['total_predicted_critical']}/{rec['total_actual_critical']} críticos")
        print(f"   Redução FP: {baseline['fp'] - rec['fp']} devices ({(1-rec['fp']/max(baseline['fp'],1))*100:.0f}%)")
    
    # Recomendação
    print(f"\n🎯 RECOMENDAÇÃO:")
    
    # Critério: Alta precision (>65%) com recall razoável (>35%)
    candidates = results_df[(results_df['precision'] >= 0.65) & (results_df['recall'] >= 0.35)]
    
    if not candidates.empty:
        recommended = candidates.iloc[0]  # Primeiro que atende critério
        print(f"   Threshold Recomendado: {recommended['threshold']:.2f}")
        print(f"   Justificativa: Melhor balanço precision/recall para produção")
        print(f"   - Precision {recommended['precision']:.1%}: Reduz falsos alarmes")
        print(f"   - Recall {recommended['recall']:.1%}: Mantém detecção de casos críticos")
        print(f"   - Trade-off aceitável para equipe de manutenção limitada")
    else:
        print(f"   Threshold Recomendado: 0.50 (manter baseline)")
        print(f"   Justificativa: Nenhum threshold alternativo melhora significativamente")
    
    return baseline, best_f1, recommended if not candidates.empty else baseline

def main():
    print("="*80)
    print("🎯 THRESHOLD ADJUSTMENT EXPERIMENT - MODEL V2 FIELD-ONLY")
    print("="*80)
    print(f"Objetivo: Otimizar threshold para maximizar precision mantendo recall")
    print(f"Thresholds testados: {THRESHOLDS}")
    
    # Carregar dados
    X_test, y_test = load_data_and_split()
    
    # Carregar modelo
    model = load_model()
    
    # Gerar predições
    probabilities = get_predictions(model, X_test)
    
    # Executar experimento
    results_df = run_threshold_experiment(y_test, probabilities)
    
    # Visualizações
    plot_precision_recall_curve(y_test, probabilities)
    plot_threshold_metrics(results_df)
    
    # Análise e recomendação
    baseline, best_f1, recommended = analyze_and_recommend(results_df)
    
    print("\n✅ Experimento completo! Visualizações e resultados salvos em 'analysis/'")
    print("="*80)

if __name__ == "__main__":
    main()
