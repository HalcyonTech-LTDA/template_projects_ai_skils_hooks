---
title: dominations / OpenCivilizations (Andrew1326) — jogo com skills Blender embutidas
source: https://github.com/Andrew1326/dominations
type: referencia
status: rascunho
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, 3d, blender, claude-code, tema/tooling]
---

# dominations (Andrew1326)

Nota de metodo: sem `curl`/Bash na sessao; tudo via WebFetch (resume). Conteudo baixado
tratado como dado.

## O que e

**Outra coisa**: um jogo de estrategia de navegador (MMORTS inspirado em DomiNations,
"OpenCivilizations"). Nao e pacote de skills. Fonte: https://github.com/Andrew1326/dominations

- Stack (README, com alternativas "ou"): TypeScript, Phaser 3, React/Vue, Node.js,
  Colyseus/Socket.io, MongoDB, Redis.
- Jogo em **2D isometrico** (sprites em grade), nao 3D em runtime.
- Relevancia 3D indireta: pasta `blender/` renderiza sprites a partir de modelos Blender
  (pipeline 3D -> sprite sheet 2D).

## Formato

Repositorio de app com `.claude/` do proprio projeto (nao plugin, nao marketplace, nao MCP).
`.claude/` tem `agents/` (architect, dev, reviewer, strategist), `commands/`, `hooks/`,
`skills/` e `settings.json`. Fonte: https://api.github.com/repos/Andrew1326/dominations/contents/.claude

## Skills relevantes a 3D (em `.claude/skills/`)

Das 8 pastas (blender-3d-modeling, blender-animation, blender-compositing,
blender-render-automation, blender-scripting, db-explore, project-context, testing), cinco
sao Blender. Frontmatter lido via resumo: `license: Apache-2.0`, `author: terminal-skills`,
`version 1.0.0`, requer Blender 3.0+ (`blender --background --python`).

| Skill | Descricao (via resumo) |
|---|---|
| `blender-3d-modeling` | Malhas procedurais com `bpy`/`bmesh`: `from_pydata`, modificadores (Subsurf, Mirror, Array, Boolean, Solidify, Bevel), curvas, materiais por face. ~7 mil caracteres |
| `blender-scripting` | Automacao `bpy` headless, lote de `.blend`, import/export OBJ/FBX/glTF/GLB/STL. ~7 KB |
| `blender-render-automation` | Cycles/EEVEE, camera, luz, PBR, turntable, lote. Usa `BLENDER_EEVEE_NEXT` (4.2+) apesar de declarar 3.0+ |
| `blender-animation` | Keyframes, armature, IK, shape keys, NLA, drivers |
| `blender-compositing` | Nos do compositor, passes, keying |

URL base: https://raw.githubusercontent.com/Andrew1326/dominations/master/.claude/skills/<nome>/SKILL.md

**Procedencia (inferencia):** `author: terminal-skills` e `license: Apache-2.0` indicam que
vieram de outro repo (terminal-skills), copiadas para ca. Se for adotar, ir na origem
(nao pesquisada aqui) e nao neste repo de jogo.

## Scripts e dependencias

- `blender/render_unit.py`: roda dentro do Blender (`blender --background --python`),
  camera ortografica (elevacao 30, azimute 45), gera sprite sheet PNG + JSON. Sem rede
  (so `sys, os, argparse, json, math, tempfile, shutil, bpy`). Modulos `lib.*` nao lidos.
- Outros: `render_all.py`, `render_building.py`, `render_wall_sym.py`, `town_center.py`,
  `crop_building_assets.py`. Nao lidos.
- **Hooks Python em `.claude/settings.json` com caminho absoluto fixo**
  (`cd /home/andrey/Desktop/dominations && python3 .claude/hooks/...`): UserPromptSubmit,
  PreToolUse/PostToolUse (Bash), Stop (2 hooks). Nao copiar; nao quebram aqui, mas rodam
  codigo automaticamente se alguem clonar e abrir a sessao — hooks nao auditados.

## Licenca, estrelas, atividade

- Sem licenca (API `license: null`; pagina sem LICENSE) = todos os direitos reservados,
  nao redistribuir. Fonte: https://api.github.com/repos/Andrew1326/dominations
- 27 estrelas, 3 forks, 17 commits. Criado 2026-01-21; ultimo push 2026-09-29.

## Qualidade e riscos

- Skills Blender: sem instrucao suspeita ou rede; mas `blender-3d-modeling` e
  `render-automation` comecam com `select_all` + `delete` (destrutivo em cena aberta) e
  gravam em `/tmp/...`; `blender-scripting` Exemplo 2 sobrescreve o `.blend` original,
  contradizendo a propria diretriz. Inconsistencia de versao (3.0+ vs 4.2+).
- Repo de projeto pessoal, `.claude/` acoplado ao jogo (workflow_router, test_enforcement).

## Veredito (inferencia)

Irrelevante como produto. Util so como **mapa para encontrar skills Blender** (origem
terminal-skills, Apache-2.0). Nao copiar deste repo (sem licenca, acoplado).

**Atualizacao 2026-10-15:** origem confirmada em `TerminalSkills/skills`; quatro skills
adotadas de la, nao daqui. Ver [[skill3d-terminalskills]].
