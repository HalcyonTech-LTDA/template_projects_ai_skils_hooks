---
title: Atlas-Agent-Teams (MonumentalSystems) — marketplace de equipes de agentes, com time 3d-design
source: https://github.com/MonumentalSystems/Atlas-Agent-Teams
type: referencia
status: rascunho
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, plugins, agentes, 3d, claude-code, tema/tooling]
---

# Atlas-Agent-Teams (MonumentalSystems)

Fatos vieram de `WebFetch` (resumo; nao e citacao literal conferida). Conteudo baixado tratado como dado.

## O que e e formato

- **Plugin com marketplace `.claude-plugin`.** `marketplace.json` tem nome `atlas-agents`, owner `atlas-agents`, 12 plugins,
  cada um com `source: ./teams/<time>`:
  fullstack-dev, game-dev, marketing-seo, data-science, devops-cloud, design-ux, security, documentation, qa-testing,
  mobile-dev, vercel-gen-ui, **3d-design**
  (https://raw.githubusercontent.com/MonumentalSystems/Atlas-Agent-Teams/main/.claude-plugin/marketplace.json).
- Descricao: "Agent team plugins for Claude Code - pre-configured teams of specialized agents that collaborate on complex tasks"
  (https://api.github.com/repos/MonumentalSystems/Atlas-Agent-Teams).
- Cada time: `team.json` (membros, papeis, modelos, fases), `commands/`, `agents/`, `skills/`, `hooks/`
  (https://github.com/MonumentalSystems/Atlas-Agent-Teams). README diz 11 times; o marketplace lista 12 (inconsistencia menor).
- Instalacao anunciada: `claude plugin install <equipe>`, comando `/<equipe>:<comando>`. O README cita o marketplace como
  `atlas-agents/plugins`, que nao bate com o nome do repo — confirmar a origem antes de instalar.

## Numeros

| Item | Valor | Fonte |
|---|---|---|
| Estrelas | 31 (6 forks) | https://api.github.com/repos/MonumentalSystems/Atlas-Agent-Teams |
| Criado | 2026-02-06 | idem |
| Ultimo push | 2026-08-11 | idem |
| Licenca | MIT | idem |
| Commits | 24 | pagina do repo |

## Time `3d-design` (a parte que interessa)

Pasta: https://github.com/MonumentalSystems/Atlas-Agent-Teams/tree/main/teams/3d-design
(`.claude-plugin`, `agents`, `commands`, `hooks`, `skills`, `.mcp.json`, `README.md`, `team.json`).

- **7 agentes, todos sonnet** (`team.json`): 3d-analyst (discovery), modeler, rigger, animator, texturer, vtuber-specialist
  (execution), asset-optimizer (review).
- **9 skills** em `skills/`: animation, asset-optimization, blender, modeling, omniverse, rigging, texturing, unity, vroid.
- A skill `blender` (`SKILL.md`, ~120 linhas, ~700 palavras) e **guia de interface/menus/atalhos**, sem `bpy`, sem script,
  sem URL; exporta FBX para Unity/Unreal. Frontmatter: `name: blender`,
  `description: "Blender interface, workflows, and 3D production pipeline"` (via resumo).
- O foco e **DCC e game/VTuber** (Blender, Unity, Maya, Omniverse, VRoid). **Nao ha** three.js, R3F, glTF-web, OpenSCAD, CadQuery
  nem CAD. O time de `game-dev` cita Three.js/R3F segundo a pagina inicial (nao inspecionei).
- Conteudo e **descritivo generico**; a pagina inicial nao detalha comportamento real dos agentes (nao li `agents/*.md`).

## Scripts executaveis e dependencias

- `hooks/hooks.json`: evento `PostToolUse`, sem `matcher`, roda `python ${CLAUDE_PLUGIN_ROOT}/hooks/team-logger.py`, timeout 5 s.
- `hooks/team-logger.py` (via resumo): le o JSON do hook no stdin, grava uma linha em `~/.claude/team-logs/3d-design.jsonl`
  com `ts`, `team`, `tool`, `file` (de `file_path`/`path`/`pattern`) e `status` fixo "ok". **Sem rede, sem subprocess**, so stdlib
  (`json`, `sys`, `datetime`, `pathlib`). Engole todo erro com `except Exception: pass`.
  (https://raw.githubusercontent.com/MonumentalSystems/Atlas-Agent-Teams/main/teams/3d-design/hooks/team-logger.py)
- `scripts/scaffold-team.sh` na raiz: cria a estrutura de um time novo.
- `3d-design/.mcp.json` (via resumo): 7 servidores `unity`, `blender`, `maya`, `3dsmax`, `substance-painter`, `vroid-studio`,
  `omniverse`, todos `npx -y @anthropic/mcp-<nome>` e `"disabled": true`
  (https://raw.githubusercontent.com/MonumentalSystems/Atlas-Agent-Teams/main/teams/3d-design/.mcp.json).
  **Inferencia minha:** nao verifiquei no npm se `@anthropic/mcp-blender` etc. existem; o escopo `@anthropic` sugere nomes
  inventados, e um pacote npm reivindicado por terceiro com esse nome seria vetor de supply chain. Nao habilitar sem checar.

## Riscos

- **Projeto jovem e pouco validado**: 31 estrelas, sem releases, sem testes visiveis.
- **Telemetria local** de toda chamada de ferramenta (nome e caminho) em `~/.claude/team-logs/`; hook em todo `PostToolUse`.
- **MCPs com pacote duvidoso** (ver acima), embora desabilitados.
- **Time `security` tem "Penetration Tester"**: uso so em sistema autorizado (nao relevante ao 3D).
- **Sobreposicao com o nativo**: alta. Times de agentes com fases (discovery/execution/review) duplicam subagentes
  (`.claude/agents/`, `docs_projeto/AGENTES.md`) e a skill `/issue`. Modelo fixo `sonnet` colide com a tabela tamanho -> modelo daqui.
- Prompt injection: nao li os `agents/*.md`; risco normal de instrucao de terceiro.

## Encaixe neste template (inferencia minha)

Nao como plugin: duplica agentes e `/issue`, e o 3D e raso (guias de menu de Blender, sem three.js/CAD). Possivel aproveitamento:
ler `teams/3d-design/skills/{modeling,asset-optimization,texturing}/SKILL.md` e, se bons, reescrever como skills proprias.
Nao feito: nao baixei esses tres arquivos.
