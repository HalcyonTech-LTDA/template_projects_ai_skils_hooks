---
title: Adocao do pacote taste-skill e criacao do catalogo de skills
type: decisao
status: aprovado
created: 2026-09-07
updated: 2026-09-07
project: template_projetos
tags: [decisao, skills, design, tema/tooling]
---

# 2026-09-07 — Pacote taste-skill e catalogo de precedencia

## O que mudou

1. As **13 skills** de `Leonxlnx/taste-skill` entraram em `.claude/skills/` (36 → 49)
2. `skills-lock.json` passou a ser versionado na raiz, como registro de procedencia
3. Novo [[../SKILLS|docs_projeto/SKILLS.md]] — catalogo e **precedencia** entre skills de design
4. Nova ficha [[../referencias/skills-taste-leonxlnx|referencias/skills-taste-leonxlnx.md]]
5. As 13 foram propagadas para os **7 projetos derivados** com `.claude/skills/`

## Por que

O pedido foi adicionar a "taste-skill". Ao inspecionar, o repositorio traz 13 skills, e o
template ja tinha 6 skills de design concorrendo por gatilho. Instalar sem tratar isso
tornaria a escolha de skill nao-reproduzivel entre sessoes.

Decisao do usuario: instalar as 13 (pacote integro) e **resolver a colisao por documentacao**,
mantendo as `description` originais intactas. Editar description de arquivo de terceiro criaria
divergencia sem ganho, ja que a politica adotada e de fork sem update.

## Alternativas descartadas

- **So a `design-taste-frontend`** — menor superficie, mas perderia `full-output-enforcement`
  e `redesign-existing-projects`, que sao uteis e nao colidem
- **Aposentar `ui-ux-pro-max` / `frontend-design`** — reduziria ruido de verdade, mas as duas
  cobrem dashboard e componente isolado, terreno que a `design-taste-frontend` recusa por escrito
- **Seguir o upstream com `skills update`** — descartado: o autor declara a v2 experimental e em
  iteracao ativa; update silencioso mudaria o comportamento do agente em 8 repositorios

## Consequencias

- **Nao rodar `npx skills update` neste repositorio.** As skills sao fork proprio
- Quatro skills (`brandkit`, `imagegen-frontend-web`, `imagegen-frontend-mobile` e,
  parcialmente, `image-to-code`) estao **inertes**: exigem geracao de imagem, e o catalogo
  de MCPs nao tem servidor de imagem. Se isso mudar, revisar a secao 3 do `SKILLS.md`
- Os 7 projetos derivados receberam as skills **sem commit** — cada um e repositorio
  independente e o commit fica a criterio do dono do repo
