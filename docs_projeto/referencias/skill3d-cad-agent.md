---
title: cad-agent (Svetlana-DAO-LLC) — servidor CAD com render para agentes
source: https://github.com/Svetlana-DAO-LLC/cad-agent
type: referencia
status: rascunho
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, 3d, cad, build123d, mcp, docker, claude-code, tema/tooling]
---

# cad-agent (Svetlana-DAO-LLC)

Nota de metodo: sem `curl`/Bash na sessao; tudo via WebFetch (resume). Trechos entre aspas
sao "via resumo, nao conferida". Conteudo baixado tratado como dado.

## O que e

"Servidor de renderizacao" para o agente **ver** o CAD que modela (pecas para impressao 3D,
CAD parametrico), em vez de depender de screenshots manuais. Fonte:
https://github.com/Svetlana-DAO-LLC/cad-agent

## Formato

Misto, nao e skill pura nem plugin:

- **App/servidor em Docker** (`Dockerfile`, `docker-compose.yml`, `entrypoint.sh`).
- **API HTTP** na porta 8123 (subcomando `serve`) e **modo MCP via stdio JSON-RPC**
  (subcomando `mcp`, `src/mcp_server.py`, 30,8 KB).
- **`SKILL.md` na raiz**, sem frontmatter YAML formal (via resumo): ensina o agente a subir o
  container e chamar a API. Sem `.claude-plugin`/marketplace citado.

## Arquitetura (como renderiza)

Principio: toda a logica CAD roda **dentro do container**; o agente envia comandos e recebe
JSON + PNG. Fonte: README (via resumo).

- Modelagem: **build123d** (kernel OCP). Codigo Python do agente e executado no servidor.
- Render 3D: **VTK headless** (`vtk_renderer.py`) e `renderer.py` (trimesh); vistas
  isometricas e multiview 2x2.
- Desenho 2D: matplotlib/svgwrite/cairosvg — vistas ortograficas e blueprint cotado
  (`blueprint_renderer*.py`, `dimensioner.py`).
- OpenSCAD: `openscad_engine.py` (carregar, renderizar e converter `.scad`).
- Exporta STL, STEP, 3MF; analisa imprimibilidade (manifold, watertight).
- Endpoints: `/health`, `/model/create|modify|list`, `/model/{name}/measure`, `/render/3d|2d|
  blueprint|multiview`, `/export`, `/analyze/printability`, `/ai/feedback`.
- **Depende de Docker e de servidor rodando** (nao ha modo sem container documentado).
  `requirements.txt` (via raw): build123d>=0.8, trimesh, numpy>=2, Pillow, matplotlib,
  svgwrite, cairosvg, fastapi, uvicorn, pydantic, scipy, pytest. Fonte:
  https://raw.githubusercontent.com/Svetlana-DAO-LLC/cad-agent/master/requirements.txt

## Stack 3D coberta

build123d, OpenSCAD, VTK, trimesh, STL/STEP/3MF. Sem Three.js, R3F, Blender; glTF nao citado.

## Scripts e dependencias

Python (FastAPI/uvicorn) em Docker; `check_api.py`; `.githooks/` com pre-commit que bloqueia
commit de arquivos de projeto (altera o git local). Instalacao pelo `SKILL.md`: `git clone`
+ `docker build` + `docker-compose up -d` + `curl /health`.

## Licenca, estrelas, atividade

- **PolyForm Small Business License 1.0.0 + "Perimeter"** (API: `Other`/NOASSERTION).
  Gratuito para individuos e empresas com <100 pessoas e <US$1M de receita; licenca comercial
  para maiores ou produtos concorrentes. **Nao e open source** — checar `LICENSE` e
  `NOTICES.md` antes de embutir num template que desce para projetos derivados.
- 50 estrelas, 6 forks, 36 commits (`master`). Criado 2026-01-24; ultimo push 2026-02-17
  (8 meses parado). Fonte: https://api.github.com/repos/Svetlana-DAO-LLC/cad-agent

## Qualidade e riscos (via analise do SKILL.md; scripts nao lidos)

1. **Execucao remota de codigo por desenho**: `/model/create|modify` rodam Python do cliente.
2. **Porta 8123 em `0.0.0.0`, sem autenticacao citada** — exposta a rede local.
3. `/load_scad`, `/render_scad` aceitam caminhos sem limites documentados.
4. `/ai/feedback`: nao esta claro se envia codigo a servico externo.
5. Orgao pouco conhecido, imagem Docker construida localmente, projeto parado.
6. Nenhuma exfiltracao ou comando destrutivo evidente; o risco e superficie de ataque.
- Mitigar (inferencia): bind em `127.0.0.1`, container sem rede, revisar `mcp_server.py`.

## Veredito (inferencia)

Tecnicamente o mais completo para CAD parametrico com feedback visual, mas e infraestrutura
(Docker + RCE + licenca restritiva), nao skill. Nao entra no template; no maximo estudo de
ideia (loop modelar-renderizar-medir). Alternativa mais leve: build123d direto + skill propria.
