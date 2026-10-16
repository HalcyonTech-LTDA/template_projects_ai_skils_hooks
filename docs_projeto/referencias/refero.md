---
title: Refero — acervo de telas e fluxos reais
source: https://refero.design
type: referencia
status: aprovado
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, frontend, design, pesquisa, tema/tooling]
---

# Refero

Biblioteca de referencia de UI: telas, fluxos e estilos extraidos de produtos reais.
**Nao fornece componentes nem codigo.** No protocolo do projeto, e a fonte do passo
"pesquisa" — ver `.claude/skills/_shared/fontes-frontend.md`.

## O que tem

Numeros do proprio fornecedor, sem auditoria independente:

- **150.000+ telas** de produtos reais (web e iOS)
- **6.000+ fluxos** de varios passos (onboarding, checkout, cancelamento)
- **Estilos**: referencia semantica extraida de paginas de marketing/produto — tese visual,
  tokens, tipografia, ritmo de secao, regras de faca/nao faca. Cobrem paginas de marketing;
  **nao** cobrem dashboard, auth, settings nem telas iOS como sistema de estilo

## Planos

- Gratuito: so parte do acervo (uma listagem de terceiro fala em ~3%)
- MCP exige plano pago (Pro, Team ou Lifetime). Precos divergem entre fontes; conferir em
  `https://refero.design/pricing` antes de assinar

## MCP

- URL: `https://api.refero.design/mcp` (Streamable HTTP, OAuth ou `Authorization: Bearer`)
- Limite: **8.000 chamadas por mes por usuario licenciado**, sem acumular
- Setup no Claude Code:

```bash
claude mcp add --transport http refero https://api.refero.design/mcp
```

Tools: `refero_search_site`, `refero_search_app`, `refero_search_styles`, `refero_get_style`,
`refero_search_screens`, `refero_get_screen`, `refero_get_similar_screens`,
`refero_get_screen_image`, `refero_search_flows`, `refero_get_flow`.

**Decisao 2026-10-15: o projeto nao usa o MCP** (sem plano pago). Pesquisa pelo site via
navegador.

## Armadilha: WebFetch nao le o site

`refero.design` e renderizado por JS. WebFetch devolve so o `<title>`. Para pesquisar sem o
MCP, use Playwright ou Chrome e capture screenshot.

## Refero Skill

Skill `refero-design` (MIT, `referodesign/refero_skill`, v1.0.3 em 2026-10-15). Funciona sem o
MCP como metodo. Fluxo: brief → estilos → telas e fluxos → sintese com "reference lock" e
"decision ledger" → implementacao → QA visual.

**Nao foi instalada.** O metodo foi absorvido em `.claude/skills/_shared/fontes-frontend.md`
para nao somar mais uma skill as 15+ de design que ja colidem por gatilho. A `description`
dela se declara "Primary/default skill for UI design" e manda preteri-la sobre skills
genericas — instalar criaria disputa direta com a arvore de [[../SKILLS|SKILLS.md]].

Ideias aproveitadas:
- **Nao tirar a media**: entre referencias conflitantes, escolher uma dominante
- **Papel do token**: cor de CTA fica em CTA; gradiente decorativo nao vira superficie
- **Toda decisao rastreavel** a uma referencia, restricao ou regra de craft

## Fontes

- https://doc.refero.design/mcp/getting-started
- https://doc.refero.design/mcp/tools
- https://doc.refero.design/skill/overview
- https://github.com/referodesign/refero_skill
