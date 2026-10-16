---
title: {{placa}} Rev {{rev}} · Bring-up
type: relatorio-teste
status: rascunho
created: {{data}}
updated: {{data}}
project: {{projeto}}
module: 03_Hardware
layer: hardware
placa: {{placa}}
revisao: {{rev}}
date:
tags: [relatorio-teste, layer/hardware, module/hardware]
---

# {{placa}} Rev {{rev}} · Bring-up

Ordem segura: inspecao, curto, fonte limitada, trilho a trilho, so depois MCU e cargas. Anote tudo,
inclusive o que funcionou de primeira — e evidencia para a proxima revisao.

## 1. Recebimento

- Placas recebidas / montadas:
- Inspecao visual (pontes de solda, componente faltando, rotacao, polaridade):

## 2. Antes de energizar

| Medicao (multimetro, placa desligada) | Esperado | Medido | Ok |
|---|---|---|---|
| Resistencia entrada → GND | > alguns k ohm | | |
| +3V3 → GND | | | |

## 3. Energizacao

Fonte de bancada com limite de corrente baixo (ex.: 50-100 mA acima do consumo esperado sem carga).

| Trilho | Esperado | Medido | Corrente da fonte | Ok |
|---|---|---|---|---|
| | | | | |

## 4. Gravacao e teste por bloco

| Bloco | Teste | Resultado |
|---|---|---|
| | | |

## 5. Defeitos e mudancas para a proxima revisao

| # | Defeito | Causa | Correcao provisoria (retrabalho) | Mudanca na Rev seguinte |
|---|---|---|---|---|
| 1 | | | | |
