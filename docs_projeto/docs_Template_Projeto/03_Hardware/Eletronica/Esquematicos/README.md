---
title: Esquematicos — _Template_Projeto
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

# Esquematicos

- `<placa>_Diagrama_de_Blocos.md` — requisitos resumidos, blocos em Mermaid e orcamento de potencia
  (`type: diagrama`). E o diagrama eletrico de alto nivel; o esquematico e o detalhe.
- `<placa>_Rev<R>_Revisao_Esquematico.md` — **portao 1** (`type: gate`). O layout so comeca com ela
  em `status: aprovado`, `revisores` preenchido por pessoa e nenhum item em aberto.
- `<placa>_Rev<R>.pdf` — PDF do esquematico de cada revisao
  (`kicad-cli sch export pdf hardware/<placa>/<placa>.kicad_sch -o ...`).

Skill: `pcb-esquematico`. A fonte (`.kicad_sch` e `spec/<placa>.json`) fica em `hardware/<placa>/`.

> Template. Ao duplicar para um novo projeto, substituir pelo conteúdo real desta pasta.
