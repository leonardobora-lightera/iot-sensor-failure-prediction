# 📊 CHECKPOINT - Sexta 31/Out/2025

## ✅ Status Geral do Projeto
**Data:** 31 de outubro de 2025 (Sexta-feira - Fim de semana)  
**Fase:** Análise de Correlação de Telemetrias (Notebook 02)  
**Status:** **CONCLUÍDO COM SUCESSO** ✅

---

## 🎯 Objetivos Alcançados Hoje

### 1. Correção RSSI (Crítico)
- ✅ **Problema identificado:** RSSI estava sendo procurado em `eyon_metadata.decoded_payload.rssi` (não existe)
- ✅ **Solução:** RSSI está em `eyon_metadata.rssi` (45.5% cobertura, valores numéricos limpos)
- ✅ **Validação:** Célula específica adicionada para confirmar existência e tipo de dados
- ✅ **Resultado:** 4 parâmetros de sinal agora disponíveis (SNR, RSRP, RSRQ, RSSI)

### 2. Execução Completa do Notebook 02
- ✅ **21 células executadas** sem erros
- ✅ **Train-test split temporal** implementado (70/30) ANTES de agregações
- ✅ **Missing values analysis** reportado para todas telemetrias
- ✅ **Correlações calculadas** com validação estatística (p-values)
- ✅ **Feature importance** obtido com Random Forest + CV=5
- ✅ **Test set processado** e salvo separadamente

---

## 📈 Principais Descobertas

### Correlações com msg6_rate (Spearman)

| Feature | Correlação (r) | P-value | Significância | Interpretação |
|---------|----------------|---------|---------------|---------------|
| **RSRP** | **-0.2205** | 5.77e-05 | ✅ **STRONGEST** | Sinal RSRP baixo → mais msg6 |
| **RSRQ** | -0.2072 | 1.61e-04 | ✅ Significativo | Qualidade sinal baixa → mais msg6 |
| **RSSI** | -0.1884 | 4.61e-04 | ✅ Significativo | Força sinal baixa → mais msg6 |
| **SNR** | +0.0040 | 0.94 | ❌ **NÃO significativo** | SNR isoladamente NÃO prediz msg6 |

### Feature Importance (Random Forest)

| Rank | Feature | Importance | Observação |
|------|---------|------------|------------|
| 🥇 | snr_mean | 30.7% | **⚠️ CONTRADIÇÃO:** Importance alta mas r≈0 |
| 🥈 | rsrq_mean | 26.3% | Consistente com correlação |
| 🥉 | battery_mean | 14.2% | Validado |
| 4 | rsrp_mean | 6.5% | Consistente com correlação |
| 5 | rssi_mean | 5.7% | Consistente com correlação |

---

## ⚠️ Problemas Identificados

### 1. Contradição SNR (CRÍTICO)
**Sintoma:** SNR tem feature importance #1 (30.7%) mas correlação Spearman r=0.004 (não significativa)

**Hipóteses:**
- ✅ SNR pode estar interagindo com outras features (interação não-linear SNR × Battery)
- ✅ Random Forest captura relações que correlação bivariada não detecta
- ❌ Possível overfitting do Random Forest em ruído

**Ação recomendada:** Investigar interações com SHAP values ou partial dependence plots

---

### 2. Recall Instável (ALTO)
**Sintoma:** Recall CV=5 = 0.30 ±0.40 (scores: [0.5, 0.0, 1.0, 0.0, 0.0])

**Problemas:**
- Variância EXTREMA entre folds (de 0% a 100%)
- Média 30% significa que modelo captura apenas 1 em 3 falhas críticas
- Class imbalance severo: 45 critical vs 631 non-critical (1:14)

**Ação recomendada:** 
- Aplicar SMOTE ou class_weight ajustado
- Considerar threshold tuning para aumentar recall
- Validar em test set para confirmar performance real

---

### 3. Cobertura de Dados (MÉDIO)
**Sintoma:** ~45% de missing values em telemetrias (optical, temp, battery, RSSI)

**Impacto:**
- Treino com apenas 342-676 devices (de 676 disponíveis)
- Teste com 636 devices (de 689 disponíveis)
- Viés potencial: devices com telemetria podem ser diferentes dos sem telemetria

**Ação recomendada:** Verificar se devices sem telemetria são versão antiga de firmware

---

## 📁 Arquivos Gerados

```
data/
├── device_features_train_with_telemetry.csv  ✅ (676 devices, 37 features)
└── device_features_test_with_telemetry.csv   ✅ (689 devices, 37 features)
```

**Features incluídas:**
- Base: device_id, total_messages, msg6_count, msg6_rate, is_critical
- Optical Power: mean, std, min, max, readings, below_threshold, range
- Temperatura: mean, std, min, max, above_threshold, range
- Bateria: mean, std, min, max, below_threshold
- Sinal: snr_mean/std/min, rsrp_mean/std/min, rsrq_mean/std/min, rssi_mean/std/min
- Target: is_critical_target (msg6_rate > 25%)

---

## 🔬 Validação Científica

### ✅ APROVADO - Metodologia Anti-Data Leakage
- ✅ Train-test split temporal (70/30) implementado ANTES de agregações
- ✅ Agregações calculadas APENAS em df_train (FIT)
- ✅ Test set aplicou transformações sem re-fit (TRANSFORM)
- ✅ Multicolinearidade verificada (nenhum par |r|>0.9)
- ✅ Missing values reportados (45% em telemetrias)

### ⚠️ PENDENTE - Validação de Performance
- ⏳ Modelo não testado em test set ainda
- ⏳ Recall 30% é BAIXO (baseline Isolation Forest = 99%)
- ⏳ Contradição SNR precisa ser investigada

---

## 📋 Próximas Tarefas (Segunda-feira)

### Prioridade ALTA
1. **Investigar contradição SNR**
   - Gerar SHAP values ou partial dependence plots
   - Verificar interações SNR × Battery, SNR × RSRP
   - Decidir: manter SNR ou remover do modelo

2. **Validar modelo em test set**
   - Treinar modelo final no train completo
   - Predizer em test set (689 devices)
   - Comparar recall/precision com CV

3. **Otimizar recall**
   - Aplicar class_weight='balanced' ou custom weights
   - Testar SMOTE para balanceamento
   - Threshold tuning para maximizar recall

### Prioridade MÉDIA
4. **Feature engineering temporal**
   - Rolling statistics (7d, 14d, 30d)
   - Slopes (tendência de degradação)
   - Time-since-last-msg6

5. **Análise de missing values**
   - Verificar firmware version × telemetry availability
   - Considerar imputação ou flag de missingness

### Prioridade BAIXA
6. **Pipeline sklearn**
   - Encapsular preprocessing em Pipeline
   - Garantir reproducibilidade

---

## 📊 Métricas de Progresso

| Métrica | Valor | Meta | Status |
|---------|-------|------|--------|
| Train-test split | ✅ 70/30 temporal | ✅ Temporal | ✅ |
| Missing values report | ✅ 45% | ✅ Reportado | ✅ |
| Correlações validadas | ✅ 4/4 sinais | ✅ SNR, RSRP, RSRQ, RSSI | ✅ |
| Feature importance | ✅ Top 5 | ✅ Obtido | ✅ |
| Multicolinearidade | ✅ Nenhuma | ✅ |r|<0.9 | ✅ |
| Test set processado | ✅ 689 devices | ✅ Salvo | ✅ |
| **Recall no CV** | ⚠️ **30%** | 🎯 **>70%** | ❌ |
| Validação em test | ⏳ Pendente | ✅ Obrigatório | ⏳ |

---

## 💡 Insights Científicos

### Descoberta 1: RSRP > RSSI > RSRQ
**Ordem de importância dos sinais para predição:**
1. RSRP (Reference Signal Received Power) - correlação -0.22
2. RSRQ (Reference Signal Received Quality) - correlação -0.21
3. RSSI (Received Signal Strength Indicator) - correlação -0.19
4. SNR (Signal-to-Noise Ratio) - correlação ~0 (não preditivo isoladamente)

**Interpretação física:** Potência do sinal de referência (RSRP) é melhor preditor que força total (RSSI) porque RSRP mede especificamente o sinal LTE/NB-IoT, enquanto RSSI inclui ruído e interferência.

### Descoberta 2: SNR como Feature de Interação
**Paradoxo:** SNR não correlaciona com msg6 mas é top feature no Random Forest.

**Explicação provável:** SNR modera o efeito de outras features. Exemplo:
- Battery baixa + SNR baixo = alta probabilidade de msg6
- Battery baixa + SNR alto = probabilidade moderada

Isso sugere que **SNR é um modificador de risco, não um preditor direto**.

### Descoberta 3: Class Imbalance Severo
**Distribuição:** 45 critical (7%) vs 631 non-critical (93%) no treino

**Impacto:** Modelo tende a predizer "não-crítico" para maximizar accuracy. Recall 30% reflete isso - modelo só identifica casos mais óbvios.

**Solução:** Focar em RECALL (não accuracy) e aplicar técnicas de balanceamento.

---

## 🔐 Compliance Constitucional

### ✅ Princípios Aplicados
- ✅ **Ground-Truth First:** msg_type==6 preservado, dataset completo usado
- ✅ **Evidence-Based ML:** Correlações testadas ANTES de modelagem
- ✅ **Temporal Validation:** Split temporal (não random) implementado
- ✅ **Domain Knowledge:** Thresholds físicos validados (optical -28dBm, temp 70°C, battery 2.5V)

### 📝 Documentação
- ✅ Todas células com markdown explicativo
- ✅ Descobertas documentadas (SNR contradição, RSRP strongest)
- ✅ Decisões rastreáveis (por que usar Spearman, por que CV=5)

---

## 🚀 Estado para Segunda

**O que está PRONTO:**
- ✅ Dataset limpo e dividido (train/test)
- ✅ Features engenheiradas e validadas
- ✅ Correlações conhecidas (RSRP, RSRQ, RSSI preditivos)
- ✅ Baseline Random Forest treinado
- ✅ Problemas identificados (SNR contradição, recall baixo)

**O que FALTA:**
- ⏳ Validação em test set
- ⏳ Otimização de recall (SMOTE, class_weight)
- ⏳ Investigação SNR (SHAP values)
- ⏳ Feature engineering temporal (rolling stats)
- ⏳ Pipeline final de produção

**Bloqueadores:** NENHUM - todas tarefas podem prosseguir na segunda

---

## 📞 Contatos Necessários

- **Engenharia de Produto:** Validar thresholds RSRP (qual valor crítico?)
- **Enzo (Suporte):** Confirmar se devices sem telemetria são firmware antigo
- **Mariana (P.O.):** Apresentar resultados parciais e confirmar meta de recall

---

## 🎉 Conquistas da Semana

1. ✅ Constituição ratificada (v0.1.0)
2. ✅ Notebook 01 temporal analysis completo
3. ✅ Notebook 02 correlation analysis completo
4. ✅ RSSI descoberto e validado
5. ✅ Train-test split anti-leakage implementado
6. ✅ 12/12 correções ML aplicadas com sucesso
7. ✅ Knowledge graph atualizado (13 entidades, 14 relações)

---

**Bom fim de semana! 🌴**  
**Próxima sessão:** Segunda-feira (começar com validação test set)

---

_Checkpoint criado automaticamente por GitHub Copilot_  
_Última atualização: 31/out/2025 - 18:00 BRT_
