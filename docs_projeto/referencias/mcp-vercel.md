---
title: MCP Vercel
source: https://vercel.com/docs/agent-resources/vercel-mcp
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, vercel, deploy, tema/tooling]
---

# MCP Vercel

Servidor remoto oficial da Vercel. Consulta projetos, deploys, logs de build, dominios e
variaveis de ambiente, alem da documentacao da plataforma.

## Instalacao

```bash
claude mcp add -s user -t http vercel https://mcp.vercel.com
```

O flag `-t http` indica endpoint HTTP streamable. O primeiro uso dispara OAuth no browser;
a credencial nunca toca o arquivo de config.

## Quando ele ganha

O caso que justifica o servidor e **build quebrado**: em vez de abrir o dashboard, copiar
log e colar na sessao, o agente puxa o log do deploy que falhou e correlaciona com o
commit. Mesma coisa para "por que a variavel de ambiente nao chegou em preview".

## Quando ele nao ganha

Desenvolvimento local. Enquanto voce roda `next dev`, a Vercel nao tem nada a dizer, e as
tools ficam ocupando contexto.

## Custo de contexto

Medio-baixo.

## Cuidado

Tem acesso a variaveis de ambiente do projeto. Dependendo do escopo concedido no OAuth,
segredo de producao entra no contexto do modelo se alguem pedir. Conceda o escopo minimo.

## Projetos do vault que usam Vercel

- `Desenvolvimento/produtos/HalcyonTech-Notes` (Vercel Functions em `api/`)
- `Desenvolvimento/produtos/HalcyonTech-LandingPage` (Vercel Analytics)

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 3.7
- Skill relacionada no repo: `senior-devops`
