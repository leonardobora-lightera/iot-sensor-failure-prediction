# AWS Payload Transformation - README

## 📊 Transformação de Payloads AWS → Formato do Modelo

Este diretório contém payloads AWS transformados de **formato RAW (message-level)** para **formato agregado (device-level)** compatível com o sistema de batch upload.

---

## 🎯 Problema Resolvido

**ANTES (AWS Raw):**
- Formato: 1 linha = 1 mensagem/timestamp
- Exemplo: `payload_aws_raw_teste.csv` tinha 1,138,275 mensagens
- Colunas: 116 (nested JSON: `eyon_metadata.decoded_payload.*`)
- **INCOMPATÍVEL** com modelo (0/29 features esperadas)

**DEPOIS (Transformado):**
- Formato: 1 linha = 1 device (estatísticas agregadas)
- Exemplo: `payload_aws_raw_teste_transformed.csv` tem 789 devices
- Colunas: 30 (device_id + 29 features esperadas)
- **✅ 100% COMPATÍVEL** com batch upload

---

## 📁 Arquivos Gerados

### 1. `payload_aws_BORA_transformed.csv`
- **Origem:** `payloads_aws/payload_aws_BORA.csv` (324,695 mensagens)
- **Output:** 640 devices com 29 features agregadas
- **Período:** Outubro 2025
- **Status:** ✅ Pronto para batch upload

### 2. `payload_aws_raw_teste_transformed.csv`
- **Origem:** `payloads_aws/payload_aws_raw_teste.csv` (1,138,275 mensagens)
- **Output:** 789 devices com 29 features agregadas
- **Período:** Janeiro-Novembro 2025
- **Status:** ✅ Pronto para batch upload

---

## 🔄 Pipeline de Transformação

O script `scripts/transform_aws_payload.py` executa as seguintes etapas:

### 1. **Load AWS Payload**
- Carrega CSV AWS raw
- Identifica colunas variáveis:
  - Device ID: `device_id`, `sn_fkw`, ou `identificator_in_network`
  - Frame Count: `f_cnt`, `f_count`, ou `eyon_metadata.f_count`

### 2. **Aggregate by Device**
Agrupa mensagens por `device_id` e calcula estatísticas:

#### **Optical Power** (7 features)
- Fonte: `eyon_metadata.decoded_payload.optical_power_1490nm`
- Agregações:
  - `optical_mean` = média
  - `optical_std` = desvio padrão
  - `optical_min` = mínimo
  - `optical_max` = máximo
  - `optical_range` = max - min
  - `optical_readings` = contagem de readings
  - `optical_below_threshold` = readings < -28 dBm

#### **Temperature** (6 features)
- Fonte: `eyon_metadata.decoded_payload.temperature`
- Agregações:
  - `temp_mean`, `temp_std`, `temp_min`, `temp_max`
  - `temp_range` = max - min
  - `temp_above_threshold` = readings > 70°C

#### **Battery** (5 features)
- Fonte: `eyon_metadata.decoded_payload.battery`
- Agregações:
  - `battery_mean`, `battery_std`, `battery_min`, `battery_max`
  - `battery_below_threshold` = readings < 2.5V

#### **Connectivity** (9 features)
- Fontes: `eyon_metadata.decoded_payload.{snr, rsrp, rsrq}`
- Agregações para cada:
  - `{signal}_mean`, `{signal}_std`, `{signal}_min`

#### **Messaging** (2 features)
- `total_messages` = contagem de mensagens por device
- `max_frame_count` = máximo de `f_cnt`

### 3. **Validate Output**
- Verifica presença das 29 features esperadas
- Confirma tipos de dados corretos

### 4. **Save**
- Salva apenas 30 colunas: `device_id` + 29 features
- Formato CSV pronto para upload

---

## 🔢 Thresholds Utilizados

Baseado em `docs/BIAS_MITIGATION_CHECKLIST.md`:

| Sensor        | Threshold | Unidade | Uso                              |
|---------------|-----------|---------|----------------------------------|
| Optical Power | -28       | dBm     | Conta readings abaixo do limite  |
| Temperature   | 70        | °C      | Conta readings acima do limite   |
| Battery       | 2.5       | V       | Conta readings abaixo do limite  |

---

## 📊 Estatísticas de Transformação

### payload_aws_BORA.csv
```
Input:  324,695 mensagens (96 colunas AWS)
Output: 640 devices (30 colunas)
Agregação: ~508 mensagens/device (média)
Compatibilidade: ✅ 29/29 features
```

### payload_aws_raw_teste.csv
```
Input:  1,138,275 mensagens (116 colunas AWS)
Output: 789 devices (30 colunas)
Agregação: ~1,443 mensagens/device (média)
Compatibilidade: ✅ 29/29 features
```

---

## 🚀 Como Usar

### 1. **Processar Novos Payloads AWS**
```bash
# Coloque CSVs AWS em payloads_aws/
python scripts/transform_aws_payload.py
```

### 2. **Validar Transformação**
```bash
python scripts/validate_transformed.py
```

### 3. **Upload no Streamlit**
```bash
streamlit run streamlit_app.py
# Navegue para "Batch Upload"
# Selecione arquivo em payloads_processed/
```

---

## 🧪 Validação

Todos os arquivos transformados passaram por:

✅ **29/29 features presentes**  
✅ **Tipos de dados corretos**  
✅ **Preparação para predição bem-sucedida**  
✅ **Compatibilidade com batch upload confirmada**

Script de validação: `scripts/validate_transformed.py`

---

## 📝 Notas Técnicas

### Mapeamento de Campos

| AWS Column                                      | Application Feature        | Agregação          |
|-------------------------------------------------|----------------------------|--------------------|
| `eyon_metadata.decoded_payload.optical_power_1490nm` | `optical_mean`             | mean()             |
|                                                 | `optical_std`              | std()              |
|                                                 | `optical_min`              | min()              |
|                                                 | `optical_max`              | max()              |
|                                                 | `optical_range`            | max - min          |
|                                                 | `optical_readings`         | count()            |
|                                                 | `optical_below_threshold`  | count(< -28 dBm)   |
| `eyon_metadata.decoded_payload.temperature`     | `temp_mean`, `temp_std`, etc. | Similar a optical  |
| `eyon_metadata.decoded_payload.battery`         | `battery_mean`, etc.       | Similar a optical  |
| `eyon_metadata.decoded_payload.snr`             | `snr_mean`, `snr_std`, `snr_min` | mean/std/min       |
| `eyon_metadata.decoded_payload.rsrp`            | `rsrp_*`                   | mean/std/min       |
| `eyon_metadata.decoded_payload.rsrq`            | `rsrq_*`                   | mean/std/min       |
| `device_id`                                     | `device_id`                | -                  |
| (contagem de linhas)                            | `total_messages`           | count()            |
| `f_cnt`                                         | `max_frame_count`          | max()              |

### Tratamento de Missing Values

- NaN removidos ANTES da agregação (para não distorcer estatísticas)
- Se device não tem readings de um sensor, feature fica NaN
- Batch upload tem imputation (mediana) para NaN

---

## 📚 Referências

- **Script de Transformação:** `scripts/transform_aws_payload.py`
- **Lógica Original:** `notebooks/old/02_correlacao_telemetrias_msg6.ipynb`
- **Features Esperadas:** `utils/preprocessing.py` (REQUIRED_FEATURES)
- **Documentação de Thresholds:** `docs/BIAS_MITIGATION_CHECKLIST.md`

---

## ✅ Status

**Data da Transformação:** 13/11/2025  
**Arquivos Processados:** 2/2  
**Taxa de Sucesso:** 100%  
**Devices Processados:** 1,429 (640 + 789)  
**Mensagens Processadas:** 1,462,970 (324,695 + 1,138,275)

🎉 **Transformação completa e validada!**
