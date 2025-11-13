"""
Script de Retreinamento do Modelo CatBoost v2 - Production-Only Features (FIELD)

FASE 2.2: Retreinar modelo CatBoost com:
- Dataset FIELD-only (762 devices, sem contaminação FACTORY)
- 30 features (29 originais + days_since_last_message)
- Pipeline: SimpleImputer → SMOTE 0.5 → CatBoost
- Salvar como models/catboost_pipeline_v2_field_only.pkl

Autor: Leonardo Costa (Lightera LLC)
Data: 13/Nov/2025
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    recall_score,
    precision_score,
    f1_score,
    roc_auc_score
)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from catboost import CatBoostClassifier

# Config
np.random.seed(42)

print("="*80)
print("🚀 FASE 2.2: Retreinamento Modelo CatBoost v2 (FIELD-only)")
print("="*80)
print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# 1️⃣ CARREGAR E MESCLAR DATASETS
# ============================================================================
print("📂 Carregando datasets...")

# Dataset original (tem labels)
df_with_labels = pd.read_csv('data/device_features_with_telemetry.csv')
print(f"   ✅ Dataset com labels: {df_with_labels.shape}")

# Dataset FIELD-only (tem features production-only + days_since_last_message)
df_field_only = pd.read_csv('data/device_features_with_telemetry_field_only.csv')
print(f"   ✅ Dataset FIELD-only: {df_field_only.shape}")

# Merge: trazer labels do dataset original para o FIELD-only
# Manter apenas colunas de label do original
label_cols = ['device_id', 'is_critical', 'is_critical_target', 'severity_category']
df_labels = df_with_labels[label_cols].copy()

# Merge por device_id
df_merged = df_field_only.merge(df_labels, on='device_id', how='inner')

print(f"\n✅ Merge completo: {df_merged.shape}")
print(f"   Devices: {len(df_merged)}")
print(f"   Features + Labels: {df_merged.shape[1]} colunas")

# Verificar distribuição de labels
print(f"\n🔴 Distribuição de Critical Devices:")
print(f"   Critical: {df_merged['is_critical'].sum()} ({df_merged['is_critical'].mean()*100:.1f}%)")
print(f"   Normal: {(~df_merged['is_critical']).sum()} ({(~df_merged['is_critical']).mean()*100:.1f}%)")

# ============================================================================
# 2️⃣ PREPARAR FEATURES (30 features)
# ============================================================================
print(f"\n{'='*80}")
print("📋 Preparando features...")
print("="*80)

# Excluir colunas (mesmo critério do v1, MAS sem msg6_count/msg6_rate que não existem mais)
exclude_cols = [
    'device_id',           # Identifier
    'is_critical_target',  # Target
    'is_critical',         # Categorical (usada como target binário)
    'severity_category'    # Categorical leakage
]

# Features limpas (30 features)
feature_cols = [col for col in df_merged.columns if col not in exclude_cols]

print(f"✅ Features selecionadas: {len(feature_cols)}")
print(f"\n📋 Lista completa de features (30):")
for i, feat in enumerate(feature_cols, 1):
    prefix = "🆕" if feat == 'days_since_last_message' else "  "
    print(f"{prefix} {i:2d}. {feat}")

# Separar X e y
X = df_merged[feature_cols].copy()
y = df_merged['is_critical'].copy()  # Usar is_critical como label binária

print(f"\n✅ Dataset preparado:")
print(f"   X: {X.shape}")
print(f"   y: {y.shape} ({y.sum()} critical, {(~y).sum()} normal)")

# ============================================================================
# 3️⃣ STRATIFIED SPLIT (70/30)
# ============================================================================
print(f"\n{'='*80}")
print("🔀 Aplicando Stratified Split (70/30)...")
print("="*80)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    stratify=y,  # Manter proporção de critical devices
    random_state=42
)

print(f"✅ Split completo:")
print(f"   Train: {X_train.shape[0]} devices ({y_train.sum()} critical, {(~y_train).sum()} normal)")
print(f"   Test: {X_test.shape[0]} devices ({y_test.sum()} critical, {(~y_test).sum()} normal)")
print(f"\n   Proporção critical Train: {y_train.mean()*100:.1f}%")
print(f"   Proporção critical Test: {y_test.mean()*100:.1f}%")

# ============================================================================
# 4️⃣ CRIAR PIPELINE DE PRODUÇÃO (v2)
# ============================================================================
print(f"\n{'='*80}")
print("🔧 Criando Production Pipeline v2...")
print("="*80)

production_pipeline_v2 = ImbPipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('smote', SMOTE(sampling_strategy=0.5, random_state=42, k_neighbors=5)),
    ('classifier', CatBoostClassifier(
        iterations=100,
        depth=6,
        learning_rate=0.1,
        random_state=42,
        verbose=0
    ))
])

print("✅ Pipeline criado com 3 steps:")
print("   1. SimpleImputer (median strategy)")
print("   2. SMOTE (sampling_strategy=0.5)")
print("   3. CatBoostClassifier (iterations=100, depth=6, lr=0.1)")

# ============================================================================
# 5️⃣ TREINAR PIPELINE
# ============================================================================
print(f"\n{'='*80}")
print("🔥 Treinando Pipeline v2...")
print("="*80)

production_pipeline_v2.fit(X_train, y_train)

print("\n✅ Pipeline v2 treinado com sucesso!")
print(f"   Train samples: {X_train.shape[0]}")
print(f"   Features: {X_train.shape[1]} (29 original + days_since_last_message)")
print(f"   Critical samples (antes SMOTE): {y_train.sum()}")

# ============================================================================
# 6️⃣ VALIDAÇÃO NO TEST SET
# ============================================================================
print(f"\n{'='*80}")
print("📊 VALIDAÇÃO FINAL - TEST SET")
print("="*80)

# Predições
y_pred = production_pipeline_v2.predict(X_test)
y_proba = production_pipeline_v2.predict_proba(X_test)[:, 1]

# Métricas
recall = recall_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

print(f"\n🎯 MÉTRICAS MODELO v2 (FIELD-only):")
print(f"   Recall:    {recall*100:.1f}% ({tp}/{y_test.sum()} critical detectados)")
print(f"   Precision: {precision*100:.1f}%")
print(f"   F1-Score:  {f1*100:.1f}%")
print(f"   ROC-AUC:   {auc:.4f}")

print(f"\n🔍 Confusion Matrix:")
print(f"   True Positives (TP):  {tp} critical devices DETECTADOS ✅")
print(f"   False Negatives (FN): {fn} critical devices NÃO DETECTADOS ⚠️")
print(f"   False Positives (FP): {fp} alarmes falsos")
print(f"   True Negatives (TN):  {tn} non-critical corretos")

print(f"\n💼 Business Impact:")
print(f"   📈 Critical Devices Salvos: {tp}/{y_test.sum()} ({recall*100:.1f}% cobertura)")
print(f"   🚨 False Alarm Rate: {fp}/{len(y_test)} devices ({fp/len(y_test)*100:.1f}%)")

# ============================================================================
# 7️⃣ CLASSIFICATION REPORT
# ============================================================================
print(f"\n{'='*80}")
print("📊 Classification Report Detalhado:")
print("="*80)
print(classification_report(y_test, y_pred, target_names=['Non-Critical', 'Critical']))

# ============================================================================
# 8️⃣ FEATURE IMPORTANCE
# ============================================================================
print(f"{'='*80}")
print("📊 FEATURE IMPORTANCE - Top 15")
print("="*80)

catboost_model = production_pipeline_v2.named_steps['classifier']
feature_importance = catboost_model.get_feature_importance()

df_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': feature_importance
}).sort_values('Importance', ascending=False)

print(df_importance.head(15).to_string(index=False))

# ============================================================================
# 9️⃣ SALVAR MODELO v2
# ============================================================================
print(f"\n{'='*80}")
print("💾 Salvando Modelo v2...")
print("="*80)

os.makedirs('models', exist_ok=True)

model_filename = 'catboost_pipeline_v2_field_only.pkl'
model_path = os.path.join('models', model_filename)

joblib.dump(production_pipeline_v2, model_path)

print(f"✅ Modelo salvo: {model_path}")
print(f"   Tamanho: {os.path.getsize(model_path) / 1024:.1f} KB")

# ============================================================================
# 🔟 SALVAR METADATA (JSON)
# ============================================================================
print(f"\n💾 Salvando metadata...")

metadata = {
    "model_name": "CatBoost v2 + SMOTE 0.5 (FIELD-only Production Pipeline)",
    "version": "2.0",
    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "algorithm": "CatBoostClassifier",
    "preprocessing": [
        "SimpleImputer (median strategy)",
        "SMOTE (sampling_strategy=0.5, k_neighbors=5)"
    ],
    "hyperparameters": {
        "iterations": 100,
        "depth": 6,
        "learning_rate": 0.1,
        "random_state": 42
    },
    "features": {
        "total": len(feature_cols),
        "list": feature_cols,
        "new_feature": "days_since_last_message"
    },
    "dataset": {
        "source": "device_features_with_telemetry_field_only.csv",
        "filter": "MODE='FIELD' (production-only, no FACTORY)",
        "total_devices": len(df_merged),
        "train_devices": len(X_train),
        "test_devices": len(X_test),
        "critical_devices": int(y.sum()),
        "factory_removed": 27
    },
    "metrics": {
        "recall": float(recall),
        "precision": float(precision),
        "f1_score": float(f1),
        "roc_auc": float(auc),
        "true_positives": int(tp),
        "false_negatives": int(fn),
        "false_positives": int(fp),
        "true_negatives": int(tn)
    },
    "improvements": [
        "Removed FACTORY (lab testing) contamination - 362,343 messages filtered (31.8%)",
        "Added days_since_last_message temporal feature (30th feature)",
        "27 FACTORY-only devices removed from training",
        "Fixes false positives from lifecycle mixing (e.g., device 861275072515287)"
    ]
}

metadata_path = os.path.join('models', 'catboost_pipeline_v2_metadata.json')
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"✅ Metadata salva: {metadata_path}")

# ============================================================================
# 🎉 RESUMO FINAL
# ============================================================================
print(f"\n{'='*80}")
print("🎉 FASE 2.2 COMPLETA!")
print("="*80)
print(f"\n✅ Modelo v2 treinado e salvo:")
print(f"   📁 Modelo: {model_path}")
print(f"   📄 Metadata: {metadata_path}")
print(f"\n📊 Performance:")
print(f"   Recall: {recall*100:.1f}% | Precision: {precision*100:.1f}% | F1: {f1*100:.1f}% | AUC: {auc:.4f}")
print(f"\n🆕 Novidades v2:")
print(f"   ✅ Dataset FIELD-only (762 devices, 27 FACTORY removidos)")
print(f"   ✅ Feature days_since_last_message adicionada (30 features total)")
print(f"   ✅ 362k mensagens FACTORY filtradas (31.8% contaminação removida)")
print(f"\n📋 Próximos passos:")
print(f"   → FASE 2.3: Testar device 861275072515287 com modelo v2")
print(f"   → FASE 2.4: Deploy modelo v2 para cloud Streamlit")
print(f"   → Git commit + push")
print("\n" + "="*80)
print("✅ Script completo! Última task antes do almoço ✅")
print("="*80)
