---
title: Eletronica — _Template_Projeto
area: Hardware/Eletronica
tags: [readme, template, projeto]
project: _Template_Projeto
created: 2026-04-22
updated: 2026-10-12
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Eletronica

Eletronica do produto, feita com a familia de skills `pcb-*` (mapa e fluxo em [[../README|03_Hardware]]).
A fonte KiCad fica em `hardware/<placa>/` na raiz do repositorio; aqui fica o que a equipe le e aprova.

| Subpasta | Recebe |
|---|---|
| [[Esquematicos/README\|Esquematicos]] | Diagrama de blocos, PDF do esquematico por revisao, nota do portao 1 |
| [[PCB_Layout/README\|PCB_Layout]] | Renders e decisoes de layout (stack-up, posicionamento, roteamento manual) |
| [[Gerber/README\|Gerber]] | Nota do portao 2 (liberacao para fabricacao) e registro do pedido |
| [[BOM/README\|BOM]] | BOM comentada: escolhas, segunda fonte, pecas criticas |
| [[Simulacoes/README\|Simulacoes]] | Simulacoes SPICE, termicas e EMC |

As notas de cada placa sao criadas por `novo_projeto.py --docs` a partir dos modelos em
`.claude/skills/pcb-projeto/assets/docs/`.

> Template. Ao duplicar para um novo projeto, substituir pelo conteúdo real desta pasta.
