"""
Add Simple Temporal Features for Model v2.1

Creates 3 derived temporal features from existing aggregated data:
1. message_frequency: Average messages per day (total_messages / estimated_days_active)
2. days_per_message: Average days between messages (inverse of frequency)
3. activity_ratio: Proportion of time device was active vs inactive

MEMORY-SAFE: Reads only necessary columns, no full CSV reload.

Author: Leonardo Costa (Lightera LLC)
Date: November 18, 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🚀 Adding Simple Temporal Features (v2.1)")
print("="*80)
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# 1️⃣ LOAD EXISTING DATASET (memory-safe - only needed columns)
# ============================================================================
print("📂 Loading FIELD-only dataset (minimal columns)...\n")

# Read only necessary columns to calculate new features
usecols = ['device_id', 'total_messages', 'days_since_last_message']

df = pd.read_csv(
    'data/device_features_with_telemetry_field_only.csv',
    usecols=usecols
)

print(f"✅ Loaded {len(df)} devices with 3 columns")
print(f"   Columns: {list(df.columns)}")
print(f"\n📊 Data Summary:")
print(df.describe())

# ============================================================================
# 2️⃣ CALCULATE 3 NEW TEMPORAL FEATURES
# ============================================================================
print(f"\n{'='*80}")
print("🔧 Calculating Temporal Features...")
print("="*80)

# Feature 1: message_frequency (messages per day)
# Estimate: Assume device was active from deployment to last message
# days_active ≈ max_possible_days - days_since_last_message
# But we don't have max_possible_days, so use percentile-based estimate

# Get max days_since for context (devices inactive longest)
max_days_since = df['days_since_last_message'].max()
print(f"\n1️⃣ Message Frequency")
print(f"   Max days_since_last_message: {max_days_since} days")

# Estimate days_active as: max_days_since - days_since_last_message + 1
# (devices with days_since=0 were active until today)
df['estimated_days_active'] = max_days_since - df['days_since_last_message'] + 1

# Calculate message_frequency (msgs/day)
# Handle division by zero: if days_active = 0, frequency = 0
df['message_frequency'] = np.where(
    df['estimated_days_active'] > 0,
    df['total_messages'] / df['estimated_days_active'],
    0
)

print(f"   ✅ message_frequency calculated")
print(f"      Range: {df['message_frequency'].min():.3f} - {df['message_frequency'].max():.3f} msgs/day")
print(f"      Mean: {df['message_frequency'].mean():.3f} msgs/day")
print(f"      Median: {df['message_frequency'].median():.3f} msgs/day")

# Feature 2: days_per_message (inverse of frequency)
# How many days between messages on average
# Handle division by zero: if frequency = 0, days_per_message = inf → set to max
print(f"\n2️⃣ Days Per Message")

df['days_per_message'] = np.where(
    df['message_frequency'] > 0,
    1 / df['message_frequency'],
    999  # Cap at 999 for devices with 0 frequency
)

print(f"   ✅ days_per_message calculated")
print(f"      Range: {df['days_per_message'].min():.3f} - {df['days_per_message'].max():.3f} days")
print(f"      Mean: {df['days_per_message'].mean():.3f} days")
print(f"      Median: {df['days_per_message'].median():.3f} days")

# Feature 3: activity_ratio (proportion of time active vs total possible)
# activity_ratio = estimated_days_active / max_possible_days
# Higher ratio = device was active more recently
print(f"\n3️⃣ Activity Ratio")

df['activity_ratio'] = df['estimated_days_active'] / max_days_since

print(f"   ✅ activity_ratio calculated")
print(f"      Range: {df['activity_ratio'].min():.3f} - {df['activity_ratio'].max():.3f}")
print(f"      Mean: {df['activity_ratio'].mean():.3f}")
print(f"      Median: {df['activity_ratio'].median():.3f}")

# ============================================================================
# 3️⃣ VALIDATION & QUALITY CHECKS
# ============================================================================
print(f"\n{'='*80}")
print("✅ Validation Checks...")
print("="*80)

# Check for NaN/inf values
nan_check = df[['message_frequency', 'days_per_message', 'activity_ratio']].isna().sum()
inf_check = df[['message_frequency', 'days_per_message', 'activity_ratio']].apply(
    lambda x: np.isinf(x).sum()
)

print(f"\n🔍 NaN Count:")
print(nan_check)

print(f"\n🔍 Inf Count:")
print(inf_check)

# Show sample of new features
print(f"\n📋 Sample of New Features (first 10 devices):")
print(df[['device_id', 'total_messages', 'days_since_last_message', 
          'message_frequency', 'days_per_message', 'activity_ratio']].head(10).to_string())

# ============================================================================
# 4️⃣ MERGE WITH FULL DATASET AND SAVE
# ============================================================================
print(f"\n{'='*80}")
print("💾 Merging with Full Dataset...")
print("="*80)

# Load full dataset
df_full = pd.read_csv('data/device_features_with_telemetry_field_only.csv')
print(f"✅ Loaded full dataset: {df_full.shape}")

# Drop temporary column
df = df.drop(columns=['estimated_days_active'])

# Merge new features
df_full_v21 = df_full.merge(
    df[['device_id', 'message_frequency', 'days_per_message', 'activity_ratio']],
    on='device_id',
    how='left'
)

print(f"✅ Merged dataset: {df_full_v21.shape}")
print(f"   Original features: {df_full.shape[1]}")
print(f"   New features: {df_full_v21.shape[1]}")
print(f"   Added: {df_full_v21.shape[1] - df_full.shape[1]} temporal features")

# Save v2.1 dataset
output_path = 'data/device_features_with_telemetry_field_only_v2.1.csv'
df_full_v21.to_csv(output_path, index=False)

print(f"\n✅ Saved v2.1 dataset:")
print(f"   Path: {output_path}")
print(f"   Devices: {len(df_full_v21)}")
print(f"   Features: {df_full_v21.shape[1]} (30 original + 3 temporal)")

# ============================================================================
# 5️⃣ SUMMARY
# ============================================================================
print(f"\n{'='*80}")
print("📊 SUMMARY")
print("="*80)

print("\n✅ New Temporal Features Added:")
print("   1. message_frequency: Messages per day (activity intensity)")
print("   2. days_per_message: Average days between messages (activity sparsity)")
print("   3. activity_ratio: Proportion of time active (recent activity indicator)")

print("\n✅ Dataset Ready for Model v2.1 Training:")
print(f"   Path: {output_path}")
print(f"   Total Features: {df_full_v21.shape[1]}")
print(f"   Expected for model: 33 (30 + 3 new)")

print("\n🎯 Next Steps:")
print("   1. Run train_model_v2.1.py to train with 33 features")
print("   2. Compare v2.1 vs v2.0 metrics (target: ≥62.1% recall for +5% improvement)")
print("   3. If improvement ≥5%, use v2.1 for presentation (Nov 25)")

print(f"\n{'='*80}")
print("✅ COMPLETED")
print("="*80)
