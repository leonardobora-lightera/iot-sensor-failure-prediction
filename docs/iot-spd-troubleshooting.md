# Guia de Troubleshooting IoT SPD-AL-NB

---

**Válido para as versões 1.1.0_rc19 e 1.2.0_rc07**

## Sumário
- [Sensores SPD-AL-NB](#sensores-spd-al-nb)
- [Análise de Keep Alives](#análise-de-keep-alives)
- [Análise de conectividade](#análise-de-conectividade)
    - [Parâmetros de sinal (RSSI, SNR, RSRP, RSRQ, ECL, TX Power)](#parâmetros-de-sinal)
    - [Tempo de registro](#tempo-de-registro)
    - [Status da instalação](#status-da-instalação-do-dispositivo)
- [Análise dos SIM Cards nas plataformas de gerenciamento](#análise-dos-sim-cards-nas-plataformas-de-gerenciamento)
    - [Plataforma VIVO (Kite)](#plataforma-kite-vivo)
    - [Plataforma TIM](#plataforma-tim)
- [Análise de bateria](#análise-de-bateria)
- [Análise dos sensores](#análise-dos-sensores)
    - [Firmware](#verificar-a-versão-de-firmware-do-dispositivo)
    - [Status do sensor](#status-do-sensor)
    - [Níveis de potência](#níveis-de-potência)
    - [Níveis de luminosidade x movimento](#níveis-de-luminosidade-x-movimento)
    - [Threshold de alarmes](#valores-padrão-de-threshold-de-alarmes)
- [Realizar análise dos dispositivos via AWS](#realizar-análise-dos-dispositivos-via-aws)
    - [Análise dos logs de um dispositivo](#análise-dos-logs-de-um-dispositivo)
    - [Tabela de códigos de erros para troubleshooting](#tabela-de-códigos-de-erros-para-realização-do-troubleshooting)
    - [Análise dos pacotes via IoT Core](#análise-dos-pacotes-em-tempo-real-via-iot-core)
- [Chamados já resolvidos ou em andamento](#chamados-já-resolvidos-ou-em-andamento)
---

## Sensores SPD-AL-NB

Este documento detalha as melhores práticas de troubleshooting para sensores SPD-AL-NB, cobrindo desde análise de comunicação, conectividade (parâmetros de sinal), bateria, status, até logs e códigos de erros.

### Análise de Keep Alives

Para verificar instabilidade de comunicação, acesse o EyON, localize o sensor com base em Nome, IMEI ou Status. Realize o fluxo para visualizar pacotes uplink, analise intervalos, contadores (f_cnt) e perdas de pacotes. Monitore se ocorre perda de keep alive (KA) e alarmes.

Exemplo de payload relevante:
```json
{
  "device_id": "866207059641146",
  "msg_type": 1,
  "f_cnt": 17,
  "fw_app_version": "1.2.0",
  "apn": {"name": "furukawaelectric.com.br"},
  "imsi": "724068042233218",
  "iccid": "89550680257008774896",
  "decoded_payload": {
    "OpticalPower_dBm": "1.50 dBm",
    "battery": "3.47 V",
    "temperature": "30 °C",
    "rssi": "-55 dBm",
    "snr": "14 dB",
    "rsrp": "-60 dBm",
    "rsrq": "-5 dB",
    "txPower": "-18 dBm",
    "ecl": "0",
    "registrationTime": "16 s",
    "statusOpticalPower": "OK",
    "statusSensor": "OK",
    "mode": "FIELD"
  }
}
```

### Análise de conectividade

Analise RSSI, SNR, RSRP, RSRQ, ECL, TX Power em todos os pacotes uplink (KA e alarmes). Avalie intensidade, qualidade e potência do sinal, cobertura, consumo, retransmissões e impacto na operação. Compare valores, níveis e thresholds:
- RSSI ideal: próximo de 0 (forte), em torno de -100 (fraco)
- SNR, RSRP, RSRQ: maiores valores indicam melhor conectividade
- ECL: 0 (boa cobertura), 2 (fraca)
- TX Power: de -45 dBm até +23 dBm (aumenta consumo)

Consulte tabela para interpretação de cada parâmetro.

#### Tempo de registro

Tempo entre "despertar" do dispositivo e envio do KA/alarme. Indicativos altos (acima de ~500s) sugerem problemas de conectividade. Analise junto aos demais parâmetros e com logs AWS/EyON.

#### Status da instalação

Sensor reporta status correto ou alerta se instalado fora da recomendação (até 20º de tolerância). Status installPosition: OK/ALERT.

### Análise dos SIM Cards

Avaliação detalhada nas plataformas Kite (VIVO) e TIM:
- Login, dashboards, simcards, status, filtragem/filtros por ICCID/IMSI/IMEI
- Reset/reinicialização do SIM (recuperação após falhas), histórico de conexão, localização ERB
- Exportação de dados via CSV, relatórios e mapas de calor

### Análise de bateria

Verificar gráficos ou payloads uplink, bateria ideal acima de 2.50V. Valores baixos geram alarmes recorrentes e risco de falha. Recomenda-se substituição preventiva.

### Análise dos sensores

#### Verificação de firmware

Compare versões do firmware (ex: v1.0.3_rc11 vs. v1.2.0_rc07), impacto no conteúdo do payload e capacidade de diagnóstico.

#### Status do sensor

StatusSensor "ALERT" indica falha de hardware, requer recolhimento/substituição.

#### Níveis de potência

Utilize optical_power_1490nm de eyon_metadata como referência (igual ao dashboard do sistema).

#### Níveis de luminosidade x movimento

Alarmes simultâneos de luminosidade e movimento podem indicar furto (abertura de CTO ou vedação inadequada). Cross-check entre payload e correlacionar com alarmes.

#### Threshold padrão de alarmes

| Threshold         | Valor padrão   |
|-------------------|----------------|
| Luminosidade      | 2 lux          |
| Acelerômetro      | 20º            |
| Powermeter        | -28 dBm        |
| Temperatura       | 70º C          |
| Bateria           | 2.50 V         |

### Análise via AWS

Requer acesso, utilize CloudWatch para logs/insights:
- Filtros customizáveis
- Campos essenciais: timestamp, msg_type, battery, optical power, status, etc.
- Verifique logs de KA, alarmes e erros específicos
- Utilize IoT Core para análise em tempo real (testar MQTT, assinar tópicos de uplink)

### Tabela de códigos de erro para troubleshooting

| Error Code | Descrição                                  |
|------------|--------------------------------------------|
| 1          | APPMANAGER_KP_FAIL: Perda de keep alive    |
| 2          | APPMANAGER_ALERT_FAIL: Perda de alerta     |
| 3          | APPMANAGER_RETRANSMISSION_FAIL             |
| 4          | APPMANAGER_ERROR_MESSAGE_FAIL              |
| 5          | KP_UNCONFIRMED: Reset por kp não confirmado|
| ...        | ... (demais códigos conforme listagem)     |
| 28         | REGISTRATION_DENIED: Registro negado (CEREG=3) |

### Chamados resolvidos ou em andamento

Lista dos principais incidentes documentados
- Instabilidade NB-IoT
- Falta de comunicação
- Intermitência
- Problemas com alarmes luminosos
- Sensor CTO3 com bateria baixa
- Sensores sem conexão

Resumo de recomendações e passos análise
- Perdas de Keep Alive: aceito até 6% por mês, esporádico
- Status e níveis de sensores
- Níveis de bateria
- Frequência de alarmes e correções
- Análise de códigos de erro
- Parâmetros de sinal e tempo de registro
- Localização, operadora, histórico de ações para troubleshooting

Se nenhuma condição for atendida: direcionar para responsável N3/SIT.

---

*Este arquivo está pronto para contexto LLM, estruturado para ingestão direta em sistemas tipo RAG, context chunking e engineering. Tabela de erro e detalhes de payload prontos para mapeamento semântico.*
