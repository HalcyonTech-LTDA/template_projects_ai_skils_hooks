---
title: Catalogo de MCPs para desenvolvimento
type: decisao-repo
status: aprovado
date: 2026-09-06
created: 2026-09-06
updated: 2026-09-06
tags: [decisao, mcp, tooling, template, tema/tooling]
---

# Catalogo de MCPs para desenvolvimento

## Contexto

O repositorio template entregava skills e hooks para os projetos derivados, mas **nenhuma
orientacao sobre servidores MCP**. Levantamento no inicio desta tarefa:

- Nenhum `.mcp.json` no repo, nenhuma chave `mcpServers` em `.claude/settings.json`.
- Nenhuma mencao a MCP em `docs_projeto/` ou no `CLAUDE.md`.
- Na maquina do usuario, um unico servidor configurado (`github`), em escopo global, sem
  limite de toolsets — herdado da config pessoal, nao do template.
- Conectores claude.ai (Figma, Gmail, Google Calendar, Google Drive, Notion) listados mas
  nao autorizados.

Consequencia: cada projeto derivado improvisava a escolha de MCP, sem criterio de custo
nem de seguranca.

## Decisao

Criar um **catalogo curado**, nao uma instalacao automatica:

1. **`docs_projeto/MCPS.md`** — indice decisorio. Regra dos 3 a 6 servidores ativos,
   perfis de projeto (web, mobile, backend, fullstack, desktop, gestao), 8 fichas de
   nucleo, 4 opcionais, anti-lista, politica de segredos e escopo, politica de
   revalidacao.
2. **`docs_projeto/referencias/mcp-*.md`** — 12 fichas tecnicas, uma por servidor, com
   `verificado_em`. Mais `claude-code-mcp-configuracao.md` com a mecanica do cliente
   (escopos, expansao de `${VAR}`, OAuth, `enabledMcpjsonServers`).
3. **`.mcp.json.example`** na raiz — nucleo comentado, opt-in explicito por copia.

Nucleo escolhido pelo usuario: github, figma, mobile-next, google-workspace, playwright
(teste web), terminator (teste desktop), supabase, vercel.

### Politica de segredos

Ordem de preferencia: **OAuth** (token no cofre do Claude Code, nada em disco) →
**bloco `env` do `.claude/settings.local.json`** (gitignorado) → nunca valor literal em
`.mcp.json`.

O `.mcp.json` expande `${VAR}` em `command`, `args`, `env`, `url` e `headers`, e o `env`
de um arquivo de settings vale para a sessao e todo subprocesso. Isso permite versionar o
`.mcp.json` sem segredo dentro.

### Politica de escopo

Por natureza do servidor, nao um escopo unico: transversal (`github`, `context7`,
`vercel`, `google`) em `-s user`; amarrado ao projeto (`supabase`, `figma`, `mobile`,
`playwright`, `terminator`) em `-s project`.

## Alternativas consideradas

- **`.mcp.json` versionado ligando o nucleo por padrao** — descartado pelo usuario. Um
  pacote renomeado ou token faltando quebraria todos os projetos derivados de uma vez, e
  ligaria MCP de mobile em projeto backend.
- **So o documento, sem arquivo de exemplo** — descartado: documento sem artefato
  executavel vira enfeite.
- **Um arquivo unico com tudo** — descartado: `MCPS.md` ficaria longo demais para servir
  de referencia rapida. Separacao indice decisorio / ficha tecnica preserva os dois usos.
- **Nao incluir anti-lista** — descartado: sem freio explicito, o catalogo cresce por
  inercia e alguem instala `filesystem-mcp` degradando as sessoes sem entender por que.

## Consequencias

**Positivas**

- Projeto derivado nasce com criterio de escolha, nao com palpite.
- Custo de contexto vira variavel explicita na decisao (toda ficha declara).
- Risco de seguranca documentado onde ele existe de verdade (google-workspace, terminator,
  supabase), em vez de diluido.
- `verificado_em` por ficha torna a obsolescencia visivel em vez de silenciosa.

**Negativas / a acompanhar**

- **13 arquivos novos a manter.** O ecossistema MCP muda rapido; sem a revalidacao
  trimestral da secao 8 do `MCPS.md`, isto vira documentacao errada.
- As contagens de tools sao ordem de grandeza, obtidas de doc e nao medidas com `/mcp`
  nesta maquina. Ajustar quando houver medicao real.
- O endpoint remoto da Figma e o do Google Workspace nao foram exercitados aqui — falta
  confirmacao pratica.

## Proximos passos sugeridos

1. Aplicar `X-MCP-Toolsets` no `github` ja configurado nesta maquina, para cortar o custo.
2. Medir com `/mcp` a contagem real de tools de cada servidor ligado e corrigir as fichas.
3. Avaliar promover `github` + `context7` para `.mcp.json` versionado depois de uso diario
   comprovado.

## Ver tambem

- [[../MCPS|MCPS.md]]
- [[../referencias/README|referencias/]]
