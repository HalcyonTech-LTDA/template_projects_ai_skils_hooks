---
title: beUI — registry shadcn de componentes animados (React e React Native)
source: https://beui.dev
type: referencia
status: aprovado
created: 2026-10-21
updated: 2026-10-21
verificado_em: 2026-10-21
tags: [referencia, frontend, componentes, react, react-native, shadcn, tailwind, motion, tema/tooling]
---

# beUI

Biblioteca copy-paste de componentes animados, distribuida como registry shadcn. Repositorio
`starc007/ui-components`, **licenca MIT**, ativo (push em 2026-10-20, ~1,8 mil estrelas).
Autor: Saurabh (`github.com/starc007`). Existe um **beUI Pro** pago (licenca separada, 300+
blocos); o registry publico e o que vale aqui.

## Stack

- **Web**: React 19, **Tailwind 4** e `motion`. Mesmo terreno do Cult UI
- **beUI Native**: React Native com Reanimated, Gesture Handler e Uniwind. Unico registry
  do protocolo com **codigo** para mobile nativo (Arc e Cult so emprestam o visual)
- Tokens com os nomes do shadcn (`--background`, `--primary`, `--accent`, `--border`...) em
  `oklch`; tema escuro pela classe `.dark` e paleta de cor por `data-theme="<cor>"`
  (`violet`, `blue`, `green`...)

## Catalogo (108 itens no indice em 2026-10-21)

| Categoria | Itens | O que aproveitar |
|---|---|---|
| Components (`motion`) | 54 | Controles com motion de proposito: `select`, `combobox`, `multi-select`, `date-range-picker`, `tabs`, `switch`, `checkbox`, `tooltip`, `context-menu`, `drawer`, `animated-toast-stack`, `table` (virtualizada, 10k+ linhas), `file-tree`, `animated-sidebar`, `number` |
| Charts | 13 | `treemap`, `donut-chart`, `funnel-chart`, `heat-calendar`, `status-bar`; financeiros (`candlestick-chart`, `order-book`) |
| AI Agents | 18 | Interface de chat e agente: `prompt-input`, `message`, `streaming-response`, `tool-approval`, `tool-result`, `file-diff`, `citations`, `agent-activity`, `chat-app` |
| Blocks | 23 | `command-palette`, `notification-stack`, `file-upload`, `otp-input`, `signup-form`, `availability-scheduler`, `not-found` |

O diferencial em relacao a Arc e Cult: a categoria **AI Agents** (nenhum dos dois cobre) e o
**guia de motion** (`https://beui.dev/docs/motion-patterns.md`) — frequencia, proposito,
fisica e fallback de reduced-motion, com faixas de tempo (pressionar 100–160 ms, popover
125–200 ms, modal 200–500 ms; padrao abaixo de 300 ms). Vale como regra de craft mesmo sem
instalar nada.

## Instalacao

```bash
npx shadcn@latest add @beui/animated-toast-stack
# ou pela URL direta
npx shadcn@latest add https://beui.dev/r/animated-toast-stack.json

# React Native
npx beui-native add button
```

Endpoints: `https://beui.dev/llms.txt` (indice em Markdown), `https://beui.dev/r` (catalogo
JSON), `https://beui.dev/r/{slug}` (arquivos, dependencias e source), `/r/{slug}/raw`,
`/registry.json` (formato shadcn) e `https://beui.dev/components/{categoria}/{slug}.md`
(pagina legivel por WebFetch). Native: `https://beui.dev/native/r`.

## O que nao instalar

- **Skill `beui`** (`npx skills add starc007/ui-components --skill beui`). Colide por gatilho
  com as skills de design (ver [[../SKILLS|SKILLS.md]]); o protocolo compartilhado ja diz
  quando usar o registry
- **MCP** `https://mcp.beui.dev/mcp` (tools `list_components`, `search_components`,
  `get_component`, `get_install_command`). Opcional e fora do catalogo de `MCPS.md`: o
  `llms.txt` e o `/r` ja respondem o mesmo por WebFetch, sem custo fixo de contexto

## O que e vetado

Mesmo criterio do Cult: brilho, gradiente animado e vidro fosco sao assinatura de output de IA.
Lista em `.claude/skills/_shared/fontes-frontend.md`, secao 4. Resumo: `shader-background`,
`tilt-card` (reflexo seguindo o cursor), a variante `MetallicButton` do `button` e a varredura
cromatica do `text-animation`. `bottom-sheet` entra, mas com superficie solida no lugar do vidro.

## Fontes

- https://beui.dev
- https://beui.dev/llms.txt
- https://beui.dev/docs/ai-agents.md
- https://beui.dev/docs/motion-patterns.md
- https://github.com/starc007/ui-components
