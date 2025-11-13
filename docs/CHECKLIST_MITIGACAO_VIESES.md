# 🛡️ CHECKLIST: Mitigação de Vieses em Análises de Observabilidade IoT

**Projeto:** Observabilidade e Monitoramento NB-IoT  
**Contexto:** Análises DESCRITIVAS e INDICATIVAS (não preditivas)  
**Data:** 03 de novembro de 2025  

---

## 📋 ÍNDICE DE VIESES

1. [Viés de Seleção](#1-vi%C3%A9s-de-sele%C3%A7%C3%A3o-selection-bias)
2. [Viés de Sobrevivência](#2-vi%C3%A9s-de-sobreviv%C3%AAncia-survivorship-bias)
3. [Viés de Confirmação](#3-vi%C3%A9s-de-confirma%C3%A7%C3%A3o-confirmation-bias)
4. [Viés Temporal](#4-vi%C3%A9s-temporal-temporal-bias)
5. [Viés de Agregação](#5-vi%C3%A9s-de-agrega%C3%A7%C3%A3o-aggregation-bias)
6. [Viés de Amostragem](#6-vi%C3%A9s-de-amostragem-sampling-bias)
7. [Viés de Relatório](#7-vi%C3%A9s-de-relat%C3%B3rio-reporting-bias)
8. [Viés de Interpretação](#8-vi%C3%A9s-de-interpreta%C3%A7%C3%A3o-interpretation-bias)
9. [Viés de Medição](#9-vi%C3%A9s-de-medi%C3%A7%C3%A3o-measurement-bias)
10. [Viés Operacional](#10-vi%C3%A9s-operacional-operational-bias)

---

## 1. Viés de Seleção (Selection Bias)

### ⚠️ Risco para Este Projeto

**ALTO** - Dataset contém apenas devices que **reportaram logs** ao AWS

### 📌 Manifestações Possíveis

#### 1.1 Devices Silenciosos

**Problema:** Devices que falharam **completamente** não aparecem nos logs  
**Exemplo:** Device com bateria totalmente esgotada não envia msg_type 6

**ATUALIZAÇÃO 13/Nov/2025 - VALIDADO EM PRODUÇÃO:**

**Problema Específico Identificado:** Devices **INATIVOS** após testes de laboratório sendo classificados como críticos

**Case Study:** Device 861275072515287
- **Probabilidade predita:** 97.5% (HIGH RISK)
- **Realidade:** FALSO POSITIVO por inatividade pós-laboratório
- **Evidências:**
  - Última comunicação: 31/10/2025 17:35 (12 dias de inatividade)
  - Telemetrias FIELD saudáveis: optical -12.30 dBm, temp 27°C, battery 3.40V
  - Distribuição MODE: 465 FIELD + 38 FACTORY + 174 NaN
  - Shutdown planejado: 3x msg_type 43 (heartbeat sem telemetrias)

**Problema Raiz:** Modelo agrega features de TODO o lifecycle (FACTORY + FIELD) sem contexto temporal

**Checklist de Mitigação ATUALIZADO:**
- [x] ✅ **IMPLEMENTADO:** Filtrar MODE='FIELD' em transform_aws_payload.py
- [x] ✅ **IMPLEMENTADO:** Adicionar feature days_since_last_message
- [ ] Retreinar modelo com features production-only (FASE 2 - Esta Semana)
- [ ] Classificar devices: "INACTIVE_NEEDS_INVESTIGATION" (>7 dias) vs "CRITICAL_ACTIVE" (<7 dias)
- [ ] Adicionar warning no dashboard: "X devices inativos >7 dias - não são falhas ativas"
- [ ] Documentar no dashboard: "Análise cobre apenas devices ATIVOS em produção (MODE=FIELD)"
- [ ] Criar métrica: "% devices ativos nos últimos 7/30 dias"
- [ ] Implementar features temporais completas (FASE 3 - 2 semanas)

**Mitigação Definitiva (ROADMAP):**
1. **QUICK WIN (HOJE):** Filtro MODE='FIELD' + days_since_last_message
2. **MÉDIO PRAZO (ESTA SEMANA):** Retreinamento com features production-only
3. **LONGO PRAZO (2 SEMANAS):** Features temporais completas (FEATURE_ENGINEERING_TEMPORAL.md)

**Referências:**
- `docs/TEMPORAL_LIMITATIONS.md` - Documentação completa das limitações
- `docs/FEATURE_ENGINEERING_TEMPORAL.md` - Roadmap de features temporais
- `device_861275072515287_2025-11-13.csv` - Case study completo
- `analyze_device_861275072515287.py` - Script de análise temporal

#### 1.2 Firmware Antigo

**Problema:** Devices com firmware antigo podem não reportar certas telemetrias (optical_power, RSSI)  
**Exemplo:** 45% missing values em telemetrias pode indicar versão antiga

**Checklist de Mitigação:**
- [ ] Agrupar devices por fw_app_version e calcular % missing telemetry
- [ ] Documentar correlação: "Firmware <v1.1.0 não reporta RSSI"
- [ ] Adicionar filtro no dashboard: "Apenas devices com firmware v1.1.0+"
- [ ] Criar seção "Cobertura de Dados" mostrando % devices com cada telemetria
- [ ] Alertar stakeholders sobre limitação de análise em devices antigos

#### 1.3 Carrier-Specific Bias

**Problema:** VIVO pode ter cobertura NB-IoT diferente de outras carriers  
**Exemplo:** Padrões observados em VIVO podem não se aplicar a TIM/Claro

**Checklist de Mitigação:**
- [ ] Segmentar análises por carrier (VIVO, TIM, Claro, etc)
- [ ] Calcular distribuição de devices por carrier
- [ ] Documentar: "Análise baseada principalmente em dados VIVO (X%)"
- [ ] Evitar generalizar padrões VIVO para outras carriers sem validação
- [ ] Criar análises comparativas quando houver dados suficientes de múltiplas carriers

---

## 2. Viés de Sobrevivência (Survivorship Bias)

### ⚠️ Risco para Este Projeto

**MÉDIO** - Já validado em 30/Out que devices se recuperam após msg_type 6

### 📌 Manifestações Possíveis

#### 2.1 Devices "Condenados"

**Problema:** Assumir que device com msg_type 6 está permanentemente falhado  
**Exemplo:** "Device X tem 100 msg_type 6 → Device X está quebrado" (FALSO)

**Checklist de Mitigação:**
- [x] ✅ **JÁ VALIDADO:** Devices se recuperam (reunião 03/Nov confirmou)
- [ ] Calcular taxa de auto-recuperação: "X% devices voltam a funcionar após msg_type 6"
- [ ] Criar métrica "Tempo médio de recuperação" por tipo de erro
- [ ] Documentar no dashboard: "msg_type 6 NÃO significa falha permanente"
- [ ] Adicionar visualização: "Timeline de falha → recuperação → nova falha"

#### 2.2 Devices Substituídos

**Problema:** Devices que pararam de reportar podem ter sido substituídos (não falharam)  
**Exemplo:** Device sem logs há 60 dias pode ter sido trocado em manutenção programada

**Checklist de Mitigação:**
- [ ] Cruzar dados de logs com dados de manutenção/substituição (se disponível)
- [ ] Criar métrica: "Último log há X dias" vs "Device marcado como substituído"
- [ ] Evitar concluir "device falhou" sem confirmar com dados de campo
- [ ] Adicionar filtro: "Excluir devices substituídos das análises"

#### 2.3 Viés de "Sobreviventes Saudáveis"

**Problema:** Devices que **nunca** falharam podem ter características diferentes (hardware, instalação, ambiente)  
**Exemplo:** Devices indoor vs outdoor podem ter taxas de falha muito diferentes

**Checklist de Mitigação:**
- [ ] Incluir devices com **zero** msg_type 6 nas análises descritivas
- [ ] Criar grupo de controle: "Devices saudáveis (0 msg_type 6 em 6 meses)"
- [ ] Comparar características: Firmware, região, carrier entre saudáveis vs falhadores
- [ ] Documentar limitação: "Não sabemos se devices saudáveis têm melhor hardware ou melhor ambiente"

---

## 3. Viés de Confirmação (Confirmation Bias)

### ⚠️ Risco para Este Projeto

**ALTO** - Risco de buscar padrões que confirmem hipóteses pré-existentes

### 📌 Manifestações Possíveis

#### 3.1 "Temperatura Causa Falhas"

**Problema:** Enzo mencionou temperatura → Risco de forçar correlação temperatura × msg_type 6  
**Exemplo:** Encontrar correlação fraca (r=0.1) e interpretar como "confirmado"

**Checklist de Mitigação:**
- [ ] Definir threshold de correlação **antes** de analisar (ex: |r| > 0.3 para "relevante")
- [ ] Calcular p-value e exigir p < 0.01 para "estatisticamente significativo"
- [ ] Testar hipótese OPOSTA: "Temperatura NÃO correlaciona com falhas"
- [ ] Documentar correlações **fracas** honestamente: "r=0.15 sugere correlação fraca"
- [ ] Evitar cherry-picking: Reportar **todas** correlações testadas, não só as significativas

#### 3.2 "RSSI Explica Tudo"

**Problema:** Notebook 02 mostrou RSRP como top correlação → Risco de focar excessivamente em sinal  
**Exemplo:** Ignorar outros fatores (bateria, erro de firmware) ao diagnosticar falha

**Checklist de Mitigação:**
- [ ] Criar análise multivariada: "Falhas com RSSI ALTO e bateria BAIXA"
- [ ] Documentar: "RSSI explica X% da variância, Y% permanece inexplicado"
- [ ] Adicionar seção dashboard: "Falhas SEM correlação com RSSI (Z%)"
- [ ] Evitar título simplista: "RSSI causa falhas" → Usar: "RSSI correlaciona com falhas"

#### 3.3 Análise Seletiva de Devices

**Problema:** Focar apenas em "serial offenders" (top 5 devices com mais msg_type 6)  
**Exemplo:** Ignorar padrão emergente em devices com 10-50 msg_type 6

**Checklist de Mitigação:**
- [ ] Analisar **toda distribuição**: Baixa (1-10), Moderada (11-50), Alta (51-100), Crítica (>100)
- [ ] Criar visualizações para cada segmento, não só extremos
- [ ] Documentar: "Padrão X aparece em 80% dos devices, não só top 5"
- [ ] Evitar generalizar padrões de outliers para população geral

---

## 4. Viés Temporal (Temporal Bias)

### ⚠️ Risco para Este Projeto

**ALTO** - Dataset cobre Jan-Out 2025, padrões podem mudar ao longo do tempo

### 📌 Manifestações Possíveis

#### 4.1 Sazonalidade Não Identificada

**Problema:** Padrões de Jan podem não se aplicar a Out  
**Exemplo:** Temperatura externa em Jan (verão BR) vs Jul (inverno BR)

**Checklist de Mitigação:**
- [ ] Calcular correlações **por mês** e verificar estabilidade temporal
- [ ] Criar visualização: "Correlação temperatura × msg6_rate por mês"
- [ ] Testar sazonalidade com decomposição de séries temporais (STL decomposition)
- [ ] Documentar: "Correlação válida para período Jan-Out 2025"
- [ ] Adicionar warning se padrão muda >30% entre meses

#### 4.2 Efeito de Upgrades de Firmware

**Problema:** Upgrade de firmware pode reduzir msg_type 6 → Correlação espúria  
**Exemplo:** Redução de falhas em Ago pode ser devido a firmware v1.2.0, não sazonalidade

**Checklist de Mitigação:**
- [ ] Mapear datas de upgrades de firmware (v1.0.1 → v1.1.0 → v1.2.0)
- [ ] Criar marcadores no gráfico temporal: "Upgrade v1.1.0 em 15/Mar/2025"
- [ ] Segmentar análise: "Antes de upgrade X" vs "Depois de upgrade X"
- [ ] Documentar: "Redução de 20% em msg6_rate após upgrade v1.2.0"
- [ ] Evitar atribuir redução a fatores ambientais se coincide com upgrade

#### 4.3 Degradação Progressiva vs Eventos Pontuais

**Problema:** Confundir falha progressiva (bateria degrada lentamente) com evento pontual (queda de energia)  
**Exemplo:** "Bateria causa falhas" quando na verdade foi blackout regional

**Checklist de Mitigação:**
- [ ] Calcular rolling statistics (7d, 30d) para identificar tendências vs picos
- [ ] Criar visualização: "Falhas graduais (aumento constante) vs Falhas em rajada"
- [ ] Cruzar dados de msg_type 6 com eventos conhecidos (manutenções, blackouts)
- [ ] Adicionar filtro: "Excluir dias com eventos extraordinários"
- [ ] Documentar eventos: "Pico de falhas em 10/Mai/2025 coincide com manutenção programada"

---

## 5. Viés de Agregação (Aggregation Bias)

### ⚠️ Risco para Este Projeto

**MÉDIO** - Análises agregam dados por device_id, região, carrier, etc

### 📌 Manifestações Possíveis

#### 5.1 Simpson's Paradox

**Problema:** Correlação positiva em nível agregado, negativa em nível individual  
**Exemplo:** "Temperatura alta → mais falhas" agregado, mas "Temperatura alta → menos falhas" em SP

**Checklist de Mitigação:**
- [ ] Sempre calcular correlações em **múltiplos níveis**: global, por região, por carrier
- [ ] Criar visualização: "Correlação por região" (scatter plot facetado)
- [ ] Documentar discrepâncias: "Global r=0.3, mas SP r=-0.2, PE r=0.5"
- [ ] Evitar conclusões globais sem validar em subgrupos
- [ ] Adicionar warning: "Padrão varia significativamente entre regiões"

#### 5.2 Heterogeneidade de Devices

**Problema:** Devices com hardware diferente (versões antigas vs novas) misturados na mesma análise  
**Exemplo:** Device 2020 vs Device 2024 têm características completamente diferentes

**Checklist de Mitigação:**
- [ ] Segmentar por sn_fkw (serial number) ou fw_app_version
- [ ] Criar grupos: "Devices antigos (<v1.1.0)" vs "Devices novos (>=v1.1.0)"
- [ ] Calcular estatísticas separadamente para cada grupo
- [ ] Documentar: "Análise cobre X% devices novos, Y% devices antigos"
- [ ] Evitar comparar médias globais sem considerar heterogeneidade

#### 5.3 Granularidade Temporal

**Problema:** Agregar por dia pode esconder padrões horários  
**Exemplo:** "Sem padrão diário" quando na verdade falhas ocorrem às 3h AM

**Checklist de Mitigação:**
- [ ] Analisar **múltiplas granularidades**: horária, diária, semanal, mensal
- [ ] Criar heatmap hora × dia da semana
- [ ] Testar autocorrelação temporal (lag=1h, 24h, 7d)
- [ ] Documentar: "Padrão horário: pico às 3-4h AM (horário GMT-3)"
- [ ] Evitar agregar dados sem verificar se padrão fino se perde

---

## 6. Viés de Amostragem (Sampling Bias)

### ⚠️ Risco para Este Projeto

**MÉDIO** - Dataset pode não representar população total de devices

### 📌 Manifestações Possíveis

#### 6.1 Dataset Estático vs Frota Dinâmica

**Problema:** Dataset cobre Jan-Out 2025, mas devices foram instalados em momentos diferentes  
**Exemplo:** Device instalado em Set/2025 tem apenas 1 mês de dados (vs 10 meses para devices de Jan)

**Checklist de Mitigação:**
- [ ] Calcular "Dias de operação" por device (timestamp último log - timestamp primeiro log)
- [ ] Criar histograma: "Distribuição de dias de operação"
- [ ] Filtrar análises: "Apenas devices com >90 dias de operação"
- [ ] Documentar: "X% devices com <30 dias de dados excluídos de análise temporal"
- [ ] Evitar comparar devices novos com devices antigos sem normalizar tempo

#### 6.2 Viés Geográfico

**Problema:** Dataset pode ter concentração regional (ex: 80% devices em SP)  
**Exemplo:** Padrões observados refletem SP, não Brasil

**Checklist de Mitigação:**
- [ ] Calcular distribuição geográfica: "SP: X%, PE: Y%, RS: Z%"
- [ ] Criar mapa de calor: "Devices por estado"
- [ ] Documentar limitação: "Análise representa principalmente região Sudeste"
- [ ] Evitar generalizar: "Padrão brasileiro" quando é "Padrão SP"
- [ ] Adicionar filtro: "Análise restrita a região X"

#### 6.3 Viés de Carrier (NB-IoT)

**Problema:** VIVO é 90% dos devices → Padrões são específicos de VIVO, não NB-IoT genérico  
**Exemplo:** Cobertura VIVO em SP é diferente de TIM em PE

**Checklist de Mitigação:**
- [ ] Calcular distribuição por carrier: "VIVO: X%, TIM: Y%, Claro: Z%"
- [ ] Documentar: "Análise baseada em VIVO (X% do dataset)"
- [ ] Evitar título: "Padrões NB-IoT" → Usar: "Padrões NB-IoT (rede VIVO)"
- [ ] Adicionar disclaimer: "Conclusões podem não se aplicar a outras carriers"
- [ ] Validar padrões em múltiplas carriers quando possível

---

## 7. Viés de Relatório (Reporting Bias)

### ⚠️ Risco para Este Projeto

**ALTO** - Dashboard será usado por stakeholders para tomar decisões

### 📌 Manifestações Possíveis

#### 7.1 Cherry-Picking de Insights

**Problema:** Apresentar apenas correlações significativas, omitir correlações nulas  
**Exemplo:** "Temperatura correlaciona (r=0.3)" mas omitir "Bateria NÃO correlaciona (r=0.05)"

**Checklist de Mitigação:**
- [ ] Criar seção "Fatores Testados": Listar **todos** fatores analisados
- [ ] Reportar correlações nulas: "Bateria: r=0.05, p=0.4 (NÃO significativo)"
- [ ] Documentar: "Testamos 15 correlações, apenas 4 foram significativas"
- [ ] Evitar omitir resultados negativos - são tão importantes quanto positivos
- [ ] Adicionar seção: "O que NÃO correlaciona" (insights por negação)

#### 7.2 P-Hacking (Multiple Comparisons)

**Problema:** Testar 100 correlações e reportar apenas as 5 com p<0.05  
**Exemplo:** Com 100 testes, 5 p<0.05 aparecem **por acaso** (false positives)

**Checklist de Mitigação:**
- [ ] Aplicar correção de Bonferroni: p_adjusted = p_raw × n_comparisons
- [ ] Documentar: "Testamos X correlações, aplicamos correção Bonferroni"
- [ ] Usar threshold mais rigoroso: p < 0.01 (não p < 0.05)
- [ ] Validar correlações em holdout set (dados de Nov/2025 em diante)
- [ ] Evitar data dredging: Definir hipóteses **antes** de testar

#### 7.3 Visualizações Enganosas

**Problema:** Escala de eixo Y manipulada para exagerar diferenças  
**Exemplo:** Gráfico de barras com eixo Y começando em 90% (não 0%)

**Checklist de Mitigação:**
- [ ] Sempre começar eixo Y em zero para gráficos de barras
- [ ] Adicionar linha de referência: "Média geral" ou "Baseline"
- [ ] Documentar escala: "Eixo Y: 0-100% (escala completa)"
- [ ] Evitar truncar eixos sem justificativa clara
- [ ] Usar visualizações honestas: boxplot mostra distribuição completa, não apenas média

---

## 8. Viés de Interpretação (Interpretation Bias)

### ⚠️ Risco para Este Projeto

**ALTO** - Stakeholders não-técnicos interpretarão resultados

### 📌 Manifestações Possíveis

#### 8.1 Correlação ≠ Causação

**Problema:** Stakeholder vê r=-0.22 entre RSSI e msg6_rate e conclui "RSSI causa falhas"  
**Exemplo:** Correlação pode ser mediada por terceira variável (temperatura afeta RSSI E chip)

**Checklist de Mitigação:**
- [ ] Adicionar disclaimer SEMPRE: "Correlação não implica causação"
- [ ] Usar linguagem precisa: "RSSI correlaciona com falhas" (não "causa")
- [ ] Criar diagramas causais quando possível (temperatura → RSSI → falhas)
- [ ] Documentar confounders conhecidos: "Temperatura pode influenciar ambos"
- [ ] Evitar implicar causação em títulos de gráficos

#### 8.2 "Falso Positivo" vs "Falha Real"

**Problema:** msg_type 6 pode ser alarme falso (device funcionando mas reportou erro)  
**Exemplo:** Device reporta CHIP_FAIL mas continua funcionando normalmente após reset

**Checklist de Mitigação:**
- [ ] Adicionar métrica: "Taxa de auto-recuperação" por tipo de erro
- [ ] Documentar: "Error code 7 tem 80% auto-recuperação → provável falso positivo"
- [ ] Criar classificação: "Falhas permanentes" vs "Falhas transitórias"
- [ ] Evitar alarmar cliente com msg_type 6 que se auto-corrigem
- [ ] Adicionar contexto: "X% deste tipo de erro se resolve automaticamente"

#### 8.3 "Significância Estatística" vs "Relevância Prática"

**Problema:** p<0.001 mas r=0.05 → Estatisticamente significativo mas praticamente irrelevante  
**Exemplo:** "Temperatura correlaciona significativamente (p<0.001)" mas explica apenas 0.25% da variância

**Checklist de Mitigação:**
- [ ] Sempre reportar **tamanho do efeito** (r, r²) junto com p-value
- [ ] Documentar: "p<0.001 MAS r²=0.0025 (0.25% variância explicada)"
- [ ] Usar threshold prático: "Correlação relevante: |r| > 0.3 OU r² > 10%"
- [ ] Evitar enfatizar p-value sem contexto de magnitude
- [ ] Adicionar interpretação: "Estatisticamente significativo mas efeito FRACO"

---

## 9. Viés de Medição (Measurement Bias)

### ⚠️ Risco para Este Projeto

**MÉDIO** - Telemetrias podem ter erros de medição ou calibração

### 📌 Manifestações Possíveis

#### 9.1 Precisão de Sensores

**Problema:** Sensor de temperatura pode ter erro ±2°C  
**Exemplo:** Correlação temperatura × falhas pode ser ruído de medição

**Checklist de Mitigação:**
- [ ] Documentar precisão de sensores: "Temperatura: ±2°C, Bateria: ±0.01V"
- [ ] Calcular SNR (Signal-to-Noise Ratio) de medições
- [ ] Filtrar outliers óbvios: "Temperatura >100°C ou <-40°C → provável erro"
- [ ] Adicionar intervalo de confiança em visualizações
- [ ] Evitar interpretar correlações fracas em medições ruidosas

#### 9.2 Timestamp Accuracy

**Problema:** @timestamp pode ter drift (relógio do device dessincronizado)  
**Exemplo:** "Pico de falhas às 3h AM" pode ser artefato de timezone ou drift

**Checklist de Mitigação:**
- [ ] Verificar consistência de timestamps: "Todos timestamps em GMT? UTC?"
- [ ] Calcular gap entre mensagens consecutivas: "Gaps >24h indicam possível drift"
- [ ] Documentar timezone: "Timestamps em GMT-3 (horário Brasília)"
- [ ] Filtrar eventos com timestamps impossíveis (futuro ou 1970)
- [ ] Adicionar warning: "Precisão temporal ±5 minutos"

#### 9.3 Missing Data Patterns

**Problema:** Dados faltantes podem não ser aleatórios (MNAR - Missing Not At Random)  
**Exemplo:** RSSI ausente apenas quando sinal está MUITO fraco (device não consegue enviar)

**Checklist de Mitigação:**
- [ ] Testar se missing values são aleatórios: "Little's MCAR test"
- [ ] Comparar características de devices com/sem telemetria
- [ ] Documentar: "RSSI ausente em X% dos casos - provável viés de medição"
- [ ] Evitar imputar valores faltantes sem entender mecanismo de ausência
- [ ] Adicionar análise: "Devices sem RSSI têm taxa de msg6 Y% maior"

---

## 10. Viés Operacional (Operational Bias)

### ⚠️ Risco para Este Projeto

**ALTO** - Dashboard influenciará decisões operacionais

### 📌 Manifestações Possíveis

#### 10.1 Profecia Auto-Realizável

**Problema:** Dashboard mostra "Device X em risco" → Técnico troca device → "Predição confirmada"  
**Exemplo:** Device poderia ter se auto-recuperado, mas foi trocado preventivamente

**Checklist de Mitigação:**
- [ ] Documentar: "Recomendação NÃO é predição - device pode se auto-recuperar"
- [ ] Adicionar métrica: "Taxa de auto-recuperação histórica: X%"
- [ ] Criar protocolo: "Aguardar 24h antes de dispatch se error code Y"
- [ ] Evitar linguagem definitiva: "Device falhará" → Usar: "Device apresenta padrão Z"
- [ ] Trackear intervenções: Registrar se device foi trocado ou se auto-recuperou

#### 10.2 Otimização Prematura

**Problema:** Stakeholder vê correlação r=-0.2 e decide investir em solução cara  
**Exemplo:** "RSSI correlaciona → Vamos comprar 1000 amplificadores de sinal"

**Checklist de Mitigação:**
- [ ] Adicionar análise de ROI: "RSSI explica 4% das falhas - amplificador reduz 4% de dispatches?"
- [ ] Documentar custo-benefício: "Investimento $X para redução de Y% falhas"
- [ ] Recomendar piloto: "Testar amplificador em 10 devices antes de escalar"
- [ ] Evitar implicar que solução única resolverá problema complexo
- [ ] Adicionar seção: "Outros fatores a considerar" (temperatura, bateria, etc)

#### 10.3 Tunnel Vision

**Problema:** Dashboard foca em msg_type 6 → Time ignora outros problemas  
**Exemplo:** Device sem msg_type 6 mas com bateria crítica é negligenciado

**Checklist de Mitigação:**
- [ ] Adicionar seção: "Devices sem msg_type 6 mas com risco" (bateria <2.5V, etc)
- [ ] Criar alertas para múltiplos indicadores, não só msg_type 6
- [ ] Documentar: "msg_type 6 é apenas 1 indicador - verificar bateria, RSSI, temperatura"
- [ ] Evitar criar incentivo perverso: "Zero msg_type 6 = sucesso" (device pode estar morto)
- [ ] Adicionar métrica de saúde holística: "Health Score = f(msg6, bateria, RSSI, uptime)"

---

## ✅ CHECKLIST DE VALIDAÇÃO FINAL

### Antes de Publicar Dashboard

- [ ] Todas visualizações têm título claro e descritivo
- [ ] Todos eixos têm labels com unidades (°C, dBm, %, etc)
- [ ] Disclaimers adicionados: "Correlação ≠ Causação"
- [ ] Limitações documentadas: "Dataset cobre apenas Jan-Out 2025, rede VIVO"
- [ ] Resultados negativos reportados: "O que NÃO correlaciona"
- [ ] P-values ajustados para múltiplas comparações (Bonferroni)
- [ ] Tamanho do efeito (r, r²) reportado junto com p-value
- [ ] Intervalos de confiança adicionados em gráficos
- [ ] Seção "Como Interpretar" para stakeholders não-técnicos
- [ ] Contact info para reportar bugs ou questionar resultados

### Antes de Apresentar para Stakeholders

- [ ] Preparar slide: "Limitações desta Análise"
- [ ] Preparar slide: "O que NÃO podemos concluir"
- [ ] Preparar resposta: "Como validamos esses padrões?"
- [ ] Preparar protocolo: "Como agir baseado nestes insights?"
- [ ] Ter análise de sensibilidade: "E se removermos outliers?"
- [ ] Ter análise de robustez: "Padrão se mantém em subgrupos?"

### Monitoramento Contínuo (Pós-Deploy)

- [ ] Criar alerta: "Correlação mudou >30% no último mês"
- [ ] Criar alerta: "Novo padrão detectado (não visto antes)"
- [ ] Criar alerta: "Dataset cresceu >20% - re-validar análises"
- [ ] Documentar decisões tomadas baseadas em dashboard
- [ ] Trackear outcome: "Recomendação X levou a resultado Y?"
- [ ] Revisar checklist mensalmente: "Novos vieses identificados?"

---

## 📚 REFERÊNCIAS E RECURSOS

### Livros Recomendados

1. **"Thinking, Fast and Slow"** - Daniel Kahneman (vieses cognitivos)
2. **"The Book of Why"** - Judea Pearl (causalidade)
3. **"Trustworthy Online Controlled Experiments"** - Kohavi et al. (A/B testing, p-hacking)

### Papers Relevantes

1. **Simpson's Paradox** - IEEE Transactions on Knowledge and Data Engineering
2. **Missing Data Mechanisms** - Little & Rubin (MCAR, MAR, MNAR)
3. **Multiple Testing Corrections** - Bonferroni, Benjamini-Hochberg

### Ferramentas

1. **Scipy.stats** - Testes estatísticos (spearmanr, pearsonr, ttest_ind)
2. **Statsmodels** - Little's MCAR test, decomposição STL
3. **Plotly** - Visualizações interativas com intervalos de confiança

---

## 🎯 PRINCÍPIO GUIA

> **"Não busque confirmar o que você acha que sabe.  
> Busque REFUTAR o que você acha que sabe.  
> O que sobreviver à refutação é conhecimento robusto."**

---

**Bom trabalho! 🛡️**  
Use este checklist como **guia vivo** - adicione novos vieses conforme identificados.

---

_Checklist criado: 03/Nov/2025_  
_Última atualização: 03/Nov/2025_  
_Status: ATIVO - Revisar mensalmente_
