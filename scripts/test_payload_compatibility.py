"""
Script de Teste: Compatibilidade de Payload AWS com Batch Upload
Objetivo: Validar se os arquivos payload_aws podem ser processados pelo batch upload do Streamlit
"""
import pandas as pd
import sys
from pathlib import Path

# Add project root
sys.path.append(str(Path(__file__).parent.parent))

from utils.preprocessing import (
    validate_features,
    check_feature_types,
    prepare_for_prediction,
    REQUIRED_FEATURES
)

def test_payload_compatibility(filepath: str):
    """
    Testa compatibilidade de arquivo payload com batch upload.
    
    Args:
        filepath: Caminho para arquivo CSV
        
    Returns:
        dict com resultados do teste
    """
    print(f"\n{'='*80}")
    print(f"TESTANDO: {Path(filepath).name}")
    print(f"{'='*80}\n")
    
    results = {
        'filename': Path(filepath).name,
        'loaded': False,
        'num_rows': 0,
        'num_cols': 0,
        'has_required_features': False,
        'missing_features': [],
        'extra_features': [],
        'can_predict': False,
        'errors': []
    }
    
    try:
        # 1. CARREGAR CSV
        print("1. Carregando CSV...")
        df = pd.read_csv(filepath)
        results['loaded'] = True
        results['num_rows'] = len(df)
        results['num_cols'] = len(df.columns)
        print(f"   ✅ Carregado: {results['num_rows']} linhas, {results['num_cols']} colunas")
        
        # 2. VERIFICAR FEATURES REQUERIDAS
        print("\n2. Verificando features requeridas (29 features)...")
        is_valid, missing = validate_features(df)
        results['has_required_features'] = is_valid
        results['missing_features'] = missing
        
        if is_valid:
            print(f"   ✅ Todas 29 features requeridas presentes!")
        else:
            print(f"   ❌ FALTANDO {len(missing)} features:")
            for feat in missing[:10]:  # Mostrar primeiras 10
                print(f"      - {feat}")
            if len(missing) > 10:
                print(f"      ... e mais {len(missing) - 10} features")
        
        # 3. VERIFICAR FEATURES EXTRAS
        print("\n3. Verificando features extras...")
        extra = set(df.columns) - set(REQUIRED_FEATURES) - {'device_id'}
        results['extra_features'] = list(extra)
        
        if extra:
            print(f"   ⚠️  {len(extra)} features extras encontradas (serão ignoradas):")
            for feat in list(extra)[:10]:
                print(f"      - {feat}")
            if len(extra) > 10:
                print(f"      ... e mais {len(extra) - 10} features")
        else:
            print(f"   ✅ Nenhuma feature extra")
        
        # 4. VERIFICAR TIPOS
        print("\n4. Verificando tipos de dados...")
        df_checked = check_feature_types(df)
        print(f"   ✅ Tipos validados")
        
        # 5. PREPARAR PARA PREDIÇÃO
        print("\n5. Preparando features para predição...")
        if is_valid:
            features_df = prepare_for_prediction(df)
            results['can_predict'] = True
            print(f"   ✅ Features preparadas: {features_df.shape}")
            print(f"      - Shape: {features_df.shape[0]} devices x {features_df.shape[1]} features")
        else:
            print(f"   ❌ Não é possível preparar (features faltando)")
        
        # 6. VERIFICAR VALORES FALTANTES
        print("\n6. Análise de valores faltantes...")
        missing_counts = df[REQUIRED_FEATURES].isnull().sum()
        total_missing = missing_counts.sum()
        
        if total_missing > 0:
            print(f"   ⚠️  {total_missing} valores faltantes encontrados")
            top_missing = missing_counts[missing_counts > 0].sort_values(ascending=False).head(5)
            for feat, count in top_missing.items():
                print(f"      - {feat}: {count} valores ({count/len(df)*100:.1f}%)")
        else:
            print(f"   ✅ Nenhum valor faltante")
        
        # 7. MOSTRAR PREVIEW
        print("\n7. Preview dos dados (primeiras 3 linhas):")
        print(df[REQUIRED_FEATURES[:5]].head(3).to_string())
        
    except Exception as e:
        results['errors'].append(str(e))
        print(f"\n❌ ERRO: {e}")
    
    return results


def print_summary(results_list):
    """Imprime resumo comparativo dos testes."""
    print(f"\n\n{'='*80}")
    print("RESUMO COMPARATIVO")
    print(f"{'='*80}\n")
    
    for res in results_list:
        status = "✅ OK" if res['can_predict'] else "❌ INCOMPATÍVEL"
        print(f"{res['filename']:40s} {status}")
        print(f"  - Linhas: {res['num_rows']}")
        print(f"  - Colunas: {res['num_cols']}")
        print(f"  - Features faltando: {len(res['missing_features'])}")
        print(f"  - Features extras: {len(res['extra_features'])}")
        print()


if __name__ == "__main__":
    # Testar ambos arquivos
    payloads_dir = Path("payloads_aws")
    
    test_files = [
        payloads_dir / "payload_aws_raw_teste.csv",
        payloads_dir / "payload_aws_BORA.csv"
    ]
    
    results = []
    for filepath in test_files:
        if filepath.exists():
            res = test_payload_compatibility(str(filepath))
            results.append(res)
        else:
            print(f"❌ Arquivo não encontrado: {filepath}")
    
    # Resumo
    print_summary(results)
    
    # Recomendações
    print(f"\n{'='*80}")
    print("RECOMENDAÇÕES")
    print(f"{'='*80}\n")
    
    incompatible = [r for r in results if not r['can_predict']]
    
    if incompatible:
        print("⚠️  Arquivos INCOMPATÍVEIS encontrados!\n")
        print("Para usar no batch upload, você precisa:")
        print("  1. Mapear as colunas do payload AWS para as 29 features esperadas")
        print("  2. Criar script de transformação/agregação")
        print("  3. Ou modificar o batch upload para aceitar formato AWS\n")
        
        print("Exemplo de mapeamento necessário:")
        print("  eyon_metadata.decoded_payload.optical_power_1490nm → optical_mean")
        print("  eyon_metadata.decoded_payload.temperature → temp_mean")
        print("  eyon_metadata.decoded_payload.battery → battery_mean")
        print("  etc...")
    else:
        print("✅ Todos arquivos são COMPATÍVEIS com batch upload!")
        print("Você pode fazer upload diretamente no Streamlit app.")
