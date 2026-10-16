---
title: Mecanica — _Template_Projeto
area: Hardware/Mecanica
tags: [readme, template, projeto, pendente::ingestao]
project: _Template_Projeto
created: 2026-04-22
updated: 2026-10-12
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Mecanica

Mecânica do produto: modelos CAD 3D, desenhos 2D, enclosure e moldes de injeção.

Integracao com a placa: o contorno e os furos de fixacao da placa seguem o desenho da caixa
(DXF importavel no KiCad em `Edge.Cuts`), e o STEP da placa montada (`exportar_fab.py`, skill
`pcb-fabricacao`) volta para `CAD_3D/` quando a mecanica precisa dele.

> Template. Ao duplicar para um novo projeto, substituir pelo conteúdo real desta pasta.
