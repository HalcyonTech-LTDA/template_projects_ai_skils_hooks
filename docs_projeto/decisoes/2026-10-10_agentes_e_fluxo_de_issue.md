---
title: Subagentes do projeto e fluxo de issue por tamanho
type: decisao
status: aprovado
created: 2026-10-10
updated: 2026-10-10
project: template_projetos
tags: [decisao, agentes, subagentes, custo, tema/tooling]
---

# 2026-10-10 — Subagentes do projeto e fluxo de issue por tamanho

## O que mudou

1. Nova pasta `.claude/agents/` com 5 subagentes: `explorer`, `researcher`, `worker`, `implementer` e `reviewer`
2. Nova skill `.claude/skills/issue/` (`/issue`), que conduz uma issue escolhendo agente e modelo pelo tamanho (49 → 50 skills)
3. Novo [[../AGENTES|docs_projeto/AGENTES.md]], com o catalogo, a tabela tamanho → modelo, o handoff e o advisor
4. `inject-rules.js`: a regra 1 lista os agentes e aponta a `/issue`; a regra 3 ganhou a excecao de XS/S
5. `.gitignore`: `/.claude/handoff/`, onde fica o handoff entre fatias
6. Propagado para o TelemeVisus, o primeiro projeto derivado com o fluxo, com a secao "Adaptacao local" preenchida

## Por que

Uma auditoria dos registros do Claude Code (2026-10-02 a 09, ~6.000 chamadas no TelemeVisus) mostrou que o gasto semanal vinha do **contexto relido**, nao da resposta:

- 2,05 bilhoes de tokens lidos do cache contra 3,9 milhoes de saida.
- 61% do contexto lido veio de chamadas acima de 400 mil tokens, com a compactacao automatica desligada.
- Um implementador mantido vivo por `SendMessage` atraves de 9 fatias chegou a 966 mil tokens e foi o maior gasto da semana.

O fluxo que funcionava (Plan Opus, implementador Opus, testes no Sonnet) estava so na memoria pessoal de uma maquina. Ele virou regra versionada, com as correcoes de custo embutidas.

## Decisoes do usuario

- **Mesmos nomes dos agentes globais, e os globais saem.** Agente de projeto vence o de usuario com o mesmo nome; manter os dois geraria divergencia.
- **Tamanho pela label `size/*`, senao por estimativa declarada.** Funciona sem GitHub Projects, porque o template e generico.
- **Tabela de modelos:** XS/S na sessao; M = Plan Opus + implementer Sonnet; L/XL = Plan Opus + implementer Opus por fatia + reviewer.
- **XS/S fora da regra das 5 perguntas.**
- **Handoff em `.claude/handoff/<issue>.md`**, local e ignorado pelo git.
- **Reviewer obrigatorio em L/XL e em codigo sensivel**, em qualquer tamanho.

## Alternativas descartadas

- **Tool `Workflow` como orquestrador.** Exige opt-in explicito a cada uso e pode abrir dezenas de agentes: e o oposto do objetivo de custo.
- **Esforco `medium` em todos os agentes Opus como forma de economizar.** O esforco reduz a saida, que e ~7% do custo; o contexto relido nao muda.
- **Opus `high` como padrao da sessao principal.** Encarece justamente o contexto que domina o gasto.
- **Graphify ou outro indice do codigo.** A premissa de que o Claude rele todos os arquivos a cada chat e falsa: a abertura de sessao foi ~2% do contexto lido. O `explorer` resolve a busca sem um indice para manter.

## Consequencias

- Cada `description` de agente entra em todo prompt. Criar um sexto agente exige um papel que os cinco nao cobrem.
- Projetos derivados criados antes desta data nao tem o fluxo ate alguem copiar `.claude/agents/`, `.claude/skills/issue/`, `inject-rules.js`, `AGENTES.md` e a linha do `.gitignore`.
- A prova de aceite e abrir uma sessao nova num projeto com o fluxo e disparar um agente de verdade.
