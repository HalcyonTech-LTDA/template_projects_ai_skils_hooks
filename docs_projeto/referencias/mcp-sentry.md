---
title: MCP Sentry
source: https://mcp.sentry.dev/
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, sentry, observabilidade, debug, tema/tooling]
---

# MCP Sentry

Traz erro de producao para dentro da sessao: stack trace, frequencia, release afetada,
breadcrumb. Fecha o ciclo entre "quebrou la" e "corrige aqui".

## Instalacao

```bash
claude mcp add -s project -t http sentry https://mcp.sentry.dev/mcp
```

O endpoint aceita escopo por organizacao e projeto:

```
https://mcp.sentry.dev/mcp/{organizationSlug}/{projectSlug}
```

Escopar por projeto reduz ruido e superficie de acesso. Prefira a forma escopada.

Autenticacao por OAuth: `/mcp` ou `claude mcp login sentry`.

## Custo de contexto

Medio-baixo.

## Quando ligar

- Investigar issue especifica com o codigo aberto ao lado.
- Priorizar correcao por impacto real em vez de palpite.
- Confirmar que uma release parou de emitir determinado erro.

## Quando nao ligar

Desenvolvimento de feature nova. Nao ha erro de producao para consultar.

## Cuidado

Stack trace de producao pode conter dado de usuario em variavel local ou breadcrumb.
Ao trazer para a sessao, esse dado entra no contexto do modelo. Vale conferir a politica
de scrubbing do projeto no Sentry antes de ligar.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 4
- Skill relacionada no repo: `systematic-debugging`
