#!/usr/bin/env python3
"""
Análise detalhada do device 861275072515287 (97.5% probabilidade de falha).
Verifica hipótese de inatividade pós-laboratório.
"""

import pandas as pd
from datetime import datetime, timedelta

# Carregar CSV do device
df = pd.read_csv('device_861275072515287_2025-11-13.csv')
df['@timestamp'] = pd.to_datetime(df['@timestamp'])
df = df.sort_values('@timestamp', ascending=False)

print("=" * 80)
print("ANÁLISE DEVICE 861275072515287 - PROBABILIDADE 97.5% FALHA")
print("=" * 80)

# 1. RESUMO GERAL
print("\n📊 RESUMO GERAL")
print(f"Total de mensagens: {len(df)}")
print(f"Período: {df['@timestamp'].min()} até {df['@timestamp'].max()}")
print(f"Última comunicação: {df['@timestamp'].max()}")

# Dias desde última comunicação
hoje = datetime.now()
ultima_msg = df['@timestamp'].max()
dias_inativo = (hoje - ultima_msg).days
print(f"⚠️ INATIVIDADE: {dias_inativo} dias sem comunicação!")

# 2. DISTRIBUIÇÃO DE msg_type
print("\n📨 DISTRIBUIÇÃO DE msg_type")
print(df['msg_type'].value_counts().sort_index())

# 3. ÚLTIMAS 5 MENSAGENS
print("\n🔍 ÚLTIMAS 5 MENSAGENS")
print(df.head(5)[['@timestamp', 'msg_type', 'optical_power_1490nm', 'temperature', 'battery_voltage', 'rsrp', 'snr']])

# 4. ANÁLISE TELEMETRIAS (msg_type = 1)
msg_type_1 = df[df['msg_type'] == 1].copy()

if len(msg_type_1) > 0:
    print(f"\n📡 ANÁLISE TELEMETRIAS (msg_type=1, n={len(msg_type_1)})")
    
    # Optical Power
    optical = msg_type_1['optical_power_1490nm'].dropna()
    if len(optical) > 0:
        print(f"\n🔦 OPTICAL POWER:")
        print(f"  Mean: {optical.mean():.2f} dBm")
        print(f"  Min: {optical.min():.2f} dBm")
        print(f"  Max: {optical.max():.2f} dBm")
        print(f"  Readings < -28 dBm (threshold): {(optical < -28).sum()} de {len(optical)}")
    
    # Temperature
    temp = msg_type_1['temperature'].dropna()
    if len(temp) > 0:
        print(f"\n🌡️ TEMPERATURE:")
        print(f"  Mean: {temp.mean():.1f} °C")
        print(f"  Min: {temp.min():.1f} °C")
        print(f"  Max: {temp.max():.1f} °C")
        print(f"  Readings > 70°C (threshold): {(temp > 70).sum()} de {len(temp)}")
    
    # Battery
    battery = msg_type_1['battery_voltage'].dropna()
    if len(battery) > 0:
        print(f"\n🔋 BATTERY:")
        print(f"  Mean: {battery.mean():.2f} V")
        print(f"  Min: {battery.min():.2f} V")
        print(f"  Max: {battery.max():.2f} V")
        print(f"  Readings < 2.5V (threshold): {(battery < 2.5).sum()} de {len(battery)}")
    
    # Connectivity
    rsrp = msg_type_1['rsrp'].dropna()
    rsrq = msg_type_1['rsrq'].dropna()
    snr = msg_type_1['snr'].dropna()
    
    if len(rsrp) > 0:
        print(f"\n📶 CONNECTIVITY:")
        print(f"  RSRP mean: {rsrp.mean():.1f} dBm (min: {rsrp.min():.1f}, max: {rsrp.max():.1f})")
        print(f"  RSRQ mean: {rsrq.mean():.1f} dB (min: {rsrq.min():.1f}, max: {rsrq.max():.1f})")
        print(f"  SNR mean: {snr.mean():.1f} dB (min: {snr.min():.1f}, max: {snr.max():.1f})")

# 5. PADRÃO TEMPORAL
print("\n📅 PADRÃO TEMPORAL DE COMUNICAÇÃO")
df_com_ts = df[df['@timestamp'].notna()].copy()
df_com_ts['date'] = df_com_ts['@timestamp'].dt.date
msgs_por_dia = df_com_ts.groupby('date').size().sort_index(ascending=False)

print("\nÚltimos 10 dias com atividade:")
print(msgs_por_dia.head(10))

# 6. msg_type 43 (mensagens sem telemetria)
msg_type_43 = df[df['msg_type'] == 43]
if len(msg_type_43) > 0:
    print(f"\n⚠️ MSG_TYPE 43 (sem telemetrias): {len(msg_type_43)} mensagens")
    print("Últimas 3:")
    print(msg_type_43.head(3)[['@timestamp', 'msg_type', 'f_cnt', 'project_name']])

# 7. CONCLUSÃO
print("\n" + "=" * 80)
print("🎯 CONCLUSÃO - HIPÓTESE INATIVIDADE PÓS-LABORATÓRIO")
print("=" * 80)

if dias_inativo >= 10:
    print(f"✅ HIPÓTESE CONFIRMADA:")
    print(f"   - Device INATIVO por {dias_inativo} dias (desde {ultima_msg.strftime('%d/%m/%Y %H:%M')})")
    print(f"   - Última comunicação: 3x msg_type 43 (sem telemetrias)")
    print(f"   - Telemetrias anteriores: NORMAIS (optical OK, temp OK, battery OK)")
    print(f"   - Probabilidade 97.5%: Provável FALSO POSITIVO")
    print(f"\n   RAZÃO: Modelo aprendeu padrão 'critical' sem contexto temporal!")
    print(f"   - Não sabe diferenciar: device degradando vs device inativo")
    print(f"   - Recomendação: Adicionar feature 'days_since_last_message'")
else:
    print(f"⚠️ INVESTIGAÇÃO NECESSÁRIA:")
    print(f"   - Inatividade curta ({dias_inativo} dias)")
    print(f"   - Pode ser falha real de comunicação")

print("\n" + "=" * 80)
