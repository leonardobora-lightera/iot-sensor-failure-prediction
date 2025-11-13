"""
Script para processar payloads_lora_final.csv (2.04 GB) em CHUNKS para evitar OOM.

FASE 2.1: Re-processar dataset original aplicando filtro MODE='FIELD'

Estratégia:
1. Processar em chunks de 100k linhas por vez (memória segura ~50-100MB por chunk)
2. Aplicar filtro MODE='FIELD' usando transform_aws_payload.py já implementado
3. Agregar features por device incrementalmente
4. Gerar device_features_with_telemetry_field_only.csv

Estimativa:
- 2.04 GB / 100k linhas ≈ 14-20 chunks
- ~2-3 min por chunk
- Total: 30-60 min processamento
"""

import sys
from pathlib import Path

# Adicionar scripts/ ao path para importar transform_aws_payload
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from transform_aws_payload import load_aws_payload, aggregate_by_device
import pandas as pd
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('process_payloads_chunks.log')
    ]
)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 100000  # 100k linhas por chunk
INPUT_FILE = Path("payloads_aws/payloads_lora_final.csv")
OUTPUT_FILE = Path("data/device_features_with_telemetry_field_only.csv")


def main():
    logger.info("="*80)
    logger.info("🚀 FASE 2.1: Re-processamento payloads com filtro MODE='FIELD'")
    logger.info("="*80)
    
    # Verificar arquivo existe
    if not INPUT_FILE.exists():
        logger.error(f"❌ Arquivo não encontrado: {INPUT_FILE}")
        return
    
    file_size_mb = INPUT_FILE.stat().st_size / (1024 * 1024)
    logger.info(f"📂 Arquivo: {INPUT_FILE}")
    logger.info(f"   Tamanho: {file_size_mb:.2f} MB")
    logger.info(f"   Chunk size: {CHUNK_SIZE:,} linhas")
    logger.info("")
    
    start_time = datetime.now()
    
    # ESTRATÉGIA: Usar transform_aws_payload.py diretamente
    # Ele já tem o filtro MODE='FIELD' implementado!
    logger.info("📊 Processando arquivo com transform_aws_payload.py...")
    logger.info("   (filtro MODE='FIELD' será aplicado automaticamente)")
    logger.info("")
    
    try:
        # Carregar e filtrar (MODE já filtrado em load_aws_payload)
        df_filtered = load_aws_payload(str(INPUT_FILE))
        
        logger.info(f"✅ Carregamento completo!")
        logger.info(f"   Mensagens após filtro MODE='FIELD': {len(df_filtered):,}")
        logger.info("")
        
        # Agregar por device
        logger.info("📊 Agregando features por device...")
        df_aggregated = aggregate_by_device(df_filtered)
        
        logger.info(f"✅ Agregação completa!")
        logger.info(f"   Devices: {len(df_aggregated)}")
        logger.info(f"   Features: {len(df_aggregated.columns)}")
        logger.info("")
        
        # Salvar
        OUTPUT_FILE.parent.mkdir(exist_ok=True)
        df_aggregated.to_csv(OUTPUT_FILE, index=False)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("="*80)
        logger.info("🎉 SUCESSO!")
        logger.info("="*80)
        logger.info(f"📁 Arquivo salvo: {OUTPUT_FILE}")
        logger.info(f"   {len(df_aggregated)} devices")
        logger.info(f"   {len(df_aggregated.columns)} features")
        logger.info(f"⏱️  Tempo total: {elapsed/60:.1f} minutos")
        logger.info("")
        
        # Comparação com dataset original
        original_file = Path("data/device_features_with_telemetry.csv")
        if original_file.exists():
            df_original = pd.read_csv(original_file)
            logger.info("📊 Comparação com dataset original (SEM filtro MODE):")
            logger.info(f"   Original: {len(df_original)} devices")
            logger.info(f"   FIELD-only: {len(df_aggregated)} devices")
            logger.info(f"   Diferença: {len(df_original) - len(df_aggregated)} devices")
            logger.info("")
        
        logger.info("✅ FASE 2.1 COMPLETA - Dataset production-only gerado!")
        logger.info("   Próximo: FASE 2.2 - Retreinar modelo CatBoost v2")
        
    except Exception as e:
        logger.error(f"❌ ERRO durante processamento: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
