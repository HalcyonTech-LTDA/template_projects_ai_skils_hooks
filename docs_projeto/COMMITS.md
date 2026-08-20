---
title: Convencao de commits e a skill /commit
type: convencao
status: rascunho
created: 2026-08-20
updated: 2026-08-20
tags: [convencao, git, commit, claude-code, skill]
---

# Convencao de commits e a skill `/commit`

> **Template.** Esta pagina e o esqueleto que cada projeto derivado deve preencher.
> A skill `/commit` le **este arquivo primeiro** — o que estiver aqui vira a regra
> que ela aplica. Enquanto ela estiver com `status: rascunho` e as tabelas vazias,
> a skill cai no fallback (Conventional Commits puro + escopos derivados do
> historico do repo).

Os commits seguem **Conventional Commits**.

## Formato

```
<tipo>(<escopo>): <descricao em ingles, imperativo, <= 72 chars>

<corpo opcional: bullets com o PORQUE>

<rodape opcional: BREAKING CHANGE:, Refs: ADR-00XX, Closes #N>
```

Descricao em **ingles**, verbo no imperativo, minuscula inicial, sem ponto final.
Descreve o efeito, nao o arquivo: `fix(auth): retry only idempotent requests`,
nunca `fix(auth): update client.ts`.

## Tipos

`feat` `fix` `docs` `style` `refactor` `test` `chore` `perf` `build` `ci` `revert`

## Escopos

<!-- PREENCHER: o escopo sai do path dominante do diff. Liste os deste projeto. -->

| Path | Escopo |
|---|---|
| `src/<modulo>/` | nome do modulo |
| `docs_projeto/` | tipo `docs`, escopo = modulo |
| `.claude/` | tipo `chore`, escopo `claude` |

Escopo e opcional quando o diff e realmente transversal. Nao invente escopo que
nao exista no repo.

## Guardas de path (bloqueantes)

<!-- PREENCHER: acrescente aqui o que este projeto proibe de commitar e o MOTIVO.
     A skill nomeia o motivo ao recusar, entao motivo generico gera recusa fraca. -->

| Padrao | Motivo |
|---|---|
| `node_modules/`, `dist/`, `build/` | Gerado. Nunca versionar. |
| `.env*`, `*.keystore`, `*.pem` | Segredos. |
| `.claude/settings.local.json` | Configuracao pessoal, fora do git. |

## Rodape de coautoria

<!-- PREENCHER: decida uma vez e registre aqui. -->

Este repositorio **nao** usa `Co-Authored-By` nem `Generated with Claude Code`.

## Ver tambem

- `.claude/skills/commit/SKILL.md` — o fluxo que a skill executa
- [[CONVENCOES]] — schema da documentacao
