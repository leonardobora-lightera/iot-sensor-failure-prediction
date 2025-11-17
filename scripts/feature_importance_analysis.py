"""
Feature Importance Analysis - Model v2 FIELD-only
==================================================
Analisa quais features são mais importantes para as predições do modelo.
Valida se days_since_last_message contribui significativamente.
"""

import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configurações
MODEL_PATH = Path("models/catboost_pipeline_v2_field_only.pkl")
OUTPUT_PATH = Path("analysis")
OUTPUT_PATH.mkdir(exist_ok=True)

# Features na ordem correta (30 features) - do model_v2_metadata.json
FEATURES_ORDER = [
    'total_messages',
    'max_frame_count',
    'days_since_last_message',
    'optical_mean',
    'optical_std',
    'optical_min',
    'optical_max',
    'optical_readings',
    'optical_range',
    'optical_below_threshold',
    'temp_mean',
    'temp_std',
    'temp_min',
    'temp_max',
    'temp_range',
    'temp_above_threshold',
    'battery_mean',
    'battery_std',
    'battery_min',
    'battery_max',
    'battery_below_threshold',
    'snr_mean',
    'snr_std',
    'snr_min',
    'rsrp_mean',
    'rsrp_std',
    'rsrp_min',
    'rsrq_mean',
    'rsrq_std',
    'rsrq_min'
]

def load_model():
    """Carrega o modelo v2"""
    print(f"📂 Carregando modelo: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modelo carregado: {type(model).__name__}")
    return model

def extract_feature_importance(model):
    """Extrai feature importance do CatBoost"""
    print("\n🔍 Extraindo feature importance...")
    
    # CatBoost está dentro do pipeline
    # Pipeline tem steps: [('imputer', SimpleImputer), ('smote', SMOTE), ('classifier', CatBoostClassifier)]
    catboost_model = model.named_steps['classifier']
    
    # Obter feature importances
    importances = catboost_model.feature_importances_
    
    # Criar DataFrame
    feature_importance_df = pd.DataFrame({
        'feature': FEATURES_ORDER,
        'importance': importances
    })
    
    # Ordenar por importância
    feature_importance_df = feature_importance_df.sort_values('importance', ascending=False)
    feature_importance_df['rank'] = range(1, len(feature_importance_df) + 1)
    feature_importance_df['importance_pct'] = (feature_importance_df['importance'] / 
                                                feature_importance_df['importance'].sum() * 100)
    
    return feature_importance_df

def analyze_feature_categories(df):
    """Agrupa features por categoria e analisa contribuição"""
    print("\n📊 Analisando por categoria...")
    
    # Definir categorias
    categories = {
        'Messaging': ['total_messages', 'max_frame_count', 'days_since_last_message'],
        'Optical': [f for f in df['feature'] if f.startswith('optical_')],
        'Temperature': [f for f in df['feature'] if f.startswith('temp_')],
        'Battery': [f for f in df['feature'] if f.startswith('battery_')],
        'Signal_RSSI': [f for f in df['feature'] if f.startswith('rssi_')],
        'Signal_RSRP': [f for f in df['feature'] if f.startswith('rsrp_')],
        'Signal_RSRQ': [f for f in df['feature'] if f.startswith('rsrq_')],
        'Signal_SNR': [f for f in df['feature'] if f.startswith('snr_')]
    }
    
    category_importance = {}
    for category, features in categories.items():
        total_importance = df[df['feature'].isin(features)]['importance'].sum()
        category_importance[category] = total_importance
    
    category_df = pd.DataFrame({
        'category': list(category_importance.keys()),
        'importance': list(category_importance.values())
    }).sort_values('importance', ascending=False)
    
    category_df['importance_pct'] = (category_df['importance'] / 
                                      category_df['importance'].sum() * 100)
    
    return category_df

def plot_top_features(df, top_n=15):
    """Plota top N features"""
    print(f"\n📈 Criando visualização top {top_n} features...")
    
    top_features = df.head(top_n)
    
    plt.figure(figsize=(12, 8))
    bars = plt.barh(range(len(top_features)), top_features['importance'])
    
    # Colorir days_since_last_message diferente
    for i, feature in enumerate(top_features['feature']):
        if feature == 'days_since_last_message':
            bars[i].set_color('#FF6B6B')  # Vermelho para destacar
        else:
            bars[i].set_color('#4ECDC4')  # Azul-verde
    
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Feature Importance', fontsize=12, fontweight='bold')
    plt.ylabel('Features', fontsize=12, fontweight='bold')
    plt.title(f'Top {top_n} Most Important Features - Model v2 FIELD-only', 
              fontsize=14, fontweight='bold', pad=20)
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Adicionar valores nas barras
    for i, (importance, pct) in enumerate(zip(top_features['importance'], 
                                               top_features['importance_pct'])):
        plt.text(importance, i, f'  {pct:.1f}%', 
                va='center', fontsize=9)
    
    plt.tight_layout()
    output_file = OUTPUT_PATH / 'feature_importance_top15.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {output_file}")
    plt.close()

def plot_category_importance(category_df):
    """Plota importância por categoria"""
    print("\n📈 Criando visualização por categoria...")
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(range(len(category_df)), category_df['importance'])
    
    # Colorir Messaging diferente (contém days_since_last_message)
    for i, category in enumerate(category_df['category']):
        if category == 'Messaging':
            bars[i].set_color('#FF6B6B')  # Vermelho
        else:
            bars[i].set_color('#95E1D3')  # Verde-água
    
    plt.yticks(range(len(category_df)), category_df['category'])
    plt.xlabel('Total Importance', fontsize=12, fontweight='bold')
    plt.ylabel('Feature Category', fontsize=12, fontweight='bold')
    plt.title('Feature Importance by Category - Model v2 FIELD-only', 
              fontsize=14, fontweight='bold', pad=20)
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Adicionar percentuais
    for i, (importance, pct) in enumerate(zip(category_df['importance'], 
                                               category_df['importance_pct'])):
        plt.text(importance, i, f'  {pct:.1f}%', 
                va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    output_file = OUTPUT_PATH / 'feature_importance_by_category.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {output_file}")
    plt.close()

def analyze_days_since_contribution(df):
    """Análise específica da feature days_since_last_message"""
    print("\n🎯 Análise: days_since_last_message")
    print("=" * 60)
    
    days_since = df[df['feature'] == 'days_since_last_message'].iloc[0]
    
    print(f"Rank: #{days_since['rank']}/{len(df)}")
    print(f"Importance: {days_since['importance']:.4f}")
    print(f"Contribution: {days_since['importance_pct']:.2f}% do total")
    
    # Comparar com outras features de messaging
    messaging_features = df[df['feature'].isin(['total_messages', 'max_frame_count', 
                                                  'days_since_last_message'])]
    print(f"\n📨 Comparação com outras features de Messaging:")
    for _, row in messaging_features.iterrows():
        print(f"  {row['feature']:30s} - Rank #{row['rank']:2d} - {row['importance_pct']:5.2f}%")
    
    # Interpretação
    if days_since['rank'] <= 5:
        interpretation = "🔥 TOP 5 - Feature CRÍTICA para o modelo!"
    elif days_since['rank'] <= 10:
        interpretation = "✅ TOP 10 - Feature IMPORTANTE, contribui significativamente"
    elif days_since['rank'] <= 15:
        interpretation = "⚠️ TOP 15 - Feature MODERADA, contribui mas não é crítica"
    else:
        interpretation = "❌ Fora do TOP 15 - Feature tem BAIXA contribuição"
    
    print(f"\n💡 Interpretação: {interpretation}")
    
    return days_since

def main():
    print("=" * 80)
    print("🔍 FEATURE IMPORTANCE ANALYSIS - MODEL V2 FIELD-ONLY")
    print("=" * 80)
    
    # Carregar modelo
    model = load_model()
    
    # Extrair importâncias
    feature_importance_df = extract_feature_importance(model)
    
    # Salvar CSV completo
    csv_file = OUTPUT_PATH / 'feature_importance_complete.csv'
    feature_importance_df.to_csv(csv_file, index=False)
    print(f"\n✅ Feature importance completa salva: {csv_file}")
    
    # Mostrar top 15
    print("\n📊 TOP 15 FEATURES:")
    print("=" * 80)
    top_15 = feature_importance_df.head(15)
    for _, row in top_15.iterrows():
        print(f"#{row['rank']:2d}  {row['feature']:30s}  {row['importance']:8.4f}  ({row['importance_pct']:5.2f}%)")
    
    # Análise por categoria
    category_df = analyze_feature_categories(feature_importance_df)
    
    print("\n📊 IMPORTÂNCIA POR CATEGORIA:")
    print("=" * 80)
    for _, row in category_df.iterrows():
        print(f"{row['category']:15s}  {row['importance']:8.4f}  ({row['importance_pct']:5.2f}%)")
    
    # Análise days_since_last_message
    days_since_info = analyze_days_since_contribution(feature_importance_df)
    
    # Visualizações
    plot_top_features(feature_importance_df, top_n=15)
    plot_category_importance(category_df)
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📋 SUMÁRIO DA ANÁLISE")
    print("=" * 80)
    print(f"Total de features: {len(feature_importance_df)}")
    print(f"Feature mais importante: {feature_importance_df.iloc[0]['feature']} ({feature_importance_df.iloc[0]['importance_pct']:.2f}%)")
    print(f"Categoria mais importante: {category_df.iloc[0]['category']} ({category_df.iloc[0]['importance_pct']:.2f}%)")
    print(f"\ndays_since_last_message:")
    print(f"  - Rank: #{days_since_info['rank']}/{len(feature_importance_df)}")
    print(f"  - Contribuição: {days_since_info['importance_pct']:.2f}%")
    
    # Validação da hipótese FASE 2
    print("\n🎯 VALIDAÇÃO DA HIPÓTESE FASE 2:")
    if days_since_info['rank'] <= 15:
        print("✅ days_since_last_message É RELEVANTE para o modelo")
        print("✅ Feature temporal foi uma ADIÇÃO VÁLIDA na FASE 2")
    else:
        print("❌ days_since_last_message tem BAIXA importância")
        print("⚠️ Feature temporal pode não ser tão útil quanto esperado")
    
    print("\n✅ Análise completa! Visualizações salvas em 'analysis/'")

if __name__ == "__main__":
    main()
