---
title: MCP GitHub
source: https://github.com/github/github-mcp-server
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, github, tema/tooling]
---

# MCP GitHub

Servidor oficial do GitHub. Da ao agente acesso a repositorios, issues, pull requests,
Actions, releases e code search sem sair da sessao.

## Endpoint e instalacao

Servidor remoto (preferido — sem instalacao local, OAuth):

```
https://api.githubcopilot.com/mcp/
```

```bash
claude mcp add -s user -t http github https://api.githubcopilot.com/mcp/
```

Autentique com `/mcp` na primeira chamada, ou `claude mcp login github`.

## Toolsets

O servidor e dividido em toolsets. Conjunto padrao quando nada e informado:

```
context, repos, issues, pull_requests, users
```

Toolsets disponiveis incluem: `actions`, `code_quality`, `code_security`, `discussions`,
`gists`, `git`, `governance`, `issues`, `labels`, `notifications`, `organizations`,
`projects`, `pull_requests`, `repos`, `secret_protection`, `security_advisories`,
`stargazers`, `users`. Valores especiais: `all` (tudo) e `default` (padrao + extras).

Tres formas de limitar:

| Forma | Como |
|---|---|
| Header (remoto) | `X-MCP-Toolsets: repos,issues,pull_requests` |
| Flag (local) | `--toolsets repos,issues,pull_requests` |
| Env (local) | `GITHUB_TOOLSETS="repos,issues,pull_requests"` |

Ha tambem `--read-only`, que tem prioridade e derruba as tools de escrita mesmo que o
toolset delas esteja habilitado.

## Custo de contexto

100+ tools com `all`. ~50 no conjunto padrao. **Sempre limite os toolsets** — e o maior
consumidor de contexto do catalogo por padrao.

## Quando nao usar

Para operacao simples de git ou GitHub num repo so, o CLI `gh` pelo Bash faz o mesmo por
uma fracao do custo. O MCP ganha quando a tarefa e cross-repo, envolve review estruturado
ou precisa de code search da plataforma.

## Estado nesta maquina

Ja configurado em escopo global no `~/.claude.json`, sem limite de toolsets. Vale aplicar
o header `X-MCP-Toolsets` para reduzir o peso.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 3.1
- [[claude-code-mcp-configuracao]]
