
"""
inference.py - Funções de Inferência para Modelo de Produção
CatBoost + SMOTE 0.5 Pipeline

Uso:
    from inference import load_model, predict_device, predict_batch, log_prediction

    # Carregar modelo
    pipeline = load_model('models/catboost_pipeline_v1_20251107.pkl')

    # Single prediction
    result = predict_device(features_dict, pipeline)

    # Batch prediction
    df_results = predict_batch(df_devices, pipeline)
    
    # Log prediction (POC exemplo audit trail)
    log_prediction(device_id, result['prediction'], result['probability'])
"""

import joblib
import pandas as pd
import json
from datetime import datetime
from pathlib import Path


def log_prediction(device_id, prediction, probability, model_version="v1.0.0"):
    """
    POC EXEMPLO - Logging básico de predições para audit trail.
    
    Para produção: Expandir com features_hash, execution_time, user_id,
    structured logging (logs/predictions/YYYY-MM-DD.jsonl), rotation policy.
    
    Args:
        device_id (str): ID do dispositivo
        prediction (int): Predição (0=normal, 1=critical)
        probability (float): Probabilidade crítico
        model_version (str): Versão do modelo usado
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "device_id": device_id,
        "prediction": "CRITICAL" if prediction == 1 else "NORMAL",
        "probability": round(probability, 4),
        "model_version": model_version
    }
    
    # POC: Print to console (produção: save to JSON file)
    print(f"[AUDIT] {json.dumps(log_entry)}")
    
    # Produção: logs_dir = Path("logs/predictions")
    # with open(logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl", "a") as f:
    #     f.write(json.dumps(log_entry) + "\n")


def load_model(model_path):
    """
    Carrega o pipeline de produção salvo.

    Args:
        model_path (str): Caminho para o arquivo .pkl

    Returns:
        Pipeline treinado
    """
    pipeline = joblib.load(model_path)
    print(f"✅ Modelo carregado de: {model_path}")
    return pipeline


def predict_device(features_dict, pipeline):
    """
    Predição para um ÚNICO device.

    Args:
        features_dict (dict): Dicionário com 29 features {feature_name: value}
        pipeline: Pipeline já carregado

    Returns:
        dict com 'prediction' (0/1), 'probability' (0.0-1.0), 'risk_level', 'verdict'
    """
    # Converter dict para DataFrame
    df_input = pd.DataFrame([features_dict])

    # Predição
    prediction = pipeline.predict(df_input)[0]
    probability = pipeline.predict_proba(df_input)[0, 1]

    # Risk level
    if probability < 0.3:
        risk_level = 'Low'
    elif probability < 0.7:
        risk_level = 'Medium'
    else:
        risk_level = 'High'

    return {
        'prediction': int(prediction),
        'probability': float(probability),
        'risk_level': risk_level,
        'verdict': 'CRITICAL' if prediction == 1 else 'NORMAL'
    }


def predict_batch(df_devices, pipeline):
    """
    Predição em LOTE para múltiplos devices.

    Args:
        df_devices (DataFrame): DataFrame com 29 features (1 row por device)
        pipeline: Pipeline já carregado

    Returns:
        DataFrame original + colunas 'prediction', 'probability', 'risk_level', 'verdict'
    """
    # Predições
    predictions = pipeline.predict(df_devices)
    probabilities = pipeline.predict_proba(df_devices)[:, 1]

    # Risk levels
    risk_levels = pd.cut(
        probabilities,
        bins=[0, 0.3, 0.7, 1.0],
        labels=['Low', 'Medium', 'High']
    )

    # Adicionar colunas
    df_result = df_devices.copy()
    df_result['prediction'] = predictions
    df_result['probability'] = probabilities
    df_result['risk_level'] = risk_levels
    df_result['verdict'] = df_result['prediction'].map({0: 'NORMAL', 1: 'CRITICAL'})

    return df_result
