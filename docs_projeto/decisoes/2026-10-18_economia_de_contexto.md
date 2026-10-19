---
title: Economia de contexto
type: decisao
status: aprovado
created: 2026-10-18
tags: [decisao, custo, tokens, hooks]
---

# Economia de contexto

## Contexto

Uma tarefa M deste repo gastou 8,55 M tokens, 84% deles em leitura de cache: 51 chamadas de
~145 mil tokens cada. A sessao ja comecava com 72 mil tokens de preambulo, e o hook
`inject-rules.js` somava 5,3 KB a cada prompt, repetindo a lista de skills e agentes que o prompt
do sistema ja traz.

## Decisao

1. `docs_projeto/ECONOMIA.md`: menos chamadas por tarefa, contexto menor e modelo pela tarefa.
2. `inject-rules.js` caiu de seis regras e 5,3 KB para quatro regras e 0,7 KB. Saiu a lista de
   skills e agentes. A regra de economia entrou como regra 2.
3. As regras 3 (5 perguntas) e 4 (advogado do diabo) viraram uma so e escalam pelo tamanho:
   pergunta so o ambiguo; 5 perguntas e 2 alternativas com tradeoffs so em tarefa M ou maior.
4. Fora do repo, na mesma operacao: o `CLAUDE.md` da raiz `D:\HalcyonTech` mandou comandos,
   hooks, armadilhas e lacunas para `D:\HalcyonTech\.claude\mapa\` (24,8 KB para 14,8 KB), e o
   `~/.claude/CLAUDE.md` ganhou o resumo.

## Consequencias

- Projeto derivado criado antes desta data so ganha a economia ao copiar `inject-rules.js` e
  `ECONOMIA.md`.
- A lista de skills deixa de chegar pelo hook; ela continua no prompt do sistema, com descricao.
