# 🔄 PIVOT ESTRATÉGICO - De Predição para Observabilidade

**Data:** 03 de novembro de 2025  
**Stakeholders:** Mariana Salamoni (P.O.), Enzo (Suporte Técnico/Domain Expert), Leonardo Costa (Dev)  
**Status:** ✅ **PIVOT CONFIRMADO E APROVADO**

---

## 🎯 DESCOBERTA FUNDAMENTAL

### ❌ O que NÃO funciona (Abordagem Anterior)
**Problema:** msg_type 6 é **RETROSPECTIVO** por natureza
- Device **JÁ FALHOU** quando emite msg_type 6
- Logs reportam "o que aconteceu" (passado), não "o que vai acontecer" (futuro)
- Device com msg_type 6 **NÃO está condenado** - muitos se recuperam
- Predição de falhas **não faz sentido** neste contexto

### ✅ O que FUNCIONA (Nova Abordagem)
**Solução:** Análises **INDICATIVAS TEMPORAIS**
- **Observabilidade:** Compreender padrões nos dados
- **Monitoramento:** "QUANDO" ocorrem falhas, "QUAIS" fatores influenciam
- **Diagnóstico:** Encontrar falhas **FÍSICAS** através de padrões digitais
  - Temperatura externa extrema
  - Desconexão física do SIM (mal-contato)
  - Interferência ambiental
  - Degradação de componentes

---

## 📊 PALAVRA-CHAVE: OBSERVABILIDADE

**Definição operacional:**  
> "Compreender os dados para revelar padrões que entreguem valor acionável ao cliente"

**Não é:**
- ❌ Predição de falhas futuras
- ❌ Machine Learning complexo
- ❌ Scores preditivos de "risco"

**É:**
- ✅ Análises descritivas inteligentes
- ✅ Padrões temporais indicativos
- ✅ Correlações acionáveis
- ✅ Diagnóstico de causas raiz

---

## 🎨 MODELO DE REFERÊNCIA: Aplicação Enzo

### Características da UX "Banquete" (Palavras de Salamoni)

**Stack Técnico:**
- Streamlit (interface intuitiva)
- Login via AWS
- Consulta interativa de logs

**Features Principais:**
1. **Status de Sensores**
   - Ativos / Inativos / Alarmados / Silenciados
   
2. **Foco NB-IoT** (não LoRa)
   - Monitoramento generalista **não serve** suporte técnico
   - Análises específicas permitem diagnóstico preciso
   
3. **Apresentação Intuitiva**
   - Dados complexos → Visualizações compreensíveis
   - Cliente entende → Cliente age

**Por que funciona:**
- Resolve problema real do suporte (especificidade NB-IoT)
- UX permite exploração interativa dos dados
- Não cria mais trabalho - **reduz** gargalo

---

## 🏢 CONTEXTO DE NEGÓCIO

### Clientes Principais
- **VIVO:** Maior cliente NB-IoT (volume ativo significativo)
- **Fibrasil:** Maior cliente LoRa (mas muitos inativos - **não nosso foco**)

### Módulo Insights do EyOn
**Situação Atual:**
- ✅ Já existe
- ✅ Modelo de negócio BI-like
- ❌ **Não entrega valor suficiente** na ponta para o cliente

**Oportunidade:**
- Evoluir módulo existente
- Adicionar análises indicativas
- Focar em valor acionável

### Restrição Crítica: Time é Gargalo
**Problema:**
- Time JÁ está sobrecarregado
- Solução **não pode criar mais carga**

**Implicação:**
- Dashboard deve ser **sustentável**
- Análises devem ser **escaláveis**
- Manutenção deve ser **mínima**

---

## 🔍 PERGUNTAS-CHAVE A RESPONDER

### 1. Quando mais ocorrem as falhas?
**Análises:**
- Distribuição por hora do dia
- Distribuição por dia da semana
- Sazonalidade mensal/anual
- Correlação com eventos (manutenções, upgrades)

**Valor:**
- Identificar janelas de vulnerabilidade
- Planejar manutenções preventivas
- Evitar upgrades em horários críticos

---

### 2. Quais fatores influenciam as falhas?
**Análises:**
- Correlação com temperatura externa
- Correlação com RSSI/RSRP/RSRQ
- Correlação com battery voltage
- Análise por região geográfica (VIVO SP vs VIVO Pernambuco)

**Valor:**
- Distinguir falhas digitais vs físicas
- Priorizar intervenções (temperatura > conectividade)
- Identificar lotes problemáticos de hardware

---

### 3. Padrões de recuperação após falhas?
**Análises:**
- Tempo médio de auto-recuperação
- Taxa de recuperação por tipo de erro
- Devices que precisam intervenção vs auto-corrigem

**Valor:**
- Evitar dispatches desnecessários (device se recupera sozinho)
- Identificar devices que **realmente** precisam troca
- Otimizar SLA de atendimento

---

### 4. Falhas digitais vs físicas?
**Análises:**
- Padrão de erro code 7 (CHIP_FAIL) vs temperatura
- Padrão de erro code 9 (REGISTRATION_TIMEOUT) vs RSSI
- Padrão de error clusters vs localização geográfica

**Valor:**
- Diagnóstico remoto mais preciso
- Direcionamento correto: troca device vs ajuste infraestrutura
- Redução de custos operacionais

---

## 📈 ROADMAP DE IMPLEMENTAÇÃO

### Fase 1: Foundation Analytics (2-3 semanas)
**Objetivo:** Análises descritivas core

**Deliverables:**
1. ✅ Database msg_type 6 (notebook 01b - **JÁ FEITO**)
2. ✅ Análise temporal (notebook 01 - **JÁ FEITO**)
3. ✅ Correlações hardware (notebook 02 - **JÁ FEITO**)
4. 🔜 **Dashboard Streamlit v0.1:**
   - Login AWS (reutilizar código Enzo)
   - Visualização distribuição temporal msg_type 6
   - Filtros: device_id, date_range, error_code
   - Tabela top 20 serial offenders

**Critério de Sucesso:** Mariana + Enzo validam utilidade das visualizações

---

### Fase 2: Indicative Patterns (3-4 semanas)
**Objetivo:** Análises que revelam "QUANDO" e "QUAIS FATORES"

**Deliverables:**
1. **Análise Temporal Avançada:**
   - Heatmap hora × dia da semana
   - Clustering de eventos (rajadas vs espaçados)
   - Sazonalidade mensal

2. **Análise de Correlações:**
   - Temperature × msg6 rate (por region)
   - RSSI × error code distribution
   - Battery voltage × auto-recovery time

3. **Dashboard Streamlit v0.2:**
   - Seção "Quando ocorrem falhas?"
   - Seção "Fatores correlacionados"
   - Drill-down por device_id

**Critério de Sucesso:** Cliente VIVO identifica padrão acionável

---

### Fase 3: Root Cause Insights (4-5 semanas)
**Objetivo:** Análises que distinguem falhas físicas vs digitais

**Deliverables:**
1. **Análise de Error Chains:**
   - Sequências [1, 15, 7] vs [1, 9, 10]
   - Root cause distribution por região
   - Co-ocorrência de error codes

2. **Physical Failure Indicators:**
   - Temperatura extrema + CHIP_FAIL → "Provável falha térmica"
   - Battery drop + REGISTRATION_TIMEOUT → "Provável mal-contato SIM"
   - RSSI baixo + error code 9 → "Provável cobertura fraca"

3. **Dashboard Streamlit v0.3:**
   - Seção "Diagnóstico de Causas Raiz"
   - Recomendações automáticas ("Device X: verificar temperatura ambiente")
   - Exportar relatório PDF para cliente

**Critério de Sucesso:** Suporte técnico reduz tempo de diagnóstico em 30%

---

### Fase 4: Integration & Scale (ongoing)
**Objetivo:** Integrar ao módulo Insights do EyOn

**Deliverables:**
1. API de integração com EyOn
2. Autenticação centralizada
3. Permissões por cliente (VIVO vê só VIVO)
4. Processamento batch para escalabilidade

**Critério de Sucesso:** Módulo Insights entrega valor mensurável ao cliente

---

## 🔧 STACK TÉCNICO

### Backend
- **Python 3.11+** (análises)
- **Pandas** (processamento dados)
- **AWS SDK** (logs access)

### Frontend
- **Streamlit** (dashboard interativo)
- **Plotly** (visualizações)
- **Altair** (gráficos declarativos)

### Infraestrutura
- **AWS Lambda** (processamento batch)
- **S3** (armazenamento análises)
- **Secrets Manager** (credenciais)

**Princípio:** Reutilizar código da aplicação Enzo sempre que possível

---

## ✅ VALIDAÇÃO DO TRABALHO ANTERIOR

### O que foi VÁLIDO (aproveitar)
1. ✅ **Notebook 01b:** Database msg_type 6 - **CORE** da observabilidade
2. ✅ **Notebook 01:** Análise temporal - responde "QUANDO" ocorrem falhas
3. ✅ **Notebook 02:** Correlações hardware - responde "QUAIS FATORES"
4. ✅ **Constitution:** Princípios de ground-truth e evidência - **MANTÉM**
5. ✅ **Train-test split temporal:** Boa prática - útil para validar padrões

### O que foi EXERCÍCIO (aprendizado)
1. 📚 **Notebooks 02b-02g:** Tentativas de predição - ensinaram **o que não fazer**
2. 📚 **Survivorship bias check:** Validou que predição não é o caminho
3. 📚 **Feature importance:** Mostrou SNR paradox - insights sobre interações

**Lição aprendida:** "Falhar rápido" foi CORRETO - pivotamos antes de investir meses

---

## 🚫 O QUE ABANDONAR

### Descontinuar Imediatamente
1. ❌ Modelos preditivos (Random Forest, Isolation Forest)
2. ❌ Health scores probabilísticos
3. ❌ SMOTE, class balancing, threshold tuning
4. ❌ Feature engineering para predição
5. ❌ Train-test split para validação de modelo

### Por que abandonar?
- msg_type 6 é retrospectivo (não preditivo)
- Device não está "condenado" após falha
- Valor está em **entender padrões**, não **prever futuro**
- Time já é gargalo - ML complexo criaria mais carga

---

## 📋 PRÓXIMAS AÇÕES

### Semana 04-08 Nov 2025
1. **Criar notebook 03:** Análises descritivas para dashboard
   - Distribuição temporal (hora × dia)
   - Top error codes por região
   - Correlação temperatura × msg6_rate

2. **Protótipo Streamlit v0.1:**
   - Setup básico com login AWS
   - Visualização distribuição temporal
   - Tabela devices com mais msg_type 6

3. **Reunião validação (sexta):**
   - Demo para Mariana + Enzo
   - Coletar feedback UX
   - Priorizar análises Fase 2

---

## 🎓 LIÇÕES APRENDIDAS

### 1. Natureza dos Dados Define Abordagem
**Erro:** Assumir que logs de erro são preditivos  
**Correção:** Entender que msg_type 6 é retrospectivo  
**Princípio:** **Sempre perguntar "O que esses dados REALMENTE dizem?"**

---

### 2. Stakeholder Alignment é Crítico
**Erro:** Trabalhar 2 semanas em predição sem validação  
**Correção:** Reunião com Mariana + Enzo revelou real necessidade  
**Princípio:** **Validar direção ANTES de implementar**

---

### 3. Simplicidade > Sofisticação
**Erro:** Buscar ML complexo (RF, SMOTE, SHAP)  
**Correção:** Análises descritivas entregam mais valor  
**Princípio:** **Resolver problema real, não exibir técnica**

---

### 4. Sustentabilidade é Requisito
**Erro:** Não considerar que time é gargalo  
**Correção:** Dashboard Streamlit é sustentável, ML não seria  
**Princípio:** **Solução deve reduzir trabalho, não criar mais**

---

## 🎯 CRITÉRIOS DE SUCESSO (REDEFINIDOS)

### Métrica 1: Adoção pelo Cliente
**Meta:** VIVO usa dashboard **semanalmente** para análise de frota  
**Como medir:** Logs de acesso AWS

---

### Métrica 2: Redução Tempo Diagnóstico
**Meta:** Suporte técnico reduz tempo de diagnóstico em **30%**  
**Como medir:** Tempo médio de ticket "device com msg_type 6"

---

### Métrica 3: Identificação Padrões Acionáveis
**Meta:** Cliente identifica **3+ padrões** que levam a ações (ex: "trocar devices em região X por temperatura")  
**Como medir:** Relatórios de ação pós-análise

---

### Métrica 4: Sustentabilidade do Time
**Meta:** Dashboard **não aumenta** carga de trabalho do time  
**Como medir:** Survey interno pré/pós implantação

---

## 🔐 COMPLIANCE CONSTITUCIONAL

### Princípios que SE MANTÊM
1. ✅ **Ground-Truth First:** msg_type 6 continua sendo fonte de verdade
2. ✅ **Evidence-Based:** Correlações testadas antes de apresentar
3. ✅ **Domain Knowledge:** Validação com Enzo mantida

### Princípios que MUDAM
1. 🔄 **Temporal Validation:** Não é mais sobre ML - é sobre padrões temporais
2. 🔄 **Root Cause Analysis:** Foco em diagnóstico, não predição

### Novo Princípio Adicionado
**Princípio VI - Acionabilidade:**
> "Toda análise deve responder 'E daí? O que fazer com isso?'. Insights sem ação são ruído."

---

## 📞 STAKEHOLDER EXPECTATIONS

### Mariana Salamoni (P.O.)
**Expectativa:** Dashboard que entrega **valor mensurável** ao cliente  
**Definição de valor:** Cliente VIVO consegue tomar decisões operacionais baseadas em insights  
**Prazo:** Protótipo v0.1 em **2 semanas** (18 Nov)

---

### Enzo (Suporte Técnico)
**Expectativa:** Ferramenta que **reduz tempo de diagnóstico**  
**Definição de redução:** De "investigar logs manualmente" para "ver painel e saber causa"  
**Prazo:** Dashboard v0.2 com root cause insights em **6 semanas** (15 Dez)

---

### Leonardo (Dev - Você)
**Expectativa:** Construir solução **sustentável** que não vire legado  
**Definição de sustentável:** Código simples, documentado, reutilizável  
**Prazo:** Roadmap completo até **Q1 2026**

---

## 🏁 CONCLUSÃO

### ✅ PIVOT APROVADO
- De **Predição** para **Observabilidade**
- De **ML Complexo** para **Análises Descritivas Inteligentes**
- De **"Vai falhar"** para **"Por que falhou"**

### 🎯 VALOR REAL
- Encontrar **falhas físicas** através de padrões digitais
- Responder **"QUANDO"** e **"QUAIS FATORES"**
- Entregar **insights acionáveis** ao cliente

### 🚀 PRÓXIMO PASSO
- **Semana 04-08 Nov:** Notebook 03 + Streamlit v0.1
- **Sexta 08 Nov:** Demo para Mariana + Enzo
- **Semana 11-15 Nov:** Iterar baseado em feedback

---

**Bom trabalho! 🎉**  
A decisão de pivotar foi **CORRETA** e **NO TEMPO CERTO**.

---

_Documento criado: 03/Nov/2025_  
_Última atualização: 03/Nov/2025_  
_Status: APROVADO por Mariana Salamoni e Enzo_
