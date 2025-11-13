"""
Script para transformar payloads AWS (formato RAW) para formato esperado pelo modelo.

PROBLEMA:
- AWS payloads contêm dados MESSAGE-LEVEL (1 row = 1 message/timestamp)
- Modelo espera dados DEVICE-LEVEL agregados (1 row = 1 device com estatísticas)

SOLUÇÃO:
- GroupBy device_id
- Calcular agregações: mean, std, min, max, count
- Aplicar thresholds (optical -28dBm, temp 70°C, battery 2.5V)
- Gerar 29 features esperadas

Baseado em: notebooks/old/02_correlacao_telemetrias_msg6.ipynb
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('transform_aws_payload.log')
    ]
)
logger = logging.getLogger(__name__)

# THRESHOLDS (baseado em docs/BIAS_MITIGATION_CHECKLIST.md)
OPTICAL_THRESHOLD = -28  # dBm
TEMP_THRESHOLD = 70      # °C
BATTERY_THRESHOLD = 2.5  # V

# MAPEAMENTO DE COLUNAS AWS → Features esperadas
AWS_COLUMN_MAPPING = {
    'optical': 'eyon_metadata.decoded_payload.optical_power_1490nm',
    'temp': 'eyon_metadata.decoded_payload.temperature',
    'battery': 'eyon_metadata.decoded_payload.battery',
    'snr': 'eyon_metadata.decoded_payload.snr',
    'rsrp': 'eyon_metadata.decoded_payload.rsrp',
    'rsrq': 'eyon_metadata.decoded_payload.rsrq',
    'frame_count': 'f_cnt',  # ou f_count dependendo do arquivo
    'device_id': 'device_id'  # ou sn_fkw ou identificator_in_network
}

# Features esperadas (29 features conforme utils/preprocessing.py)
REQUIRED_FEATURES = [
    # Telemetry - Optical (7)
    'optical_mean', 'optical_std', 'optical_min', 'optical_max',
    'optical_readings', 'optical_below_threshold', 'optical_range',
    # Telemetry - Temperature (6)
    'temp_mean', 'temp_std', 'temp_min', 'temp_max',
    'temp_above_threshold', 'temp_range',
    # Telemetry - Battery (5)
    'battery_mean', 'battery_std', 'battery_min', 'battery_max',
    'battery_below_threshold',
    # Connectivity (9)
    'snr_mean', 'snr_std', 'snr_min',
    'rsrp_mean', 'rsrp_std', 'rsrp_min',
    'rsrq_mean', 'rsrq_std', 'rsrq_min',
    # Messaging (2)
    'total_messages', 'max_frame_count'
]


def load_aws_payload(filepath: str) -> pd.DataFrame:
    """
    Carrega CSV AWS e identifica colunas disponíveis.
    
    AWS payload tem colunas nested tipo:
    - eyon_metadata.decoded_payload.optical_power_1490nm
    - f_cnt ou f_count
    - device_id ou sn_fkw ou identificator_in_network
    """
    logger.info(f"📂 Carregando {filepath}...")
    df = pd.read_csv(filepath)
    
    logger.info(f"✅ Carregado: {len(df):,} linhas, {len(df.columns)} colunas")
    
    # Identificar variações de nomes de colunas
    cols = df.columns.tolist()
    
    # Device ID
    device_col = None
    for candidate in ['device_id', 'sn_fkw', 'identificator_in_network']:
        if candidate in cols:
            device_col = candidate
            break
    
    if device_col is None:
        raise ValueError("❌ Coluna device_id não encontrada! Tentou: device_id, sn_fkw, identificator_in_network")
    
    # Frame count
    frame_col = None
    for candidate in ['f_cnt', 'f_count', 'eyon_metadata.f_count']:
        if candidate in cols:
            frame_col = candidate
            break
    
    logger.info(f"🔍 Colunas identificadas:")
    logger.info(f"   - Device ID: {device_col}")
    logger.info(f"   - Frame Count: {frame_col}")
    
    # Atualizar mapeamento
    AWS_COLUMN_MAPPING['device_id'] = device_col
    if frame_col:
        AWS_COLUMN_MAPPING['frame_count'] = frame_col
    
    return df


def aggregate_by_device(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega mensagens por device_id calculando estatísticas.
    
    Padrão baseado em notebooks/old/02_correlacao_telemetrias_msg6.ipynb:
    - GroupBy device_id
    - Agg: mean, std, min, max para sensores
    - Count para total_messages/readings
    - Thresholds customizados
    """
    device_col = AWS_COLUMN_MAPPING['device_id']
    
    logger.info(f"📊 Agregando por {device_col}...")
    
    aggregated = {}
    
    # 1. OPTICAL POWER
    optical_col = AWS_COLUMN_MAPPING['optical']
    if optical_col in df.columns:
        logger.info("   Processando optical power...")
        
        # Remover NaN antes de agregar
        df_optical = df[df[optical_col].notna()].copy()
        
        optical_stats = df_optical.groupby(device_col)[optical_col].agg([
            ('optical_mean', 'mean'),
            ('optical_std', 'std'),
            ('optical_min', 'min'),
            ('optical_max', 'max'),
            ('optical_readings', 'count')
        ]).reset_index()
        
        # Calcular range
        optical_stats['optical_range'] = optical_stats['optical_max'] - optical_stats['optical_min']
        
        # Threshold: quantidade de readings abaixo de -28 dBm
        optical_below = df_optical[df_optical[optical_col] < OPTICAL_THRESHOLD].groupby(device_col).size()
        optical_stats['optical_below_threshold'] = optical_stats[device_col].map(optical_below).fillna(0).astype(int)
        
        aggregated['optical'] = optical_stats
    else:
        logger.warning(f"⚠️  Coluna {optical_col} não encontrada!")
    
    # 2. TEMPERATURE
    temp_col = AWS_COLUMN_MAPPING['temp']
    if temp_col in df.columns:
        logger.info("   Processando temperature...")
        
        df_temp = df[df[temp_col].notna()].copy()
        
        temp_stats = df_temp.groupby(device_col)[temp_col].agg([
            ('temp_mean', 'mean'),
            ('temp_std', 'std'),
            ('temp_min', 'min'),
            ('temp_max', 'max')
        ]).reset_index()
        
        # Calcular range
        temp_stats['temp_range'] = temp_stats['temp_max'] - temp_stats['temp_min']
        
        # Threshold: quantidade de readings acima de 70°C
        temp_above = df_temp[df_temp[temp_col] > TEMP_THRESHOLD].groupby(device_col).size()
        temp_stats['temp_above_threshold'] = temp_stats[device_col].map(temp_above).fillna(0).astype(int)
        
        aggregated['temp'] = temp_stats
    else:
        logger.warning(f"⚠️  Coluna {temp_col} não encontrada!")
    
    # 3. BATTERY
    battery_col = AWS_COLUMN_MAPPING['battery']
    if battery_col in df.columns:
        logger.info("   Processando battery...")
        
        df_battery = df[df[battery_col].notna()].copy()
        
        battery_stats = df_battery.groupby(device_col)[battery_col].agg([
            ('battery_mean', 'mean'),
            ('battery_std', 'std'),
            ('battery_min', 'min'),
            ('battery_max', 'max')
        ]).reset_index()
        
        # Threshold: quantidade de readings abaixo de 2.5V
        battery_below = df_battery[df_battery[battery_col] < BATTERY_THRESHOLD].groupby(device_col).size()
        battery_stats['battery_below_threshold'] = battery_stats[device_col].map(battery_below).fillna(0).astype(int)
        
        aggregated['battery'] = battery_stats
    else:
        logger.warning(f"⚠️  Coluna {battery_col} não encontrada!")
    
    # 4. CONNECTIVITY (SNR, RSRP, RSRQ)
    for signal in ['snr', 'rsrp', 'rsrq']:
        signal_col = AWS_COLUMN_MAPPING[signal]
        if signal_col in df.columns:
            logger.info(f"   Processando {signal.upper()}...")
            
            df_signal = df[df[signal_col].notna()].copy()
            
            signal_stats = df_signal.groupby(device_col)[signal_col].agg([
                (f'{signal}_mean', 'mean'),
                (f'{signal}_std', 'std'),
                (f'{signal}_min', 'min')
            ]).reset_index()
            
            aggregated[signal] = signal_stats
        else:
            logger.warning(f"⚠️  Coluna {signal_col} não encontrada!")
    
    # 5. MESSAGING (total_messages, max_frame_count)
    logger.info("   Processando messaging...")
    
    messaging_stats = df.groupby(device_col).agg(
        total_messages=('device_id', 'count')  # Conta linhas por device
    ).reset_index()
    
    # max_frame_count
    frame_col = AWS_COLUMN_MAPPING.get('frame_count')
    if frame_col and frame_col in df.columns:
        frame_max = df.groupby(device_col)[frame_col].max().reset_index(name='max_frame_count')
        messaging_stats = messaging_stats.merge(frame_max, on=device_col)
    else:
        messaging_stats['max_frame_count'] = np.nan
    
    aggregated['messaging'] = messaging_stats
    
    # 6. MERGE TODOS OS DataFrames
    logger.info("🔗 Juntando todas as agregações...")
    
    final_df = aggregated['messaging']  # Começa com messaging (tem todos devices)
    
    for key, df_agg in aggregated.items():
        if key != 'messaging':
            final_df = final_df.merge(df_agg, on=device_col, how='left')
    
    # Renomear device_id para padrão
    final_df = final_df.rename(columns={device_col: 'device_id'})
    
    logger.info(f"✅ Agregação completa: {len(final_df)} devices, {len(final_df.columns)} colunas")
    
    return final_df


def validate_output(df: pd.DataFrame) -> Dict:
    """
    Valida se output tem 29 features esperadas.
    """
    logger.info("🔍 Validando output...")
    
    present_features = [f for f in REQUIRED_FEATURES if f in df.columns]
    missing_features = [f for f in REQUIRED_FEATURES if f not in df.columns]
    
    result = {
        'valid': len(missing_features) == 0,
        'total_required': len(REQUIRED_FEATURES),
        'present': len(present_features),
        'missing': missing_features,
        'num_devices': len(df)
    }
    
    if result['valid']:
        logger.info(f"✅ VALIDAÇÃO OK: {result['present']}/29 features presentes, {result['num_devices']} devices")
    else:
        logger.error(f"❌ VALIDAÇÃO FALHOU: {len(missing_features)} features faltando:")
        for feat in missing_features:
            logger.error(f"   - {feat}")
    
    return result


def transform_aws_to_model_format(input_filepath: str, output_dir: str = "payloads_processed"):
    """
    Pipeline completo: AWS raw → Model format.
    
    Args:
        input_filepath: Caminho para CSV AWS raw
        output_dir: Diretório para salvar output
    """
    try:
        # 1. Load
        df_raw = load_aws_payload(input_filepath)
        
        # 2. Aggregate
        df_aggregated = aggregate_by_device(df_raw)
        
        # 3. Validate
        validation = validate_output(df_aggregated)
        
        # 4. Save
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        input_name = Path(input_filepath).stem
        output_file = output_path / f"{input_name}_transformed.csv"
        
        # Salvar APENAS as 29 features + device_id
        output_columns = ['device_id'] + REQUIRED_FEATURES
        df_output = df_aggregated[output_columns].copy()
        
        df_output.to_csv(output_file, index=False)
        logger.info(f"💾 Salvo: {output_file}")
        logger.info(f"   {len(df_output)} devices, {len(df_output.columns)} colunas")
        
        # 5. Summary
        logger.info("\n" + "="*60)
        logger.info("📊 SUMÁRIO DA TRANSFORMAÇÃO")
        logger.info("="*60)
        logger.info(f"Input:  {input_filepath}")
        logger.info(f"        {len(df_raw):,} mensagens")
        logger.info(f"Output: {output_file}")
        logger.info(f"        {len(df_output)} devices")
        logger.info(f"        {validation['present']}/{validation['total_required']} features")
        
        if validation['valid']:
            logger.info("Status: ✅ COMPATÍVEL com batch upload")
        else:
            logger.warning(f"Status: ⚠️  {len(validation['missing'])} features faltando")
        
        logger.info("="*60 + "\n")
        
        return output_file, validation
        
    except Exception as e:
        logger.error(f"❌ ERRO na transformação: {e}")
        raise


def main():
    """
    Processa todos os CSVs em payloads_aws/.
    """
    logger.info("="*60)
    logger.info("🚀 TRANSFORM AWS PAYLOAD → MODEL FORMAT")
    logger.info("="*60 + "\n")
    
    payloads_dir = Path("payloads_aws")
    
    if not payloads_dir.exists():
        logger.error(f"❌ Diretório {payloads_dir} não encontrado!")
        return
    
    csv_files = list(payloads_dir.glob("*.csv"))
    
    if not csv_files:
        logger.error(f"❌ Nenhum CSV encontrado em {payloads_dir}")
        return
    
    logger.info(f"📁 Encontrados {len(csv_files)} arquivo(s):")
    for f in csv_files:
        logger.info(f"   - {f.name}")
    logger.info("")
    
    results = []
    
    for csv_file in csv_files:
        logger.info(f"\n{'='*60}")
        logger.info(f"📄 Processando: {csv_file.name}")
        logger.info(f"{'='*60}\n")
        
        try:
            output_file, validation = transform_aws_to_model_format(str(csv_file))
            results.append({
                'input': csv_file.name,
                'output': output_file.name,
                'valid': validation['valid'],
                'devices': validation['num_devices']
            })
        except Exception as e:
            logger.error(f"❌ Falha ao processar {csv_file.name}: {e}")
            results.append({
                'input': csv_file.name,
                'output': None,
                'valid': False,
                'error': str(e)
            })
    
    # RESUMO FINAL
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMO FINAL")
    logger.info("="*60)
    
    for r in results:
        status = "✅" if r['valid'] else "❌"
        logger.info(f"{status} {r['input']}")
        if r.get('output'):
            logger.info(f"   → {r['output']} ({r['devices']} devices)")
        if r.get('error'):
            logger.info(f"   ERROR: {r['error']}")
    
    logger.info("="*60 + "\n")
    
    # Check se há arquivos transformados válidos
    valid_count = sum(1 for r in results if r['valid'])
    
    if valid_count > 0:
        logger.info(f"🎉 Transformação concluída! {valid_count}/{len(results)} arquivo(s) pronto(s) para batch upload.")
        logger.info("\nPróximo passo:")
        logger.info("1. Verificar payloads_processed/*.csv")
        logger.info("2. Testar com scripts/test_payload_compatibility.py")
        logger.info("3. Fazer upload via Streamlit (pages/2_Batch_Upload.py)")
    else:
        logger.error("❌ Nenhum arquivo transformado com sucesso.")


if __name__ == "__main__":
    main()
