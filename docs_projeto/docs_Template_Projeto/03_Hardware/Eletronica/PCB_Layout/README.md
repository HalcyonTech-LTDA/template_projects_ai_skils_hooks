---
title: PCB_Layout — _Template_Projeto
area: Hardware/Eletronica/PCB_Layout
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

# PCB Layout

O arquivo-fonte do layout fica em `hardware/<placa>/<placa>.kicad_pcb`, com as regras de DRC da
JLCPCB em `<placa>.kicad_dru` — nao aqui. Esta pasta recebe:

- renders do posicionamento usados na revisao (`kicad-cli pcb render`);
- decisoes de layout que nao pedem uma ADR: stack-up escolhido, zonas, o que foi roteado a mao
  (potencia, alta tensao, USB, antena) e o que o Freerouting roteou.

O checklist de layout esta na nota do portao 2, em [[../Gerber/README|Gerber]]. Skill: `pcb-layout`.

> Template. Ao duplicar para um novo projeto, substituir pelo conteúdo real desta pasta.
