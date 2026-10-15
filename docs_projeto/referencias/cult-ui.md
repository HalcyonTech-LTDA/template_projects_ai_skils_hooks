---
title: Cult UI — registry shadcn com ilustracoes e componentes animados
source: https://pro.cult-ui.com/illustrations
type: referencia
status: aprovado
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, frontend, componentes, react, shadcn, tailwind, tema/tooling]
---

# Cult UI

Registry shadcn de componentes, blocos e ilustracoes animadas. Repositorio
`nolly-studio/cult-ui`, **licenca MIT**, ativo (push em 2026-10-14).

## Pro acabou — e virou gratis

`pro.cult-ui.com` **nao vende mais.** O autor nao vai criar novos templates, blocos ou
componentes Pro. Os **58 componentes Pro ja estao gratis no registry**, 137 componentes ao
todo (o `registry.json` lista 307 itens contando demos e aliases).
Ou seja: as ilustracoes da URL citada se instalam pelo registry publico, sem compra.

## Stack

- **Tailwind** + `motion` + Base UI (alguns com Radix Slot, Sonner, shaders da Paper Design, COBE)
- O CLI instala as dependencias npm e os componentes shadcn base que cada item usa

## Instalacao

```bash
npx shadcn@latest add @cult-ui/folded-card
```

Indice: `https://www.cult-ui.com/r/registry.json` e `https://www.cult-ui.com/llms.txt`
(cada componente tem pagina `.md` em `https://www.cult-ui.com/docs/components/<nome>.md`).

## O que aproveitar

- **Ilustracoes SVG**: `gateway-*-illustration`, `illustration-graph`, `illustration-globe-vercel`,
  `illustration-cursor`, `illustration-comment-bubble`, `fluid-ai-workloads`, `security-checkpoint`
- **Device frames**: `apple-iphone-17-pro`, `apple-watch-ultra`, `apple-pro-display-xdr`,
  `apple-keyboard`, `mac-screen`, `mock-browser-window`
- **Produto**: `kanban-board`, `sortable-list`, `wizard-expandable`, `onboarding`,
  `code-block`, `copy-button`, `rolling-number`
- **Cards sem efeito de brilho**: `folded-card`, `organic-card`, `shadow-card`, `cutout-card`, `minimal-card`

## O que e vetado

Parte do catalogo e exatamente a assinatura visual de output de IA: feixe na borda, brilho,
gradiente animado, vidro fosco. Decisao 2026-10-15: vetados nominalmente — lista em
`.claude/skills/_shared/fontes-frontend.md`, secao 4. Resumo: `border-beam-*`, `grid-beam`,
familia `halo-*` (menos `halo-field`) e seus aliases `animated-*`, `cosmic-button`,
`metal-button`, `gradient-*`, `bg-animated-gradient`, `bg-animate-button`, `circuit-board`,
`distorted-glass`.

Note que a familia `halo-*` cobre quase todos os controles de formulario do Cult. Para
controles, use Arc ou o shadcn base.

## Fontes

- https://pro.cult-ui.com/illustrations
- https://pro.cult-ui.com/pricing
- https://www.cult-ui.com/docs
- https://github.com/nolly-studio/cult-ui
