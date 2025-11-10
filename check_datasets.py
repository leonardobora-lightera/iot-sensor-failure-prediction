import pandas as pd

# Load temporal split datasets
train = pd.read_csv('data/device_features_train_with_telemetry.csv')
test = pd.read_csv('data/device_features_test_with_telemetry.csv')

print("="*70)
print("TEMPORAL SPLIT DATASETS (Original from Notebook 02)")
print("="*70)
print(f"TRAIN: {len(train):,} rows, {train['device_id'].nunique():,} unique devices")
print(f"TEST: {len(test):,} rows, {test['device_id'].nunique():,} unique devices")
print(f"\nColumns ({len(train.columns)}): {list(train.columns[:10])}")
print(f"\nTrain critical devices: {train['is_critical_target'].sum() if 'is_critical_target' in train.columns else 'N/A'}")
print(f"Test critical devices: {test['is_critical_target'].sum() if 'is_critical_target' in test.columns else 'N/A'}")

# Check if datasets have time-series structure (multiple rows per device)
print(f"\nTrain: Max rows per device = {train.groupby('device_id').size().max()}")
print(f"Test: Max rows per device = {test.groupby('device_id').size().max()}")

print("\n" + "="*70)
print("AGGREGATED DATASET")
print("="*70)
complete = pd.read_csv('data/device_features_with_telemetry.csv')
print(f"COMPLETE: {len(complete):,} rows, {complete['device_id'].nunique():,} unique devices")
print(f"Critical devices: {complete['is_critical_target'].sum() if 'is_critical_target' in complete.columns else 'N/A'}")
