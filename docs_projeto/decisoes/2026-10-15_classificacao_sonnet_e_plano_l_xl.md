---
title: Classificacao de tamanho no Sonnet e plano formal so em L/XL
type: decisao
status: aprovado
created: 2026-10-15
updated: 2026-10-15
project: template_projetos
tags: [decisao, agentes, custo, issue, tema/tooling]
---

# 2026-10-15 — Classificacao de tamanho no Sonnet e plano formal so em L/XL

Ajusta [[2026-10-10_agentes_e_fluxo_de_issue]].

## O que mudou

1. **Classificacao:** a `/issue` abre o `explorer` com `model: sonnet` no passo 2. Ele localiza o codigo afetado e propoe o tamanho, com justificativa. Antes, quem estimava era a sessao principal, que em geral roda em Opus.
2. **Label:** o `explorer` roda tambem quando a issue ja tem `size/*`, e vale o maior dos dois tamanhos. Rebaixar a label continua sendo decisao do usuario.
3. **M sem plano formal:** a M nao tem mais `Plan` opus nem advisor momento 1. A sessao grava de 3 a 6 linhas de fatias em `## Fatias` no handoff. Se uma fatia pedir decisao de desenho que nao cabe numa linha, ou passar de 6 fatias, a issue sobe para L.
4. **Plano fora do chat:** em nenhum tamanho o plano e mostrado. Ele fica no handoff, e a sessao diz so quantas fatias sao.
5. Arquivos: `.claude/skills/issue/SKILL.md` (v1.1), `.claude/agents/explorer.md`, [[../AGENTES|AGENTES.md]] e `CLAUDE.md`.

## Por que

- Classificar e um julgamento curto, e a sessao Opus precisava ler o codigo para isso. O `explorer` ja le esse codigo no passo 1; chama-lo em Sonnet junta as duas coisas e tira essa leitura do contexto principal.
- O gasto de "fazer o plano" estava no `Plan` opus lendo o codigo do zero e no advisor relendo a conversa inteira, nao no texto mostrado. Na M, uma lista de fatias escrita pela sessao basta.

## Decisoes do usuario

- `explorer` em Sonnet, em vez de um agente `classifier` novo, cuja `description` entraria em todo prompt.
- Na M, lista curta na sessao, em vez de um `implementer` direto sem plano ou de tratar M como S.
- Plano so no handoff, nem resumido no chat.
- Duvida entre M e L sobe para L automaticamente.
- Issue com label tambem passa pelo Sonnet, para conferir a label.
- **Sem medicao:** a mudanca entra sem registrar tamanho proposto contra tamanho real.

## Riscos aceitos

- **A fronteira M/L ficou mais cara de errar.** Uma L classificada como M agora perde o plano e, se nao for sensivel, o `reviewer`. As travas sao a regra "na duvida, o maior", a subida para L quando as fatias nao cabem em uma linha e a label nunca rebaixada sem o usuario.
- **Sem medicao, o erro de classificacao so aparece como retrabalho.** Se surgir, a primeira providencia e registrar o tamanho proposto e o real por umas 10 issues.
- **Issue XS com label paga um agente a mais**, porque o `explorer` sempre roda. Ele ja rodava para localizar o codigo; o acrescimo e a troca de Haiku por Sonnet.

## Consequencias

- Projetos derivados (o TelemeVisus inclusive) continuam no fluxo antigo ate alguem copiar os 4 arquivos acima.
