""""""

Página 5: Contexto da Pesquisa - Descobertas e AprendizadosPage 5: Research Context - Project Background & Key Discoveries

Versão PT-BR Acessível - Linguagem Simplificada para Stakeholders"""

"""import streamlit as st

import streamlit as stimport sys

import sysfrom pathlib import Path

from pathlib import Path

# Add project root to path

# Add project root to pathsys.path.append(str(Path(__file__).parent.parent))

sys.path.append(str(Path(__file__).parent.parent))

from utils.translations import get_text, get_language_from_session

# Header

st.title("📖 Contexto da Pesquisa & Descobertas")# Get language

st.markdown("### Como desenvolvemos o modelo de predição de falhas e o que aprendemos no processo")lang = get_language_from_session(st.session_state)



st.markdown("---")# Header

st.title(get_text('research', 'title', lang))

# ===== SEÇÃO 1: O PROBLEMA =====st.markdown(f"### {get_text('research', 'subtitle', lang)}")

st.subheader("🎯 O Problema que Queríamos Resolver")

st.markdown("---")

col1, col2 = st.columns([2, 1])

# Section 1: The Problem

with col1:st.subheader(get_text('research', 'problem_title', lang))

    st.markdown("""

    **Sensores IoT Falhando Sem Aviso Prévio**col1, col2 = st.columns([2, 1])

    

    Imagine uma empresa com **789 sensores IoT** espalhados monitorando sistemas críticos with col1:

    (temperatura, umidade, conectividade, etc.). Ao longo do tempo, **45 desses sensores     st.markdown("""

    falharam** (5.7% do total), causando:    **IoT Device Failures in Production Environments**

        

    - 🚨 **Paradas não planejadas**: Sistemas param de funcionar sem aviso    Our organization deployed **789 IoT devices** for critical monitoring applications. 

    - 💰 **Custo elevado**: Manutenção emergencial custa 3-5x mais que preventiva    Over time, **45 devices (5.7%) exhibited critical failures** requiring emergency maintenance.

    - ⏰ **Tempo perdido**: Equipe técnica precisa investigar 789 sensores para achar os 45 problemáticos    

    - 😰 **Risco operacional**: Falhas podem afetar clientes e operações críticas    **Challenges:**

        - 🚨 **Unplanned downtime** causes revenue loss and customer dissatisfaction

    **Nossa Missão:**      - ⚙️ **Emergency repairs** cost 3-5x more than preventive maintenance

    Criar um sistema que **preveja QUAIS sensores vão falhar ANTES de falharem**,     - 📊 **No early warning system** - failures discovered reactively

    permitindo manutenção preventiva e evitando custos emergenciais.    - 🔍 **Manual inspection** of 789 devices infeasible (resource constraints)

        

    Pense nisso como um "check-up médico" para sensores - detectar problemas antes     **Business Objective:**

    de virarem emergências! 🏥    Build a machine learning model to **predict critical devices BEFORE failure** 

    """)    enabling **preventive maintenance** and **resource optimization**.

    """)

with col2:

    st.info("""with col2:

    **📊 Números do Projeto**    st.info("""

        **Impact Metrics**

    - **789** sensores no total    

    - **45** falharam (5.7%)    - **789** total devices

    - **744** funcionaram normalmente    - **45** critical failures (5.7%)

    - **29** características analisadas    - **16.8:1** imbalance ratio

    - **78.6%** taxa de detecção    - **29** telemetry features

    - **0.8%** alarmes falsos    - **78.6%** recall achieved

    """)    - **84.6%** precision achieved

    """)

st.markdown("---")

st.markdown("---")

# ===== SEÇÃO 2: NOSSA SOLUÇÃO =====

st.subheader("💡 Como Resolvemos (Processo Simplificado)")# Section 2: Technical Approach

st.subheader("🔬 Technical Approach & Pipeline")

st.markdown("""

Desenvolvemos uma solução em **3 passos principais**, usando Machine Learning st.markdown("""

(ensinar computador a reconhecer padrões):Our solution follows a **rigorous data science methodology** with emphasis on validation and avoiding data leakage.

""")""")



col1, col2, col3 = st.columns(3)# Pipeline diagram

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""with col1:

    ### 1️⃣ Separar Dados    st.markdown("""

        **1️⃣ Data Preparation**

    **O que fizemos:**    

    - Dividimos os 789 sensores em dois grupos    - ✅ **Stratified split** by device_id

    - **552 sensores** para "ensinar" o computador    - ✅ **Zero overlap** (552 train, 237 test)

    - **237 sensores** para "testar" se aprendeu    - ✅ **Balanced proportions** (5.6% vs 5.9% critical)

        - ❌ **Temporal split REJECTED** (data leakage)

    **Por que assim:**    """)

    - É como estudar com 70% das questões e fazer prova com 30% inéditas

    - Garante que modelo não está "colando" - precisa realmente entender padrõeswith col2:

    - Nenhum sensor aparece nos dois grupos (zero repetição)    st.markdown("""

        **2️⃣ Feature Engineering**

    **Desafio:**    

    - 45 falhas é pouco (5.7% apenas)    - 📊 **29 clean features** (telemetry + connectivity + messaging)

    - Precisamos dividir mantendo proporção similar nos dois grupos    - ⚠️ **Leakage detection** (removed msg6_count, msg6_rate)

    - Usamos técnica "estratificada" para garantir equilíbrio    - 📈 **Statistical analysis** (t-tests, distributions)

    """)    - 🔗 **Correlation study** (multicollinearity check)

    """)

with col2:

    st.markdown("""with col3:

    ### 2️⃣ Testar Algoritmos    st.markdown("""

        **3️⃣ Model Development**

    **O que fizemos:**    

    - Testamos 3 algoritmos diferentes (tipos de "cérebro" do computador)    - 🎯 **SMOTE 0.5** (handle 16.8:1 imbalance)

    - **XGBoost**: Algoritmo popular, nossa referência inicial    - 🤖 **Algorithm comparison** (XGB, LGBM, CatBoost)

    - **LightGBM**: Algoritmo rápido, mas acertou menos    - 🏆 **CatBoost WINNER** (78.6% recall, 84.6% precision)

    - **CatBoost**: Algoritmo mais cuidadoso, VENCEDOR! 🏆    - 📦 **Production pipeline** (SimpleImputer → SMOTE → CatBoost)

        """)

    **Resultados:**

    - XGBoost: 71.4% de acerto (10 de 14 falhas detectadas)st.markdown("---")

    - LightGBM: 64.3% de acerto (9 de 14 falhas detectadas)

    - **CatBoost: 78.6% de acerto** (11 de 14 falhas detectadas)# Section 2.5: Why CatBoost?

    st.subheader("🤖 Why CatBoost? - Algorithm Explained")

    **Por que CatBoost ganhou:**

    - Aprende de forma mais "cuidadosa" (evita decorar padrões falsos)st.markdown("""

    - Funciona melhor com poucos dados (nosso caso - só 45 falhas)**CatBoost** (Categorical Boosting) is a gradient boosting algorithm developed by Yandex. 

    - Gerou menos alarmes falsos (2 vs 4 do XGBoost)We selected it over XGBoost and LightGBM based on rigorous comparison (see MODEL_COMPARISON.md).

    """)""")



with col3:col1, col2 = st.columns(2)

    st.markdown("""

    ### 3️⃣ Validar Rigorosamentewith col1:

        st.markdown("""

    **O que fizemos:**    **🔍 What is CatBoost?**

    - Criamos **111 testes automatizados** para validar cada parte    

    - Garantimos que resultados são **reproduzíveis** (sempre iguais)    CatBoost is an **advanced gradient boosting** algorithm that builds an ensemble of 

    - Documentamos **limitações** (ser honesto sobre o que NÃO sabemos)    **decision trees sequentially**, where each tree corrects errors from previous trees.

        

    **Validações importantes:**    **Key Technical Advantages:**

    - ✅ Modelo funciona em dados nunca vistos (237 sensores teste)    

    - ✅ Métricas exatas confirmadas por script independente    1. **Ordered Boosting** 📊

    - ✅ Sem "vazamento de informação" (dados teste não influenciam treino)       - Prevents **target leakage** during training

    - ✅ Performance estável (não varia entre execuções)       - Reduces overfitting compared to XGBoost's level-wise approach

           - Uses different permutations to compute residuals

    **Resultado Final:**    

    - 78.6% das falhas detectadas antecipadamente    2. **Symmetric Trees** 🌳

    - Apenas 0.8% de alarmes falsos (2 em 237)       - Builds **balanced binary trees** (fewer leaves)

    - Modelo pronto para teste em produção 🚀       - Faster prediction time in production

    """)       - Better generalization on unseen data

    

st.markdown("---")    3. **Native Categorical Support** 🏷️

       - Handles categorical features WITHOUT one-hot encoding

# ===== SEÇÃO 3: DESCOBERTAS DO CAMINHO =====       - Computes optimal splits using target statistics

st.subheader("🔍 Descobertas Importantes do Caminho")       - (Not used in this project - all features numerical)

    """)

st.markdown("""

Durante o desenvolvimento, fizemos **descobertas importantes** que mudaram nossa abordagem. with col2:

Cada erro foi uma oportunidade de aprender! Aqui estão os 4 principais aprendizados:    st.markdown("""

""")    **🏆 Why CatBoost Won for This Project**

    

# Descoberta 1: Split Temporal Falhou    We compared 3 algorithms using identical SMOTE 0.5 preprocessing:

with st.expander("**🚨 Descoberta 1: Tentar Dividir por Tempo Foi Um Desastre (0% de Acerto)**", expanded=False):    

    st.markdown("""    | Algorithm | Recall | Precision | F1 | False Alarms |

    #### O Que Tentamos Fazer    |-----------|--------|-----------|----|--------------| 

        | XGBoost   | 71.4%  | 71.4%     | 71.4% | 4/237 (1.7%) |

    Pensamos: "Vamos usar dados antigos para treinar e dados recentes para testar".     | LightGBM  | 64.3%  | 69.2%     | 66.7% | 4/237 (1.7%) |

    Parecia fazer sentido - como aprender história usando fatos passados para prever futuros!    | **CatBoost** | **78.6%** | **84.6%** | **81.5%** | **2/237 (0.8%)** |

        

    #### O Que Aconteceu    **CatBoost delivered:**

        - ✅ **+7.2pp recall** vs XGBoost (1 more critical device detected)

    **Resultado: 0% de acerto!** 😱      - ✅ **+13.2pp precision** vs XGBoost (50% fewer false alarms)

    O modelo não detectou NENHUMA falha nos dados de teste. Total fracasso.    - ✅ **Exceeds 80% precision target** (business requirement)

        - ✅ **21.4% miss rate** vs 28.6% XGBoost (better risk reduction)

    #### Por Que Falhou (Descoberta Técnica)    

        **Business Impact:**

    **Problema:** Nossos dados não são uma "linha do tempo" - são uma **foto final**.    - 11/14 critical devices detected (vs 10/14 XGBoost)

        - Only 2 false alarms in 237 devices (vs 4 XGBoost)

    Imagine assim:    - Optimized investigation workload

    - Cada sensor tem **1 linha** juntando TODOS os meses de operação    

    - É como tirar foto de alguém aos 30 anos e tentar adivinhar como era aos 10    **Technical Insight:**

    - Dados "antigos" e "recentes" são na verdade **o mesmo sensor em momentos diferentes**    CatBoost's **ordered boosting** likely performed better due to our 

    - 650 sensores apareceram nos DOIS grupos (treino E teste) - vazamento massivo!    **small critical sample size** (31 training critical devices). The algorithm's 

        built-in overfitting protection proved crucial for this imbalanced dataset.

    **Analogia:**    """)

    > É como estudar questões de uma prova e depois fazer a MESMA prova pensando 

    > que é diferente. Óbvio que você vai gabaritar... mas não aprendeu nada de verdade!st.markdown("---")

    

    #### O Que Aprendemos# Section 3: Key Discoveries & Lessons Learned

    st.subheader("💡 Key Discoveries & Critical Lessons")

    ✅ **Lição:** Dividir por tempo só funciona com dados tipo "série temporal" (1 linha = 1 momento)  

    ✅ **Solução:** Dividimos por SENSOR (cada sensor aparece EM UM grupo só)  # Discovery 1: Temporal Split Failure

    ✅ **Impacto:** Performance caiu de 0% (inválido) para 50% (honesto) - começamos do zero realwith st.expander("**🚨 Discovery 1: Temporal Split Failed (0% Recall)**", expanded=True):

        st.markdown("""

    **Documentação:** Ver CHANGELOG.md Phase 2 para análise completa do erro    **Problem:** Initial approach split data by time (old messages → train, recent → test)

    """)    

    **Result:** Model achieved **0% recall** - couldn't detect ANY critical devices!

# Descoberta 2: Data Leakage MSG6    

with st.expander("**🔍 Descoberta 2: Achamos Uma 'Cola' nos Dados e Removemos**", expanded=False):    **Root Cause Analysis:**

    st.markdown("""    - Dataset was **aggregated** (1 row per device, not time-series)

    #### O Que Encontramos    - Temporal split created **650 devices in BOTH train and test** (severe leakage)

        - Model memorized device IDs instead of learning patterns

    Nosso modelo estava com **87.5% de precisão** - parecia incrível! 🎉      - Critical devices appeared in training data, test became "easy memorization"

    Mas investigamos e descobrimos que estava "colando na prova"...    

        **Lesson Learned:** 

    #### A "Cola" (Data Leakage)    > ⚠️ **Always validate split assumptions** - temporal split only valid for true time-series data

        > 

    Havia duas características suspeitas nos dados:    > ✅ **Stratified split by device_id** ensures zero overlap and honest evaluation

    - `msg6_count`: Quantidade de mensagens tipo 6 enviadas    

    - `msg6_rate`: Taxa de mensagens tipo 6    **Impact:** Switching to stratified split → **50% recall baseline** (honest performance)

        """)

    **Descoberta chocante:**  

    Mensagem tipo 6 significa **"Sensor reportando status crítico"**! 😱# Discovery 2: MSG6 Leakage

    with st.expander("**🔍 Discovery 2: Data Leakage from msg6_count Feature**", expanded=False):

    **O problema:**    st.markdown("""

    > É como perguntar "Este aluno vai reprovar?" e uma das informações disponíveis     **Problem:** Model with `msg6_count` feature achieved suspicious **87.5% precision**

    > é "Quantidade de vezes que disse 'estou reprovando'". Óbvio que é a resposta disfarçada!    

        **Investigation:** Analyzed feature importance and distributions

    **Prova do vazamento:**    

    - Feature `msg6_count` foi a **#1 mais importante** (31% do modelo)    **Finding:**

    - Sensores críticos: SEMPRE enviam msg6    - `msg6_count` was **#1 feature** (31% importance - red flag!)

    - Sensores normais: NUNCA enviam msg6    - Message type 6 = **"Device Critical Status Report"**

    - Correlação 100% com resposta - isso é "colar", não "prever"    - Critical devices send MORE msg6 messages by definition

        - Feature contains **ground truth label information** (data leakage)

    #### O Que Fizemos    

        **Action Taken:**

    1. ❌ **Removemos** `msg6_count` e `msg6_rate` completamente    - ❌ Removed `msg6_count` and `msg6_rate` from feature set

    2. ✅ **Re-treinamos** modelo com apenas 29 features "honestas"    - ✅ Re-trained model with 29 clean features only

    3. ✅ **Performance caiu** de 87.5% para 50% (esperado - agora é real)    - ✅ Performance dropped to 50% recall (expected with honest features)

        

    #### O Que Aprendemos    **Lesson Learned:**

        > ⚠️ **High single-feature importance = potential leakage indicator**

    ⚠️ **Lição:** Performance MUITO alta pode ser sinal de problema, não sucesso!      > 

    ✅ **Sempre perguntar:** "Esta informação estaria disponível ANTES da falha?"      > ✅ **Domain knowledge critical** - understand what features MEAN in business context

    ✅ **Entender domínio:** Saber o que features significam salva de armadilhas    > 

        > ✅ **Validate feature distributions** between critical and normal groups

    **Analogia Final:**    

    > Preferimos modelo com 78.6% HONESTO do que 95% "colando".     **Impact:** Honest baseline established → enabled real optimization work

    > Um médico que acerta 80% dos diagnósticos é melhor que um que acerta 100%     """)

    > lendo o resultado do exame! 🏥

    """)# Discovery 3: Synthetic Data Validation

with st.expander("**🧪 Discovery 3: Theoretical vs Empirical Synthetic Data**", expanded=False):

# Descoberta 3: CatBoost Venceu    st.markdown("""

with st.expander("**🏆 Descoberta 3: CatBoost Foi 7% Melhor Que XGBoost**", expanded=False):    **Experiment:** Validate model using synthetic critical devices

    st.markdown("""    

    #### Comparação de Algoritmos (Teste Cego)    **Approach 1 - Theoretical (NB06):**

        - **Assumption:** "High values = critical" (e.g., p75-p100 percentiles)

    Testamos 3 algoritmos diferentes usando os MESMOS dados para ser justo:    - **Method:** Sample from upper quartiles of general distribution

        - **Result:** 0% recall - TOTAL FAILURE ❌

    | Algoritmo | Falhas Detectadas | Alarmes Falsos | Decisão |    

    |-----------|-------------------|----------------|---------|    **Approach 2 - Empirical (NB06B):**

    | XGBoost   | 10/14 (71.4%)     | 4/237 (1.7%)   | 🥈 Baseline |    - **Validation:** Analyzed critical vs normal distributions FIRST

    | LightGBM  | 9/14 (64.3%)      | 4/237 (1.7%)   | ❌ Descartado |    - **Discovery:** Direction varies by feature (battery LOW, temp HIGH, messages VARIABLE)

    | **CatBoost** | **11/14 (78.6%)** | **2/237 (0.8%)** | 🏆 **VENCEDOR** |    - **Method:** SMOTE interpolation from REAL critical devices (preserves correlations)

        - **Result:** 100% recall - validates SMOTE works ✅

    #### Por Que CatBoost Ganhou    

        **Lesson Learned:**

    **1. Detectou MAIS falhas** (+1 sensor vs XGBoost)    > ⚠️ **Theoretical assumptions fail** - "high values = bad" is not universal

    - XGBoost: 10 de 14 críticos detectados    > 

    - CatBoost: 11 de 14 críticos detectados    > ✅ **Empirical analysis required** - test statistical differences before sampling

    - **+7.2 pontos percentuais** de melhoria    > 

        > ✅ **SMOTE preserves patterns** - interpolates within real distribution manifold

    **2. Gerou MENOS alarmes falsos** (metade!)    

    - XGBoost: 4 investigações desnecessárias    **Important Caveat:**

    - CatBoost: 2 investigações desnecessárias    - 100% synthetic recall does NOT mean model is better than 78.6% real recall

    - **50% de redução** em trabalho desperdiçado    - Synthetic generated FROM training critical → model KNOWS these patterns

        - Real test set (78.6%) remains **authoritative validation**

    **3. Funciona melhor com poucos dados**    - Synthetic useful for **stress testing edge cases**, not independent validation

    - CatBoost aprende de forma mais "cautelosa"    """)

    - Evita "decorar" padrões que são coincidência

    - Ideal para nosso caso (só 45 falhas para aprender)# Discovery 4: Algorithm Comparison

    with st.expander("**⚖️ Discovery 4: CatBoost Outperforms XGBoost and LightGBM**", expanded=False):

    #### Explicação Simples: Como Funciona?    st.markdown("""

        **Experiment:** Compare 3 gradient boosting algorithms with SMOTE 0.5

    **Analogia do Médico:**    

        **Results:**

    Imagine 3 médicos diagnosticando doenças:    

        | Model | Recall | Precision | F1-Score | AUC | Decision |

    - **LightGBM:** Médico apressado - rápido mas erra muito    |-------|--------|-----------|----------|-----|----------|

    - **XGBoost:** Médico experiente - bom mas às vezes confia demais em 1 sintoma    | XGBoost + SMOTE | 71.4% | 71.4% | 71.4% | 0.8799 | Baseline |

    - **CatBoost:** Médico meticuloso - analisa TODOS sintomas com cuidado    | LightGBM + SMOTE | 64.3% | 69.2% | 66.7% | 0.8823 | ❌ DISQUALIFIED (recall < 70%) |

        | **CatBoost + SMOTE** | **78.6%** | **84.6%** | **81.5%** | **0.8621** | ✅ **WINNER** |

    CatBoost é o "médico meticuloso" - demora um pouco mais mas acerta mais!    

        **Why CatBoost Won:**

    #### Impacto Real    - ✅ **+7.2 pp recall improvement** (10/14 → 11/14 critical detected)

        - ✅ **+13.2 pp precision improvement** (71.4% → 84.6%, only 2 false alarms)

    Em 1000 sensores hipotéticos:    - ✅ **Ordered boosting** reduces overfitting on small dataset (789 total, 45 critical)

    - **CatBoost:** 47 falhas evitadas, 8 alarmes falsos    - ✅ **Symmetric trees** provide better generalization vs XGBoost asymmetric

    - **XGBoost:** 42 falhas evitadas, 16 alarmes falsos    

        **Lesson Learned:**

    **Ganho:** +5 sensores salvos + metade do trabalho desperdiçado! 💰    > ✅ **Test multiple algorithms** - different inductive biases work better on different data

        > 

    **Documentação:** Ver MODEL_COMPARISON.md para análise técnica completa    > ✅ **CatBoost excels on small datasets** - default regularization prevents overfitting

    """)    > 

    > ⚠️ **Tradeoff exists** - CatBoost slightly lower AUC but MUCH better precision/recall

# Descoberta 4: Limitação Temporal (NOVA!)    

with st.expander("**⚠️ Descoberta 4: Dataset Tem Problema Temporal (Limitação Crítica)**", expanded=True):    **See MODEL_COMPARISON.md** for complete analysis with confusion matrices and business impact.

    st.markdown("""    """)

    #### O Problema Temporal Descoberto

    st.markdown("---")

    Durante validação final da POC, identificamos uma **limitação metodológica crítica** 

    que afeta a interpretação dos resultados.# Section 4: Features Engineering Deep Dive

    st.subheader("🔧 Features Engineering: 29 Features Explained")

    **Problema:** Cada sensor tem **1 linha** agregando **TODO o período operacional**.

    st.markdown("""

    #### Entendendo a Limitação (Analogia Simples)Our final model uses **29 numerical features** extracted from IoT device telemetry, grouped into 3 categories:

    """)

    Imagine que você quer prever se uma criança vai ter problemas de saúde aos 18 anos.

    tab1, tab2, tab3 = st.tabs(["📡 Telemetry (18)", "📶 Connectivity (9)", "📨 Messaging (2)"])

    **Dataset ideal (série temporal):**

    - Linha 1: Peso aos 5 anoswith tab1:

    - Linha 2: Peso aos 10 anos    st.markdown("""

    - Linha 3: Peso aos 15 anos    ### Telemetry Features (18 total)

    - Linha 4: Peso aos 18 anos (resultado)    

        **Optical Sensor (7 features):**

    **Nosso dataset (agregado):**    - `optical_mean`, `optical_std`, `optical_min`, `optical_max` - Central tendency and spread

    - Linha única: Peso médio dos 5 aos 18 anos + resultado aos 18    - `optical_readings` - Sample count (data quality indicator)

        - `optical_below_threshold` - Degradation indicator

    **Consequência:**      - `optical_range` - Variability metric

    > Não conseguimos distinguir se "peso alto" ocorreu ANTES (causa) ou     

    > JUNTO com problema (coincidência). Tudo está misturado!    **Temperature Sensor (6 features):**

        - `temp_mean`, `temp_std`, `temp_min`, `temp_max` - Thermal distribution

    #### O Problema em 3 Fases (Lifecycle)    - `temp_above_threshold` - Overheating indicator

        - `temp_range` - Thermal stability

    Sensores passam por 3 fases de vida:    

        **Battery/Power (5 features):**

    1. **🔬 Lab:** Testados em laboratório (ambiente controlado)    - `battery_mean`, `battery_std`, `battery_min`, `battery_max` - Voltage distribution

    2. **💤 Inactive:** Guardados esperando instalação (sem uso)    - `battery_below_threshold` - Low power events

    3. **🏭 Production:** Operando em campo (ambiente real)    

        **Engineering Rationale:**

    **Nossos dados misturam tudo:**    - **Aggregations** capture both average behavior (mean) and variability (std, range)

    - Temperatura média = média Lab + Inactive + Production    - **Thresholds** encode domain knowledge (e.g., battery < 3.0V = critical)

    - Conectividade = mistura de 3 ambientes diferentes    - **Min/Max** detect extreme events (spikes, drops)

    - Não sabemos QUANDO padrão aconteceu    

        **Key Insight:** Critical devices show **LOW battery** (power failure), **HIGH temp** (overheating), 

    **Exemplo Real:**    **VARIABLE optical** (unstable sensor) - NOT universally "high values".

    > Sensor tem "temperatura alta" nos dados. Mas isso foi:    """)

    > - Em Lab (teste de estresse - normal) ✅

    > - Ou em Production (superaquecimento - problema) ❌with tab2:

    >     st.markdown("""

    > Impossível separar! Dados agregados não têm informação temporal.    ### Connectivity Features (9 total)

        

    #### O Que Isso Significa Para o Modelo    **Signal-to-Noise Ratio - SNR (3 features):**

        - `snr_mean`, `snr_std`, `snr_min` - Signal quality distribution

    **Modelo detecta CORRELAÇÃO, não prova CAUSA:**    - **Importance:** Low SNR indicates poor signal → communication failures

        

    ✅ **O que podemos dizer:**    **Reference Signal Received Power - RSRP (3 features):**

    - "Sensores com padrão X têm 78.6% chance de falhar"    - `rsrp_mean`, `rsrp_std`, `rsrp_min` - Signal strength distribution

    - "Modelo identifica 11/14 sensores problemáticos"    - **Importance:** Weak signal (< -110 dBm) → device struggling to connect

    - "Útil para priorizar inspeções"    

        **Reference Signal Received Quality - RSRQ (3 features):**

    ❌ **O que NÃO podemos dizer:**    - `rsrq_mean`, `rsrq_std`, `rsrq_min` - Link quality distribution

    - "Padrão X CAUSA falha" (pode ser coincidência temporal)    - **Importance:** Poor quality → retransmissions, latency, eventual dropout

    - "Padrão X ocorreu ANTES da falha" (pode ter sido simultâneo)    

    - "Modelo prevê o FUTURO" (pode estar detectando o PRESENTE)    **Engineering Rationale:**

        - **Mean values** show average connectivity health

    #### Por Que Isso É IMPORTANTE    - **Std/variability** indicates connection stability (stable vs flaky)

        - **Min values** detect worst-case scenarios (connection almost lost)

    **Cenário de risco:**    

    - Empresa pode implementar modelo achando que está "prevendo futuro"    **Key Insight:** Critical devices show **degrading connectivity BEFORE complete failure** 

    - Na verdade pode estar apenas "detectando presente"    (SNR dropping, RSRP weakening, RSRQ unstable) - early warning signal!

    - Sensor já pode ter falhado quando modelo alerta    """)

    

    **Analogia:**with tab3:

    > É como "prever" que alguém está doente medindo febre.     st.markdown("""

    > Tecnicamente funciona... mas febre JÁ É a doença, não previsão dela!    ### Messaging Features (2 total)

        

    #### Como Mitigamos (Consciência Científica)    **`total_messages` (count):**

        - Total number of messages sent by device in observation window

    Implementamos 3 estratégias para lidar com limitação:    - **Low values:** Silent device (already failed or communication blocked)

        - **Normal values:** Regular telemetry reporting (healthy)

    **1. 📊 Drift Monitoring (Monitoramento de Mudanças)**    - **High values:** Possible "death throes" (device spamming before failure)

    - Detecta quando dados novos são diferentes dos antigos    

    - Usa teste estatístico (KS test) em 29 características    **`max_frame_count` (integer):**

    - Alerta se modelo está "desaprendendo" (dados mudaram)    - Maximum frame count observed in message fragmentation

    - **Script:** `scripts/drift_monitor.py`    - **High values:** Device attempting **desperate reconnection** (communication stress)

        - **Importance:** #1 or #2 most important feature across all models

    **2. 🧪 A/B Testing (Teste em Produção)**    - **Interpretation:** When device struggles, it fragments messages more (retries, errors)

    - Guia completo para validar modelo empiricamente    

    - 4 fases: Shadow → Controlled → Monitoring → Full Deploy    **Engineering Rationale:**

    - Compara sensores COM predição vs SEM predição    - **Activity level** (total_messages) separates silent failures from active devices

    - **Documento:** `docs/AB_TESTING_GUIDE.md` (950 linhas)    - **Fragmentation stress** (max_frame_count) detects communication desperation

        

    **3. 🔮 Feature Engineering Temporal (Futuro)**    **Key Insight:** `max_frame_count` is a **communication stress indicator** - 

    - Roadmap para coletar dados time-series (múltiplas linhas/sensor)    critical devices show abnormally high frame counts as they struggle to maintain connection.

    - Rolling windows (janelas de 7 dias, 30 dias)    

    - Tendências temporais (aumentando vs diminuindo)    **Why only 2 messaging features?**

    - **Documento:** `docs/FEATURE_ENGINEERING_TEMPORAL.md` (850 linhas)    - Originally had `msg6_count`, `msg6_rate` → **REMOVED due to data leakage**

        - Message type 6 = "Critical Status Report" → contains ground truth label info

    #### Nossa Postura (Transparência > Ocultar)    - Keeping only neutral messaging metrics (total volume, fragmentation) ensures honest prediction

        """)

    **Por que documentamos limitação:**

    1. ✅ **Honestidade científica** - reconhecer o que não sabemosst.markdown("---")

    2. ✅ **Gerenciar expectativas** - stakeholders entendem escopo

    3. ✅ **Planejar mitigação** - roadmap claro para melhorar# Section 5: Validation Philosophy

    4. ✅ **Evitar surpresas** - produção validará empiricamentest.subheader("✅ Validation Philosophy & Best Practices")

    

    **Frase-chave:**col1, col2 = st.columns(2)

    > "Consciência das limitações é FORÇA, não fraqueza. Modelo com 78.6% honesto 

    > e transparente é melhor que modelo com 95% com assumptions escondidas."with col1:

        st.markdown("""

    **Documentação Completa:** Ver `docs/TEMPORAL_LIMITATIONS.md` (1000 linhas)     **What We Did RIGHT ✅**

    para análise técnica detalhada das limitações metodológicas.    

    """)    1. **Stratified Split by Device ID**

       - Zero overlap between train (552) and test (237)

st.markdown("---")       - Balanced proportions (5.6% vs 5.9% critical)

       - Honest evaluation on unseen devices

# ===== SEÇÃO 4: LIMITAÇÕES CONHECIDAS (NOVA SEÇÃO) =====    

st.subheader("⚠️ Limitações Conhecidas (Transparência Científica)")    2. **Leakage Detection & Removal**

       - Analyzed feature importance distributions

st.markdown("""       - Removed msg6_count/msg6_rate (ground truth leak)

**Ser honesto sobre o que NÃO sabemos é tão importante quanto demonstrar o que sabemos.**       - Validated with domain experts

    

Esta seção documenta as **limitações metodológicas** identificadas durante a POC.     3. **Empirical Validation Over Theory**

Reconhecer limitações é sinal de **maturidade científica**, não fraqueza.       - Tested synthetic data assumptions (NB06 failure)

""")       - Corrected with empirical analysis (NB06B success)

       - Statistical tests before engineering features

col1, col2 = st.columns(2)    

    4. **Multiple Algorithm Comparison**

with col1:       - XGBoost, LightGBM, CatBoost tested

    st.markdown("""       - Decision matrix with business criteria

    ### 🔴 Limitação 1: Impossibilidade Causal Temporal       - Documented tradeoffs (MODEL_COMPARISON.md)

        

    **Problema:**    5. **Production-Ready Pipeline**

    - Dataset = 1 linha/sensor agregando todo histórico       - End-to-end Pipeline (Imputer → SMOTE → CatBoost)

    - Não sabemos QUANDO padrões ocorreram       - Saved artifacts (joblib + metadata JSON)

    - Lab + Inactive + Production misturados       - Inference functions for batch/single prediction

        """)

    **Consequência:**

    - Modelo detecta **correlação**, não **causa**with col2:

    - Não podemos provar que padrão veio ANTES de falha    st.markdown("""

    - Pode estar detectando problema JÁ existente    **Lessons for Future Projects ⚠️**

        

    **Analogia:**    1. **Split Validation**

    > Médico vendo raio-X de corpo inteiro de vida toda.        - ❌ Don't assume temporal split works for aggregated data

    > Consegue ver problema, mas não sabe se foi aos 5 ou 50 anos.       - ✅ Validate overlap between train/test BEFORE modeling

           - ✅ Use stratification for imbalanced classes

    **Mitigação:**    

    - ✅ Drift monitoring detecta mudanças dados    2. **Feature Leakage**

    - ✅ A/B testing validará empiricamente produção       - ❌ Don't trust high single-feature importance blindly

    - ✅ Roadmap feature engineering temporal       - ✅ Understand what features MEAN in business context

           - ✅ Check if feature contains "future information"

    ---    

        3. **Theoretical Assumptions**

    ### 🟡 Limitação 2: Lifecycle Confounding       - ❌ Don't assume "high = bad" or "low = good"

           - ✅ Analyze distributions empirically FIRST

    **Problema:**       - ✅ Use statistical tests (t-test, Mann-Whitney)

    - Sensores passam Lab → Inactive → Production    

    - Features agregam fases com comportamentos diferentes    4. **Synthetic Validation**

    - Padrões organizacionais podem criar artifacts       - ❌ Don't use synthetic as independent validation

           - ✅ Understand synthetic = interpolation of training

    **Exemplo:**       - ✅ Use real held-out test set as authoritative

    - Sensor temperatura alta: teste Lab ou falha Production?    

    - Sensor sem mensagens: armazenado Inactive ou quebrado?    5. **Documentation**

    - Conectividade ruim: laboratório sem rede ou campo sem sinal?       - ✅ Document decisions (why CatBoost vs XGBoost?)

           - ✅ Keep history of failed approaches (learning value)

    **Consequência:**       - ✅ Create artifacts for stakeholders (MODEL_COMPARISON.md)

    - Difícil separar comportamento normal vs anormal    """)

    - Deployment patterns podem influenciar modelo

    st.markdown("---")

    **Mitigação:**

    - ✅ Documentado em TEMPORAL_LIMITATIONS.md# Section 6: Business Impact Summary

    - ✅ Validação produção comparará sensores similaresst.subheader("💼 Business Impact & ROI")

    - ✅ Futuro: separar fases lifecycle em features distintas

    """)col1, col2, col3 = st.columns(3)



with col2:with col1:

    st.markdown("""    st.metric(

    ### 🟢 Limitação 3: Amostra Pequena Classe Crítica        "Critical Devices Detected",

            "11/14",

    **Problema:**        delta="78.6% coverage",

    - Apenas 45 sensores críticos no total        help="Preventive maintenance triggered for 11 critical devices"

    - 31 para treino, 14 para teste    )

    - Difícil generalizar com poucos exemplos    st.caption("**Prevented failures** before emergency breakdown")

    

    **Consequência:**with col2:

    - Modelo pode não capturar TODOS tipos de falha    st.metric(

    - 3 falhas não detectadas (21.4% miss rate)        "False Alarms",

    - Novos modos de falha podem aparecer produção        "2/237",

            delta="0.8% FP rate",

    **Por que aceitável:**        delta_color="inverse",

    - ✅ 78.6% coverage já é grande melhoria vs 0% (reativo)        help="Only 2 false positives in entire normal population"

    - ✅ Miss rate 21.4% aceitável para POC    )

    - ✅ Modelo evolui com mais dados produção    st.caption("**Minimal investigation overhead** for operations team")

    

    **Mitigação:**with col3:

    - ✅ Continuar coletando dados produção    st.metric(

    - ✅ Re-treinar modelo periodicamente        "Missed Failures",

    - ✅ Meta médio prazo: 85-90% recall        "3/14",

            delta="21.4% miss rate",

    ---        delta_color="inverse",

            help="3 critical devices not detected (acceptable tradeoff)"

    ### 🔵 Limitação 4: Validação POC vs Produção    )

        st.caption("**Fallback:** Manual inspection + domain expertise")

    **Status Atual: POC (Proof of Concept)**

    st.markdown("""

    **O que validamos:****Scenario: 1000 Devices Deployed**

    - ✅ Viabilidade técnica (78.6% recall possível)

    - ✅ Reproducibilidade (scripts/reproduce_results.py)- ✅ **47 failures prevented** vs 42 without model (+5 devices saved)

    - ✅ Rigor metodológico (111/114 testes passing)- ✅ **12 emergency repairs** vs 17 without model (-5 urgent calls)

    - ✅ **8 false alarms** vs 16 with baseline model (-50% investigation cost)

    **O que NÃO validamos ainda:**- 💰 **Estimated savings:** $25K-$50K per year (reduced downtime + optimized maintenance)

    - ⏳ Performance em dados produção real (A/B test pendente)

    - ⏳ Latência <50ms para 1000 devices/sec**Model enables proactive maintenance strategy** shifting from reactive firefighting to planned interventions.

    - ⏳ Robustez edge cases (CSV malformado, NaN 100%)""")

    

    **Roadmap Produção (3-4 semanas):**st.markdown("---")

    1. Performance testing carga

    2. Hardening resilience (retry logic, circuit breakers)# Footer

    3. Audit trail completo (rastreabilidade)st.info("""

    4. Model registry múltiplas versões + rollback📚 **Further Reading:**

    - **MODEL_COMPARISON.md** - Complete algorithm comparison with confusion matrices

    **Postura:**- **Notebooks 02B-08** - Detailed technical implementation and validation

    > Esta é uma POC validando IDEIA, não produto final pronto. - **CHANGELOG.md** - Complete project timeline (12 phases)

    > Sabemos gaps e temos plano claro para endereçar.""")

    """)

st.caption("""

st.info("""**Research Context** | IoT Predictive Maintenance Project | CatBoost v1.0 | November 2025

💡 **Por que documentar limitações?**""")


1. **Gerenciar expectativas:** Stakeholders sabem o que esperar do modelo
2. **Planejar evolução:** Roadmap claro para melhorias futuras  
3. **Evitar surpresas:** Produção já sabe desafios potenciais
4. **Demonstrar maturidade:** Consciência científica > ocultar problemas

**Frase-chave:** "Transparência sobre limitações gera mais confiança que promessas irrealistas."
""")

st.markdown("---")

# ===== SEÇÃO 5: IMPACTO REAL =====
st.subheader("💼 Impacto Real no Negócio")

st.markdown("""
**Traduzindo métricas técnicas para valor business:**  
De cada 100 sensores críticos, conseguimos detectar 79 ANTES de falharem!
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Falhas Detectadas",
        "11/14",
        delta="78.6% cobertura",
        help="11 sensores críticos detectados antecipadamente de 14 totais"
    )
    st.caption("**Manutenção preventiva** programada antes de quebrar")

with col2:
    st.metric(
        "Alarmes Falsos",
        "2/237",
        delta="0.8% taxa FP",
        delta_color="inverse",
        help="Apenas 2 investigações desnecessárias em 237 sensores normais"
    )
    st.caption("**Overhead mínimo** para equipe operacional")

with col3:
    st.metric(
        "Falhas Não Detectadas",
        "3/14",
        delta="21.4% miss rate",
        delta_color="inverse",
        help="3 sensores críticos que modelo não previu"
    )
    st.caption("**Fallback:** Inspeção manual + expertise domínio")

st.markdown("---")

# Cenário Hipotético
st.markdown("""
### 📈 Cenário Hipotético: 1000 Sensores Implantados

**Assumindo mesma proporção 5.7% falhas (57 sensores críticos):**

| Métrica | Sem Modelo (Reativo) | Com Modelo (Preditivo) | Melhoria |
|---------|---------------------|------------------------|----------|
| **Falhas Detectadas Antecipadamente** | 0 (0%) | 45 (78.6%) | +45 sensores |
| **Manutenções Emergenciais** | 57 (100%) | 12 (21.4%) | -45 emergências |
| **Investigações Desnecessárias** | N/A | 8 (0.8% de 943) | 8 inspeções |
| **Sensores Salvos vs Baseline XGBoost** | N/A | +5 vs XGBoost | +5 sensores |

**💰 Estimativa de Economia Anual:**

- **Custo manutenção emergencial:** R$ 5.000 por sensor
- **Custo manutenção preventiva:** R$ 1.500 por sensor
- **Economia por sensor:** R$ 3.500

**Cálculo:**
- 45 sensores: manutenção preventiva (R$ 1.500) vs emergencial (R$ 5.000)
- **45 × R$ 3.500 = R$ 157.500 economizados/ano** 💰
- Mais: redução downtime, satisfação cliente, produtividade equipe

**Custo investigações falsas:**
- 8 investigações × R$ 500 = R$ 4.000
- **ROI líquido: R$ 153.500/ano** (39x retorno)

---

**Importante:** Números são estimativas baseadas em test set 237 sensores. 
Validação em produção (A/B testing) confirmará performance real.
""")

st.markdown("---")

# ===== SEÇÃO 6: VALIDAÇÃO E RIGOR =====
st.subheader("✅ Validação & Rigor Científico")

st.markdown("""
**Como garantimos que resultados são confiáveis:**
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ✅ O Que Fizemos Certo
    
    **1. Split Estratificado por Sensor**
    - ✅ Zero overlap treino/teste (552 vs 237)
    - ✅ Proporções balanceadas (5.6% vs 5.9% críticos)
    - ✅ Avaliação honesta em sensores nunca vistos
    
    **2. Detecção e Remoção Leakage**
    - ✅ Analisamos importância features
    - ✅ Removemos msg6_count/msg6_rate (vazamento)
    - ✅ Validamos com expertise domínio
    
    **3. Validação Empírica > Teórica**
    - ✅ Testamos assumptions com dados reais
    - ✅ Corrigimos quando teoria falhou (NB06)
    - ✅ Testes estatísticos antes engineering
    
    **4. Comparação Múltiplos Algoritmos**
    - ✅ XGBoost, LightGBM, CatBoost testados
    - ✅ Critérios business definidos (recall > precision)
    - ✅ Tradeoffs documentados (MODEL_COMPARISON.md)
    
    **5. Reproducibilidade Validada**
    - ✅ Script standalone confirma métricas exatas
    - ✅ 111/114 testes automatizados (97.4% passing)
    - ✅ Random seed fixo (determinismo)
    - ✅ `scripts/reproduce_results.py` prova científica
    """)

with col2:
    st.markdown("""
    ### 📚 Lições Para Futuros Projetos
    
    **1. Validação de Split**
    - ⚠️ Sempre verificar overlap treino/teste
    - ⚠️ Split temporal só para séries temporais reais
    - ✅ Estratificação mantém balanceamento classes
    
    **2. Feature Leakage**
    - ⚠️ Alta importância 1 feature = red flag
    - ⚠️ Entender significado business de features
    - ✅ Perguntar: "Info disponível ANTES de alvo?"
    
    **3. Assumptions Teóricas**
    - ⚠️ "Alto = ruim" ou "Baixo = ruim" nem sempre
    - ✅ Análise distribuições empíricas PRIMEIRO
    - ✅ Testes estatísticos (t-test, Mann-Whitney)
    
    **4. Validação Sintética**
    - ⚠️ Sintético ≠ validação independente
    - ✅ Sintético = interpolação do treino
    - ✅ Test set real = validação autoritativa
    
    **5. Documentação**
    - ✅ Documentar decisões (por que CatBoost?)
    - ✅ Manter histórico falhas (valor aprendizado)
    - ✅ Criar evidências stakeholders
    
    **6. Limitações (NOVO)**
    - ✅ Documentar o que NÃO sabemos
    - ✅ Transparência > ocultar fraquezas
    - ✅ Roadmap mitigação claro
    """)

st.markdown("---")

# ===== FOOTER =====
st.success("""
🎯 **Resumo Executivo:**

Este projeto demonstra como **desenvolver uma POC de Machine Learning com rigor científico** 
mantendo **transparência sobre limitações**. 

**Principais conquistas:**
- ✅ Modelo CatBoost com 78.6% recall e 84.6% precision
- ✅ 111/114 testes automatizados validando pipeline
- ✅ Documentação extensiva (TEMPORAL_LIMITATIONS, AB_TESTING_GUIDE, MODEL_COMPARISON)
- ✅ Consciência científica sobre impossibilidade causal temporal
- ✅ Roadmap claro para produção (3-4 semanas) e evolução (3-6 meses)

**Diferencial:** Não apenas resultados, mas **processo validável e transparente**.
""")

st.info("""
📚 **Documentação Técnica Completa:**

- **TEMPORAL_LIMITATIONS.md** (1000 linhas) - Análise limitações temporais dataset agregado
- **AB_TESTING_GUIDE.md** (950 linhas) - Guia validação empírica produção
- **MODEL_COMPARISON.md** - Comparação XGBoost vs LightGBM vs CatBoost
- **FEATURE_ENGINEERING_TEMPORAL.md** (850 linhas) - Roadmap features time-series
- **CHANGELOG.md** - Histórico completo projeto (12 fases desenvolvimento)
- **Notebooks 02B-08** - Implementação técnica detalhada

💡 **Para leitores técnicos:** Consulte documentação .md para detalhes metodológicos completos.
""")

st.caption("""
---
**Contexto da Pesquisa** | Projeto POC IoT Sensor Failure Prediction | CatBoost v1.0.0  
Leonardo Bora | Estágio P&D Lightera | Novembro 2025
""")
