# Archive - Historical Experiments & One-Time Analyses

Este diretório contém scripts experimentais, análises específicas e documentação histórica que não são mais utilizados ativamente no projeto, mas são mantidos para referência e rastreabilidade.

---

## 📁 Estrutura

### `discovery_0/`
**Análise do Device 861275072515287 (Discovery 0 - Contaminação FACTORY)**
- Script de análise específica que descobriu contaminação de dados FACTORY
- Análise detalhada que levou à criação do modelo v2 FIELD-only
- **Data:** Novembro 13, 2025
- **Importância:** Descoberta crítica que mudou o rumo do projeto

### `data_processing/`
**Scripts de processamento de dados one-time**
- Scripts usados para transformações específicas de datasets
- Processamento em chunks de CSVs grandes
- **Uso:** Executados uma vez durante desenvolvimento

### `testing/`
**Scripts de teste temporários**
- Testes ad-hoc e validações pontuais
- Scripts de verificação de modificações
- **Uso:** Validação durante desenvolvimento, não fazem parte da suite de testes

### `validation/`
**Scripts de validação de dados**
- Validações rápidas de CSVs e features
- Verificações de compatibilidade
- **Uso:** Ferramentas auxiliares durante desenvolvimento

### `analysis_nov14/`
**Análises específicas - Novembro 14, 2025**
- CSVs de análise de 3 devices críticos
- Datasets sintéticos para experimentação SMOTE
- **Contexto:** Experimentos científicos de validação do modelo v2

### `fase2_planning/`
**Documentação de planejamento FASE 2**
- Planos de ação para correção de falsos positivos
- Documentos de pivot e estratégias
- **Status:** FASE 2 completa - documentação histórica

### `historical_docs/`
**Documentação histórica do projeto**
- Documentos relacionados ao modelo v1
- Limitações temporais (resolvidas em v2)
- **Uso:** Referência histórica, contexto de decisões passadas

---

## ⚠️ Importante

**Estes arquivos NÃO devem ser usados em produção.**

- São mantidos apenas para **rastreabilidade** e **contexto histórico**
- Experimentos já foram incorporados no código principal onde relevante
- Para uso em produção, consulte os diretórios principais do projeto

---

## 🔍 Como Usar Este Archive

Se você precisa entender **por que** uma decisão foi tomada:
1. Consulte `CHANGELOG.md` na raiz do projeto
2. Busque por documentos relevantes neste archive
3. Compare com a implementação atual em `scripts/` ou `models/`

**Última atualização:** 17 de Novembro 2025 (Limpeza de Codebase)
