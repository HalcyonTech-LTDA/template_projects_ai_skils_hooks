---
title: GitHub Projects, sub-issues e dependencias de issue
source: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies
type: referencia
status: aprovado
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, github, projects, issues, tema/tooling]
---

# GitHub Projects, sub-issues e dependencias de issue

Os recursos nativos que a skill `/trilha` usa para controlar marcos, sequencia, bloqueios e progresso.

## Dependencias (blocked by / blocking)

- GA em 2025-08-21. Na issue: Relationships > Mark as blocked by / Mark as blocking. Precisa de permissao
  triage ou maior. Ate 50 issues por tipo de relacao.
- Busca: `is:blocked`, `is:blocking`, `blocked-by:<issue>`, `blocking:<issue>`. O changelog diz que issues
  bloqueadas aparecem nos projects, mas **nao** diz se esses filtros valem no filtro de uma view do Project:
  conferir na primeira trilha e anotar no `BOARD.md`.
- API: REST `issue-dependencies`; GraphQL `addBlockedBy(input:{issueId, blockingIssueId})` e `removeBlockedBy`;
  leitura por `issue{blockedBy{nodes{number}} blocking{nodes{number}}}` (conferido em 2026-10-15).

## Sub-issues

- GraphQL `addSubIssue`, `removeSubIssue`, `reprioritizeSubIssue`; leitura `issue{parent{number} subIssues{...}}`.
- Campos nativos do Project: `Parent issue` e `Sub-issues progress`. Workflow "Auto-add sub-issues to project".

## Issue Types

- Mutacoes `createIssueType`, `updateIssueIssueType` existem. Num repo de **conta pessoal**,
  `repository{issueTypes}` volta `null` (conferido em 2026-10-15): a skill usa labels `tipo:*` nesse caso.

## Projects (ProjectV2)

- **Ate 50 campos por Project**, contando os nativos (docs "About Projects").
- Copia: `gh project copy <N> --source-owner A --target-owner B --title T` (GraphQL `copyProjectV2`) leva campos,
  views, workflows configurados, Insights e, opcionalmente, draft items.
- Status update do Project: `createProjectV2StatusUpdate` (status `ON_TRACK`, `AT_RISK`, `OFF_TRACK`,
  `COMPLETE`, `INACTIVE`; `startDate`, `targetDate`, `body`).
- Workflows nativos vistos num Project real: Auto-add sub-issues to project, Auto-add to project, Auto-close
  issue, Item added to project, Item closed, Pull request linked to issue, Pull request merged.
- View: criar por REST `POST users/<owner>/projectsV2/<n>/views` (ids numericos de campo); a API nao agrupa,
  ordena nem fatia — isso e feito na tela.

## Fontes

- https://github.blog/changelog/2025-08-21-dependencies-on-issues/
- https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies
- https://docs.github.com/en/rest/issues/issue-dependencies
- https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects
- https://github.blog/developer-skills/github/10-things-you-didnt-know-you-could-do-with-github-projects
- https://cli.github.com/manual/gh_project
