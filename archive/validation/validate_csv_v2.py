import pandas as pd

# Carregar CSV
df = pd.read_csv('payloads_processed/payload_aws_BORA_transformed_v2.csv')

# Features obrigatórias do modelo v2
features_obrigatorias = [
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

# Validar
faltando = [f for f in features_obrigatorias if f not in df.columns]

print(f'✅ Features obrigatórias modelo v2: {len(features_obrigatorias)}')
print(f'✅ Features no CSV (sem device_id): {len([c for c in df.columns if c != "device_id"])}')
print(f'❌ Faltando: {faltando if faltando else "NENHUMA"}')
print(f'\n{"🎉 CSV PRONTO PARA UPLOAD!" if not faltando else "⚠️ CSV INCOMPLETO"}')
print(f'\n📊 Shape: {df.shape}')
print(f'📋 Colunas: {list(df.columns)}')
print(f'\n🔍 Preview (3 primeiras linhas):')
print(df.head(3))
