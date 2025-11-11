# CONTEÚDO APRESENTAÇÃO POC - IoT Sensor Failure Prediction

## SLIDE 0 - CAPA (Title Slide Layout)

**Título:**
Predição de Falhas em Sensores IoT
Proof of Concept - Machine Learning para Manutenção Preditiva

**Subtítulo:**
Leonardo Bora
Estagiário Engenharia de Software - P&D
8° período | UniBrasil Centro Universitário
Novembro 2025

---

## SLIDE 1 - OBJETIVOS DO PROJETO

**Título:** Objetivos do Projeto

**Bullets:**
- Desenvolver modelo Machine Learning para predição de falhas em sensores IoT
- Reduzir downtime operacional através de manutenção preditiva antecipada
- Validar viabilidade técnica e científica da abordagem (Proof of Concept)
- Identificar limitações metodológicas e roadmap para produção

---

## SLIDE 2 - DESENVOLVIMENTO: DATASET & FEATURES

**Título:** Desenvolvimento - Dataset & Features

**Bullets:**
- Dataset: 789 devices (552 train, 237 test) com split estratificado por device_id
- Imbalance: 45 devices críticos (5.7%) - ratio 16.8:1 Normal:Critical
- 29 Features finais após feature engineering:
  • Telemetria (18): temperatura, umidade, pressão, etc.
  • Conectividade (9): RSSI, SNR, pacotes perdidos, etc.
  • Messaging (2): msg_type_3_count, msg_type_4_count
- Período Lifecycle: Lab → Inactive → Production (dados agregados)
- Data Leakage Descoberto e Corrigido: msg6_count/msg6_rate removidos (100% correlação target)

---

## SLIDE 3 - DESENVOLVIMENTO: METODOLOGIA ML

**Título:** Desenvolvimento - Metodologia ML

**Bullets:**
- Pipeline ML: SimpleImputer (median) → SMOTE (0.5) → CatBoostClassifier
- Comparação Algoritmos (Test Set 237 devices, 14 críticos):
  • XGBoost: 71.4% recall, 71.4% precision (baseline)
  • LightGBM: 64.3% recall, 69.2% precision (rejeitado)
  • CatBoost: 78.6% recall, 84.6% precision (SELECIONADO)
- Validação Rigorosa:
  • 111/114 testes automatizados PASSING (97.4%)
  • Split estratificado zero overlap train/test
  • Reproducibilidade: scripts/reproduce_results.py confirma determinismo (random_state=42)

---

## SLIDE 4 - RESULTADOS: PERFORMANCE DO MODELO

**Título:** Resultados - Performance do Modelo

**Bullets:**
- Métricas Test Set (237 devices, 14 críticos):
  • Recall: 78.6% (11/14 devices críticos detectados)
  • Precision: 84.6% (apenas 2 falsos alarmes = 0.8% FP rate)
  • F1-Score: 81.5%
  • AUC: 86.21%
- Business Impact:
  • 78.6% cobertura manutenção preditiva antecipada
  • Overhead operacional aceitável (0.8% falsos positivos)
- CatBoost vs XGBoost: +7.2% recall, +13.2% precision

---

## SLIDE 5 - RESULTADOS: LIMITAÇÕES & CONSCIÊNCIA CIENTÍFICA

**Título:** Resultados - Limitações & Consciência Científica

**Bullets:**
- Limitação Identificada:
  • Dataset 1-row/device agregado sobre lifecycle completo
  • Lab → Inactive → Production SEM separação temporal
  • Impossível distinguir padrões causais vs simultâneos
- Lifecycle Confounding:
  • Deployment patterns podem criar artifacts organizacionais
  • Features agregadas misturam fases distintas operação
- Mitigação Implementada:
  • Drift monitoring com KS test (29 features)
  • A/B testing guide (4 fases deployment)
  • Feature engineering roadmap temporal (5 priorities)

---

## SLIDE 6 - PRÓXIMOS PASSOS

**Título:** Próximos Passos

**Bullets:**
- Produção (3-4 semanas):
  • Performance testing (carga 1000 devices/sec, latência <50ms)
  • Hardening resilience (retry logic, circuit breakers)
  • Audit trail completo (predições rastreadas JSON)
  • Model registry versões múltiplas + rollback strategy
- Médio Prazo (3-6 meses):
  • Feature engineering temporal (rolling windows, time-series)
  • Teste A/B produção novos algoritmos
  • Otimização recall (meta 85-90% coverage)

---

## SLIDE 7 - CONCLUSÕES

**Título:** Conclusões

**Bullets:**
- POC Validada:
  • Viabilidade técnica confirmada (78.6% recall, 84.6% precision)
  • Rigor validado (111/114 testes, reproducibilidade determinística)
  • Resultados promissores para produção
- Aprendizados Principais:
  • Análise empírica identifica data leakage crítico
  • Comparação algoritmos rigorosa (CatBoost > XGBoost/LightGBM)
  • Consciência científica sobre limitações metodológicas
- Próxima Fase:
  • Roadmap produtivo 3-4 semanas deployment
  • Evolução médio prazo feature engineering temporal

---

## EMAIL COPY PARA STAKEHOLDERS

**Assunto:** Apresentação POC - Predição de Falhas Sensores IoT | Estágio P&D

**Corpo:**

Prezados,

Tenho o prazer de compartilhar os resultados do Proof of Concept desenvolvido durante meu estágio em P&D na Lightera: **Predição de Falhas em Sensores IoT utilizando Machine Learning para Manutenção Preditiva**.

**Destaques do Projeto:**
- **Modelo CatBoost** com 78.6% de recall e 84.6% de precision no test set
- **Cobertura preditiva de 78.6%**: detecção antecipada de 11/14 devices críticos
- **Overhead operacional mínimo**: apenas 0.8% de falsos positivos (2/237 devices)
- **Validação rigorosa**: 111/114 testes automatizados, reproducibilidade determinística confirmada

**Consciência Científica:**
Identifiquei e documentei limitações metodológicas importantes (impossibilidade de causalidade temporal no dataset agregado, lifecycle confounding) e implementei estratégias de mitigação (drift monitoring, A/B testing guide, roadmap feature engineering temporal).

**Próximos Passos:**
Roadmap produtivo de 3-4 semanas para deployment (performance testing, hardening, audit trail completo) e evolução médio prazo (3-6 meses) focando em otimização de recall (meta 85-90%).

Anexo a apresentação completa detalhando **Objetivos**, **Desenvolvimento** e **Resultados**.

Fico à disposição para apresentar uma demo técnica ou discutir detalhes da implementação.

Atenciosamente,

**Leonardo Bora**  
Estagiário Engenharia de Software - P&D  
8° período | UniBrasil Centro Universitário  
Lightera Latam
