---
title: Arc (uiarc.dev) — componentes React animados
source: https://uiarc.dev
type: referencia
status: aprovado
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, frontend, componentes, react, shadcn, tema/tooling]
---

# Arc (uiarc.dev)

Biblioteca React de componentes e blocos animados, feita para ser usada por agentes.
Distribuida como registry shadcn: o source e copiado para o projeto.

## Numeros

| | Gratis | Pro | Total |
|---|---:|---:|---:|
| Componentes | 111 | 54 | 165 |
| Blocos | 22 | 69 | 91 |

Pro: US$ 199 uma vez ou US$ 129/ano por pessoa. Time: US$ 599 uma vez ou US$ 349/ano (ate 10).
Catalogo completo com marcacao Pro: `https://uiarc.dev/r/catalog.json`.

## Stack — o ponto que importa

- **CSS modules + variaveis CSS. Nao usa Tailwind**
- Animacao com `motion` e presets proprios (`snappy`, `smooth`, `morph`)
- Ramo de `prefers-reduced-motion` em todo componente
- Arquivos vao para `components/arc/`

## Instalacao

```bash
npx shadcn@latest add https://uiarc.dev/r/arc-foundation.json   # tokens, uma vez por app
npx shadcn@latest add https://uiarc.dev/r/button.json
```

Por nome, com o namespace em `components.json`:

```json
{ "registries": { "@uiarc": "https://uiarc.dev/r/{name}.json" } }
```

```bash
npx shadcn@latest add @uiarc/button @uiarc/dialog
```

Pro: registry `@uiarc-pro` com header `Authorization: Bearer ${ARC_PRO_TOKEN}`.
Tokens no layout raiz: `import "@/components/arc/foundation.css";`
Tema: `data-theme="dark"` no `<html>`; acento por `data-accent`.

## Colisao com shadcn / Tailwind

Os tokens semanticos do Arc — `--background`, `--surface`, `--foreground`, `--text-secondary`,
`--border`, `--accent`, `--success`, `--warning`, `--danger` — **tem os mesmos nomes** de
varios tokens do shadcn. Num projeto com os dois, o que for importado por ultimo vence, sem
erro. E o tema escuro usa `data-theme` no Arc e classe `.dark` no shadcn.
Regra de convivencia em `.claude/skills/_shared/fontes-frontend.md`, secao 3.

## Regras para agentes (do proprio Arc)

- Prefira componente ou bloco Arc existente a escrever um novo
- Leia o `.md` do componente; so props documentadas
- Tokens semanticos em vez de cor crua; conferir tema claro e escuro
- Sentence case, so pesos regular e medium, sem eyebrow, sem travessao,
  **sem gradiente ou brilho decorativo**
- Nunca reconstruir o source de um item Pro

## MCP

`https://uiarc.dev/api/mcp` — Streamable HTTP, tools de list/search/get/install/skill.
OAuth com conta Arc; conta gratis basta. Docs: `https://uiarc.dev/docs/ai`.
**Nao esta no catalogo de [[../MCPS|MCPS.md]].** Avaliar contra o limite de 3 a 6 servidores.

## Licenca

- Gratis: **MIT** — manter o aviso de copyright, inclusive ao portar para outro stack
- Pro: projetos ilimitados, entrega a cliente permitida, **uma licenca por pessoa**.
  Proibido redistribuir o source isolado e proibido usar em **UI kit, biblioteca ou
  template**. Portanto: **nunca commitar item Pro em `template_projetos`**
- O texto da licenca estava marcado como rascunho em 2026-10-15

## Fontes

- https://uiarc.dev/llms.txt
- https://uiarc.dev/license
