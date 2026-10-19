---
title: Statusline com issue, status do board, modelo e esforco
type: decisao
status: aprovado
created: 2026-10-18
updated: 2026-10-18
project: template_projetos
tags: [decisao, statusline, claude-code, issue, board, tema/tooling]
---

# 2026-10-18 — Statusline com issue, status do board, modelo e esforco

## O que mudou

1. Nova pasta `.claude/statusline/`, com a statusline, o hook de captura, a CLI `issue.js` e o
   atualizador do cache do board. Descricao em [[../STATUSLINE]].
2. `.claude/settings.json` ganhou a chave `statusLine` e uma segunda entrada no `UserPromptSubmit`.
3. A skill `/issue`, no passo 1, registra a issue na statusline pela sessao principal.

## Por que assim

- **Status do board e nao fase da `/issue`.** Foi escolha do usuario. O custo e a rede, resolvida
  com cache de 60 s renovado em segundo plano, porque o `gh` leva cerca de 1 s e a statusline e
  cancelada quando outro evento chega.
- **Hook e skill, as duas portas.** O hook pega `/issue <ref>` no prompt. A skill pega a issue que
  chegou por texto. As duas gravam o mesmo arquivo por `session_id`. Por checkout, duas sessoes no
  mesmo checkout mostrariam a mesma issue.
- **Estado no home.** Hook, CLI e statusline rodam com `cwd` diferentes, e o `session_id` e unico.
- **Contexto e tokens na linha, nao dolar.** O contexto relido e o que custa ([[../AGENTES]] secao 1).
  Pedido do usuario: tokens da sessao inteira, com subagentes, lidos dos transcripts. O payload so traz
  a sessao principal, e o `usage` de topo omite o advisor, que so aparece em `usage.iterations`.
  A soma inclui leitura de cache e mistura modelos: mede volume de contexto, nao preco.
- **No `settings.json` do projeto.** Assim a statusline desce para os derivados. Quem quiser a
  propria usa o `settings.local.json`.

## Alternativas descartadas

- **Nome da branch (`issue-42-…`):** exigiria convencao de branch que o repo nao tem.
- **Arquivo `atual.json` por checkout:** colide com duas sessoes no mesmo checkout.
- **Chamar o `gh` direto na statusline:** a barra ficaria vazia na maior parte do tempo.
