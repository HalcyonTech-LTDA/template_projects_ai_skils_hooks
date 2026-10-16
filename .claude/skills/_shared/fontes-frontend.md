# Fontes de frontend — protocolo comum

Protocolo obrigatorio para toda tarefa de interface. Lido por quatro skills:
`design-taste-frontend`, `ui-ux-pro-max`, `frontend-design` e `redesign-existing-projects`.
Elas continuam decidindo a estetica; este arquivo decide **de onde vem a evidencia e o
codigo** e **como a entrega e verificada**.

> Fonte canonica: `template_projetos/.claude/skills/_shared/`. Correcao comeca aqui.
> Esta pasta nao e uma skill (nao tem `SKILL.md`) e nao aparece no indice do hook.

O "design de IA" nao vem de falta de componente bonito. Vem de decidir sem olhar nada:
hero centralizado, tres cards, gradiente roxo. Por isso a ordem e fixa —
**referencia antes de codigo, componente pronto antes de componente inventado,
screenshot antes de entregar.**

---

## 1. As tres fontes

| Fonte | O que e | Papel no fluxo |
|---|---|---|
| [Refero](https://refero.design) | Acervo de telas, fluxos e estilos de produtos reais | **Referencia.** Diz o que olhar. Nao fornece codigo |
| [Arc](https://uiarc.dev) | Componentes e blocos React animados. CSS modules + tokens proprios, **sem Tailwind** | **Componente.** Controles, charts, blocos de produto |
| [Cult UI](https://www.cult-ui.com) | Registry shadcn com Tailwind, `motion` e Base UI. Inclui ilustracoes SVG e device frames | **Componente.** Ilustracoes, mockups de device, secoes de marketing |

Fichas completas em `docs_projeto/referencias/` (`refero.md`, `ui-arc.md`, `cult-ui.md`).
As galerias por tipo de secao (navbar, footer, CTA, 404, bento, motion) entram no passo 2,
em `galerias-de-secao.md`.

### Instalacao

```bash
# Arc — tokens uma vez por app, depois os itens
npx shadcn@latest add https://uiarc.dev/r/arc-foundation.json
npx shadcn@latest add @uiarc/button @uiarc/dialog

# Cult UI
npx shadcn@latest add @cult-ui/folded-card
```

Para instalar Arc por nome, registre o namespace em `components.json`:

```json
{ "registries": { "@uiarc": "https://uiarc.dev/r/{name}.json" } }
```

Depois do `arc-foundation`, importe os tokens uma vez no layout raiz:
`import "@/components/arc/foundation.css";`

Catalogo pesquisavel: `https://uiarc.dev/llms.txt` e `https://uiarc.dev/r/catalog.json`
(marca o que e Pro); `https://www.cult-ui.com/llms.txt` e `https://www.cult-ui.com/r/registry.json`.
Cada componente tem uma pagina `.md` legivel por WebFetch.

---

## 2. Protocolo em seis passos

### Passo 1 — Brief

Antes de pesquisar, escreva o brief em cinco linhas. Pergunte so o que mudaria o resultado.

```text
Desenhando [O QUE] para [QUEM] em [PLATAFORMA].
Objetivo: [OBJETIVO PRINCIPAL DO USUARIO].
Tom: [SENSACAO DESEJADA].
Restricoes: [marca existente, stack, acessibilidade, prazo].
Pesquisa: [estilo / telas / fluxo].
```

### Passo 2 — Pesquisa (minimo 2 a 3 referencias nomeadas)

O projeto **nao usa o MCP do Refero** (exige plano pago). A pesquisa segue esta escada;
desca so quando o degrau de cima nao render:

1. **Referencias que o usuario deu** — links, screenshots, produtos citados. Sempre vencem
2. **refero.design pelo navegador** (Playwright ou Chrome). WebFetch devolve pagina vazia:
   o site e renderizado por JS. O plano gratuito mostra so parte do acervo
3. **Galeria da secao** — capturas de sites reais por tipo de bloco (tabela abaixo). Vale
   para a camada **Tela** de uma secao especifica; **nunca** como referencia principal da
   pagina. Abra o link de origem antes de travar o lock
4. **Produtos reais citados no brief ou concorrentes diretos**, capturados por screenshot
5. **Pagina viva do componente no Arc ou no Cult** — vale para o tratamento de um
   componente (estado, motion, densidade), **nunca** como direcao visual da pagina

| Secao | Galeria | Observacao |
|---|---|---|
| Navbar | [navbar.gallery](https://navbar.gallery) | Filtro por tipo (dropdown, mega menu, side bar) |
| Footer | [footer.design](https://footer.design) | Filtro por estilo |
| CTA | [unsection.com](https://unsection.com) (CTA), depois [cta.gallery](https://cta.gallery) | cta.gallery vive de patrocinio |
| Hero, feature, pricing, FAQ, depoimentos | [unsection.com](https://unsection.com) | Maior acervo; ignore a aba de templates pagos |
| Pagina 404 | [404s.design](https://404s.design) | Filtro por estilo, interacao e setor |
| Bento grid | [bentogrids.com](https://bentogrids.com) | So navegador (JS). Filtro **Web Design**: o resto e Dribbble |
| Micro-interacao, motion | [60fps.design](https://60fps.design) | Parte gratis; foco iOS. Curva e duracao, nao layout |

Nenhuma galeria fornece codigo. `scrolltide.co` fica fora do degrau: e pago, e a licenca
proibe redistribuir. Os previews dele servem para olhar o efeito, e o prompt nao entra. Ficha
completa em `docs_projeto/referencias/galerias-de-secao.md`.

Cada referencia precisa sair com nome, link e **o que dela sera aproveitado**.
Sem referencia nomeada, o codigo nao comeca. "Inspirado em boas praticas" nao e referencia.

Busque por camada:
- **Estilo** — direcao visual: tipografia, paleta, densidade, superficies
- **Tela** — padrao concreto: tabela com filtro, empty state, pricing com toggle
- **Fluxo** — jornada de varios passos: onboarding, checkout, cancelamento

### Passo 3 — Reference lock e ledger

Antes de codar, trave a direcao e mostre ao usuario:

```text
Referencia principal: [uma so]
Preservar: [3 a 5 tracos que precisam sobreviver: fundo, tipo, acento, layout, densidade]
Emprestar so: [1 a 2 detalhes de referencias secundarias]
Papel dos tokens: [ex.: acento so em CTA; cor de sintaxe so dentro de codigo]
Rejeitar: [os defaults que diluiriam a direcao]
```

| Decisao | Fonte | Por que |
|---|---|---|
| [paleta / tipo / layout / componente] | [referencia / restricao do usuario / regra de craft] | [motivo concreto] |

Decisao sem fonte nao entra. Pesquise mais, amarre numa restricao, ou remova.

Tres regras de sintese:
- **Nao copie uma referencia.** Estude varias, sintetize uma direcao nova
- **Nao tire a media.** Se uma e escura, outra e acida e outra e serifada, a resposta nao
  e creme + laranja apagado + serifa educada. Escolha uma dominante e preserve os tracos fortes
- **Nao mude o papel do token.** Cor de CTA fica em CTA; gradiente decorativo nao vira superficie

### Passo 4 — Componentes

Ordem de preferencia:
1. Componente ou bloco pronto do Arc ou do Cult
2. Composicao de componentes desses registries
3. Escrever do zero — so quando 1 e 2 nao existem, e dizer isso na entrega

Leia o `.md` do componente antes de usar. So props documentadas.
Nunca reconstrua o source de um item **Arc Pro** a partir de demo ou screenshot.

### Passo 5 — Implementacao

Segue a skill estetica que estiver ativa. Se a implementacao comecar a fugir do lock
(cor mais segura, raio mais suave, secao generica), pare e corrija.

### Passo 6 — Verificacao por screenshot

Feche toda entrega visual com captura real:

1. Rode a pagina e capture em **1440px** e **390px** (Playwright MCP ou skill `webapp-testing`)
2. Ponha cada captura **ao lado da referencia principal** do lock
3. Liste os desvios concretos (ex.: "acento usado como fundo do card", "hero virou centralizado")
4. Corrija e capture de novo

Sem navegador disponivel, **declare na entrega que o passo 6 nao rodou**. Nao finja.

---

## 3. Misturar Arc e Cult no mesmo projeto

**Liberado**, mas os dois colidem em dois pontos que quebram em silencio:

| Colisao | Arc | Cult / shadcn | Como resolver |
|---|---|---|---|
| Nomes de token | `--background`, `--foreground`, `--border`, `--accent` em `foundation.css` | Os **mesmos nomes** em `globals.css` | Um arquivo e o dono dos valores. O que for importado por ultimo vence; escolha de proposito e confira os dois temas |
| Tema escuro | `data-theme="dark"` no `<html>` | Classe `.dark` no `<html>` | O toggle de tema seta **os dois** |

`motion` e dependencia dos dois; uma versao so no `package.json`.

---

## 4. Vetados do Cult UI

Estes componentes **nao entram**. Sao a assinatura visual do output de IA: borda com feixe
animado, brilho, gradiente animado e vidro fosco. O proprio Arc proibe "decorative gradients
or glows" nas regras para agentes.

| Grupo | Componentes |
|---|---|
| Border beam | `border-beam-button`, `border-beam-card`, `border-beam-input`, `grid-beam` |
| Familia halo (aro em gradiente animado + preenchimento fosco) | `halo-badge`, `halo-button`, `halo-card`, `halo-dropzone`, `halo-input`, `halo-notification`, `halo-progress`, `halo-search`, `halo-segmented`, `halo-select`, `halo-switch`, `halo-tabs`, `halo-toast`, `halo-toggle-group` |
| Aliases antigos da familia halo | todos os `animated-*` que o registry marca como "Deprecated alias for halo-*" |
| Gradiente animado | `cosmic-button`, `metal-button`, `gradient-button-group`, `gradient-heading`, `bg-animated-gradient`, `bg-animate-button` |
| Brilho e vidro | `circuit-board`, `distorted-glass` |

`halo-field` (so layout de label, descricao e erro) fica liberado.
Para os controles, use o equivalente do Arc ou o shadcn base.

---

## 5. Projeto sem React — portar o codigo

Os registries sao React. Fora de React, o source serve de base e e portado:

| Destino | Arc | Cult |
|---|---|---|
| Qualquer stack web | CSS module e tokens portam quase intactos (e CSS puro) | Classes Tailwind portam direto se o projeto tem Tailwind |
| Vue | `motion` → `motion-v`; primitivos → Reka UI | Base UI / Radix → Reka UI |
| Svelte | `motion` → transitions do Svelte | Base UI / Radix → Bits UI |
| HTML puro | `motion` → transicao CSS ou Web Animations API | `<dialog>`, atributo `popover`, `<details>` |
| Mobile nativo | So o visual: tokens, espacamento, curvas de motion. Nao o codigo | Idem |

Ao portar: mantenha o ramo de `prefers-reduced-motion`, o comportamento de teclado e o
**aviso de copyright** no topo do arquivo (Arc gratuito e Cult sao MIT; a licenca exige o aviso).
Item Arc Pro nunca vai para template, kit ou biblioteca: a licenca proibe.

---

## 6. MCPs relacionados

| Servidor | Situacao |
|---|---|
| Refero (`https://api.refero.design/mcp`) | **Nao usado.** Exige plano pago; 8.000 chamadas por mes por usuario |
| Arc (`https://uiarc.dev/api/mcp`) | Opcional, gratis com conta (OAuth). Fora do catalogo de `MCPS.md`; avaliar antes de ligar |
| shadcn | Instala dos dois registries pelo namespace. Conta no limite de 3 a 6 servidores por projeto |

---

Passos 1 a 3 e as regras de sintese foram adaptados de
[referodesign/refero_skill](https://github.com/referodesign/refero_skill) v1.0.3 —
MIT License, Copyright (c) 2026 Refero.
