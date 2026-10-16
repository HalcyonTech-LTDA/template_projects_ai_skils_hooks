---
title: TerminalSkills/skills — origem das skills Blender
source: https://github.com/TerminalSkills/skills
type: referencia
status: aprovado
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, skills, 3d, blender, bpy, claude-code, tema/tooling]
---

# TerminalSkills/skills — origem das skills Blender

Biblioteca aberta de `SKILL.md` para Claude Code, Codex, Gemini CLI e Cursor. E a **origem**
das cinco skills Blender que aparecem copiadas em `Andrew1326/dominations` (o frontmatter
delas traz `author: terminal-skills`). Ver [[skill3d-dominations]].

Nota de metodo: lido por `git clone --sparse` no commit `6edcf94` (2026-10-14), arquivos
inteiros, nao resumo. Licenca e estrelas pela API do GitHub.

## Dados

| Campo | Valor |
|---|---|
| Licenca | Apache-2.0 (arquivo `LICENSE` na raiz) |
| Estrelas / ultimo push | 168 / 2026-10-14 |
| Formato | uma pasta por skill: `SKILL.md` + `_scores.json` (nota interna da curadoria) |
| Scripts | nenhum nas skills 3D; so blocos de codigo `bpy` dentro do texto |

## Skills 3D no repo

| Skill | Adotada | Motivo |
|---|---|---|
| `blender-scripting` | sim | Base: headless, bmesh, modificadores, import/export |
| `blender-render-automation` | sim | Cycles/EEVEE, camera, luz, lote |
| `blender-animation` | sim | Keyframe, armature, IK, NLA; ja na API do Blender 5 |
| `blender-compositing` | sim | Nos do compositor no Blender 5.x |
| `blender-addon-dev`, `-grease-pencil`, `-motion-capture`, `-vse-pipeline` | nao | Nicho; adicionar quando um projeto pedir |
| `3dsmax-*` | nao | Software pago, Windows |
| `threejs`, `react-three-fiber` | nao | Sobrepoem `three-best-practices` / `r3f-best-practices`, mais completas |
| `spec-to-3d` | nao | Planta arquitetonica para Three.js/IFC; fora do escopo atual |

## Diferenca para a copia do dominations

As quatro adotadas **diferem** da copia em `dominations` (o upstream evoluiu: API do
Blender 5, `--python-exit-code 1`, `--factory-startup`). `blender-3d-modeling`, que existe no
`dominations`, nao existe mais no upstream — nao foi adotada.

## Riscos encontrados e guarda aplicada

- `bpy.ops.object.select_all(action='SELECT')` + `delete()` como "limpar cena": seguro so em
  arquivo novo; apaga o trabalho se rodar num `.blend` do usuario
- `save_as_mainfile(filepath="/tmp/...")`: caminho fixo Unix, quebra no Windows
- Varredura por injecao, rede e execucao (`curl`, `subprocess`, `eval`, segredo): limpa

Guarda no topo de cada `SKILL.md` adotado; procedencia no `skills-lock.json`;
`LICENSE.txt` copiado para cada pasta. Precedencia em [[../SKILLS|SKILLS.md]] secao 9.
