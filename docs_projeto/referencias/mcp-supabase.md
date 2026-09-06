---
title: MCP Supabase
source: https://supabase.com/docs/guides/ai-tools/mcp
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, supabase, postgres, banco, tema/tooling]
---

# MCP Supabase

Servidor remoto oficial da Supabase. Da ao agente acesso a schema, migracoes, branches de
banco, Edge Functions, logs e a documentacao da plataforma.

## Instalacao

```bash
claude mcp add -s project -t http supabase "https://mcp.supabase.com/mcp?features=docs,database,debugging,development,functions"
```

Autenticacao por OAuth no primeiro uso (`/mcp`). Nenhuma credencial em disco.

## O parametro `features`

O querystring `features` decide quais grupos de tool o servidor expoe — e portanto o custo
de contexto. Grupos disponiveis:

```
docs, account, database, debugging, development, functions, branching
```

| Feature | Vale a pena | Observacao |
|---|---|---|
| `docs` | Sim | Barato e evita API alucinada |
| `database` | Sim | Schema, query, migracao. O nucleo |
| `debugging` | Sim | Logs e advisors |
| `development` | Sim | URL do projeto, chaves anon, tipos TypeScript |
| `functions` | Se usar Edge Functions | Caso contrario, corte |
| `branching` | Raramente | Caro; so em fluxo que usa branch de banco |
| `account` | Raramente | Gerencia organizacao e projeto. Fora do dia a dia de codigo |

Comece pelo minimo e adicione quando faltar. Cada feature ligada e tool no prompt.

## Seguranca

Regras que valem mais que a conveniencia:

1. **Aponte para projeto de desenvolvimento, nunca producao.** O agente pode executar SQL.
2. **Prefira modo somente-leitura** quando o servidor oferecer, para trabalho de leitura
   de schema.
3. Dado de cliente em tabela acessivel vira contexto do modelo no momento em que uma query
   e rodada. Trate como decisao de privacidade.
4. RLS mal configurada mais MCP conectado e uma combinacao ruim — o agente enxerga o que a
   chave enxerga.

## Custo de contexto

Medio, e diretamente proporcional ao `features`.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 3.6
- Skills relacionadas no repo: `supabase-postgres-best-practices`, `senior-backend`
