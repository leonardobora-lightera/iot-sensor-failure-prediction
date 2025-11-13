# 🔋 IoT Critical Device Prediction - Production-Only Model v2# 🔋 IoT Critical Device Prediction - Battery Instability Detection



[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-FF4B4B.svg)](https://streamlit.io)[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-FF4B4B.svg)](https://streamlit.io)

[![CatBoost](https://img.shields.io/badge/CatBoost-1.2.8-yellow.svg)](https://catboost.ai)[![CatBoost](https://img.shields.io/badge/CatBoost-1.2.8-yellow.svg)](https://catboost.ai)

[![Model v2](https://img.shields.io/badge/Model-v2.0%20FIELD--only-green.svg)]()

**Objetivo:** Predição de dispositivos IoT com risco de instabilidade de bateria usando Machine Learning, alcançando **78.6% recall** e **84.6% precision** (excedendo target 80%).

**Predição de falhas em dispositivos IoT usando Machine Learning com dados de produção limpos (FIELD-only).**

---

---

## 📊 Resultados Finais

## 🎯 Modelo v2 - Production-Only Pipeline

**Modelo Produção:** CatBoost + SMOTE 0.5  

**Abordagem:** CatBoost + SMOTE 0.5 treinado APENAS em dados de campo (sem contaminação de laboratório)**Performance Test Set (237 devices, 14 critical):**

- ✅ **Recall:** 78.6% (11/14 críticos detectados)

### 📊 Performance (Test Set: 229 devices, 14 critical)- ✅ **Precision:** 84.6% (TARGET 80% EXCEDIDO)

- **Recall:** 57.1% (8/14 dispositivos críticos detectados)- ✅ **F1-Score:** 81.5%

- **Precision:** 57.1%- ✅ **ROC-AUC:** 0.8621

- **F1-Score:** 57.1%- ✅ **False Positive Rate:** 0.8% (~2 FP em 237 devices)

- **ROC-AUC:** **0.9186** ⬆️ (+6.6% vs v1)

- **False Positive Rate:** 2.6% (6/229 devices)**Jornada:** 0% recall (temporal split leakage) → 50% (baseline limpo) → 71.4% (SMOTE) → **78.6%** (CatBoost)



### 🆕 Diferenciais v2---

- ✅ **Dataset limpo:** 762 devices FIELD-only (removidos 362k mensagens FACTORY - 31.8%)

- ✅ **30 features:** Adicionada `days_since_last_message` para detectar inatividade## 📁 Estrutura do Projeto

- ✅ **Sem lifecycle mixing:** Lab + Production separados

- ✅ **AUC melhorado:** Melhor calibração de probabilidades (0.8621 → 0.9186)```

iot_sensor_novembro/

### 🛣️ Roadmap "3 Passos à Frente"├── notebooks/               # 9 notebooks análise + modelagem

Trade-off atual: **-21.5% recall vs v1**, mas **fundação sólida** para:│   ├── 02B_stratified_split_by_device.ipynb    # Split estratificado válido

1. **Hyperparameter Tuning:** GridSearch CatBoost (esperado +10-15% recall)│   ├── 03_status_modelagem_pratica.ipynb       # Checkpoint baseline

2. **Temporal Features (FASE 3):** 4 features adicionais (esperado +20% recall)│   ├── 04B_sem_leakage_LIMPO.ipynb             # Correção data leakage msg6

3. **Threshold Calibration:** Otimizar decision boundary│   ├── 04_correcao_class_imbalance.ipynb       # Imputation + class_weight

│   ├── 05_smote_optimization.ipynb             # SMOTE 0.5 → 71.4% recall

---│   ├── 06B_synthetic_validation_empirical.ipynb # Validação empírica

│   ├── 06_synthetic_data_validation.ipynb      # Validação teórica (FALHOU)

## 📁 Estrutura do Projeto│   ├── 07_model_optimization.ipynb             # CatBoost 78.6% VENCEDOR

│   └── 08_pipeline_producao.ipynb              # Pipeline final .pkl

```│

iot_sensor_novembro/├── streamlit_app.py        # App web multi-página

├── streamlit_app.py                    # App web (deploy Streamlit Cloud)├── pages/                  # 5 páginas Streamlit

├── pages/                               # Interface multi-página│   ├── 1_Home.py           # Dashboard métricas

│   ├── 1_Home.py                        # Dashboard│   ├── 2_Batch_Upload.py   # Predição CSV batch

│   ├── 2_Batch_Upload.py                # Upload CSV│   ├── 3_Single_Predict.py # Predição single device

│   ├── 3_Single_Predict.py              # Predição individual│   ├── 4_Insights.py       # Performance + feature importance

│   ├── 4_Insights.py                    # Performance│   └── 5_Research_Context.py # Jornada pesquisa + descobertas

│   └── 5_Research_Context.py            # Documentação│

│├── models/                 # Modelo produção

├── models/│   ├── catboost_pipeline_v1_20251107.pkl       # Pipeline treinado (126KB)

│   ├── catboost_pipeline_v2_field_only.pkl       # 🆕 Modelo v2 (127 KB)│   ├── catboost_pipeline_v1_20251107_metadata.json

│   ├── catboost_pipeline_v2_metadata.json        # Metadata v2│   └── inference.py

│   └── inference.py                              # API predição│

│├── utils/                  # Módulos suporte

├── scripts/│   ├── model_loader.py     # Carregamento pipeline

│   └── transform_aws_payload.py         # 🆕 Filtro MODE='FIELD'│   ├── preprocessing.py    # Validação features + imputation

││   └── visualization.py    # Gráficos Plotly

├── notebooks/│

│   ├── archive_v1/                      # Notebooks modelo v1 (arquivados)├── data/                   # Datasets

│   └── README.md                        # Transição v1→v2│   ├── device_features_train_stratified.csv    # 552 devices (31 critical)

││   ├── device_features_test_stratified.csv     # 237 devices (14 critical)

├── utils/                               # Helpers│   └── device_features_with_telemetry.csv      # Dataset completo (789)

│   ├── model_loader.py│

│   ├── preprocessing.py├── docs/                   # Documentação técnica

│   └── visualization.py│   └── LEAKAGE_DISCOVERY.md

││

├── data/├── MODEL_COMPARISON.md     # Comparação XGBoost/LightGBM/CatBoost

│   ├── device_features_with_telemetry.csv              # Original (789 devices)├── CHANGELOG.md            # Timeline evolutiva 13 fases

│   └── device_features_with_telemetry_field_only.csv   # 🆕 FIELD-only (762 devices)├── requirements.txt        # Dependências Python

│└── README.md               # Este arquivo

├── docs/                                # Documentação técnica```

│   ├── PLANO_ACAO_FIX_FALSOS_POSITIVOS.md

│   ├── FEATURE_ENGINEERING_TEMPORAL.md---

│   └── BIAS_MITIGATION_CHECKLIST.md

│## 🚀 Instalação e Uso

└── train_model_v2.py                    # 🆕 Script treinamento v2

```### Pré-requisitos

- Python 3.12+

---- pip



## 🚀 Quick Start### Instalação

```bash

### 1. Instalação# Clone o repositório (ou baixe os arquivos)

```bashcd iot_sensor_novembro

# Clone repositório

git clone https://github.com/leonardobora-lightera/iot-sensor-failure-prediction.git# Instale as dependências

cd iot-sensor-failure-predictionpip install -r requirements.txt

```

# Instalar dependências

pip install -r requirements.txt### Uso - Notebooks

``````bash

# Abra o Jupyter e navegue para notebooks/

### 2. Rodar Streamlit Localmentejupyter notebook notebooks/

```bash```

streamlit run streamlit_app.py

```**Ordem recomendada:**

1. `02B_stratified_split_by_device.ipynb` - Entender split válido

Acesse: `http://localhost:8501`2. `04B_sem_leakage_LIMPO.ipynb` - Baseline limpo 50% recall

3. `05_smote_optimization.ipynb` - SMOTE → 71.4% recall

### 3. Fazer Predição (Python)4. `07_model_optimization.ipynb` - CatBoost → 78.6% recall

```python5. `08_pipeline_producao.ipynb` - Pipeline final

import joblib

import pandas as pd### Uso - Streamlit App

```bash

# Carregar modelo v2# Execute o app

pipeline = joblib.load('models/catboost_pipeline_v2_field_only.pkl')streamlit run streamlit_app.py

```

# Carregar features (30 features esperadas)

df = pd.read_csv('data/device_features_with_telemetry_field_only.csv')**Acesso:** http://localhost:8501



# Predizer---

X = df.drop(['device_id', 'is_critical', 'is_critical_target', 'severity_category'], axis=1)

predictions = pipeline.predict(X)## 🌐 Streamlit Web Application

probabilities = pipeline.predict_proba(X)[:, 1]

### 5 Páginas Interativas

print(f"Críticos detectados: {predictions.sum()}")

```#### 1. **Home (🏠)** - Dashboard Overview

- Métricas principais modelo (Recall 78.6%, Precision 84.6%, F1 81.5%, AUC 0.8621)

---- Informações dataset (789 devices, 45 critical 5.7%)

- Sidebar com versão modelo e data deployment

## 📊 Features (30 total)

#### 2. **Batch Upload (📤)** - Predição em Lote

### Telemetria (18 features)- Upload CSV com features 29 colunas

- `optical_mean`, `optical_std`, `optical_min`, `optical_max`, `optical_readings`, `optical_below_threshold`, `optical_range`- Validação automática features (nomes, tipos, ranges)

- `temp_mean`, `temp_std`, `temp_min`, `temp_max`, `temp_above_threshold`, `temp_range`- Predições batch com probabilidades

- `battery_mean`, `battery_std`, `battery_min`, `battery_max`, `battery_below_threshold`- Download resultados CSV processado

- Exemplo: Processar 100+ devices simultaneamente

### Conectividade (9 features)

- `snr_mean`, `snr_std`, `snr_min`#### 3. **Single Prediction (🔍)** - Predição Individual

- `rsrp_mean`, `rsrp_std`, `rsrp_min`- Formulário interativo 29 features

- `rsrq_mean`, `rsrq_std`, `rsrq_min`- Input manual ou defaults médios

- Predição single device com probabilidade

### Messaging (2 features)- Explicação resultado (critical/normal)

- `total_messages`, `max_frame_count`- Uso: Testar cenários hipotéticos ou dispositivos específicos



### 🆕 Temporal (1 feature)#### 4. **Model Insights (📊)** - Performance e Features

- `days_since_last_message` - Detecta dispositivos inativos- Confusion matrix test set (TP/FP/FN/TN)

- Métricas detalhadas (Recall, Precision, F1, AUC)

---- Feature importance top-10 (max_frame_count 15.2%, total_messages 12.8%)

- ROC curve interativa

## 🧪 Evolução do Modelo- Uso: Entender modelo e drivers principais



### v1 (Arquivado - Mixed FACTORY+FIELD)#### 5. **Research Context (🔬)** - Jornada da Pesquisa

- Dataset: 789 devices (mixed lab + production)- **Seção 1:** Problema IoT battery instability (789 devices, imbalance 16.8:1)

- Performance: Recall 78.6%, Precision 84.6%, AUC 0.8621- **Seção 2:** Timeline 4 fases (Temporal 0% → Stratified 50% → SMOTE 71.4% → CatBoost 78.6%)

- Problema: Lifecycle mixing contamina padrões- **Seção 3:** Descoberta data leakage (msg6_count/msg6_rate features)

- **Seção 4:** Feature engineering 29 features (Telemetry, Connectivity, Messaging)

### v2 (Atual - FIELD-only)- **Seção 5:** Descobertas técnicas (SMOTE effectiveness, algoritmo comparison)

- Dataset: 762 devices (production-only)- **Seção 6:** Lições aprendidas (5 princípios: empirical analysis, leakage prevention, imbalance handling, test validation, transparency)

- Performance: Recall 57.1%, Precision 57.1%, AUC 0.9186- Uso: Stakeholders não-técnicos, onboarding novos membros, contexto decisões

- Vantagem: Dados limpos, AUC superior, base para melhorias

### Screenshots

**Filosofia:** "2 passos atrás, 3 pra frente" - sacrificar recall inicial para fundação sólida.*(Adicionar screenshots futuras do app rodando)*



---### 🌍 Nota - Tradução PT-BR Planejada

**Fase 14 (planejada):** Tradução completa do Streamlit app para português brasileiro com toggle EN/PT-BR na sidebar.

## 📚 Documentação

**Motivação:**

- **Notebooks v1:** Ver `notebooks/archive_v1/` (modelo baseline até CatBoost v1)- Maioria dos stakeholders são brasileiros

- **Plano de Ação:** `docs/PLANO_ACAO_FIX_FALSOS_POSITIVOS.md`- Research Context página beneficia de PT-BR (contexto técnico mais acessível)

- **Features Temporais:** `docs/FEATURE_ENGINEERING_TEMPORAL.md` (roadmap FASE 3)- Boas práticas i18n para futuras expansões

- **Mitigação de Vieses:** `docs/BIAS_MITIGATION_CHECKLIST.md`

**Implementação prevista:**

---- `utils/translations.py` com dicionários bilíngues (EN/PT-BR)

- `st.sidebar.selectbox` para escolha idioma

## 🔄 Próximos Passos (FASE 3)- `st.session_state` para persistir preferência usuário

- Todas 5 páginas traduzidas (código/logs permanecem inglês)

1. **Temporal Features (2 semanas):**

   - Priority 1: `deployment_age`, `last_active_period`**Estimativa:** ~60min desenvolvimento + testes

   - Priority 2: `msg_last_7days`, `msg_last_30days`

   - Esperado: +20% recall---



2. **Hyperparameter Tuning:**## 📚 Documentação Técnica

   - GridSearch CatBoost (depth, iterations, learning_rate)

   - Esperado: +10-15% recall### Documentos Principais

- **[MODEL_COMPARISON.md](MODEL_COMPARISON.md):** Comparação formal XGBoost/LightGBM/CatBoost (350+ linhas)

3. **Threshold Calibration:**  - Tabela comparativa métricas

   - ROC curve optimization  - Hyperparameters testados

   - Target: Precision >80%, Recall >75%  - Decision rationale (5 motivos técnicos)

  - Business impact (cenário 1000 devices)

---  - Feature importance top-5

  - Testing methodology (stratified split, SMOTE, hold-out)

## 🤝 Contribuindo  - Deployment readiness



Este é um projeto de pesquisa interno da **Lightera LLC**. Para dúvidas ou sugestões, contacte:- **[CHANGELOG.md](CHANGELOG.md):** Timeline evolutiva completa 13 fases

  - Fase 1: Temporal split (DESCARTADO leakage)

**Leonardo Costa**    - Fase 2-3: Stratified split válido

Estagiário Engenharia de Software - P&D    - Fase 4-5: Data leakage discovery & fix

8° período | UniBrasil Centro Universitário  - Fase 6-9: Baseline → SMOTE → CatBoost → Pipeline

  - Fase 10-11: Organization & docs

---  - Fase 12: Streamlit app (5 páginas)

  - Fase 13: Documentation (MODEL_COMPARISON.md + headers cleanup)

## 📄 Licença

- **[notebooks/README.md](notebooks/README.md):** Guia notebooks individuais

Propriedade da Lightera LLC © 2025

- **[docs/LEAKAGE_DISCOVERY.md](docs/LEAKAGE_DISCOVERY.md):** Framework validação data leakage (7 testes)

---

### Features do Modelo (29 total)

**Última atualização:** 13 de novembro de 2025 - Modelo v2.0 FIELD-only**Categorias:**

- **Telemetria (18):** optical_mean/std/min/max, temp_mean/std/min/max, battery_mean/std/min/max, etc.
- **Conectividade (9):** snr_mean/std/min, rsrp_mean/std/min, rsrq_mean/std/min
- **Messaging (2):** total_messages, max_frame_count

**Features removidas (leakage):** `msg6_count`, `msg6_rate`

---

## 🔬 Descobertas Técnicas

### 1. Data Leakage Detection Framework
**Problema:** Precision 100% artificial (modelo aprendeu definição target)  
**Solução:** Framework validação 7 testes (AUC ≥0.98 threshold, feature importance >40%, correlation >0.80)  
**Resultado:** Leakage detectado ANTES de produção (msg6 features removidas)

### 2. SMOTE Effectiveness
**Problema:** Class imbalance 16.8:1 (5.7% critical)  
**Solução:** SMOTE 0.5 interpola entre critical devices reais  
**Resultado:** Recall 50% → 71.4% (+21.4% improvement)

### 3. Algorithm Comparison
**Testados:** XGBoost (baseline), LightGBM (FAILED low recall 64.3%), CatBoost (WINNER)  
**CatBoost vantagens:** Ordered boosting (menos overfitting), categorical handling nativo, robustez hyperparameters  
**Resultado:** Recall 71.4% → 78.6%, Precision 71.4% → 84.6%

---

## 👥 Autor & Contribuições

**Autor:** Leonardo Costa  
**Colaboração:** GitHub Copilot  
**Período:** Outubro - Novembro 2025  
**Deadline:** 1 mês (contrato)

---

## 📜 Licença

*(Adicionar licença apropriada - MIT, Apache 2.0, ou proprietária)*

---

## 🔄 Status & Próximos Passos

**Status Atual:** ✅ Production pipeline COMPLETO, Streamlit app DEPLOYED, documentação PROFISSIONAL

**Próximos Passos:**
1. **Fase 14:** Tradução PT-BR Streamlit (toggle EN/PT-BR sidebar) - ~60min
2. **Fase 15:** GitHub remote configuration (opcional - colaboração)
3. **Fase 16:** CI/CD automatizado (opcional - testes + deployment)

---

**Última Atualização:** 10 de Novembro de 2025  
**Versão Modelo:** v1_20251107 (CatBoost + SMOTE 0.5)  
**App Streamlit:** 5 páginas, localhost:8501
