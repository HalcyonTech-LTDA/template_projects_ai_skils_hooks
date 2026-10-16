---
title: Galerias de secao — navbar, footer, CTA, 404, bento, secoes e motion
source: https://navbar.gallery, https://footer.design, https://cta.gallery, https://404s.design, https://unsection.com, https://bentogrids.com, https://60fps.design, https://scrolltide.co
type: referencia
status: aprovado
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, frontend, design, pesquisa, tema/tooling]
---

# Galerias de secao

Oito acervos citados pelo usuario como referencia de design. Sete sao **galerias de
captura de sites reais, organizadas por tipo de secao**. Nenhum deles entrega codigo
reaproveitavel. O oitavo, scrolltide, e um produto pago de prompt e template.

No protocolo (`.claude/skills/_shared/fontes-frontend.md`, passo 2), elas sao o degrau
**"galeria da secao"**. Servem a camada **Tela** quando a pergunta e "como sites reais
resolvem *este* bloco". Nao servem para direcao visual da pagina inteira: isso continua
com o Refero e com os produtos do brief.

## Resumo

| Site | Secao | Acesso | Leitura | No degrau? |
|---|---|---|---|---|
| [navbar.gallery](https://navbar.gallery) | Navbar | Gratis | WebFetch le | Sim |
| [footer.design](https://footer.design) | Footer | Gratis | WebFetch le | Sim |
| [cta.gallery](https://cta.gallery) | CTA | Gratis, vive de patrocinio | WebFetch le | Sim, como secundaria |
| [404s.design](https://404s.design) | Pagina 404 | Gratis | WebFetch le | Sim |
| [unsection.com](https://unsection.com) | Secoes inteiras (13 tipos) | Gratis com cadastro | WebFetch le | Sim |
| [bentogrids.com](https://bentogrids.com) | Bento grid | Gratis | **So navegador** (JS) | Sim |
| [60fps.design](https://60fps.design) | Micro-interacao, motion | Parte gratis; acervo completo pago | WebFetch le | Sim, so parte gratis |
| [scrolltide.co](https://scrolltide.co) | Scroll-driven, 3D, shaders | **Pago** | WebFetch le a home | **Nao** — so ficha |

## Por site

### navbar.gallery

Galeria de navbars de sites reais, em 38 paginas de cerca de 13 itens. Filtra por tipo:
Static, Dropdown, Mega Menu, Side Bar, Search Bar, Announcement, Full Screen e Breadcrumbs.
Autora: Christina Liubynska (supercharged.design). Patrocinio da Mobbin.

### footer.design

Galeria de rodapes reais, em 65 paginas. Filtra por estilo: Typographic, Small Type,
Illustrative, Grid, Flat, Animated, Cards, Bright, Dark, Large Type e Bold. Site do estudio
NOOON (nooon.studio). Tem anuncio patrocinado.

### cta.gallery

Galeria de CTAs. Filtra por categoria: Button, Call-to-Buy, Download, Form, Modal,
Navigation, Newsletter e Pricing. O total nao e declarado; a home lista 35 itens recentes e um
"Load More". **Aviso:** dono nao declarado, e o link "Templates" leva a terceiros
patrocinados. Para CTA, comece pela categoria CTA do unsection e use esta como segunda fonte.

### 404s.design

Paginas 404 de sites reais. Tem os melhores filtros dos oito: Style (16), Interaction (6,
incluindo Custom Cursor, Game e Scroll-driven) e Industry (8). Patrocinio da Mobbin.

### unsection.com

O maior acervo: cerca de 5.197 secoes de sites. O numero aparece ao lado de "Website" e o
site nao diz o que ele conta. Categorias: Hero, Testimonials, Feature, CTA, Footer, Blog,
Navbar, Pricing, Logo, FAQs, Team, Contact e Portfolio, com filtro de Style e Type. O cadastro
e gratis. **Aviso:** a aba `/templates` e vitrine da shadcnblocks (15 templates Framer e
Webflow a US$79, mais 1 gratis), sem licenca na pagina. Use a galeria; os templates estao
fora do protocolo.

### bentogrids.com

Galeria de bento grids, com cerca de 285 itens na carga inicial. Filtra por categoria
(Discover, Graphic Design, Web Design, Animation) e por tema (claro ou escuro). Cada item tem
o link "Go to source". **Aviso:** o acervo mistura sites reais (Stripe, Raycast, Vercel,
Clerk, Tailwind UI) com shots do Dribbble, branding e templates de Figma. Conceito do Dribbble
nao e produto real. Use o filtro **Web Design** e prefira itens que apontam para um site em
producao.

**Armadilha:** o WebFetch devolve so o `<title>`. Pesquise pelo Playwright ou pelo Chrome.
Conferido no navegador em 2026-10-15.

### 60fps.design

Videos de animacao e interacao, nao capturas estaticas. A home conta 2.110 shots de 494 apps,
93 sites de app, 83 de motion, 67 storyboards e 20 snippets. Tem 108 filtros, divididos em
Gestures, Patterns, Effects, Elements e Categories (exemplos: Spring Physics, Bottom Sheet).

- **Foco em iOS.** Use para o detalhe do movimento (curva, duracao, gatilho), nao como layout
  web
- Explorar e gratis. O acervo completo custa US$15/mes ou US$150/ano por assento ([/pro](https://60fps.design/pro))
- Tem MCP proprio e pago, separado do Pro: US$29/mes. Pesquisa cerca de 2.000 interacoes iOS
  e devolve codigo SwiftUI ([/mcp](https://60fps.design/mcp)). **Nao usado** pelo mesmo
  criterio do Refero (plano pago), e porque SwiftUI nao serve ao stack web. Se um projeto
  derivado for iOS nativo, reavaliar

### scrolltide.co — so ficha, fora do degrau

Biblioteca de templates e prompts de sites scroll-driven. A home lista 121 templates, 66
componentes, 55 shaders, 19 secoes e 14 telas, cerca de 275 itens. O stack declarado e React,
Vite, Next.js, Tailwind, Framer Motion, GSAP, Three.js, WebGL e Lenis.

- **A alegacao "600+ prompts" nao se confirma.** Nao ha fonte para o numero
- **Pago** ([/pricing](https://scrolltide.co/pricing)): US$29/mes, US$108/ano ou US$239
  vitalicio. Venda final. Sao gratis 4 templates (Glacier, Fluxora, Monsoon e Aurora), em
  [/free](https://scrolltide.co/free)
- "Prompt com source completo" **nao foi confirmado**. A pagina de precos fala em "full source
  code", mas a `/free` descreve um prompt para colar no Claude, Cursor ou v0. Nenhum prompt
  real foi visto
- **Licenca** ([/terms](https://scrolltide.co/terms) secao 3): pessoal, intransferivel e
  valida so com o plano ativo. Proibe redistribuir template ou prompt, inteiro ou modificado
- Dono nao declarado; o rodape cita o handle `himanshubuilds`. Sem `llms.txt`

**Decisao do usuario: so referencia.** Olhe os previews da home e os 4 templates gratis pelo
efeito. Nao cole o prompt: prompt pronto e decidir sem olhar, que e o que o protocolo combate.
Tambem nao vale como fonte de codigo, por tres motivos:

- Ficou fora do degrau por ser pago
- A licenca proibe redistribuir, entao **nada dele entra neste template nem nos projetos
  derivados como base reutilizavel**
- Efeito de aurora ou brilho cai no criterio de vetados da secao 4 do protocolo

## Regras de uso

- **Galeria mostra o bloco, nao a pagina.** Um footer do footer.design pode ser a
  referencia secundaria do lock (passo 3, "emprestar so"), mas nunca a principal
- **O link de origem vence a captura.** Quando a secao for decidir o lock, abra o site real:
  a captura pode estar desatualizada, e no site se ve o comportamento responsivo e o motion
- **Nenhuma delas fornece codigo.** O componente continua vindo de Arc ou Cult (passo 4) ou e
  escrito do zero
- Contagens, precos e patrocinios sao do proprio site e foram lidos em 2026-10-15. Confira de
  novo antes de citar

## Fontes

Lidas por WebFetch em 2026-10-15, exceto o bentogrids, lido pelo Playwright. O WebFetch
devolve um resumo, entao os trechos entre aspas nao foram conferidos palavra por palavra.

- https://navbar.gallery
- https://footer.design
- https://cta.gallery
- https://404s.design
- https://unsection.com, https://unsection.com/templates
- https://bentogrids.com
- https://60fps.design, https://60fps.design/pro, https://60fps.design/mcp
- https://scrolltide.co, https://scrolltide.co/pricing, https://scrolltide.co/free, https://scrolltide.co/terms
