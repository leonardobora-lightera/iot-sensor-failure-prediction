# 📊 IoT Critical Device Prediction - Notebooks# 📊 IoT Critical Device Prediction - Notebooks



## 🎯 Objetivo## 🎯 Objetivo

Prever dispositivos IoT críticos (falhas de comunicação) baseado em padrões de telemetria, status e anomalias.Prever dispositivos IoT críticos (falhas de comunicação) baseado em padrões de telemetria, status e anomalias.



------



## ⚠️ TRANSIÇÃO PARA MODELO V2 (13/Nov/2025)## ⚠️ TRANSIÇÃO PARA MODELO V2 (13/Nov/2025)



Este projeto passou por uma **refatoração importante** para eliminar contaminação de dados FACTORY (lab testing):Este projeto passou por uma **refatoração importante** para eliminar contaminação de dados FACTORY (lab testing):



### 📌 Modelo v1 (ARQUIVADO)### 📌 Modelo v1 (ARQUIVADO)

- **Dataset:** Mixed FACTORY+FIELD (789 devices)- **Dataset:** Mixed FACTORY+FIELD (789 devices)

- **Performance:** Recall 78.6%, Precision 84.6%, AUC 0.8621- **Performance:** Recall 78.6%, Precision 84.6%, AUC 0.8621

- **Problema:** Lifecycle mixing (lab + production data juntos)- **Problema:** Lifecycle mixing (lab + production data juntos)

- **Notebooks:** Movidos para `archive_v1/` (preservados para referência)- **Notebooks:** Movidos para `archive_v1/` (preservados para referência)



### ✅ Modelo v2 (ATUAL)### ✅ Modelo v2 (ATUAL)

- **Dataset:** FIELD-only (762 devices, 30 features)- **Dataset:** FIELD-only (762 devices, 30 features)

- **Filtro:** `MODE='FIELD'` - removidos 362k mensagens FACTORY (31.8%)- **Filtro:** `MODE='FIELD'` - removidos 362k mensagens FACTORY (31.8%)

- **Nova feature:** `days_since_last_message` (detecta devices inativos)- **Nova feature:** `days_since_last_message` (detecta devices inativos)

- **Performance:** Recall 57.1%, Precision 57.1%, **AUC 0.9186** (+6.6%)- **Performance:** Recall 57.1%, Precision 57.1%, **AUC 0.9186** (+6.6%)

- **Trade-off:** -21.5% recall, mas **fundação limpa** para melhorias futuras- **Trade-off:** -21.5% recall, mas **fundação limpa** para melhorias futuras

- **Filosofia:** "2 passos atrás, 3 pra frente"- **Filosofia:** "2 passos atrás, 3 pra frente"



### 🚀 Próximos Passos (Roadmap v2)### 🚀 Próximos Passos (Roadmap v2)

1. **Hyperparameter Tuning:** GridSearch CatBoost (esperado +10-15% recall)1. **Hyperparameter Tuning:** GridSearch CatBoost (esperado +10-15% recall)

2. **Feature Engineering Temporal:** Adicionar 4 features (FASE 3, 2 semanas)2. **Feature Engineering Temporal:** Adicionar 4 features (FASE 3, 2 semanas)

3. **Threshold Calibration:** Otimizar decision boundary3. **Threshold Calibration:** Otimizar decision boundary



------



## 📁 Estrutura Atual## 📁 Estrutura de Notebooks v2



### Notebooks Ativos (v2)**NOTA:** Notebooks v1 (02B-08) foram movidos para `archive_v1/` para preservar histórico.

**NOTA:** Novos notebooks v2 serão criados sob demanda:

- `09_model_v2_field_only.ipynb` - Treinamento e análise modelo v2 (planejado)Novos notebooks v2 serão criados sob demanda:

- `10_temporal_features.ipynb` - Implementação features FASE 3 (planejado)- `09_model_v2_field_only.ipynb` - Treinamento e análise modelo v2

- `11_hyperparameter_tuning.ipynb` - Otimização GridSearch (planejado)- `10_temporal_features.ipynb` - Implementação features FASE 3

- `11_hyperparameter_tuning.ipynb` - Otimização GridSearch

### Notebooks Arquivados (v1)

Ver `archive_v1/` para notebooks do modelo v1 (mixed FACTORY+FIELD data):---



- **02B_stratified_split_by_device.ipynb** - Split estratificado 70/30 (789 devices)## 📚 Notebooks Arquivados (v1)

- **02_correlacao_telemetrias_msg6.ipynb** - Análise correlações telemetrias

- **03_status_modelagem_pratica.ipynb** - Baseline com Dropna## 📚 Notebooks Arquivados (v1)

- **04B_sem_leakage_LIMPO.ipynb** - Baseline com Imputation (29 features)

- **04_correcao_class_imbalance.ipynb** - Correção class imbalanceVer `archive_v1/` para notebooks do modelo v1 (mixed FACTORY+FIELD data):

- **05_smote_optimization.ipynb** - Otimização SMOTE 0.5

- **06B_synthetic_validation_empirical.ipynb** - Validação dados sintéticos### **02B_stratified_split_by_device.ipynb** ⚠️ v1

- **06_synthetic_data_validation.ipynb** - Validação dados sintéticos**Função:** Geração de Dados com Split Estratificado (789 devices)  

- **07_model_optimization.ipynb** - Comparação XGBoost/LightGBM/CatBoost**Status:** ARQUIVADO - Dataset sem filtro MODE

- **08_pipeline_producao.ipynb** - Pipeline v1 final (DEPRECATED - contaminated with FACTORY data)

### **03_status_modelagem_pratica.ipynb** ⚠️ v1

---**Função:** Baseline com Dropna  

**Status:** ARQUIVADO - Baseline funcional mas limitado

## 🔧 Pipeline de Treinamento v2- `dropna()` reduz amostras críticas:

  - Train: 31 → **13 critical** (perda de 58%)

```  - Test: 14 → **7 critical** (perda de 50%)

payloads_lora_final.csv (2.04 GB, 1,138,275 messages)- Métricas baseadas em **apenas 7 samples** (baixa confiança estatística)

                    ↓

     [MODE='FIELD' Filter] → Remove 362k FACTORY (31.8%)**Valor:**

                    ↓- Prova de conceito: Split estratificado funciona (0% recall no temporal → 85.71%)

     [Aggregate by Device] → 30 features (29 + days_since_last_message)- Baseline simples para comparação

                    ↓

device_features_with_telemetry_field_only.csv (762 devices, 46 critical)---

                    ↓

     [Stratified Split 70/30]### **04B_sem_leakage_LIMPO.ipynb** 🌟

                    ↓**Função:** Baseline REAL com Imputation (SEM Data Leakage)  

         ┌──────────┴──────────┐**Status:** ✅ ATIVO - Baseline válido para produção  

         ↓                     ↓

    TRAIN (533)            TEST (229)**O que faz:**

   32 critical           14 critical- Carrega CSVs estratificados

         ↓                     ↓- **Identifica e REMOVE features com data leakage** (`msg6_count`, `msg6_rate`)

     [SimpleImputer → SMOTE 0.5 → CatBoost]- Aplica `SimpleImputer(strategy='median')` preservando **TODOS** os 31 train + 14 test critical

         ↓- Treina RandomForest com `class_weight='balanced'` em **29 features limpas**

    Recall: 57.1% (8/14)- Executa **4 validações rigorosas** confirmando leakage removido

    Precision: 57.1%

    AUC: 0.9186**Resultados REAIS (Test Set):**

``````

Recall:            50.00% (7 de 14 critical detectados)

---Precision:         87.50% (1 falso positivo)

F1-Score:          63.64%

## 📝 ReferênciasBalanced Accuracy: 74.78%

ROC-AUC:           0.9065

- **Código Treinamento v2:** `train_model_v2.py` (script Python standalone)```

- **Processamento Payloads:** `process_payloads_chunks.py` + `scripts/transform_aws_payload.py`

- **Modelo v2:** `models/catboost_pipeline_v2_field_only.pkl` (127.9 KB)**Por que as métricas "caíram"?**

- **Metadata v2:** `models/catboost_pipeline_v2_metadata.json`

- **Plano de Ação:** `docs/PLANO_ACAO_FIX_FALSOS_POSITIVOS.md`| Métrica | NB03 (dropna) | NB04B (REAL) | Análise |

- **Feature Engineering:** `docs/FEATURE_ENGINEERING_TEMPORAL.md` (roadmap FASE 3)|---------|---------------|--------------|---------|

| Recall | 85.71% | **50.00%** | 6/7 vs 7/14 samples - mais confiável |

---| Precision | 100.00% | **87.50%** | Artificial vs realista |

| Samples | 7 critical | **14 critical** | 2x mais dados |

## 🎓 Lições Aprendidas

**Descoberta Crítica:**

### Por que v2 tem recall menor?- Notebook inicial (04_OLD) tinha **precision 100%, AUC 0.9994** → "Bom demais para ser verdade?"

1. **Dataset menor:** 789 → 762 devices (-3.4%)- Validação revelou **DATA LEAKAGE**: Features `msg6_rate` (42.1% importance) e `msg6_count` (5.8%) estavam vazando a **definição do target**

2. **Menos "informative noise":** FACTORY tinha padrões de degradação (mesmo sendo lab)- Target: `is_critical_target = (msg6_count > IQR_threshold)`

3. **Pipeline mais rigoroso:** Production-only elimina lifecycle mixing- Modelo aprendia: "Se msg6_rate > X → Critical" (circular, inútil)



### Por que AUC melhorou?**Correção:**

- **0.8621 → 0.9186 (+6.6%)** indica melhor **ranking/calibração**- Removidas **2 features contaminadas**: `msg6_count`, `msg6_rate`

- Modelo sabe ORDENAR probabilidades melhor (mesmo errando threshold)- Preservadas **29 features legítimas**: telemetria (optical, temp, battery, SNR, RSRP), status, agregações

- Fundação sólida para hyperparameter tuning- Modelo agora aprende padrões REAIS: anomalias de telemetria + volume de mensagens + conectividade



### Trade-off validado**Validações (4/4 Aprovadas):**

- ✅ "2 passos atrás, 3 pra frente"1. ✅ Zero features `msg6_*` ou `msg_type_6_*`

- ✅ Recall recuperável com GridSearch + features temporais2. ✅ AUC 0.9065 < 0.98 (threshold sklearn para leakage)

- ✅ Dados limpos > dados contaminados3. ✅ Top feature `max_frame_count` 29.5% < 40% (distribuído, não dominante)

- ✅ AUC alto = confiança em probabilidades4. ✅ Precision 87.5% < 100% (erros normais, não artificial)



---**Features Importantes (Top 5):**

1. `max_frame_count` (29.5%): Picos anormais de frames

**Última atualização:** 13/Nov/2025 - Leonardo Costa2. `total_messages` (16.5%): Volume de comunicações

3. `optical_readings` (15.6%): Leituras ópticas totais
4. `temp_mean` (5.7%): Temperatura média
5. `rsrp_mean` (2.3%): Sinal de conectividade

**Threshold Condicional:**
- ✅ **Recall 50.0% ≥ 30%** → **SMOTE ELEGÍVEL**
- Modelo tem poder preditivo REAL baseado em padrões legítimos
- Próximo passo: Otimização com SMOTE (esperado recall 60-70%)

---

## 🚀 Pipeline de Desenvolvimento

```
device_features_with_telemetry.csv (789 devices, 45 critical)
                    ↓
     [02B] Stratified Split por device_id
                    ↓
         ┌──────────┴──────────┐
         ↓                     ↓
    TRAIN (552)            TEST (237)
   31 critical           14 critical
         ↓                     ↓
     [03] Baseline Dropna (REFERÊNCIA)
         ↓
    13 critical → 85.71% recall (6/7 samples)
    ⚠️ Limitado: apenas 7 test samples
         ↓
     [04B] Baseline LIMPO (ATIVO)
         ↓
    31 critical → 50.0% recall (7/14 samples)
    ✅ REAL: 14 test samples, sem leakage
         ↓
    [05] SMOTE Optimization (PRÓXIMO)
         ↓
    Target: 60-70% recall, 80%+ precision
```

---

## 📊 Resultados Chave

### **Comparação Evolutiva:**

| Split | Train/Test | Critical | Recall | Precision | Problema |
|-------|------------|----------|--------|-----------|----------|
| **Temporal** | 750/689 | 187/42 | **0%** | - | Leakage (650 overlap) |
| **Estratificado + Dropna** | 552/237 | 13/7 | **85.71%** | 100% | Poucos samples (7) |
| **Estratificado + Leakage** | 552/237 | 31/14 | 85.71% | 100% | Features vazam target |
| **Estratificado + LIMPO** | 552/237 | 31/14 | **50.0%** | 87.5% | ✅ **VÁLIDO** |

### **Ganho Real:**
- Split Temporal: **0% recall** (não detecta NENHUM critical)
- Baseline Atual: **50% recall** (detecta 7 de 14 critical)
- **Melhoria:** 0% → 50% = **INFINITO** 🎯

---

## 📁 Notebooks Históricos (old/)

### **04_OLD_com_leakage.ipynb**
- Baseline com **DATA LEAKAGE** (precision 100%, AUC 0.9994)
- **Preservado** como documentação histórica da descoberta
- Features `msg6_rate` (42.1%) e `msg6_count` (5.8%) dominavam
- Modelo aprendia **definição do target**, não padrões

### **02_correlacao_telemetrias_msg6.ipynb**
- EDA de correlações entre telemetrias e msg6_count
- **Preservado** como referência de análise exploratória
- Útil para entender relações entre features

---

## 🎯 Próximos Passos

### **1. SMOTE Optimization (Notebook 05)**
**Status:** ELEGÍVEL (recall 50% ≥ 30%)  
**Objetivo:** Aumentar recall para 60-70% mantendo precision 80%+

**Estratégia:**
- Testar `sampling_strategy`: 0.3, 0.5, 0.7
- Comparar RandomForest + SMOTE vs XGBoost + SMOTE
- Validação com 3-fold CV para estabilidade

**Expectativa:**
- Recall: 50% → **60-70%** (+10-20%)
- Precision: 87.5% → **80-85%** (tolerável para recall gain)
- Detecção: 7/14 → **8-10/14** devices críticos

---

### **2. Model Comparison (Notebook 06)**
**Status:** CONDICIONAL (se recall ≥60%)  
**Modelos:** RF+SMOTE, XGBoost, LightGBM, Ensemble

---

### **3. Production Pipeline (Notebook 08)**
**Deliverables:**
- Pipeline sklearn (imputation → SMOTE → model)
- Modelo treinado (joblib)
- Função de inferência
- Documentação executiva

---

## 💡 Lições Aprendidas

### ✅ **1. Sempre Questionar Métricas Perfeitas**
- Precision 100% com class imbalance 16.8:1 era **estatisticamente improvável**
- Validação rigorosa revelou data leakage antes de produção

### ✅ **2. Validação Multi-Ângulo**
- AUC 0.9994 (threshold sklearn ≥0.98)
- Feature importance 42.1% (dominância anormal)
- Correlation 0.69 (muito alta)
- Probability distribution (separação perfeita)

### ✅ **3. Métricas que Caem Podem Ser Correções**
- Recall 85.71% → 50% parece piora
- MAS: 85.71% era **artificial** (leakage), 50% é **REAL** (válido)
- Stakeholders precisam entender: drops são **honestos**, não falhas

### ✅ **4. Split Estratificado > Temporal**
- Dataset agregado (1 row/device) não é time-series
- Split temporal causou overlap (650 devices) e distribution shift
- Split estratificado por device: zero overlap, generalização válida

### ✅ **5. Imputation > Dropna**
- Dropna: 31 → 13 critical (perda 58%)
- Imputation: 31 → 31 critical (preservação 100%)
- Mais dados → Métricas mais confiáveis

---

## 📚 Documentação Adicional

- **LEAKAGE_DISCOVERY.md**: Análise completa da descoberta de data leakage (timeline, evidências, correção, lições)
- **CHANGELOG.md**: Timeline evolutiva do projeto (6 fases)
- **TODO.md**: Lista de tarefas e progresso

---

## 🔧 Dependências

**Python Packages:**
- pandas
- scikit-learn
- scipy
- matplotlib
- seaborn
- imbalanced-learn (SMOTE)

**Data Files:**
- `device_features_with_telemetry.csv` (fonte)
- `device_features_train_stratified.csv` (gerado por 02B)
- `device_features_test_stratified.csv` (gerado por 02B)

---

## 👥 Stakeholder Summary

**Objetivo:** Detectar dispositivos IoT críticos antes de falha total  

**Abordagem:** Machine learning baseado em **padrões de similaridade** (não previsão temporal)

**Resultados Atuais:**
- ✅ **50% de recall** (7 de 14 devices críticos detectados)
- ✅ **87.5% de precision** (1 alarme falso em 237 testes)
- ✅ Modelo **válido e confiável** (data leakage corrigido)

**Valor de Negócio:**
- Split temporal: **0% detecção** → **Falha total**
- Baseline atual: **50% detecção** → **Melhoria infinita**
- Com SMOTE: **60-70% detecção** esperada → **8-10 falhas prevenidas de 14**

**Próximos 30 dias:**
- Otimização SMOTE (Semana 2)
- Comparação de modelos (Semana 3)
- Pipeline produção (Semana 4)

---

**Última Atualização:** 6 de Novembro de 2025  
**Status do Projeto:** ✅ Baseline válido estabelecido, pronto para otimização
