---
title: Skill /trilha e o board no GitHub
type: decisao
status: aprovado
created: 2026-10-15
updated: 2026-10-15
project: template_projetos
tags: [decisao, github, board, trilha, tema/tooling]
---

# 2026-10-15 — Skill /trilha e o board no GitHub

## O que mudou

1. Nova skill `.claude/skills/trilha/` (`/trilha`): planeja e controla uma frente de trabalho no GitHub — marcos
   (milestones), epico com sub-issues, dependencias nativas, sequencia calculada, progresso ponderado,
   manifesto `.yml` e os scripts `trilha:sync`, `trilha:check` e `trilha:status` (criados no primeiro uso).
2. Novo molde [[../BOARD|docs_projeto/BOARD.md]], para cada projeto anotar os IDs do proprio board.
3. Novos formularios de issue em `.github/ISSUE_TEMPLATE/` (tarefa, epico, bug), com issue em branco desligada.
4. Nova ficha [[../referencias/github-projects-issues-dependencias]].
5. `inject-rules.js`: a regra 1 aponta a `/trilha` para planejamento de frente de trabalho.

## Por que

O metodo veio do NFC-APP (Project #6), onde funcionou e onde tambem apareceram os custos:

- Um par de campos `Etapa <trilha>`/`Ordem <trilha>` por trilha levou o Project a 39 dos 50 campos permitidos.
  A `/trilha` usa um `Ordem` unico e fatia as views pelo campo `Trilha`.
- Dependencias so no texto do corpo e num campo de texto nao apareciam como bloqueio nem eram conferidas. A
  `/trilha` usa a relacao nativa blocked by e deixa o campo de texto so para bloqueio externo.
- O workflow "Pull request merged" levava a issue a Done e pulava a prova em ambiente real. A `/trilha` o
  configura para In review; Done e do dono.
- Draft items nao tem label, milestone nem dependencia. Todo trabalho passa a ser issue.

## Decisoes do usuario

- **So issues**, nada de cartao/draft.
- **Mais controle** sobre marcos de entrega, sequencia, bloqueios e progresso dos marcos.
