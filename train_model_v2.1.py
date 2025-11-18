"""
Training Script for Model v2.1 - With Simple Temporal Features

Trains CatBoost pipeline with:
- Dataset FIELD-only v2.1 (762 devices, 34 features)
- 33 features for model (30 original + 3 new temporal)
- New features: message_frequency, days_per_message, activity_ratio
- Pipeline: SimpleImputer → SMOTE 0.5 → CatBoost
- Saves as models/catboost_pipeline_v2.1.pkl

Target: ≥ 62.1% recall (+5% improvement over v2.0 57.1%)

Author: Leonardo Costa (Lightera LLC)
Date: November 18, 2025
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
print("🚀 Training Model v2.1 with Temporal Features")
print("="*80)
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# 1️⃣ LOAD DATASETS
# ============================================================================
print("📂 Loading datasets...")

# Load labels from original dataset
df_with_labels = pd.read_csv('data/device_features_with_telemetry.csv')
print(f"   ✅ Dataset with labels: {df_with_labels.shape}")

# Load v2.1 dataset (FIELD-only + 3 temporal features)
df_v21 = pd.read_csv('data/device_features_with_telemetry_field_only_v2.1.csv')
print(f"   ✅ Dataset v2.1: {df_v21.shape}")

# Merge labels
label_cols = ['device_id', 'is_critical', 'is_critical_target', 'severity_category']
df_labels = df_with_labels[label_cols].copy()

df_merged = df_v21.merge(df_labels, on='device_id', how='inner')

print(f"\n✅ Merge complete: {df_merged.shape}")
print(f"   Devices: {len(df_merged)}")
print(f"   Features + Labels: {df_merged.shape[1]} columns")

# Verify label distribution
print(f"\n🔴 Critical Device Distribution:")
print(f"   Critical: {df_merged['is_critical'].sum()} ({df_merged['is_critical'].mean()*100:.1f}%)")
print(f"   Normal: {(~df_merged['is_critical']).sum()} ({(~df_merged['is_critical']).mean()*100:.1f}%)")

# ============================================================================
# 2️⃣ PREPARE FEATURES (33 features)
# ============================================================================
print(f"\n{'='*80}")
print("📋 Preparing features...")
print("="*80)

# Exclude columns
exclude_cols = [
    'device_id',           # Identifier
    'is_critical_target',  # Target
    'is_critical',         # Target (binary)
    'severity_category'    # Categorical leakage
]

# Feature columns (33 features: 30 original + 3 new temporal)
feature_cols = [col for col in df_merged.columns if col not in exclude_cols]

print(f"✅ Features selected: {len(feature_cols)}")
print(f"\n📋 Complete feature list (33):")

# Group features for clarity
messaging_features = [f for f in feature_cols if f in ['total_messages', 'max_frame_count', 'days_since_last_message', 'message_frequency', 'days_per_message', 'activity_ratio']]
optical_features = [f for f in feature_cols if 'optical' in f]
battery_features = [f for f in feature_cols if 'battery' in f]
temp_features = [f for f in feature_cols if 'temp' in f]
signal_features = [f for f in feature_cols if any(s in f for s in ['snr', 'rsrp', 'rsrq'])]

print(f"\n🆕 Messaging & Temporal ({len(messaging_features)}):")
for feat in messaging_features:
    marker = "⭐" if feat in ['message_frequency', 'days_per_message', 'activity_ratio'] else "  "
    print(f"   {marker} {feat}")

print(f"\n   Optical ({len(optical_features)}): {', '.join(optical_features[:3])}... ({len(optical_features)} total)")
print(f"   Battery ({len(battery_features)}): {', '.join(battery_features[:3])}... ({len(battery_features)} total)")
print(f"   Temperature ({len(temp_features)}): {', '.join(temp_features[:3])}... ({len(temp_features)} total)")
print(f"   Signal ({len(signal_features)}): {', '.join(signal_features[:3])}... ({len(signal_features)} total)")

# Separate X and y
X = df_merged[feature_cols].copy()
y = df_merged['is_critical'].copy()

print(f"\n✅ Dataset prepared:")
print(f"   X: {X.shape}")
print(f"   y: {y.shape} ({y.sum()} critical, {(~y).sum()} normal)")

# ============================================================================
# 3️⃣ STRATIFIED SPLIT (70/30)
# ============================================================================
print(f"\n{'='*80}")
print("🔀 Applying Stratified Split (70/30)...")
print("="*80)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    stratify=y,
    random_state=42
)

print(f"✅ Split complete:")
print(f"   Train: {X_train.shape[0]} devices ({y_train.sum()} critical, {(~y_train).sum()} normal)")
print(f"   Test: {X_test.shape[0]} devices ({y_test.sum()} critical, {(~y_test).sum()} normal)")
print(f"\n   Critical proportion Train: {y_train.mean()*100:.1f}%")
print(f"   Critical proportion Test: {y_test.mean()*100:.1f}%")

# ============================================================================
# 4️⃣ CREATE PIPELINE v2.1
# ============================================================================
print(f"\n{'='*80}")
print("🔧 Creating Production Pipeline v2.1...")
print("="*80)

pipeline_v21 = ImbPipeline([
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

print("✅ Pipeline created with 3 steps:")
print("   1. SimpleImputer (median strategy)")
print("   2. SMOTE (sampling_strategy=0.5)")
print("   3. CatBoostClassifier (iterations=100, depth=6, lr=0.1)")

# ============================================================================
# 5️⃣ TRAIN PIPELINE
# ============================================================================
print(f"\n{'='*80}")
print("🔥 Training Pipeline v2.1...")
print("="*80)

pipeline_v21.fit(X_train, y_train)

print("\n✅ Pipeline v2.1 trained successfully!")
print(f"   Train samples: {X_train.shape[0]}")
print(f"   Features: {X_train.shape[1]} (30 original + 3 temporal)")
print(f"   Critical samples (before SMOTE): {y_train.sum()}")

# ============================================================================
# 6️⃣ VALIDATION ON TEST SET
# ============================================================================
print(f"\n{'='*80}")
print("📊 FINAL VALIDATION - TEST SET")
print("="*80)

# Predictions
y_pred = pipeline_v21.predict(X_test)
y_proba = pipeline_v21.predict_proba(X_test)[:, 1]

# Metrics
recall = recall_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

print(f"\n🎯 MODEL v2.1 METRICS:")
print(f"   Recall:    {recall*100:.1f}% ({tp}/{y_test.sum()} critical detected)")
print(f"   Precision: {precision*100:.1f}%")
print(f"   F1-Score:  {f1*100:.1f}%")
print(f"   ROC-AUC:   {auc:.4f}")

print(f"\n🔍 Confusion Matrix:")
print(f"   True Positives (TP):  {tp} critical devices DETECTED ✅")
print(f"   False Negatives (FN): {fn} critical devices NOT DETECTED ⚠️")
print(f"   False Positives (FP): {fp} false alarms")
print(f"   True Negatives (TN):  {tn} non-critical correct")

# ============================================================================
# 7️⃣ COMPARE WITH v2.0
# ============================================================================
print(f"\n{'='*80}")
print("📊 COMPARISON: v2.0 vs v2.1")
print("="*80)

# v2.0 metrics (from metadata)
v20_recall = 0.571
v20_precision = 0.571
v20_auc = 0.9186

improvement_recall = ((recall - v20_recall) / v20_recall) * 100
improvement_precision = ((precision - v20_precision) / v20_precision) * 100
improvement_auc = ((auc - v20_auc) / v20_auc) * 100

print(f"\n📊 Recall:")
print(f"   v2.0: {v20_recall*100:.1f}%")
print(f"   v2.1: {recall*100:.1f}%")
print(f"   Change: {improvement_recall:+.1f}%")

print(f"\n📊 Precision:")
print(f"   v2.0: {v20_precision*100:.1f}%")
print(f"   v2.1: {precision*100:.1f}%")
print(f"   Change: {improvement_precision:+.1f}%")

print(f"\n📊 ROC-AUC:")
print(f"   v2.0: {v20_auc:.4f}")
print(f"   v2.1: {auc:.4f}")
print(f"   Change: {improvement_auc:+.1f}%")

# Decision criterion
use_v21 = improvement_recall >= 5.0  # Target: ≥5% improvement

print(f"\n{'='*80}")
print(f"🎯 DECISION: {'USE v2.1 ✅' if use_v21 else 'KEEP v2.0 ❌'}")
print("="*80)

if use_v21:
    print(f"\n✅ v2.1 shows ≥5% recall improvement - RECOMMENDED FOR PRESENTATION")
    print(f"   Recall improvement: {improvement_recall:+.1f}%")
    print(f"   New features: message_frequency, days_per_message, activity_ratio")
else:
    print(f"\n❌ v2.1 improvement < 5% - KEEP v2.0 BASELINE FOR PRESENTATION")
    print(f"   Recall improvement: {improvement_recall:+.1f}% (target: ≥5%)")
    print(f"   Recommendation: Use honest v2.0 57.1% baseline")

# ============================================================================
# 8️⃣ FEATURE IMPORTANCE
# ============================================================================
print(f"\n{'='*80}")
print("📊 FEATURE IMPORTANCE - Top 15")
print("="*80)

catboost_model = pipeline_v21.named_steps['classifier']
feature_importance = catboost_model.get_feature_importance()

df_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': feature_importance
}).sort_values('Importance', ascending=False)

print(df_importance.head(15).to_string(index=False))

# Check ranking of new temporal features
new_features_ranking = df_importance[df_importance['Feature'].isin(['message_frequency', 'days_per_message', 'activity_ratio'])]
print(f"\n🆕 New Temporal Features Ranking:")
print(new_features_ranking.to_string(index=False))

# ============================================================================
# 9️⃣ SAVE MODEL v2.1 (if improvement ≥5%)
# ============================================================================
if use_v21:
    print(f"\n{'='*80}")
    print("💾 Saving Model v2.1...")
    print("="*80)

    os.makedirs('models', exist_ok=True)

    model_filename = 'catboost_pipeline_v2.1.pkl'
    model_path = os.path.join('models', model_filename)

    joblib.dump(pipeline_v21, model_path)

    print(f"✅ Model saved: {model_path}")
    print(f"   Size: {os.path.getsize(model_path) / 1024:.1f} KB")

    # Save metadata
    metadata = {
        "model_name": "CatBoost v2.1 + SMOTE 0.5 + Temporal Features (FIELD-only)",
        "version": "2.1",
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
            "new_features": ["message_frequency", "days_per_message", "activity_ratio"],
            "original_v2_features": 30,
            "temporal_features": 3
        },
        "dataset": {
            "source": "device_features_with_telemetry_field_only_v2.1.csv",
            "filter": "MODE='FIELD' (production-only)",
            "total_devices": len(df_merged),
            "train_devices": len(X_train),
            "test_devices": len(X_test),
            "critical_devices": int(y.sum())
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
        "improvements_vs_v2.0": {
            "recall_change_percent": float(improvement_recall),
            "precision_change_percent": float(improvement_precision),
            "auc_change_percent": float(improvement_auc)
        }
    }

    metadata_path = os.path.join('models', 'catboost_pipeline_v2.1_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Metadata saved: {metadata_path}")

# ============================================================================
# 🎉 FINAL SUMMARY
# ============================================================================
print(f"\n{'='*80}")
print("🎉 TRAINING COMPLETE!")
print("="*80)

print(f"\n📊 Model v2.1 Performance:")
print(f"   Recall: {recall*100:.1f}% | Precision: {precision*100:.1f}% | F1: {f1*100:.1f}% | AUC: {auc:.4f}")

print(f"\n🆕 New Temporal Features:")
print(f"   1. message_frequency (msgs/day)")
print(f"   2. days_per_message (avg spacing)")
print(f"   3. activity_ratio (recent activity)")

print(f"\n📋 Recommendation:")
if use_v21:
    print(f"   ✅ USE v2.1 for presentation (Nov 25)")
    print(f"   ✅ Update README with v2.1 metrics")
    print(f"   ✅ Highlight {improvement_recall:+.1f}% recall improvement")
else:
    print(f"   ❌ KEEP v2.0 for presentation (Nov 25)")
    print(f"   ❌ Improvement insufficient ({improvement_recall:+.1f}% < 5%)")
    print(f"   ❌ Use honest v2.0 57.1% baseline")

print(f"\n{'='*80}")
print("✅ Script complete!")
print("="*80)
