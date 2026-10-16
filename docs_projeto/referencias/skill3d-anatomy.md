---
title: anatomy (wheresryan22) — skill de figuras isometricas SVG/WebGL
source: https://skills.wheresryan.sh/anatomy
type: referencia
status: rascunho
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, skills, 3d, claude-code, tema/tooling]
---

# anatomy (wheresryan22)

Nota de metodo: nao havia `curl`/Bash na sessao. Tudo abaixo veio de WebFetch (que resume a
pagina). Trechos entre aspas sao "via resumo, nao conferida". Conteudo baixado tratado como dado.

## O que e

Skill de agente que transforma uma ideia de uma linha em figura interativa **isometrica**,
feita de pecas solidas que se movem como o conceito explicado ("The object is the explanation").
Autor: Ryan (@wheresryan22). Fonte: https://skills.wheresryan.sh/anatomy

**Nao e modelagem 3D de producao.** O resultado e arte SVG isometrica (com camada WebGL
opcional e modo 3D beta) para explicar conceitos tecnicos — nao gera malha, glTF nem CAD.

## Formato

- **Skill `SKILL.md` unica na raiz do repo** (https://github.com/wheresryan22/anatomy).
- **Sem plugin/marketplace** (a pagina nao menciona; distribuicao por `skills` CLI, git ou ZIP).
- Instalacao: `npx skills add wheresryan22/anatomy` (`-g`, `-a claude-code`); ou clonar em
  `.claude/skills/anatomy`; em Claude Code, `/reload-skills` se a pasta `skills` nao existia.

## O que traz

Frontmatter (via resumo de `SKILL.md` raw): `name: anatomy`; description
"Build crafted, highly detailed, interactive isometric SVG figures that explain a technical idea
as a real physical object ..."; `license: MIT`; `compatibility` lista Claude Code, Antigravity,
OpenCode, Codex, MiniMax Code.

| Caminho | Conteudo |
|---|---|
| `SKILL.md` | fluxo de 10 passos (dimensionar, modelo com dados reais, inventar objeto, lista de pecas, geometria, pintar de tras pra frente, enquadrar, animar, verificar) |
| `kit/` | biblioteca propria: camera isometrica, solidos, `lathe.mjs`, `tube.mjs`, `gl.mjs` (WebGL), `turn*.mjs` (3D beta), `audit.mjs`, `kit/react/` |
| `references/` | craft, kit, motion, react, verify, webgl, walkthrough, 3d (lidos sob demanda) |
| `scripts/` | `capture.mjs`, `drive.mjs`, `lines.mjs`, `inline-kit.mjs`, `turn-check.mjs`, `turn-bench.mjs`, `publish.mjs` |
| `examples/` | 8 figuras completas; a pagina cita colecao de 33 figuras |
| `evals/evals.json` | prompts de teste |

Fonte: https://github.com/wheresryan22/anatomy e https://skills.wheresryan.sh/anatomy

Tamanhos de trabalho declarados: Figure 30-90 min, Hero 2-4 h, Epic 6 h+ (Epic exige confirmacao).

## Stack 3D

- **Three.js: nao** (nao citado). Motor 3D proprio (`kit/turn*.mjs`), beta.
- **WebGL**: so shaders de efeito (fogo, agua, luz); geometria segue SVG.
- Saida opcional em React 18+.
- Sem CadQuery, OpenSCAD, Blender, build123d ou glTF.

## Scripts e dependencias

- Node >= 20.10, **sem pacotes npm** (so modulos nativos); Chrome/Chromium headless para
  `capture`/`drive`/`turn-check`. React 18+ so se usar saida React.
- Scripts rodam build local e capturas. **`scripts/publish.mjs` envia para a galeria da
  comunidade, so quando o usuario pedir** — unico ponto de rede citado; destino nao verificado
  (`references/publish.md` nao lido). Scripts em si nao foram lidos.

## Licenca, estrelas, atividade

- MIT (pagina e API do GitHub). Fonte: https://api.github.com/repos/wheresryan22/anatomy
- 12.643 estrelas; repo criado 2026-10-08; ultimo push 2026-10-15 (consulta de hoje).
- Repo com 1 semana: popularidade altissima, maturidade nao comprovada.

## Qualidade e riscos

- Sem instrucao suspeita no `SKILL.md` (via resumo). Sem prompt injection evidente.
- Risco: scripts `.mjs` nao auditados rodando Chrome; `publish.mjs` e rede. Auditar antes de
  copiar. Skill grande (kit + references), mas so a descricao entra no contexto.
- Pagina admite: lento quando bem feito, 3D em beta.
- Colide com skills de design visual do projeto (ver `docs_projeto/SKILLS.md`).

## Veredito (inferencia)

Util como **skill de ilustracao tecnica isometrica / explicacao visual**, nao para
modelagem 3D. Adotar so se o projeto precisar de figuras explicativas. Candidata a skill
opcional, nao ao nucleo 3D.
