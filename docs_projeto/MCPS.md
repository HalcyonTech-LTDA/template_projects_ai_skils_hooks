---
title: Catalogo de MCPs para desenvolvimento
type: convencao
status: aprovado
created: 2026-09-06
updated: 2026-10-15
project: template_projetos
tags: [convencao, mcp, ferramentas, claude-code, tema/tooling]
---

# Catalogo de MCPs para desenvolvimento

Quais servidores MCP ligar num projeto derivado deste template, **quando ligar cada um
e quando desligar**. As fichas do nucleo, com comando copiavel, escopo recomendado,
custo de contexto e data de verificacao, estao em [[MCPS_NUCLEO|MCPS_NUCLEO.md]].

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

Comando de instalacao, credencial, limites e armadilhas de cada um estao em
[[MCPS_NUCLEO|MCPS_NUCLEO.md]]. Aqui fica so o que serve para decidir.

| MCP | Escopo | Custo de contexto | Ligue quando | Ficha |
|---|---|---|---|---|
| **GitHub** | `user` | Alto (~50 tools) | PR, issue, review, busca cross-repo | [[MCPS_NUCLEO#1. GitHub\|1]] |
| **Figma** | `project` | Baixo | Tela a partir de design (rode `whoami` antes: Starter = 20 leituras/mes) | [[MCPS_NUCLEO#2. Figma\|2]] |
| **mobile-next** | `project` | Medio-alto (~30) | Fluxo em device, bug mobile. No Windows, so Android | [[MCPS_NUCLEO#3. mobile-next (mobile-mcp)\|3]] |
| **Playwright** | `project` | Medio (~25) | E2E, verificacao pre-release, bug de UI web | [[MCPS_NUCLEO#4. Playwright (teste de aplicacao web)\|4]] |
| **Terminator** | `project` | Alto (50+) | App desktop Windows. O mais caro do catalogo | [[MCPS_NUCLEO#5. Terminator (teste de aplicacao desktop)\|5]] |
| **Supabase** | `project` | Medio | Schema, migracao, RLS. Nunca em producao | [[MCPS_NUCLEO#6. Supabase\|6]] |
| **Vercel** | `user`/`project` | Medio-baixo | Build quebrado, deploy que nao subiu | [[MCPS_NUCLEO#7. Vercel\|7]] |
| **Google Workspace** | `user` | Alto | Ata, requisito por e-mail, planilha. Le o e-mail inteiro | [[MCPS_NUCLEO#8. Google Workspace\|8]] |

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

### 4.1 KiCad (experimental, fora do nucleo)

| | |
|---|---|
| **O que faz** | Edita esquematico e placa do KiCad por conversa, com a GUI aberta |
| **Escopo** | `local` — so na sessao exploratoria, desligar ao terminar |
| **Custo de contexto** | **Muito alto** — 240+ tools (`mixelpixx/KiCAD-MCP-Server` ~244; `oaslananka/kicad-mcp-pro` ~241, com perfil `minimal`) |
| **Verificado em** | 2026-10-12 |
| **Referencia** | [[referencias/kicad-mcp-e-skills]] |

Nao entra no nucleo: sozinho estoura a regra de 3 a 6 servidores da secao 1. A familia de
skills `pcb-*` faz o mesmo trabalho com `kicad-cli` e scripts proprios, sem custo de contexto
e com prova pelo ERC/DRC (ver [[SKILLS]], secao 7). Se for testar, prefira o `kicad-mcp-pro`
(mira o KiCad 10; exige Python 3.13+ via `uvx`) com perfil `minimal`. O `copperhead` tambem
expoe um MCP stdio, experimental e instavel, com poucas tools de alto nivel; mesma regra
(ver [[referencias/copperhead]]).

### 4.2 REA — engenharia reversa (sob demanda, fora do nucleo)

| | |
|---|---|
| **O que faz** | Engenharia reversa de binario nativo, Electron, .NET, APK, firmware, WASM e site |
| **Escopo** | `local` — so na pasta da investigacao, remover ao terminar |
| **Custo de contexto** | **Alto** — catalogo de tools extenso, gerado por versao |
| **Comando (Windows)** | `claude mcp add --scope local rea -- cmd.exe /d /c npx -y rea-agents@6.5.0 mcp` |
| **Verificado em** | 2026-10-15 |
| **Referencia** | [[referencias/rea-engenharia-reversa]] |

Nao rode `npx rea-agents setup`: ele registra no escopo `user` e instala a skill em
`~/.claude/skills/`, ligando o REA em todo projeto. Binario nativo exige Ghidra, IDA ou
Hopper, instalados por conta propria; no Windows o Ghidra e experimental.

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

- Toda ficha em [[MCPS_NUCLEO|MCPS_NUCLEO.md]] tem **Verificado em**.
- **Revalide a cada 3 meses** ou quando um comando falhar.
- Ao revalidar: confira o comando na fonte oficial, atualize `verificado_em` na referencia
  correspondente em `referencias/`, atualize a data na ficha e registre no changelog daqui.
- Fonte da verdade e sempre a doc oficial do servidor, nunca este arquivo.

## 9. Referencias

- [[MCPS_NUCLEO|MCPS_NUCLEO.md]] — fichas do nucleo: comando, credencial, limites, armadilhas
- [[HOOKS|HOOKS.md]] — regras injetadas por prompt
- [[CONVENCOES|CONVENCOES.md]] — schema de frontmatter
- [[referencias/README|referencias/]] — ficha tecnica de cada MCP
- [[decisoes/2026-09-06_catalogo_mcps|Decisao: catalogo de MCPs]]

## 10. Changelog

| Data | Mudanca | Motivo |
|------|---------|--------|
| 2026-09-06 | Versao inicial do catalogo (8 no nucleo, 4 opcionais, 6 anti-recomendacoes) | Template nao orientava escolha de MCP; cada projeto derivado improvisava |
| 2026-09-27 | Figma revalidado: limite de chamadas por plano e seat, `whoami` antes de planejar e escrita no canvas em beta | A ficha dizia "qualquer seat e plano", mas o Starter para em 20 leituras por mes |
| 2026-10-12 | MCP de KiCad avaliado e registrado como experimental (secao 4.1), fora do nucleo | Pedido de skill de PCB; 240+ tools contrariam a regra de 3 a 6, e a familia `pcb-*` cobre o uso |
| 2026-10-15 | Fichas da secao 3 movidas para `MCPS_NUCLEO.md`; aqui ficou uma tabela-resumo | O arquivo tinha 354 linhas e o teto de documentacao passou a ser 300 (`CONVENCOES.md` secao 7) |
| 2026-10-15 | `copperhead` citado na secao 4.1 (MCP stdio experimental), fora do nucleo | Referencia para a familia `pcb-*`; pre-1.0 e com LLM proprio |
| 2026-10-15 | REA (`morluto/rea`) registrado como MCP sob demanda (secao 4.2), escopo `local` | Referencia para engenharia reversa; o `setup` oficial liga o servidor em todo projeto |
