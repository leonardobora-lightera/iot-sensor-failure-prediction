# 🎯 PLANO DE AÇÃO - Fix Definitivo para Falsos Positivos por Inatividade

**Data:** 13 de novembro de 2025  
**Contexto:** Resolução do problema identificado com device 861275072515287 (97.5% prob, FALSO POSITIVO)  
**Objetivo:** Eliminar falsos positivos por inatividade pós-laboratório e melhorar precisão do modelo

---

## 📊 PROBLEMA IDENTIFICADO

### Case Study: Device 861275072515287

**Sintomas:**
- ✅ Predição: 97.5% probabilidade de falha (HIGH RISK)
- ❌ Realidade: FALSO POSITIVO por inatividade após testes de laboratório

**Evidências Coletadas:**

| Métrica | Valor | Interpretação |
|---------|-------|---------------|
| **Última comunicação** | 31/10/2025 17:35 | 12 dias de inatividade |
| **Telemetrias FIELD** | optical -12.30 dBm, temp 27°C, battery 3.40V | ✅ SAUDÁVEIS |
| **Distribuição MODE** | 465 FIELD + 38 FACTORY + 174 NaN | Lifecycle mixing! |
| **Shutdown** | 3x msg_type 43 (heartbeat sem dados) | Planejado, não falha |

**Problema Raiz:**
```
Modelo agrega features de TODO o lifecycle:
- FACTORY (testes de laboratório)
- INACTIVE (device desligado/armazenamento)
- FIELD (produção real)

Não tem contexto temporal:
- days_since_last_message ❌
- lifecycle_phase ❌
- is_active ❌

Resultado: Confunde device inativo com device degradando
```

**Validação da Hipótese:**
- ✅ Documentado em `docs/TEMPORAL_LIMITATIONS.md` (escrito ANTES do problema)
- ✅ Roadmap existente em `docs/FEATURE_ENGINEERING_TEMPORAL.md`
- ✅ Análise completa em `analyze_device_861275072515287.py`
- ✅ Correlação perfeita com seção "Devices Silenciosos" do CHECKLIST_MITIGACAO_VIESES.md

---

## 🚀 SOLUÇÃO EM 3 FASES

### FASE 1: QUICK WIN (HOJE - 2-3 horas)

**Objetivo:** Eliminar contaminação FACTORY e adicionar contexto temporal mínimo

**Tarefas:**

1. **Atualizar `scripts/transform_aws_payload.py`:**
```python
def load_aws_payload(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    
    # ⭐ NOVO: Filtrar apenas MODE='FIELD'
    if 'mode' in df.columns:
        initial_count = len(df)
        df = df[df['mode'] == 'FIELD']
        factory_removed = initial_count - len(df)
        logger.info(f"🔧 Removed {factory_removed} FACTORY entries ({factory_removed/initial_count*100:.1f}%)")
    
    return df
```

2. **Adicionar `days_since_last_message`:**
```python
def aggregate_by_device(df: pd.DataFrame) -> pd.DataFrame:
    # ... existing aggregations ...
    
    # ⭐ NOVO: Temporal context
    last_msg_timestamp = df.groupby(device_col)['@timestamp'].max()
    messaging_stats['last_message_timestamp'] = last_msg_timestamp
    messaging_stats['days_since_last_message'] = (
        datetime.now() - pd.to_datetime(last_msg_timestamp)
    ).dt.days
    
    return final_df
```

3. **Re-processar payloads:**
   - Executar transform_aws_payload.py nos arquivos originais (se existirem)
   - Gerar novos CSVs em `payloads_processed/`
   - Validar device 861275072515287 transformado

4. **Commit e push:**
   ```bash
   git add scripts/transform_aws_payload.py payloads_processed/
   git commit -m "feat: Add MODE=FIELD filter and days_since_last_message feature"
   git push origin main
   ```

**Entregáveis:**
- ✅ Payloads transformados production-only (FIELD)
- ✅ Nova feature days_since_last_message (30ª feature)
- ✅ Log de quantos FACTORY entries foram removidos

**Métricas de Sucesso:**
- Device 861275072515287: total_messages reduz de 677 → ~465
- optical_mean/std mudam (sem FACTORY)
- days_since_last_message = 12 para device 861275072515287

---

### FASE 2: RETREINAMENTO (ESTA SEMANA - 1 dia)

**Objetivo:** Modelo aprende padrões production-only

**Tarefas:**

1. **Re-gerar dataset de treino:**
   - Aplicar filtro MODE='FIELD' nos dados brutos originais
   - Re-calcular features para TODOS os devices
   - Gerar novo `data/device_features_with_telemetry_field_only.csv`
   - Comparar distribuição de labels critical/normal

2. **Retreinar modelo CatBoost:**
   ```python
   # 30 features: 29 existentes + days_since_last_message
   pipeline = Pipeline([
       ('imputer', SimpleImputer(strategy='median')),
       ('smote', SMOTE(random_state=42)),
       ('model', CatBoostClassifier(**best_params))
   ])
   
   pipeline.fit(X_train_field_only, y_train)
   
   # Salvar como v2
   joblib.dump(pipeline, 'models/catboost_pipeline_v2_field_only.pkl')
   ```

3. **Validar device 861275072515287:**
   - Carregar modelo v2
   - Fazer predição com features FIELD-only
   - Comparar: v1 (97.5%) vs v2 (esperado <50%)

4. **Deploy:**
   - Substituir modelo v1 por v2
   - Update Streamlit se necessário
   - Testar batch upload com novos payloads

**Entregáveis:**
- ✅ Dataset de treino production-only
- ✅ Modelo v2 (catboost_pipeline_v2_field_only.pkl)
- ✅ Comparação de métricas v1 vs v2
- ✅ Validação de device 861275072515287

**Métricas de Sucesso:**
- Recall ≥ 78.6% (manter ou melhorar)
- Precision > 84.6% (esperado: melhoria significativa)
- Device 861275072515287: prob < 50% OU classificação "INACTIVE"
- Redução de falsos positivos: >20%

---

### FASE 3: FEATURES TEMPORAIS COMPLETAS (2 SEMANAS)

**Objetivo:** Implementação full do `docs/FEATURE_ENGINEERING_TEMPORAL.md`

**Roadmap por Prioridade:**

#### Priority 1: Lifecycle Phase Separation (3 dias)
- Coletar metadata: `activation_timestamp`, `inactive_periods`
- Criar features: `production_duration_days`, `days_inactive_total`
- Filtrar features para production-only phase

#### Priority 2: Time-Windowed Features (3 dias)
- Calcular features em janelas: `battery_mean_last_7d`, `optical_mean_last_30d`
- Enables causal precedence validation (observável ANTES da falha)

#### Priority 3: Trend Features (2 dias)
- Fit linear regression: `battery_trend_30d = slope`
- Captura degradation rate (física), não snapshots

#### Priority 4: Delta and Rate Features (2 dias)
- Calcular change over time: `delta_battery_30d`, `delta_optical_7d`

#### Priority 5: Temporal Metadata Features (2 dias)
- `num_inactive_periods`, `days_since_last_reactivation`
- `message_frequency_per_day` (production only)

**Entregáveis:**
- ✅ Metadata collection pipeline
- ✅ Feature engineering completo (Priority 1-5)
- ✅ Modelo v3 com temporal features
- ✅ A/B testing conforme AB_TESTING_GUIDE.md
- ✅ Deployment gradual

**Métricas de Sucesso:**
- Recall ≥ 80% (target business)
- Precision ≥ 90% (redução de falsos positivos)
- Falsos positivos por inatividade: 0%
- AUC-ROC > 0.90

---

## ⚠️ RISCOS E MITIGAÇÕES

### Risco 1: Filtro MODE='FIELD' remove dados críticos

**Probabilidade:** BAIXA  
**Impacto:** ALTO  

**Mitigação:**
- Validar que devices críticos conhecidos têm dados FIELD suficientes
- Comparar distribuição de labels antes/depois do filtro
- Se perder >10% de devices críticos: revisar estratégia

### Risco 2: Retreinamento piora recall

**Probabilidade:** MÉDIA  
**Impacto:** ALTO  

**Mitigação:**
- Manter threshold de recall ≥ 78.6% (baseline v1)
- Se recall cair: ajustar class_weights ou threshold
- Validar em holdout set antes de deploy

### Risco 3: days_since_last_message tem valores extremos

**Probabilidade:** ALTA  
**Impacto:** MÉDIO  

**Mitigação:**
- Cap values: `days_since_last_message = min(days, 365)`
- Ou usar log-transform: `np.log1p(days)`
- Validar distribuição antes de treinar

### Risco 4: Metadata para Fase 3 não está disponível

**Probabilidade:** ALTA  
**Impacto:** ALTO  

**Mitigação:**
- Coletar metadata AGORA (activation_timestamp, inactive_periods)
- Se indisponível: inferir de logs (first_message → activation)
- Implementar coleta prospectiva para devices novos

---

## 📈 MÉTRICAS DE SUCESSO

### KPIs por Fase

| Fase | Métrica | Baseline (v1) | Target | Como Medir |
|------|---------|---------------|--------|------------|
| **FASE 1** | Payloads processados | N/A | 100% | Log de transform_aws_payload.py |
| | FACTORY entries removidos | N/A | >0 | Comparar antes/depois |
| | days_since_last_message | N/A | ✅ Adicionado | Verificar CSV |
| **FASE 2** | Recall | 78.6% | ≥ 78.6% | Test set evaluation |
| | Precision | 84.6% | > 90% | Test set evaluation |
| | Device 861275072515287 prob | 97.5% | < 50% | Single prediction |
| | Falsos positivos | Baseline | -20% | Manual review top 20 |
| **FASE 3** | Recall | 78.6% | ≥ 80% | Test set evaluation |
| | Precision | 84.6% | ≥ 90% | Test set evaluation |
| | AUC-ROC | 0.8621 | > 0.90 | Test set evaluation |
| | Inatividade FP | Unknown | 0% | Filter days_since > 7 |

### Validação Qualitativa

**Checklist de Validação Fase 1:**
- [ ] Log mostra X FACTORY entries removidos
- [ ] Device 861275072515287: total_messages < 677
- [ ] Device 861275072515287: days_since_last_message = 12
- [ ] CSV tem 30 colunas (29 + days_since_last_message)

**Checklist de Validação Fase 2:**
- [ ] Modelo v2 carrega sem erros
- [ ] Predição device 861275072515287: prob < 50% OU status "INACTIVE"
- [ ] Recall test set ≥ 78.6%
- [ ] Precision test set > 90%
- [ ] Batch upload funciona em cloud

**Checklist de Validação Fase 3:**
- [ ] Todas Priority 1-5 implementadas
- [ ] Features temporais validadas em notebook
- [ ] Modelo v3 supera v2 em precision
- [ ] A/B testing em shadow mode (30 dias)
- [ ] Deploy gradual sem degradação de métricas

---

## 📋 TODO LIST (GERADO)

10 tarefas criadas no sistema de TODO:

**FASE 1 (Tasks 1-5):**
1. Atualizar transform_aws_payload.py com filtro MODE='FIELD'
2. Adicionar days_since_last_message em aggregate_by_device()
3. Re-processar payloads AWS com filtros novos
4. Validar transformação de device 861275072515287
5. Commit e push Fase 1

**FASE 2 (Tasks 6-9):**
6. Filtrar MODE='FIELD' no dataset de treino original
7. Retreinar modelo CatBoost com features production-only
8. Testar predição de device 861275072515287 com modelo v2
9. Deploy modelo v2 para cloud Streamlit

**FASE 3 (Task 10):**
10. Planejar implementação features temporais completas

---

## 🎓 LIÇÕES APRENDIDAS

### O Que Funcionou Bem

1. **Documentação Prévia:** TEMPORAL_LIMITATIONS.md previu o problema ANTES de ocorrer
2. **Checklist de Vieses:** CHECKLIST_MITIGACAO_VIESES.md guiou a investigação
3. **Case Study:** Device 861275072515287 forneceu evidência clara
4. **Raciocínio Estruturado:** Sequential thinking levou à solução em 8 passos

### O Que Aprendemos

1. **MODE column é CRÍTICA:** Separa FACTORY/FIELD - deve ser filtrada sempre
2. **Temporal context importa:** days_since_last_message é feature essencial
3. **Lifecycle mixing causa FP:** Agregação sem separação de fases = falsos positivos
4. **Inatividade ≠ Falha:** Devices inativos precisam flag separada

### Aplicação Futura

1. **Sempre filtrar MODE='FIELD'** em qualquer agregação
2. **Adicionar temporal features** desde o início de projetos IoT
3. **Separar lifecycle phases** em feature engineering
4. **Validar com case studies** reais antes de deploy

---

## 📚 REFERÊNCIAS

### Documentação Técnica
- `docs/TEMPORAL_LIMITATIONS.md` - Limitações temporais do modelo atual
- `docs/FEATURE_ENGINEERING_TEMPORAL.md` - Roadmap completo de features temporais
- `docs/CHECKLIST_MITIGACAO_VIESES.md` - Checklist de vieses (seção 1.1 atualizada)
- `docs/AB_TESTING_GUIDE.md` - Guia de A/B testing para Fase 3

### Scripts e Dados
- `scripts/transform_aws_payload.py` - Pipeline de transformação (a ser atualizado)
- `analyze_device_861275072515287.py` - Análise temporal do case study
- `device_861275072515287_2025-11-13.csv` - Dados completos do device crítico

### Notebooks de Referência
- `notebooks/old/02_correlacao_telemetrias_msg6.ipynb` - Padrões de agregação

---

**Status:** PRONTO PARA IMPLEMENTAÇÃO  
**Próxima Ação:** Começar Fase 1 - Task 1  
**Owner:** Time de Data Science  
**Prazo Fase 1:** 13/Nov/2025 (hoje)  
**Prazo Fase 2:** 15/Nov/2025 (sexta-feira)  
**Prazo Fase 3:** 27/Nov/2025 (2 semanas)

---

**Aprovado por:** _[Aguardando aprovação do usuário]_  
**Data de Aprovação:** _[Pendente]_
