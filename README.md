# 🔋 IoT Critical Device Prediction - Battery Instability Detection

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-FF4B4B.svg)](https://streamlit.io)
[![CatBoost](https://img.shields.io/badge/CatBoost-1.2.8-yellow.svg)](https://catboost.ai)

**Objetivo:** Predição de dispositivos IoT com risco de instabilidade de bateria usando Machine Learning, alcançando **78.6% recall** e **84.6% precision** (excedendo target 80%).

---

## 📊 Resultados Finais

**Modelo Produção:** CatBoost + SMOTE 0.5  
**Performance Test Set (237 devices, 14 critical):**
- ✅ **Recall:** 78.6% (11/14 críticos detectados)
- ✅ **Precision:** 84.6% (TARGET 80% EXCEDIDO)
- ✅ **F1-Score:** 81.5%
- ✅ **ROC-AUC:** 0.8621
- ✅ **False Positive Rate:** 0.8% (~2 FP em 237 devices)

**Jornada:** 0% recall (temporal split leakage) → 50% (baseline limpo) → 71.4% (SMOTE) → **78.6%** (CatBoost)

---

## 📁 Estrutura do Projeto

```
iot_sensor_novembro/
├── notebooks/               # 9 notebooks análise + modelagem
│   ├── 02B_stratified_split_by_device.ipynb    # Split estratificado válido
│   ├── 03_status_modelagem_pratica.ipynb       # Checkpoint baseline
│   ├── 04B_sem_leakage_LIMPO.ipynb             # Correção data leakage msg6
│   ├── 04_correcao_class_imbalance.ipynb       # Imputation + class_weight
│   ├── 05_smote_optimization.ipynb             # SMOTE 0.5 → 71.4% recall
│   ├── 06B_synthetic_validation_empirical.ipynb # Validação empírica
│   ├── 06_synthetic_data_validation.ipynb      # Validação teórica (FALHOU)
│   ├── 07_model_optimization.ipynb             # CatBoost 78.6% VENCEDOR
│   └── 08_pipeline_producao.ipynb              # Pipeline final .pkl
│
├── streamlit_app.py        # App web multi-página
├── pages/                  # 5 páginas Streamlit
│   ├── 1_Home.py           # Dashboard métricas
│   ├── 2_Batch_Upload.py   # Predição CSV batch
│   ├── 3_Single_Predict.py # Predição single device
│   ├── 4_Insights.py       # Performance + feature importance
│   └── 5_Research_Context.py # Jornada pesquisa + descobertas
│
├── models/                 # Modelo produção
│   ├── catboost_pipeline_v1_20251107.pkl       # Pipeline treinado (126KB)
│   ├── catboost_pipeline_v1_20251107_metadata.json
│   └── inference.py
│
├── utils/                  # Módulos suporte
│   ├── model_loader.py     # Carregamento pipeline
│   ├── preprocessing.py    # Validação features + imputation
│   └── visualization.py    # Gráficos Plotly
│
├── data/                   # Datasets
│   ├── device_features_train_stratified.csv    # 552 devices (31 critical)
│   ├── device_features_test_stratified.csv     # 237 devices (14 critical)
│   └── device_features_with_telemetry.csv      # Dataset completo (789)
│
├── docs/                   # Documentação técnica
│   └── LEAKAGE_DISCOVERY.md
│
├── MODEL_COMPARISON.md     # Comparação XGBoost/LightGBM/CatBoost
├── CHANGELOG.md            # Timeline evolutiva 13 fases
├── requirements.txt        # Dependências Python
└── README.md               # Este arquivo
```

---

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.12+
- pip

### Instalação
```bash
# Clone o repositório (ou baixe os arquivos)
cd iot_sensor_novembro

# Instale as dependências
pip install -r requirements.txt
```

### Uso - Notebooks
```bash
# Abra o Jupyter e navegue para notebooks/
jupyter notebook notebooks/
```

**Ordem recomendada:**
1. `02B_stratified_split_by_device.ipynb` - Entender split válido
2. `04B_sem_leakage_LIMPO.ipynb` - Baseline limpo 50% recall
3. `05_smote_optimization.ipynb` - SMOTE → 71.4% recall
4. `07_model_optimization.ipynb` - CatBoost → 78.6% recall
5. `08_pipeline_producao.ipynb` - Pipeline final

### Uso - Streamlit App
```bash
# Execute o app
streamlit run streamlit_app.py
```

**Acesso:** http://localhost:8501

---

## 🌐 Streamlit Web Application

### 5 Páginas Interativas

#### 1. **Home (🏠)** - Dashboard Overview
- Métricas principais modelo (Recall 78.6%, Precision 84.6%, F1 81.5%, AUC 0.8621)
- Informações dataset (789 devices, 45 critical 5.7%)
- Sidebar com versão modelo e data deployment

#### 2. **Batch Upload (📤)** - Predição em Lote
- Upload CSV com features 29 colunas
- Validação automática features (nomes, tipos, ranges)
- Predições batch com probabilidades
- Download resultados CSV processado
- Exemplo: Processar 100+ devices simultaneamente

#### 3. **Single Prediction (🔍)** - Predição Individual
- Formulário interativo 29 features
- Input manual ou defaults médios
- Predição single device com probabilidade
- Explicação resultado (critical/normal)
- Uso: Testar cenários hipotéticos ou dispositivos específicos

#### 4. **Model Insights (📊)** - Performance e Features
- Confusion matrix test set (TP/FP/FN/TN)
- Métricas detalhadas (Recall, Precision, F1, AUC)
- Feature importance top-10 (max_frame_count 15.2%, total_messages 12.8%)
- ROC curve interativa
- Uso: Entender modelo e drivers principais

#### 5. **Research Context (🔬)** - Jornada da Pesquisa
- **Seção 1:** Problema IoT battery instability (789 devices, imbalance 16.8:1)
- **Seção 2:** Timeline 4 fases (Temporal 0% → Stratified 50% → SMOTE 71.4% → CatBoost 78.6%)
- **Seção 3:** Descoberta data leakage (msg6_count/msg6_rate features)
- **Seção 4:** Feature engineering 29 features (Telemetry, Connectivity, Messaging)
- **Seção 5:** Descobertas técnicas (SMOTE effectiveness, algoritmo comparison)
- **Seção 6:** Lições aprendidas (5 princípios: empirical analysis, leakage prevention, imbalance handling, test validation, transparency)
- Uso: Stakeholders não-técnicos, onboarding novos membros, contexto decisões

### Screenshots
*(Adicionar screenshots futuras do app rodando)*

### 🌍 Nota - Tradução PT-BR Planejada
**Fase 14 (planejada):** Tradução completa do Streamlit app para português brasileiro com toggle EN/PT-BR na sidebar.

**Motivação:**
- Maioria dos stakeholders são brasileiros
- Research Context página beneficia de PT-BR (contexto técnico mais acessível)
- Boas práticas i18n para futuras expansões

**Implementação prevista:**
- `utils/translations.py` com dicionários bilíngues (EN/PT-BR)
- `st.sidebar.selectbox` para escolha idioma
- `st.session_state` para persistir preferência usuário
- Todas 5 páginas traduzidas (código/logs permanecem inglês)

**Estimativa:** ~60min desenvolvimento + testes

---

## 📚 Documentação Técnica

### Documentos Principais
- **[MODEL_COMPARISON.md](MODEL_COMPARISON.md):** Comparação formal XGBoost/LightGBM/CatBoost (350+ linhas)
  - Tabela comparativa métricas
  - Hyperparameters testados
  - Decision rationale (5 motivos técnicos)
  - Business impact (cenário 1000 devices)
  - Feature importance top-5
  - Testing methodology (stratified split, SMOTE, hold-out)
  - Deployment readiness

- **[CHANGELOG.md](CHANGELOG.md):** Timeline evolutiva completa 13 fases
  - Fase 1: Temporal split (DESCARTADO leakage)
  - Fase 2-3: Stratified split válido
  - Fase 4-5: Data leakage discovery & fix
  - Fase 6-9: Baseline → SMOTE → CatBoost → Pipeline
  - Fase 10-11: Organization & docs
  - Fase 12: Streamlit app (5 páginas)
  - Fase 13: Documentation (MODEL_COMPARISON.md + headers cleanup)

- **[notebooks/README.md](notebooks/README.md):** Guia notebooks individuais

- **[docs/LEAKAGE_DISCOVERY.md](docs/LEAKAGE_DISCOVERY.md):** Framework validação data leakage (7 testes)

### Features do Modelo (29 total)
**Categorias:**
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
