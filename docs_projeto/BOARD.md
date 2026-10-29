---
title: Board do projeto no GitHub
type: convencao
status: rascunho
created: 2026-10-15
updated: 2026-10-15
project: template_projetos
tags: [convencao, github, board, trilha, tema/tooling]
---

# Board do projeto no GitHub

Os IDs e ajustes do board **deste** projeto, para nenhuma sessao precisar redescobri-los. O metodo (marcos,
sequencia, bloqueios, progresso) esta na skill `/trilha` (`.claude/skills/trilha/SKILL.md`); aqui so o que e
local. No `template_projetos` esta nota e o molde vazio: num projeto derivado, preencha e mude `status` para
`aprovado`.

## 1. Onde

| Item | Valor |
|---|---|
| Repo de planejamento (todas as issues moram aqui) | `OWNER/REPO` |
| Outros repos onde o codigo muda | — |
| Project | `#N`, id `PVT_...`, dono `OWNER` (`users/` ou `orgs/`) |
| Copiado do Project-modelo | `#N` em AAAA-MM-DD |
| Tipo da issue | Issue Types (org) / labels `tipo:*` (conta pessoal) |
| Limite WIP (In progress) | 3 |

## 2. Labels

| Label | Uso |
|---|---|
| `tipo:epico`, `tipo:tarefa`, `tipo:bug`, `tipo:decisao` | so em conta pessoal (sem Issue Types) |
| `size/XS` .. `size/XL` | tamanho, lido pela `/issue` |
| `bloqueado` | so bloqueio **externo**, junto com o campo `Bloqueio externo` |

Criar: `gh label create "size/M" --color ededed --force` (idempotente com `--force`).

## 3. Campos

Teto de 50 campos por Project, contando os nativos. Campo novo exige motivo nesta tabela.

| Campo | Tipo | id | Opcoes (nome = id) |
|---|---|---|---|
| Status | single select | `PVTSSF_...` | Backlog = , Ready = , In progress = , In review = , Done = |
| Priority | single select | `PVTSSF_...` | P0 = , P1 = , P2 = |
| Size | single select | `PVTSSF_...` | XS = , S = , M = , L = , XL = |
| Trilha | single select | `PVTSSF_...` | (uma por trilha, secao 6) |
| Ordem | numero | `PVTF_...` (databaseId ) | — |
| Bloqueio externo | texto | `PVTF_...` | — |

Os ids saem de `gh project field-list N --owner "@me" --format json` (ids GraphQL) e de
`gh api users/OWNER/projectsV2/N/fields` (ids numericos, usados para criar view).

## 4. Views

| # | View | Conferido em |
|---|---|---|
| 1 | Sequencia | |
| 2 | Quadro | |
| 3 | Marcos | |
| 4 | Prontas | |
| 5 | Bloqueadas (`is:blocked` aceito no filtro do Project? sim/nao) | |
| 6 | Externo | |
| 7 | Espera o dono | |
| 8 | Triagem | |

## 5. Workflows nativos

| Workflow | Estado |
|---|---|
| Auto-add to project | ligado, filtro `is:issue` |
| Auto-add sub-issues to project | ligado |
| Item added to project | Backlog |
| Item closed | Done |
| Auto-close issue | ligado |
| Pull request linked to issue | In progress |
| Pull request merged | **In review** |
| Item reopened | In progress |

A `/issue` usa sempre `Refs #N`, entao o merge cai em In review por este workflow. Quando toda a prova e
automatizada, ela mesma poe Done depois do merge (`issue.js mover "Done" --conferir`, que reaplica se o
workflow chegar depois). Ver `.claude/skills/issue/SKILL.md`, F8, passo 7.

## 6. Trilhas

| Prefixo | Epico | Milestones | Issues | Plano e manifesto | Estado |
|---|---|---|---|---|---|
| | # | | #..# | `docs_projeto/.../Roadmap/` | |
