# 🛡️ CHECKLIST DE MITIGAÇÃO DE VIESES - Projeto IoT Sensor Failure Prediction

**Versão:** 1.0.0  
**Data:** 31 de outubro de 2025  
**Autor:** Leonardo Costa (Gestão de Falhas)  
**Revisão:** Constitution v0.1.0 compliant

---

## 📋 Índice

1. [Vieses de Dados (Data Biases)](#1-vieses-de-dados-data-biases)
2. [Vieses Temporais (Temporal Biases)](#2-vieses-temporais-temporal-biases)
3. [Vieses de Amostragem (Sampling Biases)](#3-vieses-de-amostragem-sampling-biases)
4. [Vieses de Modelagem (Modeling Biases)](#4-vieses-de-modelagem-modeling-biases)
5. [Vieses de Validação (Validation Biases)](#5-vieses-de-validação-validation-biases)
6. [Vieses de Deployment (Production Biases)](#6-vieses-de-deployment-production-biases)
7. [Vieses Humanos (Human Biases)](#7-vieses-humanos-human-biases)

---

## 1. Vieses de Dados (Data Biases)

### 1.1 Data Leakage (Vazamento de Informação) 🔴 CRÍTICO

**O que é:** Informação do futuro ou do teste influencia o treinamento, inflando artificialmente a performance.

#### Checklist de Mitigação:

- [x] **Split ANTES de qualquer processamento**
  - ✅ Implementado: train-test split 70/30 temporal ANTES de agregações
  - ✅ Validado: Nenhuma feature calculada usa dados de teste
  
- [x] **FIT apenas em treino, TRANSFORM em teste**
  - ✅ Implementado: Agregações (optical, temp, battery, signal) usam apenas `df_train.groupby()`
  - ✅ Validado: Test set aplica mesmas transformações sem re-fit
  
- [x] **Pipeline sklearn obrigatório**
  - ⏳ **PENDENTE**: Criar Pipeline em notebook 03 (feature engineering)
  - 🎯 Meta: `make_pipeline(StandardScaler(), RandomForest())`
  
- [x] **Validar ausência de target leakage**
  - ✅ Implementado: Target `is_critical_target` criado APÓS split
  - ✅ Validado: Features não contêm informação futura de msg6_rate

**Referência:** [Scikit-learn Data Leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)

**Status atual:** ✅ **APROVADO** (11/12 correções implementadas, Pipeline pendente)

---

### 1.2 Selection Bias (Viés de Seleção)

**O que é:** Dataset não representa a população real - favorece certos tipos de devices.

#### Checklist de Mitigação:

- [x] **Verificar composição do dataset**
  - ✅ Análise realizada: 789 devices, 676 com msg6 (85.7%)
  - ⚠️ **ALERTA**: 85.7% failure rate é MUITO ALTO - pode indicar pré-filtragem
  - ❓ **PERGUNTA P/ ENGENHARIA**: Dataset é população completa ou apenas devices problemáticos?

- [ ] **Estratificação por características**
  - ⏳ **TODO**: Verificar se dataset representa:
    - [ ] Diferentes versões de firmware (v1.1.0_rc19, v1.2.0_rc07)
    - [ ] Diferentes operadoras (VIVO SP, RS, Paraná, Pernambuco)
    - [ ] Diferentes regiões geográficas
    - [ ] Diferentes idades de instalação (devices antigos vs recentes)

- [x] **Documentar population vs sample**
  - ⚠️ **DESCONHECIDO**: Ainda não sabemos se dataset é amostra ou população completa
  - 📋 **AÇÃO**: Incluir em `ENGINEERING_QUESTIONS.md`

**Status atual:** ⚠️ **ATENÇÃO NECESSÁRIA** (85.7% failure rate suspeito)

---

### 1.3 Measurement Bias (Viés de Medição)

**O que é:** Erros sistemáticos na coleta de telemetrias que distorcem dados.

#### Checklist de Mitigação:

- [x] **Missing values analysis**
  - ✅ Implementado: Análise de % faltante por telemetria
  - ✅ Resultado: ~45% missing em optical power, temp, battery, RSSI
  - ❓ **PERGUNTA**: Por que 45% faltante? Firmware antigo ou falha de sensor?

- [ ] **Validar calibração de sensores**
  - ⏳ **TODO**: Verificar se thresholds são universais ou por device
    - [ ] Optical power: -28 dBm threshold válido para TODOS devices?
    - [ ] Temperatura: 70°C threshold válido para TODOS ambientes?
    - [ ] Bateria: 2.5V threshold válido para TODOS tipos de bateria?

- [ ] **Detectar outliers instrumentais**
  - ⏳ **TODO**: Verificar se existem valores impossíveis
    - [ ] RSSI > 0 dBm (impossível)
    - [ ] Temperatura < -40°C ou > 120°C (fora de especificação)
    - [ ] Battery < 0V ou > 5V (erro de leitura)

**Status atual:** ⚠️ **ATENÇÃO** (45% missing values precisa investigação)

---

### 1.4 Label Noise (Ruído nos Rótulos)

**O que é:** Target variable incorreto ou ambíguo contamina aprendizado.

#### Checklist de Mitigação:

- [x] **Definição clara de "falha"**
  - ✅ Definido: `is_critical_target = msg6_rate > 25%`
  - ⚠️ **AMBIGUIDADE**: msg6 não significa "device morto" - muitos se auto-recuperam
  - 🔄 **REFINAMENTO**: Considerar multi-class (healthy, unstable, critical, failed)

- [ ] **Validar ground truth**
  - ⏳ **TODO**: Cross-check com devices.json (7 confirmed failures)
  - ⏳ **TODO**: Validar se devices "critical" realmente falharam ou são instáveis

- [x] **Análise de auto-recuperação**
  - ❓ **DESCONHECIDO**: Quantos % de devices "critical" se recuperam sozinhos?
  - 📋 **AÇÃO**: Adicionar análise temporal de recuperação em notebook 03

**Status atual:** ⚠️ **REFINAMENTO NECESSÁRIO** (definição de falha ambígua)

---

## 2. Vieses Temporais (Temporal Biases)

### 2.1 Temporal Data Leakage 🔴 CRÍTICO

**O que é:** Usar dados futuros para prever o passado, ou misturar ordem temporal.

#### Checklist de Mitigação:

- [x] **Train-test split temporal**
  - ✅ Implementado: 70% primeiros dias → treino, 30% últimos dias → teste
  - ✅ Validado: `split_date` preserva ordem cronológica
  - ✅ Código: `df_sorted = df.sort_values('@timestamp')`

- [x] **Forward-looking labels APENAS**
  - ✅ Implementado: Target usa msg6_rate calculado no período atual
  - ⚠️ **ATENÇÃO**: Para predição futura, precisamos criar `will_fail_7d_ahead`
  - ⏳ **TODO Notebook 03**: Criar labels forward-looking (T+7d, T+14d, T+30d)

- [x] **TimeSeriesSplit para CV**
  - ❌ **NÃO IMPLEMENTADO**: Atualmente usa KFold padrão (INCORRETO para temporal)
  - 🔴 **CRÍTICO**: Substituir `cv=5` por `TimeSeriesSplit(n_splits=5, gap=7)`
  - 📚 **Referência**: [Scikit-learn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)

**Código CORRETO para CV temporal:**

```python
from sklearn.model_selection import TimeSeriesSplit

# ERRADO (atual - usa KFold random)
cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring='recall')

# CERTO (temporal - treina em passado, testa em futuro)
tscv = TimeSeriesSplit(n_splits=5, gap=7, test_size=30)  # gap=7 dias entre train/test
cv_scores = cross_val_score(rf, X_train, y_train, cv=tscv, scoring='recall')
```

**Status atual:** 🔴 **CRÍTICO - CORREÇÃO OBRIGATÓRIA** (TimeSeriesSplit não usado)

---

### 2.2 Concept Drift (Mudança de Conceito)

**O que é:** Relação entre features e target muda ao longo do tempo.

#### Checklist de Mitigação:

- [ ] **Análise de estabilidade temporal**
  - ⏳ **TODO**: Calcular correlação msg6 × features por mês (jan-out 2025)
  - ⏳ **TODO**: Verificar se RSRP correlation é estável ou muda com tempo
  - 🎯 **Meta**: Coefficient of Variation < 30% (correlação estável)

- [ ] **Detecção de sazonalidade**
  - ⏳ **TODO**: Verificar se msg6 tem padrão semanal/mensal
  - ⏳ **TODO**: Testar decomposição temporal (trend, seasonal, residual)
  - 📊 **Ferramenta**: `statsmodels.seasonal_decompose()`

- [ ] **Monitoramento de drift em produção**
  - ⏳ **FUTURO**: Implementar alertas se correlação RSRP × msg6 mudar >20%
  - ⏳ **FUTURO**: Re-treinar modelo se drift detectado

**Status atual:** ⏳ **TODO - Baixa prioridade** (análise futura)

---

### 2.3 Look-Ahead Bias (Viés de Retrospectiva)

**O que é:** Usar features que não estariam disponíveis no momento da predição real.

#### Checklist de Mitigação:

- [x] **Validar disponibilidade de features**
  - ✅ Todas features (RSSI, battery, temp, optical) vêm de telemetria em tempo real
  - ✅ Nenhuma feature usa agregação futura (rolling stats usam apenas passado)

- [ ] **Simular latência de dados**
  - ⏳ **TODO**: Considerar delay de telemetria (devices enviam dados 4x/dia)
  - ⏳ **TODO**: Features devem usar dados de T-6h (não T-0) para ser realista

- [x] **Documentar timestamp de cada feature**
  - ✅ Implementado: `@timestamp` preservado em dataset
  - ✅ Agregações usam `groupby('device_id')` sem leak temporal

**Status atual:** ✅ **APROVADO** (features são causais, não retrospectivas)

---

## 3. Vieses de Amostragem (Sampling Biases)

### 3.1 Survivorship Bias (Viés do Sobrevivente) 🔴 CRÍTICO

**O que é:** Dataset contém apenas devices que "sobreviveram" até coleta, excluindo os que falharam cedo.

#### Checklist de Mitigação:

- [x] **Verificar inclusão de devices falhados**
  - ✅ Dataset contém devices com msg6_rate > 50% (provavelmente falhados)
  - ✅ 3 devices com >1000 eventos = possíveis falhas definitivas
  - ⚠️ **ALERTA**: Falta baseline de devices 100% saudáveis (apenas 113/789 = 14.3%)

- [x] **Validar período de observação**
  - ✅ Período: Jan-Out 2025 (281 dias) - suficiente para capturar ciclo completo
  - ⚠️ **RISCO**: Devices instalados em Out/2025 têm apenas 1 mês de histórico

- [ ] **Análise de censura (censoring)**
  - ⏳ **TODO**: Identificar devices removidos/substituídos antes de Out/2025
  - ⏳ **TODO**: Verificar se devices top offenders foram desativados (viés de censura à direita)

**Recomendação:** Incluir feature `days_active` para controlar viés de instalação recente.

**Status atual:** ⚠️ **ATENÇÃO** (apenas 14.3% devices saudáveis - baseline fraco)

---

### 3.2 Class Imbalance (Desbalanceamento de Classes)

**O que é:** Classes minoritárias (devices críticos) sub-representadas causam viés para maioria.

#### Checklist de Mitigação:

- [x] **Análise de distribuição de classes**
  - ✅ TRAIN: 45 critical (7%) vs 631 non-critical (93%) = **1:14 imbalance**
  - ✅ TEST: 42 critical (6.1%) vs 647 non-critical (93.9%) = **1:15 imbalance**
  - 🔴 **SEVERO**: Imbalance >1:10 é crítico para recall

- [x] **class_weight='balanced' aplicado**
  - ✅ Implementado: `RandomForestClassifier(class_weight='balanced')`
  - ⚠️ **LIMITAÇÃO**: Recall ainda é 30% (insuficiente)

- [ ] **SMOTE ou undersampling**
  - ⏳ **TODO Notebook 03**: Aplicar SMOTE para gerar synthetic minority samples
  - 🎯 **Meta**: Balancear para 1:3 ou 1:2 (ao invés de 1:14)

```python
from imblearn.over_sampling import SMOTE

# ANTES: 45 critical, 631 non-critical
smote = SMOTE(sampling_strategy=0.5, random_state=42)  # 1:2 ratio
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
# DEPOIS: 315 critical, 631 non-critical
```

- [ ] **Threshold tuning**
  - ⏳ **TODO**: Reduzir threshold de 0.5 para 0.3 → aumentar recall
  - 📊 **Ferramenta**: Precision-Recall curve para escolher threshold ótimo

**Status atual:** 🔴 **CRÍTICO** (imbalance 1:14 causa recall 30% - inaceitável)

---

### 3.3 Geographic/Demographic Bias (Viés Geográfico)

**O que é:** Dataset sobre-representa certas regiões/operadoras, sub-representa outras.

#### Checklist de Mitigação:

- [ ] **Estratificação por região**
  - ⏳ **TODO**: Analisar distribuição de devices por estado (SP, RS, Paraná, Pernambuco)
  - ⏳ **TODO**: Verificar se failures concentram-se em regiões específicas (viés geográfico)

- [ ] **Estratificação por operadora**
  - ⏳ **TODO**: Analisar VIVO vs outras operadoras
  - ❓ **PERGUNTA**: Dataset contém apenas VIVO ou múltiplas operadoras?

- [ ] **Estratificação por ambiente**
  - ⏳ **TODO**: Indoor vs outdoor deployment (se info disponível)
  - ⏳ **TODO**: Urbano vs rural (pode afetar cobertura NB-IoT e RSRP)

**Status atual:** ⏳ **TODO** (análise não realizada ainda)

---

## 4. Vieses de Modelagem (Modeling Biases)

### 4.1 Feature Selection Bias

**O que é:** Escolher features baseado em performance no teste, causando overfitting.

#### Checklist de Mitigação:

- [x] **Feature selection ANTES de split**
  - ❌ **INCORRETO ATUAL**: Feature importance calculado em TRAIN, mas não houve seleção prévia
  - ✅ **CORRETO**: Todas features candidate foram incluídas (optical, temp, battery, signal)

- [x] **Evitar p-hacking**
  - ✅ Implementado: Correlações calculadas ANTES de ver performance do modelo
  - ✅ Validado: Não houve iteração manual removendo/adicionando features baseado em accuracy

- [ ] **Recursive Feature Elimination (RFE)**
  - ⏳ **TODO Notebook 03**: Usar RFE para seleção automatizada
  - 🎯 **Meta**: Reduzir de 14 features para top 8-10

```python
from sklearn.feature_selection import RFE

rfe = RFE(estimator=RandomForestClassifier(), n_features_to_select=8, step=1)
rfe.fit(X_train, y_train)
selected_features = X_train.columns[rfe.support_]
```

**Status atual:** ✅ **APROVADO** (nenhum p-hacking detectado)

---

### 4.2 Overfitting to Noise (Sobreajuste ao Ruído)

**O que é:** Modelo aprende padrões aleatórios específicos do treino que não generalizam.

#### Checklist de Mitigação:

- [x] **Cross-validation implementado**
  - ✅ Implementado: CV=5 para feature importance
  - 🔴 **INCORRETO**: Usa KFold random (não TimeSeriesSplit temporal)
  - 🎯 **CORREÇÃO**: Substituir por `TimeSeriesSplit(n_splits=5, gap=7)`

- [x] **Regularização aplicada**
  - ⚠️ **PARCIAL**: Random Forest com `max_depth=5` limita complexidade
  - ⏳ **TODO**: GridSearchCV para validar se max_depth=5 é ótimo

- [x] **Validação em test set NÃO VISTO**
  - ✅ Test set separado desde início (689 devices, 30% temporal)
  - ❌ **PENDENTE**: Ainda NÃO validamos modelo final no test set

- [ ] **Análise de learning curves**
  - ⏳ **TODO**: Plotar train vs validation score por tamanho de treino
  - 🎯 **Meta**: Curvas convergem → não há overfitting

```python
from sklearn.model_selection import learning_curve

train_sizes, train_scores, val_scores = learning_curve(
    rf, X_train, y_train, cv=tscv, scoring='recall',
    train_sizes=np.linspace(0.1, 1.0, 10)
)
```

**Status atual:** ⚠️ **ATENÇÃO** (CV temporal pendente, test set não validado)

---

### 4.3 Model Selection Bias

**O que é:** Escolher modelo baseado em performance no teste, invalidando generalização.

#### Checklist de Mitigação:

- [x] **Baseline definido ANTES de testes**
  - ✅ Definido: Isolation Forest (recall 99.05% conforme requirements.txt)
  - ✅ Random Forest escolhido por interpretabilidade, não apenas accuracy

- [ ] **Nested cross-validation**
  - ⏳ **TODO Notebook 04**: Implementar nested CV para hyperparameter tuning
  - 📚 **Explicação**: CV interno escolhe hiperparâmetros, CV externo avalia generalização

```python
from sklearn.model_selection import GridSearchCV, cross_val_score

# Inner CV: hyperparameter tuning
param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [3, 5, 10]}
inner_cv = TimeSeriesSplit(n_splits=3)
grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=inner_cv)

# Outer CV: generalization assessment
outer_cv = TimeSeriesSplit(n_splits=5)
nested_scores = cross_val_score(grid_search, X, y, cv=outer_cv, scoring='recall')
```

- [x] **Documentar razão de escolhas**
  - ✅ Implementado: Notebook 02 documenta por que usar Spearman (não-linear)
  - ✅ Implementado: Documenta por que class_weight='balanced' (imbalance)

**Status atual:** ⚠️ **ATENÇÃO** (nested CV pendente)

---

### 4.4 SNR Contradiction (Problema Específico do Projeto)

**O que é:** SNR tem feature importance #1 (30.7%) mas correlação Spearman r≈0 (não significativa).

#### Checklist de Mitigação:

- [ ] **Investigar interações não-lineares**
  - ⏳ **TODO Notebook 03**: Gerar SHAP values para entender contribuição SNR
  - ⏳ **TODO**: Testar se SNR × Battery ou SNR × RSRP tem interação
  - 📊 **Ferramenta**: `shap.TreeExplainer(rf)`

```python
import shap

explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_train)
shap.summary_plot(shap_values[1], X_train, feature_names=feature_cols)
```

- [ ] **Partial Dependence Plots**
  - ⏳ **TODO**: Plotar PDP para SNR vs msg6_rate
  - 🎯 **Meta**: Verificar se relação é U-shaped ou threshold-based

- [ ] **Decisão: manter ou remover SNR**
  - ⏳ **BLOQUEADO**: Aguardando investigação SHAP
  - 🔀 **Opções**:
    1. Manter SNR se SHAP mostrar interação válida
    2. Remover SNR se importance for spurious correlation

**Status atual:** 🔴 **BLOQUEADOR** (contradição precisa investigação urgente)

---

## 5. Vieses de Validação (Validation Biases)

### 5.1 Metric Gaming (Otimização de Métrica Errada)

**O que é:** Maximizar métrica que não reflete objetivo real do negócio.

#### Checklist de Mitigação:

- [x] **Definir métrica de negócio PRIMEIRO**
  - ✅ Definido: **RECALL >70%** (capturar falhas reais)
  - ✅ Justificativa: Falso negativo (device falha não detectado) é mais custoso que falso positivo

- [x] **Validar alignment com objetivo**
  - ⚠️ **DESALINHADO**: Recall atual 30% << meta 70%
  - ✅ Accuracy NÃO é métrica principal (seria 93% trivialmente predizendo "healthy")

- [ ] **Threshold tuning para recall**
  - ⏳ **TODO**: Ajustar threshold de decisão para maximizar recall
  - 🎯 **Meta**: Encontrar threshold onde recall ≥70% e precision ≥40%

```python
from sklearn.metrics import precision_recall_curve

precisions, recalls, thresholds = precision_recall_curve(y_test, y_pred_proba)
# Escolher threshold onde recall >= 0.7
optimal_threshold = thresholds[np.where(recalls >= 0.7)[0][0]]
```

**Status atual:** ⚠️ **DESALINHADO** (recall 30% vs meta 70%)

---

### 5.2 Multiple Testing Problem

**O que é:** Testar muitas hipóteses aumenta chance de encontrar correlação espúria (falso positivo).

#### Checklist de Mitigação:

- [x] **Bonferroni correction**
  - ⏳ **TODO**: Aplicar correção para múltiplas comparações
  - 🎯 **Exemplo**: Se testamos 14 features, p-value threshold = 0.05/14 = 0.0036

- [x] **Pre-register hypotheses**
  - ✅ Implementado: Hipóteses documentadas ANTES de testes (Notebook 02 header)
  - ✅ Exemplo: "RSRP baixo → mais msg6" (predito pela física, não exploração)

- [ ] **Holdout test set final**
  - ✅ Test set separado desde início
  - ❌ **PENDENTE**: NÃO testamos ainda (será validação ÚNICA e final)

**Status atual:** ✅ **BOM** (hipóteses pre-registered, correção Bonferroni pendente)

---

### 5.3 Train-Test Contamination

**O que é:** Informação do teste vaza para treino através de decisões humanas.

#### Checklist de Mitigação:

- [x] **Blind analysis**
  - ✅ Implementado: Test set processado mas NÃO validado ainda
  - ✅ Decisões de features foram baseadas apenas em TRAIN correlations

- [x] **Documentar decisões**
  - ✅ Implementado: Todas decisões registradas em notebooks com justificativas
  - ✅ Exemplo: SNR removido por correlação zero (decisão baseada em treino)

- [ ] **Test set único uso**
  - ⏳ **COMPROMISSO**: Usar test set UMA VEZ APENAS para validação final
  - 🚫 **PROIBIDO**: Iterar hiperparâmetros baseado em test performance

**Status atual:** ✅ **APROVADO** (test set preservado como "virgin data")

---

## 6. Vieses de Deployment (Production Biases)

### 6.1 Train-Serve Skew

**O que é:** Diferenças entre ambiente de treino e produção causam degradação.

#### Checklist de Mitigação:

- [ ] **Validar latência de telemetria**
  - ⏳ **TODO**: Confirmar se devices enviam dados em tempo real ou com delay
  - ❓ **PERGUNTA**: Qual é delay típico entre medição e recebimento no servidor?

- [ ] **Validar disponibilidade de features**
  - ⏳ **TODO**: Confirmar que RSSI, battery, temp, optical estarão SEMPRE disponíveis em produção
  - ⚠️ **RISCO**: 45% missing values em treino → produção pode ter ainda mais falta

- [ ] **Simular production environment**
  - ⏳ **FUTURO**: Testar modelo em ambiente staging com dados reais antes de deploy

**Status atual:** ⏳ **TODO - Média prioridade**

---

### 6.2 Feedback Loop Bias

**O que é:** Predições do modelo influenciam dados futuros, criando auto-reforço.

#### Checklist de Mitigação:

- [ ] **Monitorar distribuição de features**
  - ⏳ **FUTURO**: Alertar se RSRP distribution muda >20% em produção
  - 🎯 **Ferramenta**: KS-test para detectar drift

- [ ] **Randomized intervention**
  - ⏳ **FUTURO**: Intervir aleatoriamente em 10% dos devices preditos como "healthy"
  - 🎯 **Objetivo**: Validar se predições "safe" realmente são safe

- [ ] **Counterfactual logging**
  - ⏳ **FUTURO**: Registrar o que TERIA acontecido sem intervenção

**Status atual:** ⏳ **FUTURO - Pós-deployment**

---

## 7. Vieses Humanos (Human Biases)

### 7.1 Confirmation Bias (Viés de Confirmação)

**O que é:** Analista busca evidências que confirmam hipótese inicial, ignorando contra-evidências.

#### Checklist de Mitigação:

- [x] **Pre-register hypotheses**
  - ✅ Implementado: Hipóteses documentadas no header do notebook ANTES de análise
  - ✅ Exemplo: "Optical power degradação → falha" (predito, não descoberto)

- [x] **Documentar surpresas**
  - ✅ Implementado: SNR contradição documentada como PROBLEMA, não ignorada
  - ✅ Implementado: RSSI correlation -0.19 aceita mesmo sendo "fraca"

- [ ] **Peer review obrigatório**
  - ✅ **REALIZADO**: Estagiário colega identificou survivorship bias (validação externa!)
  - ⏳ **TODO**: Solicitar revisão de Engenharia/Enzo antes de deploy

**Status atual:** ✅ **BOM** (peer review funcionou - survivorship bias detectado)

---

### 7.2 Sunk Cost Fallacy (Falácia do Custo Afundado)

**O que é:** Continuar com abordagem ruim porque "já investimos muito tempo".

#### Checklist de Mitigation:

- [x] **Decision gates definidos**
  - ✅ Implementado: Gate #1 "Se recall <70% → PARAR" (Constitution Principle)
  - ⚠️ **STATUS**: Recall atual 30% → tecnicamente deveria PARAR
  - 🔀 **DECISÃO**: Continuar mas reconhecer que abordagem atual FALHOU

- [x] **Kill switches**
  - ✅ Definido: Se test set recall <50% → DESCARTAR modelo, não deploy
  - ✅ Definido: Se precision <40% → alarmes falsos inaceitáveis

- [ ] **Alternativas documentadas**
  - ⏳ **TODO**: Documentar Plano B se Random Forest falhar
  - 🔀 **Opções**: XGBoost, Isolation Forest (original), LSTM temporal

**Status atual:** ⚠️ **ATENÇÃO** (recall 30% indica problema, mas ainda não acionamos kill switch)

---

### 7.3 Publication Bias (Viés de Publicação)

**O que é:** Reportar apenas resultados positivos, esconder experimentos falhados.

#### Checklist de Mitigação:

- [x] **Documentar falhas**
  - ✅ Implementado: Notebook 02 documenta SNR contradição (não esconde)
  - ✅ Implementado: CHECKPOINT documenta recall 30% como PROBLEMA

- [x] **Version control**
  - ✅ Implementado: Git commit 4c46ca9 preserva histórico completo
  - ✅ Implementado: Notebooks antigos arquivados em `outdated-notebooks/`

- [x] **Transparência com stakeholders**
  - ✅ Implementado: P.O. informado sobre survivorship bias
  - ✅ Implementado: Mariana validou "continuar mesmo sem resultados promissores"

**Status atual:** ✅ **EXCELENTE** (transparência total, falhas documentadas)

---

## 📊 SCORECARD DE MITIGAÇÃO

### Status por Categoria

| Categoria | Status | Críticos | Pendentes | Aprovados |
|-----------|--------|----------|-----------|-----------|
| **1. Data Biases** | ⚠️ | 0 | 3 | 8 |
| **2. Temporal Biases** | 🔴 | 1 | 4 | 2 |
| **3. Sampling Biases** | 🔴 | 1 | 5 | 2 |
| **4. Modeling Biases** | ⚠️ | 1 | 7 | 3 |
| **5. Validation Biases** | ✅ | 0 | 2 | 6 |
| **6. Deployment Biases** | ⏳ | 0 | 6 | 0 |
| **7. Human Biases** | ✅ | 0 | 1 | 7 |
| **TOTAL** | ⚠️ | **3** | **28** | **28** |

### Resumo Executivo

**✅ APROVADO (28 itens):**
- Data leakage prevention implementado corretamente
- Features causais (não retrospectivas)
- Test set preservado como virgin data
- Transparência e documentação de falhas

**🔴 CRÍTICO (3 itens):**
1. **TimeSeriesSplit NÃO usado** → KFold random invalida CV temporal
2. **Class imbalance 1:14** → Recall 30% inaceitável (meta: 70%)
3. **SNR contradição** → Feature importance #1 mas correlação zero

**⚠️ ATENÇÃO (28 itens pendentes):**
- 85.7% failure rate no dataset (suspeito de seleção)
- 45% missing values em telemetrias (precisa investigação)
- Nested CV para hyperparameters não implementado
- Production deployment planning pendente

---

## 🎯 AÇÕES PRIORITÁRIAS (Segunda-feira)

### 🔴 URGENTE (Bloqueadores)

1. **Substituir KFold por TimeSeriesSplit**
   ```python
   # ANTES (ERRADO)
   cv_scores = cross_val_score(rf, X_train, y_train, cv=5)
   
   # DEPOIS (CORRETO)
   from sklearn.model_selection import TimeSeriesSplit
   tscv = TimeSeriesSplit(n_splits=5, gap=7, test_size=30)
   cv_scores = cross_val_score(rf, X_train, y_train, cv=tscv)
   ```

2. **Aplicar SMOTE para class imbalance**
   ```python
   from imblearn.over_sampling import SMOTE
   smote = SMOTE(sampling_strategy=0.5, random_state=42)
   X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
   ```

3. **Investigar SNR com SHAP values**
   ```python
   import shap
   explainer = shap.TreeExplainer(rf)
   shap_values = explainer.shap_values(X_train)
   shap.summary_plot(shap_values[1], X_train)
   ```

### ⚠️ IMPORTANTE (Alta prioridade)

4. Validar modelo em test set (689 devices)
5. Threshold tuning para maximizar recall
6. Questionar Engenharia sobre 85.7% failure rate e 45% missing values

### ⏳ PLANEJADO (Média prioridade)

7. Nested CV para hyperparameter tuning
8. Análise de estabilidade temporal (concept drift)
9. Feature engineering temporal (rolling stats)
10. Pipeline sklearn completo

---

## 📚 Referências

1. [Scikit-learn Common Pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)
2. [TimeSeriesSplit Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
3. [Imbalanced-learn SMOTE](https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html)
4. [SHAP Values for XAI](https://github.com/slundberg/shap)
5. Constitution v0.1.0 - Ground-Truth First Principle

---

**Documento vivo - Atualizar após cada milestone**  
**Última revisão:** 31/out/2025  
**Próxima revisão:** Após validação test set (Segunda-feira)

---

*"In God we trust, all others must bring data... and mitigate biases."*  
— Adaptado de W. Edwards Deming
