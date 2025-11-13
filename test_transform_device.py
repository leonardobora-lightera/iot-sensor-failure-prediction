"""
Script de teste para validar modificações em transform_aws_payload.py

Testa com device_861275072515287_2025-11-13.csv:
- Filtro MODE='FIELD' (esperado: remover 38 FACTORY entries)
- Feature days_since_last_message (esperado: ~12 dias)
- 30 features geradas
"""

import sys
sys.path.insert(0, 'scripts')

from transform_aws_payload import load_aws_payload, aggregate_by_device, validate_output
import pandas as pd

print("="*60)
print("🧪 TESTE: transform_aws_payload.py - Modificações FASE 1")
print("="*60)

# 1. Carregar CSV do device
csv_path = "device_861275072515287_2025-11-13.csv"
print(f"\n📂 Carregando {csv_path}...")

df_raw = load_aws_payload(csv_path)

print(f"\n✅ Carregado após filtro MODE='FIELD':")
print(f"   Total linhas: {len(df_raw)}")
print(f"   Esperado: ~639 (677 - 38 FACTORY)")

# 2. Agregar
print(f"\n📊 Agregando por device...")
df_agg = aggregate_by_device(df_raw)

print(f"\n✅ Agregado:")
print(f"   Devices: {len(df_agg)}")
print(f"   Colunas: {len(df_agg.columns)}")

# 3. Validar
validation = validate_output(df_agg)

# 4. Verificar days_since_last_message
if 'days_since_last_message' in df_agg.columns:
    days = df_agg['days_since_last_message'].iloc[0]
    print(f"\n✅ days_since_last_message: {days} dias")
    print(f"   Esperado: ~12 dias (última msg 31/10)")
else:
    print(f"\n❌ days_since_last_message NÃO encontrado!")

# 5. Verificar total_messages
if 'total_messages' in df_agg.columns:
    total = df_agg['total_messages'].iloc[0]
    print(f"\n✅ total_messages: {total}")
    print(f"   Esperado: ~639 (FIELD only)")
else:
    print(f"\n❌ total_messages NÃO encontrado!")

# 6. Mostrar todas as colunas
print(f"\n📋 Features geradas ({len(df_agg.columns)}):")
for i, col in enumerate(df_agg.columns, 1):
    print(f"   {i:2d}. {col}")

print("\n" + "="*60)
if validation['valid']:
    print("✅ TESTE PASSOU! Todas 30 features presentes.")
else:
    print(f"❌ TESTE FALHOU! {len(validation['missing'])} features faltando:")
    for feat in validation['missing']:
        print(f"   - {feat}")
print("="*60)
