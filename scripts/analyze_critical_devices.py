"""
Análise dos 3 Devices Críticos Detectados - Modelo v2
=====================================================

Objetivo: Validar se os 3 devices flagados como críticos pelo modelo v2
são realmente problemáticos ou falsos positivos.

Devices analisados:
- 866207059671895 (99.7% probabilidade - HIGH)
- 861275072514504 (82.1% probabilidade - HIGH)  
- 861275072341072 (59.8% probabilidade - MEDIUM)

Dataset: payload_aws_BORA_transformed_v2.csv (640 devices, 31 colunas)
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# Configuração
PROJECT_ROOT = Path(__file__).parent.parent
CSV_PATH = PROJECT_ROOT / "payloads_processed" / "payload_aws_BORA_transformed_v2.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "catboost_pipeline_v2_field_only.pkl"

# Devices críticos detectados no batch upload
CRITICAL_DEVICES = {
    '866207059671895': {'prob': 0.997, 'risk': 'HIGH'},
    '861275072514504': {'prob': 0.821, 'risk': 'HIGH'},
    '861275072341072': {'prob': 0.598, 'risk': 'MEDIUM'}
}

# 30 features do modelo v2 (ordem importa!)
FEATURES_ORDER = [
    'total_messages', 'max_frame_count', 'days_since_last_message',  # Messaging (3)
    'optical_mean', 'optical_std', 'optical_min', 'optical_max', 'optical_readings', 
    'optical_below_threshold', 'optical_range',  # Optical (7)
    'temp_mean', 'temp_std', 'temp_min', 'temp_max', 'temp_above_threshold', 'temp_range',  # Temperature (6)
    'battery_mean', 'battery_std', 'battery_min', 'battery_max', 'battery_below_threshold',  # Battery (5)
    'snr_mean', 'snr_std', 'snr_min',  # SNR (3)
    'rsrp_mean', 'rsrp_std', 'rsrp_min',  # RSRP (3)
    'rsrq_mean', 'rsrq_std', 'rsrq_min'  # RSRQ (3)
]


def load_data():
    """Carrega CSV com 640 devices."""
    print(f"📂 Carregando {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"✅ {len(df)} devices carregados, {len(df.columns)} colunas")
    return df


def analyze_device_features(df, device_id):
    """Analisa features de um device específico vs baseline do dataset."""
    
    # Filtrar device
    device_row = df[df['device_id'] == int(device_id)]
    if len(device_row) == 0:
        print(f"⚠️ Device {device_id} NÃO encontrado no CSV!")
        return None
    
    device_row = device_row.iloc[0]
    
    # Estatísticas do dataset (baseline)
    baseline_stats = df[FEATURES_ORDER].describe()
    
    print(f"\n{'='*80}")
    print(f"📊 ANÁLISE: Device {device_id}")
    print(f"   Probabilidade: {CRITICAL_DEVICES[device_id]['prob']:.1%}")
    print(f"   Risco: {CRITICAL_DEVICES[device_id]['risk']}")
    print(f"{'='*80}\n")
    
    # Comparar features
    deviations = []
    
    for feature in FEATURES_ORDER:
        device_value = device_row[feature]
        mean = baseline_stats.loc['mean', feature]
        std = baseline_stats.loc['std', feature]
        p25 = baseline_stats.loc['25%', feature]
        p75 = baseline_stats.loc['75%', feature]
        
        # Z-score (quantos desvios padrão da média)
        z_score = (device_value - mean) / std if std > 0 else 0
        
        # Percentil aproximado
        if device_value < p25:
            percentil = "< P25 (quartil inferior)"
        elif device_value > p75:
            percentil = "> P75 (quartil superior)"
        else:
            percentil = "P25-P75 (normal)"
        
        # Identificar outliers (|z| > 2)
        is_outlier = abs(z_score) > 2
        
        if is_outlier:
            deviations.append({
                'feature': feature,
                'value': device_value,
                'mean': mean,
                'std': std,
                'z_score': z_score,
                'percentil': percentil
            })
    
    # Mostrar features NORMAIS
    print("✅ FEATURES NORMAIS (dentro de 2σ):")
    normal_features = [f for f in FEATURES_ORDER if f not in [d['feature'] for d in deviations]]
    for feature in normal_features[:5]:  # Mostrar só primeiras 5
        print(f"   {feature}: {device_row[feature]:.2f}")
    if len(normal_features) > 5:
        print(f"   ... e mais {len(normal_features)-5} features normais")
    
    # Mostrar OUTLIERS
    if deviations:
        print(f"\n⚠️ FEATURES ANORMAIS ({len(deviations)} outliers > 2σ):")
        for dev in sorted(deviations, key=lambda x: abs(x['z_score']), reverse=True):
            direction = "↑ ALTO" if dev['z_score'] > 0 else "↓ BAIXO"
            print(f"   {dev['feature']:30s} = {dev['value']:8.2f}  (μ={dev['mean']:6.2f}, z={dev['z_score']:+5.2f}σ)  {direction}  [{dev['percentil']}]")
    else:
        print("\n✅ Nenhum outlier detectado (todas features dentro de 2σ)")
    
    return {
        'device_id': device_id,
        'total_features': len(FEATURES_ORDER),
        'normal_features': len(normal_features),
        'outliers': deviations,
        'outlier_count': len(deviations)
    }


def predict_device(model, df, device_id):
    """Faz predição com modelo v2 para validar probabilidade."""
    device_row = df[df['device_id'] == int(device_id)]
    if len(device_row) == 0:
        return None
    
    # Extrair features na ordem correta
    X = device_row[FEATURES_ORDER].values
    
    # Predição
    prob = model.predict_proba(X)[0, 1]  # Probabilidade de classe 1 (crítico)
    pred = model.predict(X)[0]  # Classe predita (0 ou 1)
    
    return {
        'predicted_prob': prob,
        'predicted_class': pred,
        'risk_level': 'CRITICAL' if prob >= 0.5 else 'NORMAL'
    }


def main():
    """Execução principal."""
    
    print("\n" + "="*80)
    print("🔍 ANÁLISE DE DEVICES CRÍTICOS - MODELO v2 FIELD-only")
    print("="*80 + "\n")
    
    # 1. Carregar dados
    df = load_data()
    
    # 2. Carregar modelo
    print(f"\n🤖 Carregando modelo {MODEL_PATH}...")
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Modelo v2 carregado com sucesso")
    except Exception as e:
        print(f"⚠️ Erro ao carregar modelo: {e}")
        print("   Análise continuará sem predições do modelo")
        model = None
    
    # 3. Analisar cada device crítico
    results = []
    
    for device_id in CRITICAL_DEVICES.keys():
        analysis = analyze_device_features(df, device_id)
        
        if analysis and model:
            # Validar predição
            prediction = predict_device(model, df, device_id)
            if prediction:
                print(f"\n🎯 PREDIÇÃO DO MODELO:")
                print(f"   Probabilidade: {prediction['predicted_prob']:.1%}")
                print(f"   Classe: {prediction['predicted_class']} ({prediction['risk_level']})")
                analysis['prediction'] = prediction
        
        if analysis:
            results.append(analysis)
    
    # 4. Sumário final
    print("\n" + "="*80)
    print("📋 SUMÁRIO DA ANÁLISE")
    print("="*80 + "\n")
    
    for result in results:
        device_id = result['device_id']
        outlier_pct = (result['outlier_count'] / result['total_features']) * 100
        print(f"Device {device_id}:")
        print(f"  - Probabilidade modelo: {CRITICAL_DEVICES[device_id]['prob']:.1%}")
        print(f"  - Features outliers: {result['outlier_count']}/{result['total_features']} ({outlier_pct:.1f}%)")
        print(f"  - Features normais: {result['normal_features']}/{result['total_features']}")
        
        if result['outliers']:
            top_outlier = max(result['outliers'], key=lambda x: abs(x['z_score']))
            print(f"  - Maior desvio: {top_outlier['feature']} (z={top_outlier['z_score']:+.2f}σ)")
        print()
    
    # 5. Interpretação
    print("="*80)
    print("💡 INTERPRETAÇÃO")
    print("="*80 + "\n")
    
    avg_outliers = np.mean([r['outlier_count'] for r in results])
    
    if avg_outliers >= 5:
        print("✅ Devices críticos apresentam MÚLTIPLOS outliers (média {:.1f} features anormais)".format(avg_outliers))
        print("   → Modelo está capturando padrões REAIS de degradação")
        print("   → Detecções são LEGÍTIMAS (não são falsos positivos)")
    elif avg_outliers >= 2:
        print("⚠️ Devices críticos apresentam ALGUNS outliers (média {:.1f} features anormais)".format(avg_outliers))
        print("   → Modelo pode estar capturando sinais fracos")
        print("   → Recomenda-se validação com dados históricos de manutenção")
    else:
        print("❌ Devices críticos têm POUCAS anomalias (média {:.1f} features anormais)".format(avg_outliers))
        print("   → Possíveis FALSOS POSITIVOS")
        print("   → Modelo pode estar superajustado ou threshold muito sensível")
    
    print("\n📝 Próximos passos:")
    print("   1. Comparar com logs de manutenção do STC (ground truth)")
    print("   2. Analisar feature importance do modelo (quais features pesam mais)")
    print("   3. Se falsos positivos confirmados → ajustar threshold ou retreinar")
    print()


if __name__ == "__main__":
    main()
