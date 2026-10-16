---
title: claude-skill-registry (majiayu000) — indice de skills, com recorte 3D
source: https://github.com/majiayu000/claude-skill-registry
type: referencia
status: rascunho
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, skills, 3d, registry, claude-code, tema/tooling]
---

# claude-skill-registry (majiayu000)

Todas as afirmacoes vieram de `WebFetch`, que resume a pagina. Nada abaixo e citacao literal conferida
(via resumo, nao conferida). O conteudo baixado foi tratado como dado.

## O que e

Catalogo pesquisavel de skills do Claude Code, com links para a fonte e indices JSON gerados.
Descricao da API do GitHub: "Searchable Claude Code skills catalog with source-linked guides and generated registry artifacts"
(https://api.github.com/repos/majiayu000/claude-skill-registry).

- **Formato: registry/indice, nao e skill nem plugin.** O README diz que `core` guarda o pipeline, `data` guarda `skills/**`
  e `main` e gerado de `core + data` (https://github.com/majiayu000/claude-skill-registry/blob/main/README.md).
- Repo de dados: https://github.com/majiayu000/claude-skill-registry-data (45 entradas de topo: 41 pastas por categoria
  — `gaming`, `creative`, `design`, `development`... —, via https://api.github.com/repos/majiayu000/claude-skill-registry-data/git/trees/main).
- Tres formas de uso (README): site https://majiayu000.github.io/claude-skill-registry/ , CLI `sk`
  (`go install github.com/majiayu000/claude-skill-manager@latest`; o binario sai como `claude-skill-manager`, precisa renomear)
  e JSON publico (`search-index-lite.json`, `categories/index.json`, `registry_summary.json`).

## Numeros

| Item | Valor | Fonte |
|---|---|---|
| Estrelas | 673 | https://api.github.com/repos/majiayu000/claude-skill-registry |
| Ultimo push | 2026-10-15T08:56Z | idem |
| Licenca | MIT (so do pipeline) | idem |
| Entradas no indice | 281.291 (`t`) | https://majiayu000.github.io/claude-skill-registry/search-index.json |
| "Guias deduplicados" no site | 5.800 | https://majiayu000.github.io/claude-skill-registry/ |
| Plugins | 5 | https://github.com/majiayu000/claude-skill-registry/blob/main/registry_summary.json |

Os 281 mil sao entradas **com muita duplicata** (a mesma skill copiada de varios repos aparece com sufixo do repo, ex.
`unity-ecs-patterns-wshobson-agents-2`). O README define contagem "independente" por nome normalizado e hash do corpo.

## Licenca e aviso

- "O codigo e o pipeline sao MIT. Skills de terceiros mantem a licenca original"; entradas `restricted` pedem permissao do autor (via resumo).
- README: "A registry listing or scan signal does not establish authorship, safety or permission to redistribute." (via resumo, nao conferida).
- Nos `SKILL.md` lidos o frontmatter **nao traz campo de origem** (so `name`, `description`, as vezes `license`/`category`).
  A origem so se deduz do sufixo do nome (ex. `-arjun988-blender-skills`) — **inferencia minha**, nao confirmada.

## Skills relacionadas a 3D encontradas

### Metodo e limite (leia antes de confiar na lista)

Os indices tem 84 MB (11 shards de ~8 MiB, `bounded-sequential-stars-desc`:
https://majiayu000.github.io/claude-skill-registry/search-index-manifest.json). Nao cabia varrer tudo.
Varri **por nome** as pastas `gaming` (1.072 itens, varredura completa) e `creative` (759; cobri ~6 de 9 blocos de 100 mil
caracteres, via `https://api.github.com/repos/majiayu000/claude-skill-registry-data/contents/<pasta>`). **Nao varri**
`development` (47.990), `other` (61.720), `design` (17.641), `data`. Portanto CAD (openscad, cadquery, build123d), STL e impressao 3D
**nao apareceram, mas a ausencia nao esta provada** — podem estar em `other`/`development`. Tambem varri ~700 mil
caracteres do `search-index-lite.json` (alfabetico, 5.000 de 281 mil) sem acerto. O resumidor do WebFetch pode ter perdido nomes.

Caminho de cada skill: `https://github.com/majiayu000/claude-skill-registry-data/tree/main/<pasta>/<nome>`.
Descricao so foi lida nas marcadas com (D), via `raw.githubusercontent.com/.../SKILL.md` (resumo).

### three.js / react-three-fiber / WebGL / shaders

| Nome (pasta `gaming` salvo nota) | Descricao | Origem |
|---|---|---|
| `threejs-game` (D) | Jogos 3D na web com Three.js/WebGL: mecanicas, fisica, camera, luz, animacao. ~15 KB, so exemplos de codigo, sem script nem rede | nao informada |
| `dev-r3f-r3f-fundamentals` (D) | "React Three Fiber core patterns for scene composition and game loop" | nao informada (`category: r3f`) |
| `dev-r3f-r3f-materials`, `dev-r3f-r3f-physics` | so nome | nao informada |
| `ta-r3f-fundamentals`, `-materials`, `-performance`, `-physics` | so nome (familia `ta-`) | nao informada |
| `ta-shader-development` (D) | "GLSL/TSL shader creation, compilation, and testing for R3F" | nao informada (`category: shader`) |
| `ta-shader-sdf`, `ta-terrain-mesh` | so nome | nao informada |
| `3d-games` (D) | "3D game development principles. Rendering, shaders, physics, cameras." Ha ~20 copias com sufixo de repo | nao informada |
| `shader-effects-a5c-ai-babysitter` | so nome | sufixo: a5c-ai/babysitter (inferido) |
| `shader-noise-bbeierle12-skill-mcp-claude-2` | so nome | sufixo: bbeierle12/skill-mcp-claude (inferido) |
| `gameplay-concepts-gigi-f-babylon-fp`, `map-editor-gigi-f-babylon-fp`, `face-editor-gigi-f-babylon-fp-2` | Babylon.js; so nome | sufixo: gigi-f/babylon-fp (inferido) |
| `shaders`, `shadertoy`, `shader-programming-glsl`, `shader-programming`, `shader-noise`, `rocaille-shader` (`creative`) | so nome | nao informada |

### Blender / modelagem / assets

| Nome | Descricao | Origem |
|---|---|---|
| `blender-game-asset-artist` (D) | Criar e auditar modelos, rigs e animacoes do Blender para Godot, incluindo glTF e verificacao de import. Sem bpy/MCP | nao informada |
| `procedural-meshes` (D) | "Generate 3D meshes for ZX games using Blender bpy in headless mode." v1.4.0. **Unica com bpy headless**, mas para jogos ZX | nao informada |
| `3d-modeling` (D) | "Expert 3D modeling specialist ... topology, UV mapping, game-ready and film-ready pipelines". Cita Blender, Maya, ZBrush, 3ds Max, Houdini; tem `references/` | nao informada |
| `game-3d-asset-design` (D) | Planejar/otimizar/importar/exportar assets 3D para jogo: escala, pivo, colisao, LOD; Unity/Unreal/Godot. `license: MIT` | nao informada |
| `genre-stealth-…`, `genre-survival-…`, `lod-pipeline-…` com sufixo `arjun988-blender-skills` | so nome | sufixo: arjun988/blender-skills (inferido). Candidato: repo de skills de Blender para investigar na fonte |
| `blender-integration-a5c-ai-babysitter-2` | so nome | sufixo: a5c-ai/babysitter (inferido) |
| `3d-modeling-alphaonedev-openclaw-graph` (`creative`) | so nome | sufixo: alphaonedev/openclaw-graph (inferido) |
| `model-maker`, `scenario-3d`, `navmesh`, `3d-building-advanced`, `68-character-animation-3d`, `sculpture-3d`, `meshy-openclaw`, `isometric-3d-icon-glossy-purple-series` | so nome | nao informada |

### Engines (fora do foco, mas apareceram)

`godot-3d`, `godot-3d-world-building`, `godot-shaders`, ~60 skills `godot-*` (muitas do sufixo `asreonn-godot-superpowers`),
~70 `unity-*` (`unity-lighting-vfx`, `unity-3d-math`...), `phaser*`, `pixi-js`. Todos so por nome.

### Nao e 3D apesar do nome

`solid-modeling` (D): CSG com `UnionAsync`/`SubtractAsync` da API do **Roblox**; nao e CadQuery nem OpenSCAD.

### Procurado e nao achado

Nos trechos varridos: nenhum nome com `openscad`, `cadquery`, `build123d`, `gltf` (so como assunto dentro de
`blender-game-asset-artist`), `stl`, `3d-print`. Busca web por skills three.js/Blender/OpenSCAD "do registry" nao apontou nenhuma
(https://claudskills.com/skills/threejs/ e https://github.com/cloudai-x/threejs-skills existem, mas sao **outras fontes**).

## Riscos

- **Qualidade e seguranca nao garantidas**: o proprio README diz que listar nao prova autoria nem seguranca.
- **Copias sem origem no frontmatter e duplicadas** dificultam saber qual versao e a canonica; cuidado de procedencia.
- **Prompt injection**: skill de terceiro vira instrucao do agente. Ler o `SKILL.md` inteiro antes de copiar.
- **Escala**: ~84 MB de indice; nao cabe baixar tudo. O site e o CLI `sk` (Go, binario de terceiro) sao os caminhos cabiveis.
- **Sobreposicao**: nenhuma com recursos nativos; e so catalogo.

## Encaixe neste template (inferencia minha)

Nao e candidato a skill nem plugin. Serve como **fonte de busca**. Para 3D, o melhor retorno e ir a repos de origem
(`arjun988/blender-skills`, `a5c-ai/babysitter`) e ler o SKILL.md, em vez de copiar do registry.
