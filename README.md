# 🔋 Predição de Falhas em Sensores IoT
## Transformando Manutenção Corretiva em Preditiva através de Machine Learning

> **Projeto Final de Estágio | Fault Management Team | Lightera LLC**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-FF4B4B.svg)](https://streamlit.io)
[![CatBoost](https://img.shields.io/badge/CatBoost-1.2.8-yellow.svg)](https://catboost.ai)
[![Model v2](https://img.shields.io/badge/Model-v2.0%20FIELD--only-green.svg)]()

---

## 📋 Sobre o Projeto

Este projeto representa o **trabalho final de estágio** desenvolvido para o time de **Fault Management (Gestão de Falhas)** da Lightera LLC, com o objetivo de **investigar e validar a viabilidade de Machine Learning** para transformar a operação de manutenção de dispositivos IoT através da mudança de paradigma: de **manutenção corretiva** para **manutenção preditiva**.

### 🔬 Abordagem de Pesquisa

**Este projeto demonstra metodologia científica aplicada:** formulação de hipótese → desenvolvimento → validação crítica → pivots estratégicos → aprendizados documentados.

**Jornada de Desenvolvimento:**

1. **Hipótese Inicial:** "Padrões de telemetria (bateria, sinal, óptica) podem prever falhas de dispositivos IoT antes que ocorram?"

2. **v1.0 - Primeiro Modelo:** 78.6% recall com 789 dispositivos (aparentemente excelente)

3. **🔍 Discovery 0 - Pensamento Crítico:** Ao investigar false positive, **identifiquei contaminação de dados** não documentada:
   - 31.8% do dataset (362,343 mensagens) eram de ciclo FACTORY (testes de laboratório)
   - 27 dispositivos de 789 total eram pré-deployment
   - Métricas estavam infladas por padrões de teste, não produção real

4. **💡 Pivot Estratégico - Resiliência:** Em vez de ignorar problema, **escolhi qualidade de dados sobre métricas infladas**:
   - Filtrei dataset: 762 FIELD-only devices (100% produção)
   - Re-treinei v2.0: Recall caiu para 57.1% (-21.5%)
   - ROC-AUC melhorou +6.6% (0.8621 → 0.9186)
   - **Fundação limpa > métricas impressionantes**

5. **Tentativa de Melhoria v2.1:** Adicionei 3 temporal features (message_frequency, days_per_message, activity_ratio)
   - Resultado: +0.1% recall (insuficiente)
   - **Decisão baseada em critério:** Manter v2.0 57.1% baseline honesto

6. **Resultado:** **MVP validado** com baseline honesto (57.1%), insights acionáveis, e roadmap claro para FASE 3

**Demonstração de Skills:**
- ✅ **Proatividade:** Auto-auditoria que descobriu Discovery 0
- ✅ **Pensamento Crítico:** Questionei métricas "perfeitas", investiguei e encontrei contaminação
- ✅ **Resiliência:** Aceitei queda de -21.5% recall para garantir dados limpos
- ✅ **Rigor Científico:** Documentei limitações transparentemente (5 issues conhecidas)
- ✅ **Planejamento Estratégico:** FASE 3 roadmap com metas realistas

### O Desafio

Dispositivos IoT de telemetria na rede apresentam falhas inesperadas de bateria e conectividade que geram:
- 💸 **Custos emergenciais** elevados (até 3x mais que manutenção planejada)
- ⚡ **Downtime de serviço** imprevisto
- 🔧 **Desperdício de recursos técnicos** em inspeções reativas sem critério

### A Solução

Sistema preditivo baseado em **Machine Learning** que analisa padrões de comportamento de **762 dispositivos reais em campo** (bateria, sinal óptico, conectividade, mensageria) para identificar devices com **alta probabilidade de falha antes que ela ocorra**.

**Tecnologias:** CatBoost (gradient boosting), SMOTE (balanceamento de classes), Streamlit (interface web interativa).

### O Impacto

**Mudança de paradigma operacional:** permitindo ações preventivas, otimizando recursos técnicos e reduzindo custos através de decisões baseadas em dados, não em achismos.

---

## 💡 Valor para o Negócio

### Por que Machine Learning em Fault Management?

#### 🔻 Redução de Custos Operacionais
- Manutenções emergenciais custam até **3x mais** que preventivas
- Predição permite **planejamento de rotas e equipes** com antecedência
- **Redução de deslocamentos** desnecessários para inspeção manual

#### ⚡ Prevenção de Downtime
- Detecção antecipada evita **interrupções de serviço** ao cliente final
- Impacto direto na **satisfação do cliente** e reputação da empresa
- **SLA mais confiável e previsível**

#### 🎯 Otimização de Recursos Técnicos
- Foco em dispositivos de **alto risco** (baseado em probabilidade, não intuição)
- **Priorização inteligente** de manutenções por criticidade
- Melhor **alocação de equipes de campo** (menos desperdício)

#### 📊 Decisões Data-Driven
- **Insights quantitativos** substituem avaliações subjetivas
- Histórico de comportamento (30 features analisadas) vs inspeção manual
- **Transparência sobre drivers de falha**: bateria, sinal óptico, conectividade, mensageria

---

## 🚀 A Mudança de Paradigma: Corretiva → Preditiva

| Manutenção Corretiva (Tradicional) | Manutenção Preditiva (Machine Learning) |
|------------------------------------|------------------------------------------|
| ❌ Reagir **após** falha ocorrer | ✅ Agir **antes** da falha acontecer |
| ❌ Custos emergenciais 3x maiores | ✅ Manutenção planejada com antecedência |
| ❌ Downtime inesperado para cliente | ✅ Janelas de manutenção controladas |
| ❌ Inspeção baseada em achismos | ✅ Priorização por probabilidade ML |
| ❌ Visitas desnecessárias (desperdício) | ✅ Foco preciso em dispositivos de risco |
| ❌ Sem histórico de comportamento | ✅ Análise de 30 features de telemetria |

**Resultado esperado:** Redução de até **40% no tempo de resposta** a incidentes e **30% nos custos** de manutenção emergencial.

---

## 📊 Resultados Obtidos

### 🎯 Modelo v2 - Validado em Dados Reais de Produção

**Abordagem:** Pipeline completo com CatBoost + SMOTE 0.5, treinado **exclusivamente em dados de campo** (sem contaminação de laboratório).

**Dataset:** 762 dispositivos FIELD-only (removidos 27 devices de lifecycle FACTORY - pureza de dados garantida).

**Features:** 30 variáveis explicáveis (telemetria de bateria, sinal óptico, conectividade, mensageria, tempo de inatividade).

#### Performance (Test Set: 229 FIELD-only devices, 14 críticos)

**Baseline Threshold 0.50:**

- ✅ **Precision:** 57.1% (8 TP, 6 FP)
- ✅ **Recall:** 57.1% (8/14 dispositivos críticos detectados)
- ✅ **ROC-AUC:** 0.9186 - Excelente capacidade de discriminação
- ✅ **F1-Score:** 0.571 - Equilíbrio entre precision e recall
- ⚠️ **Miss Rate:** 42.9% (6/14 críticos NÃO detectados)

**Contexto de Performance:**

- Dataset pequeno: 46 amostras críticas (total), 14 em test set
- Hyperparameters default (sem tuning GridSearch)
- Trade-off consciente: dados limpos (57.1%) > métricas infladas (78.6% v1 contaminado)
- Uso recomendado: Sistema de alerta antecipado, NÃO ferramenta única de decisão
- ✅ **Recall:** 57.1% (8/14 dispositivos críticos detectados)
- ✅ **F1-Score:** 0.571 - Equilíbrio entre precision e recall
- ✅ **ROC-AUC:** 0.9186 - Excelente capacidade de discriminação
- ⚠️ **Miss Rate:** 42.9% (6/14 dispositivos críticos NÃO detectados)

**Contexto de Performance:**
- Dataset pequeno: 46 amostras críticas (total), 14 em test set
- Hyperparameters default CatBoost (sem tuning)
- Trade-off consciente: dados limpos (57.1%) > métricas infladas (78.6% v1 contaminado)
- Uso recomendado: Sistema de alerta antecipado com supervisão humana

#### 🔬 Contribuição Técnica: Discovery 0 - Demonstração de Pensamento Crítico

**Contexto:** Durante análise de false positive, **questionei se métricas "boas demais" poderiam esconder problemas**.

**Metodologia de Investigação:**

1. **Observação Inicial:** Device 861275072515287 alertado como crítico, mas operacional
2. **Hipótese:** "Padrão de mensagens incomum sugere lifecycle diferente de produção"
3. **Análise Exploratória:** 460 mensagens total = 179 FACTORY (39%) + 281 FIELD (61%)
4. **Validação em Larga Escala:** 31.8% de TODAS as mensagens eram FACTORY (não apenas 1 device)
5. **Pivot Estratégico:** Decisão de sacrificar métricas infladas por fundação limpa

**O Problema Descoberto:**
- **31.8% do dataset original** (362,343 mensagens) eram de ciclo de vida FACTORY (laboratório)
- 27 dispositivos de 789 total (3.4%) eram de testes pré-deployment
- Esses devices contaminavam os padrões de produção com assinaturas de testes de laboratório
- **Resultado:** Modelo v1 aprendia padrões de LAB, não CAMPO

**A Solução Implementada:**
- Filtro MODE='FIELD' aplicado em todo o dataset
- Dataset purificado: 762 devices (100% produção)
- Modelo v2 treinado exclusivamente em dados reais de campo
- Re-split estratificado: 533 train / 229 test (zero overlap)

**O Resultado da Decisão:**
- ROC-AUC melhorou **+6.6%** (0.8621 → 0.9186) - modelo discrimina melhor
- Recall reduziu -21.5% (78.6% → 57.1%) - **MAS com dados limpos e confiáveis**
- **Fundação sólida** validada cientificamente para melhorias futuras (FASE 3)
- **Demonstração de maturidade técnica:** data quality > model complexity

**Lições Aprendidas (Valor do Estágio):**
- ✅ **Pensamento Crítico:** Questionar resultados "perfeitos" levou à descoberta
- ✅ **Proatividade:** Auto-auditoria não solicitada identificou problema estrutural
- ✅ **Resiliência:** Escolher queda de métrica (-21.5%) para garantir qualidade
- ✅ **Rigor Científico:** Preferir baseline honesto (57.1%) a claims inflados (78.6%)
- ✅ **Comunicação:** Documentar Discovery 0 transparentemente para stakeholders

**Filosofia:** "2 passos atrás, 3 passos à frente" - sacrificar métricas infladas para garantir **rigor científico** e dados limpos que permitem evolução confiável.

### ⚠️ Limitações Conhecidas

**Transparência é valor fundamental deste projeto.** 10 limitações estão documentadas em [MODEL_V2_KNOWN_ISSUES.md](docs/MODEL_V2_KNOWN_ISSUES.md):

1. **Miss Rate 42.9%** - 6 de 14 dispositivos críticos não detectados no test set
2. **Dataset Pequeno** - Apenas 46 amostras críticas totais (ideal: 100+)
3. **Sem Hyperparameter Tuning** - Parâmetros default do CatBoost (iterations=100, depth=6)
4. **Signal Variance Ambiguity** - Features de sinal podem alertar para problemas ambientais, não do device
5. **Validação em Dataset Misto** - Experimentos conduzidos antes da limpeza FACTORY (métricas não aplicáveis)

**Recomendação de Uso:**
- ✅ Sistema de priorização para equipes de campo
- ✅ Dashboard de early warning combinado com monitoramento existente
- ✅ Human-in-the-loop (validação humana antes de ação)
- ❌ NÃO usar como único critério de decisão para manutenção
- ❌ NÃO para decisões autônomas sem supervisão técnica

**Roadmap FASE 3:** Temporal features (+20% recall projetado), hyperparameter tuning (+10% recall), data collection (100+ critical samples).

---

## 🌐 Democratização de Machine Learning

---

### ⚠️ Limitações Conhecidas

**Transparência é valor fundamental deste projeto.** As 10 limitações estão documentadas em [MODEL_V2_KNOWN_ISSUES.md](docs/MODEL_V2_KNOWN_ISSUES.md):

### Principais Constraints

1. **Miss Rate 42.9%** - 6 de 14 dispositivos críticos não detectados no test set
2. **Dataset Pequeno** - Apenas 46 amostras críticas no total (ideal: 100+)
3. **Sem Hyperparameter Tuning** - Parâmetros default do CatBoost utilizados
4. **Signal Variance Ambiguity** - Pode alertar para problemas ambientais/rede, não apenas do device
5. **Validação em Dataset Misto** - Experimentos de threshold foram conduzidos antes da limpeza FACTORY

### 🎯 Posicionamento: MVP como Fundação para Valor Real

**Status Atual:** Minimum Viable Product (MVP) validado cientificamente

**O que este projeto NÃO é:**
- ❌ Sistema de produção autônomo
- ❌ Ferramenta de decisão crítica sem supervisão
- ❌ Modelo otimizado com hyperparameter tuning
- ❌ Dataset grande (100+ critical samples)

**O que este projeto É:**
- ✅ **Prova de conceito validada:** ML É viável para fault prediction
- ✅ **Fundação técnica limpa:** Dados purificados, pipeline reproduzível
- ✅ **Insights acionáveis HOJE:** optical_below_threshold #1 preditor (use para inspeções manuais)
- ✅ **Roadmap claro FASE 3:** Temporal features (+20% recall), tuning (+10% recall)
- ✅ **Demonstração de processo:** Hypothesis → validation → pivots → learnings

**Valor Imediato (Sem Esperar FASE 3):**
1. **Feature Importance:** Use `optical_below_threshold` como critério de priorização manual
2. **Streamlit App:** Democratiza acesso a predições para perfis não-técnicos
3. **Discovery 0:** Identificação de data quality issue (valor metodológico)
4. **Pipeline Template:** Fundação para futuros modelos de fault prediction

**Roadmap para Valor Operacional Completo (FASE 3):**
- Temporal features avançadas: +20% recall projetado
- Hyperparameter tuning: +10-15% recall projetado
- Dataset expansion: 100+ critical samples (confiança estatística)
- Temporal validation: Time-based split para generalização
- **Target FASE 3:** 85%+ recall com fundação limpa

### Recomendações de Uso

✅ **USAR PARA:**
- Sistema de priorização para equipes de campo
- Dashboard de early warning (alerta antecipado)
- Human-in-the-loop (validação humana antes de ação)
- Planejamento de manutenção preventiva

❌ **NÃO USAR PARA:**
- Único critério de decisão para substituição de devices
- Decisões autônomas sem supervisão técnica
- Acionamento automático de alarmes críticos

**Roadmap FASE 3:** Temporal features (+20% recall projetado), hyperparameter tuning (+10% recall), target 85%+ recall.

---

## 🌐 Democratização de Machine Learning

### Streamlit Web Application - ML Acessível para Todos os Perfis

Um dos **principais valores deste projeto** é demonstrar que **Machine Learning não precisa ser restrito a cientistas de dados**. Através de uma **interface web interativa** (Streamlit), diferentes perfis profissionais podem utilizar os insights do modelo sem necessidade de programação:

**🌐 Acesso:** [https://lightera-iot-spd-app-main-lpqmr2.streamlit.app](https://lightera-iot-spd-app-main-lpqmr2.streamlit.app)

### 5 Páginas Interativas para Diferentes Perfis

#### 1. **Home (🏠)** - Dashboard Overview
**Perfil:** Gestores, Líderes Técnicos  
**Função:** Visão geral de métricas do modelo, status do dataset, versão do pipeline.

#### 2. **Batch Upload (📤)** - Predição em Lote
**Perfil:** Equipes de Operações, Analistas de Rede  
**Função:**
- Upload de CSV com dados de múltiplos dispositivos
- Validação automática de features (nomes, tipos, ranges)
- Predições em massa com probabilidades
- Download de resultados processados
- **Exemplo:** Processar 100+ devices simultaneamente para planejamento semanal de manutenção

#### 3. **Single Prediction (🔍)** - Predição Individual
**Perfil:** Engenheiros de Campo, Troubleshooting  
**Função:**
- Formulário interativo com 30 features
- Input manual ou uso de valores médios
- Predição instantânea com probabilidade
- Explicação clara do resultado (critical/normal)
- **Exemplo:** Testar cenários hipotéticos ou validar dispositivo específico reportado por cliente

#### 4. **Model Insights (📊)** - Performance e Interpretabilidade
**Perfil:** Engenheiros de ML, P&D, Auditoria  
**Função:**
- Confusion matrix (TP/FP/FN/TN)
- Métricas detalhadas (Recall, Precision, F1, ROC-AUC)
- Feature importance top-10 (drivers principais de falha)
- ROC curve interativa
- **Exemplo:** Entender quais variáveis (bateria, sinal) mais influenciam predições

#### 5. **Research Context (🔬)** - Jornada da Pesquisa
**Perfil:** Stakeholders, Novos membros do time, Apresentações executivas  
**Função:**
- Timeline de 4 fases de desenvolvimento
- Descobertas técnicas (data leakage, SMOTE effectiveness)
- Lições aprendidas (5 princípios: análise empírica, prevenção leakage, balanceamento, validação, transparência)
- Contexto de decisões tomadas
- **Exemplo:** Onboarding de novos estagiários ou apresentação executiva do projeto

---

## 🛠️ Como Machine Learning Pode Ser Usado Amplamente

Este projeto demonstra que **Machine Learning é acessível** para diferentes perfis profissionais, não apenas cientistas de dados:

| Perfil Profissional | Como Usa o Sistema | Valor Gerado |
|---------------------|-------------------|--------------|
| **Gestor de Operações** | Dashboard com métricas de risco | Planejamento de equipes e orçamento |
| **Engenheiro de Campo** | Predição individual de device | Priorização de visitas técnicas |
| **Analista de Rede** | Batch upload de dispositivos | Relatórios semanais de criticidade |
| **Líder Técnico** | Feature importance insights | Decisões sobre upgrades de hardware/firmware |
| **Time de P&D** | Model insights e ROC curve | Validação científica e melhorias futuras |

**Resultado:** Democratização de insights de ML - **sem necessidade de código**, apenas interface web intuitiva.

---

## 🚀 Instalação e Uso

### Pré-requisitos

- Python 3.12+
- pip (gerenciador de pacotes)

### 1. Clone o Repositório

```bash
git clone https://github.com/leonardobora-lightera/iot-sensor-failure-prediction.git
cd iot-sensor-failure-prediction
```

### 2. Instale Dependências

```bash
pip install -r requirements.txt
```

**Principais bibliotecas:**
- `catboost==1.2.8` (modelo de gradient boosting)
- `streamlit==1.45.1` (interface web)
- `scikit-learn`, `imbalanced-learn` (pipeline e SMOTE)
- `pandas`, `numpy` (manipulação de dados)
- `matplotlib`, `seaborn` (visualizações)

### 3. Execute o Streamlit App

```bash
streamlit run streamlit_app.py
```

**Acesso local:** http://localhost:8501

---

## 💻 Uso Programático (Para Desenvolvedores)

### Carregar Modelo v2

```python
import joblib
import pandas as pd

# Carregar pipeline completo (SimpleImputer → SMOTE → CatBoost)
pipeline = joblib.load('models/catboost_pipeline_v2_field_only.pkl')

# Carregar features (30 features esperadas)
df = pd.read_csv('data/device_features_with_telemetry_field_only.csv')

# Predizer
X = df.drop(['device_id', 'is_critical', 'is_critical_target', 'severity_category'], axis=1)
predictions = pipeline.predict(X)
probabilities = pipeline.predict_proba(X)[:, 1]

print(f"Dispositivos críticos detectados: {predictions.sum()}")
print(f"Probabilidade média de falha: {probabilities.mean():.2%}")
```

---

## 📊 Features do Modelo (30 Total)

O modelo analisa **30 variáveis explicáveis** agrupadas em 4 categorias:

### 1. Telemetria (18 features)
**Drivers principais de falha identificados:**
- **Bateria:** `battery_mean`, `battery_std`, `battery_min`, `battery_max`, `battery_below_threshold`
- **Sinal Óptico:** `optical_mean`, `optical_std`, `optical_min`, `optical_max`, `optical_readings`, `optical_below_threshold`, `optical_range`
- **Temperatura:** `temp_mean`, `temp_std`, `temp_min`, `temp_max`, `temp_above_threshold`, `temp_range`

### 2. Conectividade (9 features)
**Qualidade de sinal de rede:**
- **SNR:** `snr_mean`, `snr_std`, `snr_min` (Signal-to-Noise Ratio)
- **RSRP:** `rsrp_mean`, `rsrp_std`, `rsrp_min` (Reference Signal Received Power)
- **RSRQ:** `rsrq_mean`, `rsrq_std`, `rsrq_min` (Reference Signal Received Quality)

### 3. Mensageria (2 features)
**Padrões de comunicação:**
- `total_messages` (volume de mensagens do dispositivo)
- `max_frame_count` (maior tamanho de frame enviado)

### 4. Temporal (1 feature - v2)
**Detecção de inatividade:**
- `days_since_last_message` (dias desde última mensagem - identifica devices silenciosos)

**Features removidas (data leakage detectado):** `msg6_count`, `msg6_rate` (correlacionavam artificialmente com target).

---

## 📁 Estrutura do Projeto

```
iot_sensor_novembro/
├── streamlit_app.py                      # App principal Streamlit
├── pages/                                # 5 páginas interativas
│   ├── 1_Home.py                         # Dashboard overview
│   ├── 2_Batch_Upload.py                 # Predição em lote
│   ├── 3_Single_Predict.py               # Predição individual
│   ├── 4_Insights.py                     # Performance e features
│   └── 5_Research_Context.py             # Jornada da pesquisa
├── models/
│   ├── catboost_pipeline_v2_field_only.pkl   # Pipeline completo v2 (127 KB)
│   ├── catboost_pipeline_v2_metadata.json    # Metadata modelo v2
│   ├── registry.json                         # Registry de modelos (v2 active, v1 deprecated)
│   └── inference.py                          # Funções de inferência
├── data/
│   ├── device_features_with_telemetry_field_only.csv   # 762 devices FIELD
│   ├── device_features_train_stratified.csv            # Training set (533)
│   ├── device_features_test_stratified.csv             # Test set (229)
│   └── device_features_with_telemetry.csv              # Dataset mixed (histórico)
├── scripts/
│   ├── analyze_critical_devices.py       # Análise devices críticos
│   ├── feature_importance_analysis.py    # Importância de features
│   ├── threshold_adjustment_experiment.py  # Experimento thresholds
│   ├── metrics_discrepancy_investigation.py  # Debug métricas
│   ├── reproduce_results.py              # Reprodução resultados
│   ├── transform_aws_payload.py          # Transformação payload AWS
│   └── drift_monitor.py                  # Monitoramento drift (futuro)
├── analysis/                             # Outputs de análises
│   ├── feature_importance_complete.csv   # 30 features ranqueadas
│   ├── feature_importance_top15.png      # Visualização top-15
│   ├── threshold_experiment_results.csv  # Teste 7 thresholds
│   └── precision_recall_curve.png        # Curva PR
├── archive/                              # Experimentos históricos (não em produção)
│   ├── discovery_0/                      # Análise Discovery 0 (contamination)
│   ├── data_processing/                  # Scripts one-time processamento
│   ├── testing/                          # Testes temporários
│   ├── validation/                       # Validações ad-hoc
│   ├── analysis_nov14/                   # Análises específicas Nov 14
│   ├── fase2_planning/                   # Docs planejamento FASE 2
│   └── historical_docs/                  # Docs históricos v1
├── docs/
│   ├── MODEL_V2_VALIDATION_REPORT.md     # Relatório validação (8 seções)
│   ├── MODEL_V2_KNOWN_ISSUES.md          # Limitações documentadas (10)
│   ├── LEAKAGE_DISCOVERY.md              # Framework detecção leakage
│   ├── PROJECT_AUDIT_NOV17.md            # Auditoria preparação apresentação
│   └── FEATURE_ENGINEERING_TEMPORAL.md   # Roadmap features temporais
├── notebooks/                            # Análise exploratória (arquivados)
│   └── archive_v1/                       # Notebooks modelo v1
├── tests/                                # Testes unitários
├── utils/                                # Funções auxiliares
├── requirements.txt                      # Dependências Python
├── CHANGELOG.md                          # Timeline 13 fases
└── README.md                             # Este arquivo
```

---

## 📝 Documentação Completa

- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de versões e descobertas (incluindo Discovery 0)
- **[MODEL_V2_VALIDATION_REPORT.md](docs/MODEL_V2_VALIDATION_REPORT.md)** - Validação experimental (⚠️ Leia disclaimer sobre dataset)
- **[MODEL_V2_KNOWN_ISSUES.md](docs/MODEL_V2_KNOWN_ISSUES.md)** - 10 limitações documentadas transparentemente
- **[VALIDATION_CHECKLIST_V2.md](docs/VALIDATION_CHECKLIST_V2.md)** - Critérios de validação científica
- **[PLANO_ACAO_FIX_FALSOS_POSITIVOS.md](docs/PLANO_ACAO_FIX_FALSOS_POSITIVOS.md)** - Roadmap FASE 3

---

## 🙏 Agradecimentos

Este projeto de estágio foi desenvolvido com apoio e orientação do time de **Fault Management** da Lightera LLC. Agradecimento especial aos mentores que incentivaram **pensamento crítico, transparência e rigor científico** ao longo da jornada.

**Lições do Estágio:**
- Questionar resultados "perfeitos" leva a descobertas reais (Discovery 0)
- Dados limpos > métricas impressionantes
- Transparência sobre limitações > claims inflados
- Resiliência para aceitar quedas métricas (-21.5%) quando necessário
- MVP bem fundamentado > sistema "production-ready" sem validação

---

**Última atualização:** 18 de Novembro de 2025 (v2.0 FIELD-only + Discovery 0 + Research Methodology)  
**Autor:** Leonardo Costa | Lightera LLC Internship  
**Contato:** leonardo.costa@lightera.com
- **[CHANGELOG.md](CHANGELOG.md):** Timeline evolutiva completa (13 fases de desenvolvimento)
- **[PROJECT_AUDIT_NOV17.md](docs/PROJECT_AUDIT_NOV17.md):** Auditoria de preparação para apresentação final

---

## 🛣️ Roadmap Futuro (FASE 3)

### Oportunidades de Melhoria

#### 1. Temporal Features Avançadas (Prioridade Alta)
**Objetivo:** Aumentar recall através de padrões temporais
- `deployment_age` (idade do dispositivo em rede)
- `msg_last_7days`, `msg_last_30days` (volume de mensagens recente)
- `battery_degradation_rate` (taxa de degradação)
- **Impacto esperado:** +15-20% recall

#### 2. Hyperparameter Tuning
**Objetivo:** Otimizar parâmetros do CatBoost
- GridSearch: `depth`, `iterations`, `learning_rate`, `l2_leaf_reg`
- Cross-validation estratificada (5-fold)
- **Impacto esperado:** +5-10% precision/recall

#### 3. Threshold Calibration
**Objetivo:** Ajustar limiar de decisão para balancear precisão/recall
- ROC curve optimization (Youden's Index)
- Business-driven threshold (custo FP vs FN)
- **Target:** Precision >60%, Recall >60%

#### 4. Validação com Ground Truth
**Objetivo:** Confirmar predições com feedback de campo
- Integração com sistema de tickets de manutenção
- Tracking de devices preditos como críticos
- Refinamento contínuo do modelo

---

## 👥 Autor & Contexto

**Autor:** Leonardo Costa  
**Posição:** Estagiário de Engenharia de Software - P&D  
**Instituição:** UniBrasil Centro Universitário (8° período)  
**Empresa:** Lightera LLC  
**Time:** Fault Management (Gestão de Falhas)  
**Período:** Outubro - Novembro 2025  
**Projeto:** Trabalho Final de Estágio

### Sobre o Estágio

Este projeto representa a **culminação de um estágio focado em aplicar Machine Learning a problemas reais de operações de rede IoT**, demonstrando:

1. **Rigor científico:** Detecção e correção de data leakage (Discovery 0)
2. **Pensamento estratégico:** Trade-off recall vs dados limpos (fundação sólida)
3. **Impacto no negócio:** Mudança de paradigma corretiva → preditiva
4. **Democratização de ML:** Interface acessível para diferentes perfis (Streamlit)
5. **Documentação profissional:** 5 relatórios técnicos, changelog completo, código comentado
6. **Transparência:** 10 limitações documentadas (honestidade científica)

**Filosofia do projeto:** "Machine Learning não é mágica - é um processo empírico, iterativo e transparente que gera valor quando alinhado às necessidades reais do negócio."

---

## 📄 Licença

Propriedade da **Lightera LLC** © 2025  
Todos os direitos reservados.

---

**Última Atualização:** 18 de Novembro de 2025  
**Versão Modelo:** v2.0 FIELD-only (CatBoost + SMOTE 0.5)  
**Métricas Baseline:** 57.1% precision/recall (229 FIELD-only test set)  
**Streamlit App:** 5 páginas bilíngues (EN/PT-BR), deploy em produção

---

## 🙏 Agradecimentos

Agradecimentos ao time de **Fault Management** da Lightera LLC pelo suporte, ao **GitHub Copilot** pela assistência durante o desenvolvimento, e a todos os stakeholders que forneceram feedback durante o processo de validação.
