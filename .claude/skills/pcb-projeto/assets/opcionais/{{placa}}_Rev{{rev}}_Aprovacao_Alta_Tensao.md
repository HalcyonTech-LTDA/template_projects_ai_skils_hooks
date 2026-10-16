---
title: {{placa}} Rev {{rev}} · Aprovacao de alta tensao
type: gate
gate: alta-tensao
status: rascunho
created: {{data}}
updated: {{data}}
project: {{projeto}}
module: 03_Hardware
layer: hardware
placa: {{placa}}
revisao: {{rev}}
revisores: []
date:
tensao_max_v:
norma_seguranca:
clearance_mm:
creepage_mm:
tags: [gate, layer/hardware, module/hardware, tema/seguranca]
---

# {{placa}} Rev {{rev}} · Aprovacao de alta tensao

Exigida pelo `portao_liberacao.py` quando a spec declara `tensao_max_v > 60` ou o projeto tem a net
class `HV`. Aprovada por uma pessoa com competencia em seguranca eletrica — nunca pelo agente.
Ver `.claude/skills/pcb-projeto/references/alta-tensao.md`.

## Justificativa

- Por que a parte de alta tensao fica na placa (e nao num modulo AC-DC certificado):
- ADR:

## Checklist

- [ ] Norma de seguranca aplicavel identificada e registrada no frontmatter (`norma_seguranca`)
- [ ] Tensao de trabalho e de pico registradas (`tensao_max_v`), incluindo tolerancia da rede
- [ ] Clearance e creepage tirados da norma (grau de poluicao, grupo de material, categoria de sobretensao) e registrados abaixo
- [ ] `clearance_mm` e `creepage_mm` do frontmatter preenchidos com os valores da norma (o portao passa a exigir esses minimos)
- [ ] Regra da net class `HV` no fim do `.kicad_dru` com esses valores, e DRC zero
- [ ] Fusivel na entrada e protecao contra surto (varistor) dimensionados
- [ ] Isolacao galvanica entre rede e baixa tensao (fonte isolada, opto/isolador digital, rele) com tensao de isolacao especificada
- [ ] Fendas de creepage onde a distancia na superficie nao basta
- [ ] Nenhum plano ou trilha de baixa tensao sob a area de rede
- [ ] Area de alta tensao marcada na serigrafia com o simbolo de risco eletrico
- [ ] Procedimento de bring-up com transformador isolador e protecao diferencial registrado

## Distancias adotadas

| Entre | Tensao de trabalho | Clearance (mm) | Creepage (mm) | Fonte |
|---|---|---|---|---|
| Rede ↔ baixa tensao | | | | |
| Fase ↔ neutro | | | | |
