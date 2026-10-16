---
title: Arquivos_Fabricacao — _Template_Projeto
area: Producao/Arquivos_Fabricacao
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

# Arquivos Fabricacao

Arquivos de fabricação consolidados para a EMS: Gerber, BOM, pick-and-place, stencil.

Placas: o pacote liberado de cada revisao fica versionado em `hardware/<placa>/releases/rev-<R>/`,
com `manifesto.json` (SHA-256 de cada arquivo), gerado pela skill `pcb-fabricacao` so depois do
portao de liberacao. Aqui entra o que e da producao seriada: painel, stencil, instrucoes da EMS.

> Template. Ao duplicar para um novo projeto, substituir pelo conteúdo real desta pasta.
