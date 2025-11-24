# Apresentação Final de Estágio - Predição de Falhas em Sensores IoT
## Transformando Manutenção Corretiva em Preditiva através de Machine Learning

**Data:** 25 de Novembro de 2025  
**Duração:** 10 minutos  
**Apresentador:** Leonardo Bora da Costa  
**Empresa:** Lightera LLC - Fault Management Team

---

## 🎯 SLIDE 1: Apresentação Pessoal

### Conteúdo do Slide:
```
LEONARDO BORA DA COSTA
Estagiário de Data Science | Lightera LLC

🏆 Prêmio IEL de Talentos 2025 - Estagiário Inovador

MISSÃO PROFISSIONAL:
Mesclar Educação com Tecnologia para democratizar conhecimento
e capacitar pessoas através da inovação

💡 "A tecnologia só transforma quando está acessível a todos"
```

### Notas do Apresentador (1 minuto):
- Bom dia a todos! Meu nome é Leonardo Bora da Costa, e é uma honra estar aqui apresentando o trabalho final do meu estágio no time de Fault Management da Lightera.
- Este ano tive a honra de receber o **Prêmio IEL de Talentos como Estagiário Inovador 2025**, um reconhecimento que me motivou ainda mais a trazer soluções criativas para os desafios da indústria.
- Minha missão profissional sempre foi **mesclar educação com tecnologia**. Além do estágio, tive a oportunidade de participar do programa de voluntariado **"Formando Crianças para o Futuro"** do SESI, onde dei aulas de língua inglesa para adolescentes do 3º ano do ensino médio. Essa experiência reforçou minha convicção: **conhecimento só transforma quando está acessível**.
- E é exatamente essa filosofia que guiou este projeto: criar uma solução de Machine Learning que **democratiza insights técnicos** para equipes operacionais, não apenas para cientistas de dados.

---

## 🔧 SLIDE 2: O Desafio Empresarial

### Conteúdo do Slide:
```
O PROBLEMA QUE PRECISÁVAMOS RESOLVER

Dispositivos IoT na rede apresentam falhas inesperadas:
- 💸 Manutenção emergencial custa até 3x mais que preventiva
- ⚡ Downtime imprevisível afeta serviço ao cliente
- 🔧 Equipes técnicas desperdiçam tempo em inspeções reativas

PERGUNTA CENTRAL:
"Podemos prever falhas ANTES que elas aconteçam?"

VALOR ESPERADO:
Transformar operação de REATIVA para PROATIVA
```

### Notas do Apresentador (1 minuto):
- A Lightera gerencia milhares de dispositivos IoT espalhados pela rede de telecomunicações. E o problema é simples: **dispositivos falham sem aviso**.
- Isso gera um efeito dominó: custos emergenciais que são até 3 vezes mais caros, interrupções de serviço, e equipes técnicas que precisam reagir ao problema ao invés de preveni-lo.
- A grande questão que me foi apresentada no início do estágio foi: **"Será que conseguimos identificar padrões de comportamento que indiquem uma falha iminente?"**
- Não era apenas sobre métricas de precisão. Era sobre **mudar o paradigma operacional** da empresa: de apagar incêndios para evitar que o fogo comece.

---

## 🔬 SLIDE 3: Hipótese e Abordagem

### Conteúdo do Slide:
```
HIPÓTESE DE PESQUISA

"Padrões de telemetria (bateria, sinal óptico, conectividade, mensageria)
podem prever falhas de dispositivos IoT antes que ocorram"

ABORDAGEM ESCOLHIDA:
✅ Machine Learning (algoritmo CatBoost)
✅ 762 dispositivos reais em campo
✅ 30 características de comportamento
✅ Foco em INTERPRETABILIDADE, não apenas acurácia

METODOLOGIA:
Desenvolvimento iterativo → Validação crítica → Pivots estratégicos
```

### Notas do Apresentador (1 minuto):
- Minha hipótese era que **sim, existe um padrão detectável**. Dispositivos que estão prestes a falhar mostram sinais: bateria fraca, quedas de sinal, comunicação irregular.
- Escolhi usar Machine Learning com o algoritmo **CatBoost**, mas não era apenas sobre treinar um modelo. Era sobre **criar uma solução que as pessoas pudessem confiar e entender**.
- Trabalhei com dados de 762 dispositivos reais, analisando 30 características diferentes de comportamento.
- E aqui está o mais importante: desde o início, adotei uma metodologia de **pesquisa científica**, não apenas engenharia. Isso significa formular hipótese, testar, **questionar os resultados**, e estar pronto para pivotar se necessário.

---

## 🔍 SLIDE 4: Discovery 0 - O Momento de Pensamento Crítico

### Conteúdo do Slide:
```
DISCOVERY 0: QUANDO AS MÉTRICAS ERAM "BOM DEMAIS PARA SER VERDADE"

PRIMEIRO MODELO (v1.0):
✅ Recall de 78.6% (parecia excelente!)
❓ Mas algo não fazia sentido...

O TRABALHO DE DETETIVE:
Ao investigar um "falso positivo", descobri:
→ 31.8% do dataset eram mensagens de ciclo FACTORY (laboratório)
→ 27 dispositivos eram de TESTES PRÉ-DEPLOYMENT
→ Modelo estava "trapaceando": aprendendo padrões de teste, não de produção

DECISÃO CRÍTICA:
🚨 REBUILD COMPLETO: Remover dados contaminados
📉 Resultado: Recall caiu para 57.1% (-21.5%)
✅ Mas agora tínhamos DADOS LIMPOS e BASELINE HONESTO
```

### Notas do Apresentador (2 minutos):
- Este é o coração da apresentação. O modelo v1 tinha 78.6% de recall. No papel, era um sucesso.
- Mas quando fui investigar um **falso positivo** específico, encontrei algo que não estava documentado: **31.8% do dataset eram mensagens de testes de laboratório** (ciclo FACTORY), não de dispositivos reais em campo.
- Imagine: é como treinar um modelo para detectar doenças usando dados de exames de rotina misturados com casos reais. As métricas ficam ótimas, mas **não refletem a realidade**.
- Eu tinha duas opções: **ignorar o problema e manter os 78.6%, ou fazer a coisa certa**. Escolhi a segunda.
- Filtrei todos os dados contaminados. Retreinei o modelo apenas com dispositivos FIELD (produção real). O recall caiu para 57.1% - uma queda de 21.5 pontos percentuais.
- **Mas agora eu tinha algo muito mais valioso que métricas impressionantes: eu tinha confiança nos dados**. E esse é o ponto que quero enfatizar: **integridade científica > números bonitos**.
- Esse momento é o que chamo de **Discovery 0** - a descoberta que veio antes de tudo, a que validou que estávamos no caminho certo, mesmo que difícil.

---

## 💪 SLIDE 5: Pivot Estratégico e Resultados Honestos

### Conteúdo do Slide:
```
MODELO v2.0 - BASELINE HONESTO (FIELD-only)

RESULTADOS TRANSPARENTES:
📊 Recall: 57.1% (8 de 14 dispositivos críticos detectados)
📊 Precision: 57.1% (6 falsos alarmes em 14 predições)
📊 ROC-AUC: 0.9186 (+6.6% vs v1)

O QUE ISSO SIGNIFICA NA PRÁTICA:
✅ Modelo detecta MAIS DA METADE dos problemas antes que ocorram
⚠️ Ainda perde 6 dispositivos (42.9% miss rate)
💡 MAS: fundação limpa para FASE 3 de melhorias

TENTATIVA v2.1:
→ Adicionei 3 features temporais
→ Resultado: +0.1% recall (insuficiente)
→ Decisão: Manter v2.0 como baseline honesto
```

### Notas do Apresentador (1.5 minutos):
- Após o rebuild, o modelo v2.0 alcançou 57.1% de recall. Traduzindo: **conseguimos detectar 8 de 14 dispositivos críticos antes da falha**.
- Isso é suficiente para produção? Ainda não. **Mas é uma fundação sólida e HONESTA**.
- Tentei uma iteração v2.1, adicionando features temporais (frequência de mensagens, dias de inatividade). O resultado foi apenas +0.1% de melhoria - estatisticamente insignificante.
- **Aprendi a não forçar melhorias artificiais**. Decidi manter o v2.0 como baseline oficial e documentar as limitações de forma transparente.
- A mensagem aqui é sobre **resiliência e maturidade profissional**: aceitar que nem todo experimento resulta em avanço, mas que **cada tentativa ensina algo**.

---

## 🎯 SLIDE 6: Valor do MVP Entregue

### Conteúdo do Slide:
```
O QUE ENTREGAMOS COMO MVP

🌐 APLICAÇÃO WEB INTERATIVA (Streamlit):
→ 5 páginas acessíveis para usuários não-técnicos
→ Upload em lote: processar centenas de dispositivos
→ Predição individual: análise device-a-device
→ Insights visuais: feature importance, matriz de confusão

💡 DEMOCRATIZAÇÃO DE ML:
Equipes operacionais podem usar o modelo SEM conhecimento técnico avançado

📈 VALOR REAL ENTREGUE:
✅ Sensor health indicators: identifica padrões de degradação
✅ Priorização inteligente: foca manutenção nos 8 dispositivos detectados
✅ Insights de negócio: quais features mais indicam falha

STATUS: MVP VALIDADO - Pronto para POC (Proof of Concept)
```

### Notas do Apresentador (1.5 minutos):
- Apesar do recall não ser 90%, **entregamos um MVP funcional e valioso**.
- Criei uma **aplicação web completa** usando Streamlit, que permite a QUALQUER PESSOA da equipe - técnicos, gestores, analistas - usarem o modelo sem saber programar.
- Pode fazer upload de um CSV com dados de 100 dispositivos e obter predições em segundos. Pode analisar um dispositivo específico e entender QUAIS características estão sinalizando risco.
- E aqui está a conexão com minha missão de **educação + tecnologia**: não basta ter um modelo preciso se ele fica trancado em um Jupyter Notebook. **Conhecimento precisa ser acessível**.
- O MVP identifica os 8 dispositivos de maior risco, permitindo que a equipe **priorize manutenção preventiva** onde tem mais impacto.
- É um POC (Proof of Concept) validado, não um produto final. Mas é **funcional, honesto, e pronto para testes piloto**.

---

## 🚀 SLIDE 7: Aprendizados e FASE 3

### Conteúdo do Slide:
```
LIÇÕES APRENDIDAS & PRÓXIMOS PASSOS

💡 APRENDIZADOS-CHAVE:
1. Qualidade de dados > Complexidade de modelo
2. Pensamento crítico > Aceitar métricas sem questionar
3. Resiliência técnica: pivotar é sinal de maturidade, não fracasso
4. Documentação transparente constrói confiança

FASE 3 - ROADMAP PARA 85%+ RECALL:
🔧 Track 1: Temporal Features (padrões ao longo do tempo)
🔧 Track 2: Hyperparameter Tuning (otimização algorítmica)
🔧 Track 3: Ensemble Methods (combinar múltiplos modelos)
🔧 Track 4: Real-time Data Pipeline (inferência contínua)

CRITÉRIO DE SUCESSO:
"Honest 85% com foundation limpa > Inflated 90% com dados duvidosos"
```

### Notas do Apresentador (1.5 minutos):
- Este projeto me ensinou mais do que Machine Learning. Me ensinou **como fazer pesquisa de verdade**.
- **Qualidade de dados é mais importante que qualquer algoritmo**. Se os dados estão errados, não importa quão sofisticado seja o modelo.
- Aprendi a **questionar resultados que parecem bons demais**. E aprendi que **pivotar não é falhar - é evoluir**.
- A FASE 3 já está mapeada: incluir features temporais mais sofisticadas, otimizar hiperparâmetros, testar ensemble methods, e construir um pipeline de inferência em tempo real.
- O objetivo é alcançar **85% de recall com dados limpos**, não 95% com dados duvidosos. E esse mindset de **integridade científica** é o que diferencia um projeto de pesquisa de um projeto de "só fazer funcionar".

---

## 🤖 SLIDE 8: IA, Futuro e Missão Contínua

### Conteúdo do Slide:
```
A REVOLUÇÃO DA IA NO AMBIENTE DE TRABALHO

COMO A IA TRANSFORMOU ESTE ESTÁGIO:
⚡ Acelerou aprendizado técnico (documentação, debugging, research)
⚡ Aumentou produtividade sem substituir pensamento crítico
⚡ Democratizou acesso a conhecimento avançado

A IA NÃO SUBSTITUI HUMANOS - ELA AMPLIFICA CAPACIDADES

CONEXÃO COM VOLUNTARIADO:
→ Ensinei inglês para adolescentes (Formando Crianças para o Futuro)
→ Vi o impacto de DEMOCRATIZAR conhecimento
→ IA é a ferramenta, EDUCAÇÃO é o propósito

MISSÃO CONTÍNUA:
"Mesclar educação com tecnologia para capacitar pessoas
através de soluções acessíveis e transformadoras"

🎓 Próximo passo: Continuar inovando onde tecnologia encontra pessoas
```

### Notas do Apresentador (1.5 minutos):
- Quero fechar falando sobre **como a IA revolucionou a forma como trabalhamos**.
- Durante este estágio, usei ferramentas de IA (como Copilot, ChatGPT) que **aceleraram dramaticamente meu aprendizado**. Debugar código, entender conceitos novos, pesquisar melhores práticas - tudo ficou mais rápido.
- **MAS** - e isso é crucial - **a IA não pensou criticamente por mim**. Ela não descobriu o Discovery 0. Ela não decidiu fazer o rebuild. Ela não escolheu honestidade sobre métricas infladas. **Eu fiz isso**.
- A IA é uma ferramenta que **amplifica capacidades humanas**, não as substitui. E quanto mais produtivo eu fico com IA, mais tempo tenho para **criar impacto real**.
- Essa experiência se conecta diretamente com meu trabalho voluntário: ensinar inglês para adolescentes do 3º ano no programa "Formando Crianças para o Futuro" do SESI me mostrou que **conhecimento muda vidas quando está acessível**.
- Por isso criei a aplicação Streamlit - para democratizar ML. Por isso documentei cada decisão - para educar quem vier depois.
- **Minha missão continua**: mesclar educação com tecnologia, criar soluções que **capacitam pessoas**, e usar inovação para transformar complexidade em clareza.
- E esse é apenas o começo. Obrigado pela oportunidade, e obrigado pela jornada.

---

## 📊 APÊNDICE: Informações Adicionais (Backup para Perguntas)

### Dados Técnicos do Projeto:
- **Dispositivos analisados:** 762 FIELD-only (após cleanup de 789 mixed)
- **Features utilizadas:** 30 (29 numéricas + 1 temporal nova)
- **Split treino/teste:** 533 train (29 critical) / 229 test (14 critical)
- **Algoritmo:** CatBoost (gradient boosting otimizado para dados categóricos)
- **Balanceamento:** SMOTE (Synthetic Minority Over-sampling Technique)
- **Deployment:** Streamlit Cloud + GitHub
- **Linguagem:** Python 3.12

### Métricas v2.0 Completas:
- **Recall (Sensibilidade):** 57.1% (8/14 critical detected)
- **Precision:** 57.1% (8/14 predictions correct)
- **F1-Score:** 0.571 (média harmônica precision/recall)
- **ROC-AUC:** 0.9186 (excelente separação de classes)
- **Miss Rate:** 42.9% (6/14 critical missed)
- **False Alarm Rate:** 2.8% (6/215 normal misclassified)

### Perguntas Antecipadas:

**P1: "Por que 57.1% é bom o suficiente?"**
R: Não é "bom o suficiente" para produção final, mas é um **baseline HONESTO** que valida a viabilidade da abordagem. Com FASE 3 (temporal features + tuning), projetamos 85%+ recall.

**P2: "Quanto tempo economiza em manutenção?"**
R: Detectando 8 de 14 falhas precocemente, evita custos emergenciais de ~8 dispositivos. Manutenção emergencial custa 3x mais, então ROI é positivo desde POC.

**P3: "Como garantir que o modelo não degrada com novos dados?"**
R: FASE 3 inclui data drift monitoring e pipeline de re-treinamento periódico. Documentação de limitações garante uso consciente.

**P4: "Qual foi a maior dificuldade técnica?"**
R: Discovery 0 - identificar contaminação não documentada. Exigiu análise forensic de mensagens individuais e decisão de rebuild completo.

**P5: "Como IA ajudou especificamente neste projeto?"**
R: Acelerou debugging (GitHub Copilot), research de hiperparâmetros (ChatGPT), e geração de documentação. Mas **decisões críticas (rebuild, baseline honesto) foram 100% humanas**.

**P6: "Planos após o estágio?"**
R: Continuar missão de mesclar educação + tecnologia. Explorar oportunidades em Data Science com foco em **ML acessível** e **soluções que democratizam insights**.

**P7: "O que você faria diferente?"**
R: Iniciaria com auditoria de dados ANTES do primeiro modelo. Discovery 0 foi valioso, mas poderia ter vindo mais cedo com processo de validação de data quality desde o início.

---

## 🎬 ROTEIRO DE APRESENTAÇÃO (10 MINUTOS)

| **Slide** | **Tempo** | **Foco** | **Mensagem-Chave** |
|-----------|-----------|----------|---------------------|
| 1. Apresentação | 1:00 | Personal branding + Missão | IEL Award + Educação/Tech mission |
| 2. Desafio | 1:00 | Business context | Reativo → Proativo |
| 3. Hipótese | 1:00 | Abordagem científica | ML + Interpretabilidade |
| 4. Discovery 0 | 2:00 | **CRÍTICO** - Critical thinking | Dados limpos > Métricas infladas |
| 5. Pivot | 1:30 | Resiliência + Honestidade | 57.1% honesto vs 78.6% duvidoso |
| 6. MVP | 1:30 | Valor entregue | Democratização de ML |
| 7. Aprendizados | 1:30 | Lições + Roadmap FASE 3 | Qualidade > Complexidade |
| 8. IA & Futuro | 1:30 | Visão + Missão contínua | IA amplifica, educação transforma |
| **TOTAL** | **10:00** | | |

---

## 🎯 MENSAGENS-CHAVE PARA LEMBRAR

1. **Prêmio IEL 2025** demonstra reconhecimento de inovação e proatividade
2. **Discovery 0** é o hero moment - pensamento crítico > métricas impressionantes
3. **57.1% honesto > 78.6% inflado** - integridade científica
4. **MVP entregue** democratiza ML para equipes não-técnicas
5. **IA revoluciona produtividade** mas não substitui decisões críticas humanas
6. **Missão contínua**: Educação + Tecnologia para capacitar pessoas
7. **Voluntariado** conecta teoria (ML) com prática (democratização de conhecimento)

---

**FIM DA APRESENTAÇÃO**

*Documento criado em: 19 de Novembro de 2025*  
*Versão: 1.0 - Final para apresentação de 25/Nov/2025*
