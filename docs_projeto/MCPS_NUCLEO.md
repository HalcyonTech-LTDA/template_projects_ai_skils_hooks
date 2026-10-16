---
title: Fichas do nucleo de MCPs
type: convencao
status: aprovado
created: 2026-09-06
updated: 2026-10-15
project: template_projetos
tags: [convencao, mcp, ferramentas, claude-code, tema/tooling]
---

# Fichas do nucleo de MCPs

Comando, escopo, custo de contexto e quando ligar ou desligar cada servidor do nucleo.
Qual escolher para cada perfil de projeto esta no indice [[MCPS|MCPS.md]]; o detalhe
tecnico de cada servidor esta em [[referencias/README|referencias/]].

> Separado de `MCPS.md` em 2026-10-15 para respeitar o teto de 300 linhas
> ([[CONVENCOES|CONVENCOES.md]] secao 7). Mesma fonte canonica: correcao comeca aqui.

## 1. GitHub

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

## 2. Figma

| | |
|---|---|
| **O que faz** | Extrai codigo, variaveis, tokens e specs do frame selecionado |
| **Escopo** | `project` — so faz sentido em projeto com design |
| **Custo de contexto** | **Baixo** — punhado de tools |
| **Credencial** | Remoto: OAuth. Desktop: nenhuma, mas exige seat Dev/Full em plano pago |
| **Limite** | Leituras: Starter 20/mes; View/Collab pago 6/mes; Dev/Full pago de 200/dia (Pro) a 600/dia (Enterprise) |
| **Verificado em** | 2026-09-27 |
| **Referencia** | [[referencias/mcp-figma]] |

```bash
# Remoto (preferido — qualquer seat e plano, mas veja o limite)
claude mcp add -s project -t http figma https://mcp.figma.com/mcp

# Desktop (alternativa; exige app Figma aberto em Dev Mode com o servidor ligado)
claude mcp add -s project -t http figma-desktop http://127.0.0.1:3845/mcp
```

- **Antes de planejar** um ciclo de design para codigo, rode a tool `whoami`, que nao gasta
  chamada. No Starter, 20 leituras por mes nao sustentam o ciclo.
- **Ligue** ao implementar tela a partir de design.
- **Desligue** depois que a tela saiu do Figma — ele nao ajuda em logica de negocio.
- **Casa com** as skills `frontend-design`, `ui-ux-pro-max` e `ui-design-system` do repo.
- **Armadilha**: o servidor desktop morre junto com o app Figma. Se as tools somem do
  `/mcp`, o Figma fechou.

## 3. mobile-next (mobile-mcp)

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

## 4. Playwright (teste de aplicacao web)

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

## 5. Terminator (teste de aplicacao desktop)

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

## 6. Supabase

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

## 7. Vercel

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

## 8. Google Workspace

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
