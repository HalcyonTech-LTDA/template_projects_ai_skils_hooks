---
title: Catalogo de MCPs para desenvolvimento
type: convencao
status: aprovado
created: 2026-09-06
updated: 2026-09-06
project: template_projetos
tags: [convencao, mcp, ferramentas, claude-code, tema/tooling]
---

# Catalogo de MCPs para desenvolvimento

Quais servidores MCP ligar num projeto derivado deste template, **quando ligar cada um
e quando desligar**. Cada ficha traz comando copiavel, escopo recomendado, custo de
contexto e data de verificacao.

Detalhe tecnico de cada servidor vive em [[referencias/README|referencias/]] — um arquivo
por MCP. Este documento e o **indice decisorio**; as referencias sao a fonte ingerida.

> **Este arquivo e a fonte canonica.** Assim como `.claude/skills/`, alteracao comeca aqui
> e desce por copia para os projetos derivados. Corrigiu num projeto? Replique aqui.

## 1. Regra de ouro: 3 a 6 servidores ativos

Todo MCP ligado injeta a definicao de **todas** as suas tools no prompt de **toda**
sessao, usada ou nao. O servidor do GitHub sozinho passa de 50 tools no conjunto padrao.
Ligar o catalogo inteiro come uma fatia grande da janela de contexto antes da primeira
linha digitada, e degrada a escolha de tool (o modelo erra mais quando tem 200 opcoes).

O consenso da comunidade em 2026 e **3 a 6 servidores ativos por projeto**. Passou disso,
a confiabilidade cai.

Portanto: **este catalogo nao e uma lista de instalacao.** E um cardapio. Escolha pelo
perfil do projeto.

## 2. Perfis de projeto

| Perfil | Ativos sugeridos | Por que |
|---|---|---|
| **Web / frontend** | github, figma, playwright, context7 | Design vira codigo, teste no browser, docs de lib atualizadas |
| **Mobile (RN / nativo)** | github, figma, mobile-next, context7 | Mesma coisa, com device real/emulador no lugar do browser |
| **Backend / API** | github, supabase (ou o do seu banco), context7, sentry | Schema, migracao, erro em producao |
| **Fullstack com deploy** | github, supabase, vercel, playwright | Cobre banco, deploy e verificacao E2E |
| **Desktop (Windows)** | github, terminator, context7 | Automacao de app desktop pela arvore de acessibilidade |
| **Documentacao / gestao** | github, google-workspace ou notion | Puxa material de fora do repo |

`github` aparece em todos porque e o unico transversal de verdade. Os outros sao
descartaveis: ligue no inicio da tarefa, desligue quando ela acabar.

## 3. Nucleo

### 3.1 GitHub

| | |
|---|---|
| **O que faz** | PRs, issues, code search, releases, Actions, branches |
| **Escopo** | `user` — transversal, serve todo projeto |
| **Custo de contexto** | **Alto** — ~50 tools no conjunto padrao, 100+ com `all` |
| **Credencial** | OAuth no primeiro uso (`/mcp`), sem token em disco |
| **Verificado em** | 2026-09-06 |
| **Referencia** | [[referencias/mcp-github]] |

```bash
claude mcp add -s user -t http github https://api.githubcopilot.com/mcp/
```

- **Ligue** quando o trabalho toca PR, issue, review ou busca cross-repo.
- **Desligue** se voce so mexe em codigo local — `gh` no Bash resolve o caso simples por
  uma fracao do contexto.
- **Corte o custo** limitando toolsets pelo header em vez de carregar tudo:
  `-H "X-MCP-Toolsets: repos,issues,pull_requests"`.

### 3.2 Figma

| | |
|---|---|
| **O que faz** | Extrai codigo, variaveis, tokens e specs do frame selecionado |
| **Escopo** | `project` — so faz sentido em projeto com design |
| **Custo de contexto** | **Baixo** — punhado de tools |
| **Credencial** | Remoto: OAuth. Desktop: nenhuma, mas exige seat Dev/Full em plano pago |
| **Verificado em** | 2026-09-06 |
| **Referencia** | [[referencias/mcp-figma]] |

```bash
# Remoto (preferido — funciona em qualquer seat e plano)
claude mcp add -s project -t http figma https://mcp.figma.com/mcp

# Desktop (alternativa; exige app Figma aberto em Dev Mode com o servidor ligado)
claude mcp add -s project -t http figma-desktop http://127.0.0.1:3845/mcp
```

- **Ligue** ao implementar tela a partir de design.
- **Desligue** depois que a tela saiu do Figma — ele nao ajuda em logica de negocio.
- **Casa com** as skills `frontend-design`, `ui-ux-pro-max` e `ui-design-system` do repo.
- **Armadilha**: o servidor desktop morre junto com o app Figma. Se as tools somem do
  `/mcp`, o Figma fechou.

### 3.3 mobile-next (mobile-mcp)

| | |
|---|---|
| **O que faz** | Dirige simulador, emulador e device fisico iOS/Android pela arvore de acessibilidade |
| **Escopo** | `project` — inutil fora de projeto mobile |
| **Custo de contexto** | **Medio-alto** — ~30 tools |
| **Credencial** | Nenhuma (local) |
| **Verificado em** | 2026-09-06 |
| **Referencia** | [[referencias/mcp-mobile-next]] |

```bash
claude mcp add -s project -t stdio mobile -- npx -y @mobilenext/mobile-mcp@latest
```

- **Pre-requisitos**: Node 20+, Android Platform Tools (`adb`) e/ou Xcode command line
  tools. **No Windows so ha caminho Android** — simulador iOS exige macOS.
- **Ligue** para testar fluxo em device, reproduzir bug, validar navegacao.
- **Desligue** ao voltar para logica pura — 30 tools paradas custam caro.
- **Vantagem real**: usa a arvore de acessibilidade, nao visao. Sem token de imagem.

### 3.4 Playwright (teste de aplicacao web)

| | |
|---|---|
| **O que faz** | Dirige Chromium, Firefox e WebKit; snapshot por arvore de acessibilidade |
| **Escopo** | `project` |
| **Custo de contexto** | **Medio** — ~25 tools |
| **Credencial** | Nenhuma (local) |
| **Verificado em** | 2026-09-06 |
| **Referencia** | [[referencias/mcp-playwright]] |

```bash
claude mcp add -s project -t stdio playwright -- npx -y @playwright/mcp@latest
```

- **Ligue** para E2E, verificacao pre-release, reproduzir bug de UI.
- **Desligue** fora de tarefa de browser.
- **Escolha entre ele e o Chrome DevTools**: Playwright para **dirigir** (cross-browser,
  deterministico, barato em token); Chrome DevTools para **depurar** (performance,
  rede, CDP). Ver [[referencias/mcp-chrome-devtools]].

### 3.5 Terminator (teste de aplicacao desktop)

| | |
|---|---|
| **O que faz** | Automacao de app desktop Windows pela UI Automation (arvore de acessibilidade) |
| **Escopo** | `project` |
| **Custo de contexto** | **Alto** — 50+ tools |
| **Credencial** | Nenhuma (local) |
| **Verificado em** | 2026-09-06 |
| **Referencia** | [[referencias/mcp-terminator]] |

```bash
claude mcp add -s project -t stdio terminator -- npx -y terminator-mcp-agent@latest
```

- **So Windows.** Nao ha suporte macOS/Linux.
- **Ligue** para automatizar ou testar app desktop nativo (Win32, WinForms, WPF, Electron).
- **Desligue** sempre que a tarefa sair do desktop — e o servidor mais caro do catalogo.
- **Risco**: dirige a maquina de verdade. Nao aponte para app com dado de producao sem
  saber exatamente o que o agente vai fazer.

### 3.6 Supabase

| | |
|---|---|
| **O que faz** | Schema, migracoes, branches de banco, Edge Functions, logs, docs |
| **Escopo** | `project` |
| **Custo de contexto** | **Medio** — varia com o parametro `features` |
| **Credencial** | OAuth (`/mcp`) |
| **Verificado em** | 2026-09-06 |
| **Referencia** | [[referencias/mcp-supabase]] |

```bash
claude mcp add -s project -t http supabase "https://mcp.supabase.com/mcp?features=docs,database,debugging,development,functions"
```

- **Ligue** ao mexer em schema, migracao ou RLS.
- **Desligue** em trabalho puro de frontend.
- **Corte o custo** removendo features do querystring (`account` e `branching` raramente
  valem o peso).
- **Regra de seguranca**: aponte para projeto de **desenvolvimento**, nunca producao, e
  prefira modo somente-leitura quando o servidor oferecer.

### 3.7 Vercel

| | |
|---|---|
| **O que faz** | Deploys, logs de build, dominios, variaveis de ambiente, docs |
| **Escopo** | `user` ou `project`, conforme voce use Vercel em tudo ou so num projeto |
| **Custo de contexto** | **Medio-baixo** |
| **Credencial** | OAuth (`/mcp`) |
| **Verificado em** | 2026-09-06 |
| **Referencia** | [[referencias/mcp-vercel]] |

```bash
claude mcp add -s user -t http vercel https://mcp.vercel.com
```

- **Ligue** ao investigar build quebrado ou deploy que nao subiu.
- **Desligue** durante desenvolvimento local — nao contribui nada ali.

### 3.8 Google Workspace

| | |
|---|---|
| **O que faz** | Gmail, Drive, Docs, Sheets, Calendar |
| **Escopo** | `user` |
| **Custo de contexto** | **Alto** — muitas tools, varia muito por implementacao |
| **Credencial** | OAuth. Conector claude.ai ou servidor remoto do Google |
| **Verificado em** | 2026-09-06 |
| **Referencia** | [[referencias/mcp-google-workspace]] |

Ha tres caminhos e eles **nao sao equivalentes** — leia a referencia antes de escolher.
Na conta em uso hoje, Gmail/Drive/Calendar aparecem como **conectores claude.ai** e
precisam ser autorizados nas configuracoes de conectores do claude.ai; ate la, as tools
existem no papel e nao funcionam.

- **Ligue** para ata de reuniao, requisito que veio por e-mail, planilha de dados.
- **Desligue** em sessao de codigo. E o MCP com pior relacao custo/beneficio dentro de
  uma tarefa tecnica.
- **Risco de dado**: da ao agente acesso de leitura ao seu e-mail corporativo inteiro.
  Trate como decisao de seguranca, nao de conveniencia.

## 4. Catalogo opcional

| MCP | O que faz | Custo | Comando |
|---|---|---|---|
| **Context7** | Docs atualizadas de bibliotecas, contra API alucinada | **Minimo** (~2 tools) | `claude mcp add -s user -t http context7 https://mcp.context7.com/mcp` |
| **Chrome DevTools** | Performance, rede, CDP. Depuracao, nao direcao | Medio | `claude mcp add -s project -t stdio chrome-devtools -- npx -y chrome-devtools-mcp@latest` |
| **Sentry** | Erro de producao com stack trace no contexto | Medio-baixo | `claude mcp add -s project -t http sentry https://mcp.sentry.dev/mcp` |
| **Notion** | Base de conhecimento, specs, roadmap | Medio | `claude mcp add -s user -t http notion https://mcp.notion.com/mcp` |

Context7 e o de melhor relacao custo/beneficio do catalogo inteiro: 2 tools, e mata a
classe de bug em que o modelo inventa uma API que nao existe mais. Se for ligar so um
opcional, ligue esse.

## 5. Nao instale isto

Servidores populares que **duplicam o que o Claude Code ja faz nativamente**, com mais
latencia, menos controle de permissao e custo de contexto adicional:

| MCP | Por que nao | Use no lugar |
|---|---|---|
| `filesystem` | Read/Write/Edit/Glob/Grep ja sao nativos e passam pelo sistema de permissao | Ferramentas nativas |
| `git` | O Bash roda `git` direto, com o hook e a skill `/commit` do repo em cima | `Bash` + `/commit` |
| `fetch` / `web-search` | WebFetch e WebSearch sao nativos | Ferramentas nativas |
| `shell` / `terminal` | Bash nativo, com allowlist de permissao granular | `Bash` |
| `memory` / `knowledge-graph` | Este repo ja resolve memoria em `docs_projeto/` e `CLAUDE.md`, versionado e legivel | `docs_projeto/` |
| `sequential-thinking` | O modelo ja raciocina em cadeia; a tool adiciona ceremonia, nao capacidade | Nada |

Regra geral: **antes de instalar, pergunte se uma tool nativa ja resolve.** Se resolve, o
MCP e custo puro.

## 6. Segredos e escopo

### Onde a credencial mora

Ordem de preferencia:

1. **OAuth** (github, figma remoto, supabase, vercel, notion, sentry). O token nunca toca
   arquivo de config — fica no cofre do Claude Code. Autorize com `/mcp` ou
   `claude mcp login <nome>`. **Prefira sempre este caminho.**
2. **Bloco `env` do `.claude/settings.local.json`** quando o servidor exige token na mao.
   Esse arquivo esta no `.gitignore` deste repo, e o `env` de um arquivo de settings vale
   para a sessao e todo subprocesso — inclusive os servidores MCP.
3. **Nunca** valor literal dentro de `.mcp.json`. Esse arquivo e versionado.

O `.mcp.json` expande `${VAR}` e `${VAR:-default}` nos campos `command`, `args`, `env`,
`url` e `headers`. E o que fecha o circuito: **o segredo mora no
`settings.local.json` (ignorado pelo git) e o `.mcp.json` so carrega o nome da variavel.**

`.claude/settings.local.json`:

```json
{
  "env": {
    "ALGUM_TOKEN": "valor-real-que-nunca-vai-pro-git"
  }
}
```

`.mcp.json`:

```json
{
  "mcpServers": {
    "exemplo": {
      "type": "http",
      "url": "https://exemplo.com/mcp",
      "headers": { "Authorization": "Bearer ${ALGUM_TOKEN}" }
    }
  }
}
```

> **Atencao**: valores de `env` vindos de arquivo de projeto so passam a valer depois que
> a pasta e marcada como confiavel (workspace trust). Num clone novo, confie na pasta
> antes de estranhar que a variavel nao expandiu.

### Qual escopo usar

| Escopo | Flag | Onde grava | Quando |
|---|---|---|---|
| **local** | `-s local` (padrao) | `~/.claude.json`, entrada do projeto | Teste rapido, MCP experimental |
| **project** | `-s project` | `.mcp.json` na raiz, **versionado** | Ferramenta amarrada ao projeto: supabase, figma, mobile, playwright |
| **user** | `-s user` | `~/.claude.json`, topo | Ferramenta transversal: github, context7, vercel, google |

`.mcp.json` **deve** ser versionado — e o ponto dele. Como so contem `${VAR}`, nao vaza
segredo. Controle quais servidores do `.mcp.json` sao aprovados com
`enabledMcpjsonServers` / `disabledMcpjsonServers` no `settings.json`.

## 7. Arquivo de exemplo

`.mcp.json.example` na raiz deste repo traz o nucleo comentado. Uso:

```bash
cp .mcp.json.example .mcp.json
# apague os servidores que o projeto nao usa (regra das secoes 1 e 2)
```

O `.example` existe justamente para nao ligar nada por padrao. Um `.mcp.json` completo
num projeto backend liga mobile e figma a toa.

> `.mcp.json` e **JSON estrito**: nao aceita comentario `//` nem virgula sobrando. Como
> nao ha sintaxe de comentario, o `.example` concentra as notas num bloco `_notas` no topo,
> fora de `mcpServers`. **Apague o bloco `_notas` ao copiar** — ele nao faz parte do schema
> e chave desconhecida pode reprovar na validacao.

## 8. Revalidacao

O ecossistema MCP troca nome de pacote e transporte em questao de meses. Comando
desatualizado e pior que ausencia de doc.

- Toda ficha tem **Verificado em**.
- **Revalide a cada 3 meses** ou quando um comando falhar.
- Ao revalidar: confira o comando na fonte oficial, atualize `verificado_em` na referencia
  correspondente em `referencias/`, atualize a data aqui e registre no changelog.
- Fonte da verdade e sempre a doc oficial do servidor, nunca este arquivo.

## 9. Referencias

- [[HOOKS|HOOKS.md]] — regras injetadas por prompt
- [[CONVENCOES|CONVENCOES.md]] — schema de frontmatter
- [[referencias/README|referencias/]] — ficha tecnica de cada MCP
- [[decisoes/2026-09-06_catalogo_mcps|Decisao: catalogo de MCPs]]

## 10. Changelog

| Data | Mudanca | Motivo |
|------|---------|--------|
| 2026-09-06 | Versao inicial do catalogo (8 no nucleo, 4 opcionais, 6 anti-recomendacoes) | Template nao orientava escolha de MCP; cada projeto derivado improvisava |
