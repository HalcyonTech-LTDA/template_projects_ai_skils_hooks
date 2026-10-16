---
title: BOM — _Template_Projeto
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

# BOM

A BOM e gerada do esquematico pelo `exportar_fab.py`: os campos `MPN`, `Fabricante`, `LCSC`,
`Mouser`, `DigiKey` e `Datasheet` de cada componente sao a fonte, e o CSV sai junto do pacote de
fabricacao. Esta pasta guarda o que o CSV nao diz:

- por que cada peca critica foi escolhida (regulador, driver, MCU, conectores);
- alternativa drop-in de cada peca critica (segunda fonte);
- pecas Extended da JLC aceitas e o custo delas; NRND justificado.

Custo por volume e imposto de importacao ficam em `08_Producao/Custos_BOM`. Skill: `pcb-componentes`.

> Template. Ao duplicar para um novo projeto, substituir pelo conteúdo real desta pasta.
