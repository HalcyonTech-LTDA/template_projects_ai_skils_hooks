---
title: {{placa}} · Diagrama de blocos e orcamento de potencia
type: diagrama
status: rascunho
created: {{data}}
updated: {{data}}
project: {{projeto}}
module: 03_Hardware
layer: hardware
placa: {{placa}}
revisao: {{rev}}
tags: [diagrama, layer/hardware, module/hardware]
---

# {{placa}} · Diagrama de blocos

Fonte KiCad: `hardware/{{placa}}/`. Modo do esquematico: **spec** (ver README da placa).

## Requisitos resumidos

| Item | Valor | Origem |
|---|---|---|
| Entrada de alimentacao | V min / V max, conector | |
| Tensao maxima na placa | V (acima de 60 V DC ou rede = alta tensao) | |
| Consumo tipico / pico | | |
| Interfaces externas | | |
| Ambiente | temperatura, IP, vibracao | |
| Mecanica | dimensao maxima, furos, caixa | |
| Montagem | JLCPCB SMT / manual | |
| Volume e custo alvo | | |
| Certificacao | Anatel / outra / nenhuma | |

## Blocos

```mermaid
flowchart LR
    ENT["Entrada 12 V<br/>borne + PTC + inversao"] -->|"+12V"| BUCK["Buck 3,3 V"]
    ENT -->|"+12V"| DRV["Driver de motor"]
    BUCK -->|"+3V3"| MCU["MCU / modulo"]
    MCU -->|"PWM, DIR"| DRV
    DRV -->|"MOTOR_A, MOTOR_B"| MOT(("Motor"))
    MCU <-->|"UART0"| PROG["Header de gravacao"]
```

Troque o exemplo pelos blocos reais. Uma seta por trilho de alimentacao (com tensao) e por grupo de
sinais (com o nome da rede ou barramento).

## Orcamento de potencia

| Trilho | Consumidor | I tipica (mA) | I pico (mA) | Observacao |
|---|---|---|---|---|
| +3V3 | | | | |
| **Total +3V3** | | | | margem >= 30% sobre o pico |

| Regulador | Vin | Vout | I max | Dissipacao | Escolha |
|---|---|---|---|---|---|
| | | | | (Vin - Vout) x I para linear; (1 - eficiencia) x Pout para buck | |

## Decisoes

- Numero de camadas e motivo:
- MCU / modulo e motivo:
- ADRs relacionadas:
