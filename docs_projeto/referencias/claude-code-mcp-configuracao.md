---
title: Configuracao de MCP no Claude Code
source: https://code.claude.com/docs/en/mcp
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, claude-code, configuracao, tema/tooling]
---

# Configuracao de MCP no Claude Code

Mecanica do cliente, independente de qual servidor voce liga. Base para
[[../MCPS|MCPS.md]] secao 6.

## Sintaxe do `claude mcp add`

```bash
claude mcp add [options] <nome> <url>
claude mcp add [options] <nome> -- <comando> [args...]
```

| Flag | Curta | Valores | Para que |
|---|---|---|---|
| `--transport` | `-t` | `http`, `sse`, `stdio`, `ws` | Protocolo de transporte |
| `--scope` | `-s` | `local` (padrao), `project`, `user` | Onde a config e gravada |
| `--env` | `-e` | `CHAVE=valor` | Variavel de ambiente (aceita varias) |
| `--header` | `-H` | `Chave:valor` | Header HTTP, tipicamente autenticacao |
| `--callback-port` | | porta | Porta fixa de callback OAuth |
| `--client-id` | | string | Client ID de OAuth |
| `--client-secret` | | (pergunta) | Client secret de OAuth, entrada mascarada |

Para servidor stdio, `--` separa as opcoes do Claude do comando do servidor:

```bash
claude mcp add --env CHAVE=valor -t stdio meuservidor -- python server.py --port 8080
```

`sse` esta obsoleto. Servidor novo usa `http` (streamable HTTP).

## Escopos

| Escopo | Carrega em | Compartilhado | Gravado em |
|---|---|---|---|
| `local` (padrao) | So o projeto atual | Nao | `~/.claude.json`, entrada do projeto |
| `project` | So o projeto atual | Sim (git) | `.mcp.json` na raiz |
| `user` | Todos os projetos | Nao | `~/.claude.json`, topo |

## Expansao de variavel no `.mcp.json`

O `.mcp.json` **expande variavel de ambiente**:

- `${VAR}` — valor de `VAR`
- `${VAR:-default}` — `VAR` se definida, senao `default`

Campos suportados: `command`, `args`, `env`, `url`, `headers`.

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": { "Authorization": "Bearer ${API_KEY}" }
    }
  }
}
```

Variavel nao definida e sem default: o Claude Code avisa e mantem o texto `${VAR}` como
esta — o servidor falha na conexao, nao no parse.

## Onde definir a variavel

O bloco `env` de um arquivo de settings "define variaveis de ambiente para toda sessao e
seus subprocessos" — o que inclui os servidores MCP. Combinado com a expansao acima:

```json
// .claude/settings.local.json  (ignorado pelo git)
{
  "env": { "API_KEY": "valor-real" }
}
```

Ressalva documentada: a maioria dos valores de `env` vindos de arquivo de projeto so passa
a valer **depois que a pasta e marcada como confiavel** (workspace trust). Em clone novo,
confie na pasta primeiro.

## OAuth em servidor remoto

1. O servidor responde `401` ou `403` e e marcado como precisando de auth.
2. `/mcp` na sessao abre o fluxo no browser. Ou, pelo terminal:
   ```bash
   claude mcp login sentry
   claude mcp login sentry --no-browser   # SSH / headless
   claude mcp logout sentry
   ```
3. Token guardado com seguranca e **renovado automaticamente**. Em `401` de servidor ja
   autenticado, o Claude Code renova, reconecta e repete a chamada uma vez antes de marcar
   o servidor como problematico no `/mcp`.

Para servidor sem Dynamic Client Registration, passe credencial pre-configurada:

```bash
MCP_CLIENT_SECRET=seu-secret claude mcp add -t http \
  --client-id seu-client-id --client-secret --callback-port 8080 \
  meu-servidor https://mcp.example.com/mcp
```

## Aprovacao de servidor de `.mcp.json`

Servidor declarado em `.mcp.json` de projeto pede aprovacao. Chaves de settings que
controlam isso:

| Chave | Efeito |
|---|---|
| `enableAllProjectMcpServers` | Aprova todos os servidores do `.mcp.json` sem prompt |
| `enabledMcpjsonServers` | Aprova servidores especificos |
| `disabledMcpjsonServers` | Rejeita servidores especificos |

Util no template: versionar o `.mcp.json` com o catalogo e usar `enabledMcpjsonServers` no
`settings.local.json` para escolher, por maquina, quais realmente sobem.

## Precedencia de settings (do mais forte para o mais fraco)

1. Managed settings (organizacao)
2. `claude --settings` (linha de comando)
3. `.claude/settings.local.json` (voce, neste projeto)
4. `.claude/settings.json` (equipe, neste projeto)
5. `~/.claude/settings.json` (voce, todo projeto)

O `~/.claude.json` e um sexto arquivo que o Claude Code escreve sozinho: sessao de login,
config de MCP e estado por projeto. Nao editar a mao.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]]
- [[../HOOKS|HOOKS.md]]
