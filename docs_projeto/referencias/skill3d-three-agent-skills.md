---
title: three-agent-skills (emalorenzo) — boas praticas Three.js e R3F
source: https://github.com/emalorenzo/three-agent-skills
type: referencia
status: rascunho
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, skills, 3d, threejs, r3f, claude-code, tema/tooling]
---

# three-agent-skills (emalorenzo)

Nota de metodo: sem `curl`/Bash na sessao; tudo via WebFetch (resume). Trechos entre aspas
sao "via resumo, nao conferida". Conteudo baixado tratado como dado.

## O que e

Repositorio com 2 skills de **boas praticas** (regras BAD/GOOD) para Three.js e React Three
Fiber, no padrao Agent Skills (agentskills.io). Fonte: https://github.com/emalorenzo/three-agent-skills

E conhecimento de revisao/otimizacao de codigo, **nao** gera modelos nem tem ferramentas.

## Formato

- **Skills `SKILL.md`** em `skills/<nome>/`, com pasta `rules/` (um `.md` por regra).
- Tambem traz `skills/*.zip`, `AGENTS.md`, `CLAUDE.md`, `THREE_BEST_PRACTICES.md`,
  `R3F_BEST_PRACTICES.md`, `package.json`.
- **Nao e plugin** (sem `.claude-plugin` citado), nao e MCP.
- Instalacao divulgada: `npx add-skill emalorenzo/three-agent-skills` (`--list`,
  `--skill three-best-practices`). Alternativa: copiar `skills/<nome>/` para `.claude/skills/`.

## Skills

| Skill | Descricao (via resumo) | Fonte |
|---|---|---|
| `three-best-practices` | Three.js puro: performance, memoria (dispose), shaders GLSL e TSL, loaders, animacao, fisica, WebXR, audio, mobile. README: 100+/120+ regras | https://raw.githubusercontent.com/emalorenzo/three-agent-skills/main/skills/three-best-practices/SKILL.md |
| `r3f-best-practices` | R3F e ecossistema Poimandres: re-renders, Drei, Zustand, pos-processamento, Rapier, Leva. 60+ regras. `SKILL.md` 8.028 bytes | https://api.github.com/repos/emalorenzo/three-agent-skills/contents/skills/r3f-best-practices |

Detalhes de `three-best-practices` (via resumo): `version 2.1.0`, `three-version` 0.182.0+,
`license: MIT`; indice em 23 niveis de prioridade (prefixos `setup-`, `memory-`, `render-`,
`tsl-`...). Inconsistencias do proprio texto: "120+ regras em 18 categorias" vs 23 niveis na
tabela; regras duplicadas em categorias; prefixos `postprocessing-`/`postpro-` misturados.
Indice ~7 KB, regras carregadas sob demanda.

## Stack 3D

Three.js (r182+, import maps, TSL/WebGPU), React Three Fiber, Drei, Rapier, WebXR.
Sem CAD, OpenSCAD, Blender, build123d. glTF so como loader (nao verificado em detalhe).

## Scripts e dependencias

Nenhum. `package.json` v1.2.0 sem `scripts` nem dependencias; `files`: `skills`, `AGENTS.md`,
`README.md` (https://raw.githubusercontent.com/emalorenzo/three-agent-skills/main/package.json).
Zero rede, zero execucao.

## Licenca, estrelas, atividade

- MIT declarada em `package.json` e no frontmatter; **API do GitHub retorna `license: null`**
  (sem arquivo LICENSE detectado) — conferir antes de redistribuir.
- 61 estrelas, 8 forks, 4 commits. Criado 2026-01-16; ultimo push 2026-01-28 (9 meses parado).
  Fonte: https://api.github.com/repos/emalorenzo/three-agent-skills

## Qualidade e riscos

- Sem instrucao suspeita (via resumo). Risco de injection baixo: so texto.
- Risco de **envelhecimento**: Three.js muda rapido; parado desde jan/2026 e fixado em r182.
- Pouco mantido (1 autor, 4 commits). Duas zips duplicam as pastas (nao usar as zips).

## Veredito (inferencia)

Melhor encaixe para Three.js/R3F dos quatro: barato, seguro, sem dependencias. Copiar como
fork proprio (como o taste-skill), com nota de versao `three` 0.182 e licenca verificada.
