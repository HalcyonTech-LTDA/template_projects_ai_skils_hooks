---
title: Gerber — _Template_Projeto
area: Hardware/Eletronica/Gerber
tags: [readme, template, projeto]
project: _Template_Projeto
created: 2026-04-24
updated: 2026-10-12
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Gerber

Liberacao para fabricacao. O pacote em si (zip de Gerber e furacao, BOM e CPL no formato da JLC,
BOM completa, PDF e `manifesto.json` com SHA-256) fica versionado em
`hardware/<placa>/releases/rev-<R>/`. Aqui ficam:

- `<placa>_Rev<R>_Liberacao_Fabricacao.md` — **portao 2** (`type: gate`): checklist de layout e de
  fabricacao, evidencia do `portao_liberacao.py` e registro do pedido;
- `<placa>_Rev<R>_Aprovacao_Alta_Tensao.md` — so com alta tensao (rede ou acima de 60 V DC); modelo
  em `.claude/skills/pcb-projeto/assets/opcionais/`.

Skill: `pcb-fabricacao`.

> Template. Ao duplicar para um novo projeto, substituir pelo conteúdo real desta pasta.
