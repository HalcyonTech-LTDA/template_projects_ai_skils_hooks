---
title: Catalogo de skills e precedencia de design
type: convencao
status: aprovado
created: 2026-09-07
updated: 2026-10-10
project: template_projetos
tags: [convencao, skills, design, claude-code, tema/tooling]
---

# Catalogo de skills e precedencia de design

Este repositorio carrega **50 skills** em `.claude/skills/`. Diferente dos MCPs, skill
nao custa contexto por sessao: so a `description` de cada uma entra no prompt, e o corpo
so e lido quando a skill dispara. O custo real e outro — **colisao de gatilho**: com 20+
skills descrevendo "design de interface", o modelo escolhe uma diferente a cada sessao e
o resultado deixa de ser reproduzivel.

Este documento resolve isso. Ele **nao** e uma lista de instalacao; e a ordem de
precedencia que o agente deve seguir quando mais de uma skill parece caber.

> **Este arquivo e a fonte canonica.** Assim como `.claude/skills/` e `MCPS.md`, correcao
> comeca aqui e desce por copia para os projetos derivados.

## 1. A regra: uma skill estetica por tarefa

As skills de direcao de arte sao **mutuamente exclusivas**. Carregar `minimalist-ui` e
`industrial-brutalist-ui` na mesma tarefa produz output incoerente — uma proibe gradiente
e sombra pesada, a outra pede degradacao analogica e contraste extremo de escala.

Escolha **uma** e siga ate o fim. Skills de processo (seção 4) podem acumular.

## 2. Arvore de decisao

Leia de cima para baixo; para na primeira que casar.

| Se a tarefa e... | Use | Por que nao a de baixo |
|---|---|---|
| Redesign / auditoria de projeto **que ja existe** | `redesign-existing-projects` | Ela audita antes de mexer. As outras assumem folha em branco e reescrevem o que funcionava |
| O usuario **nomeou** o estilo (minimalista, brutalista, "caro") | `minimalist-ui` / `industrial-brutalist-ui` / `high-end-visual-design` | Style lock explicito vence inferencia. `design-taste-frontend` iria inferir outra direcao |
| Landing page, portfolio, site de marketing | `design-taste-frontend` | E a default v2: le o brief e infere a direcao. Nao use as tres acima sem o usuario pedir |
| Motion pesado, GSAP, ScrollTrigger, pin/scrub | `gpt-taste` | Unica com esqueleto de codigo GSAP e estrutura AIDA |
| Dashboard, tabela de dados, UI de produto multi-step | `ui-ux-pro-max` | `design-taste-frontend` **se exclui** disso explicitamente ("not dashboards, not data tables") |
| Componente isolado ou artifact claude.ai | `frontend-design` + `artifacts-builder` | Skills de landing page trazem estrutura de pagina inteira que sobra aqui |
| Tokens, escala tipografica, handoff para dev | `ui-design-system` | Ortogonal — pode combinar com a estetica escolhida |
| App mobile (RN / nativo) | `mobile-design` | As taste-skills sao web-first |
| Cena 3D / WebGL | `3d-web-experience` | — |
| Texto de venda, headline, CTA | `copywriting` | — |

## 3. Skills que exigem gerador de imagem — inertes hoje

Quatro skills do pacote `taste-skill` assumem que o agente **gera imagens**:

| Skill | Estado neste stack |
|---|---|
| `imagegen-frontend-web` | **Inerte.** So gera imagem, nao escreve codigo |
| `imagegen-frontend-mobile` | **Inerte.** Idem, para telas mobile |
| `brandkit` | **Inerte.** Board de identidade visual, so imagem |
| `image-to-code` | **Degradada.** Escrita para o Codex; o passo "gere a imagem de referencia primeiro" nao roda aqui. Sobra a parte de analise/implementacao |

O catalogo de MCPs (`MCPS.md`) **nao tem servidor de geracao de imagem**. Enquanto isso
nao mudar, essas quatro nao devem ser invocadas — foram instaladas por decisao de manter
o pacote upstream integro, nao porque funcionam.

Se algum dia entrar um MCP de imagem no catalogo, revisite esta secao.

## 4. Skills de processo — acumulam

Estas nao competem com as esteticas e podem rodar junto:

- `full-output-enforcement` — proibe placeholder e `// resto do codigo aqui`. Util em
  geracao longa; e o antidoto direto para truncamento
- `clean-code`, `software-architecture`, `code-reviewer`, `systematic-debugging`
- `react-best-practices`, `nextjs-best-practices`, `tailwind-patterns`,
  `web-performance-optimization`
- `commit`, `worktree` — fluxo de entrada de trabalho no repo
- `issue` — conduz uma issue pelo tamanho, escolhendo subagente e modelo; usa `commit` e
  `worktree` por dentro. Catalogo dos agentes em [[AGENTES]]

## 5. Casos especiais

- **`stitch-design-taste`** nao produz UI: produz um `DESIGN.md` para o Google Stitch
  consumir. So use se o projeto de fato passa pelo Stitch.
- **`design-taste-frontend-v1`** existe so para compatibilidade. A v2 e uma reescrita.
  Nao invoque a v1 sem motivo explicito; ela vai divergir da v2 no mesmo brief.

## 6. Politica de upstream: fork proprio

As 13 skills do pacote `Leonxlnx/taste-skill` foram copiadas uma vez e **nao seguem o
upstream**. Nao rode `npx skills update` neste repositorio.

Motivo: o autor declara a v2 como "experimental, actively iterating". Um update silencioso
mudaria o comportamento do agente em 8 repositorios sem revisao.

O `skills-lock.json` na raiz e versionado como **registro de procedencia** (origem, caminho
no upstream, hash do conteudo instalado) — nao como mecanismo de atualizacao. Para trazer
mudanca do upstream, faca deliberadamente: leia o diff, decida, e propague por copia.

Ficha da referencia em [[referencias/skills-taste-leonxlnx]].
