---
title: Decisoes do repo template
type: readme
status: aprovado
created: 2026-05-28
updated: 2026-10-21
tags: [readme, decisoes]
---

# Decisoes do repo template

Registro de mudancas estruturais feitas **neste repositorio** (nao nos projetos derivados dele). Cada entrada e uma nota datada com o que mudou e por que.

> Para decisoes tecnicas **dentro de um projeto**, use o template ADR em `docs_Template_Projeto/_templates/ADR_Template.md` (modulo `01_Gestao/Decisoes_Tecnicas/`).

## Indice

- [[2026-05-28_configuracao_obsidian_template]] — configuracao inicial da estrutura Obsidian do template
- [[2026-09-06_catalogo_mcps]] — catalogo curado de MCPs, politica de segredos e `.mcp.json.example`
- [[2026-09-07_skills_taste]] — pacote `taste-skill` (13 skills), catalogo `SKILLS.md` e politica de fork
- [[2026-10-10_agentes_e_fluxo_de_issue]] — 5 subagentes, skill `/issue` por tamanho, handoff entre fatias e excecao das 5 perguntas em XS/S
- [[2026-10-12_skills_pcb_kicad]] — familia `pcb-*` para circuitos e PCB no KiCad 10: `kicad-cli` + scripts, portoes humanos, MCP de KiCad e `kicad-happy` fora do nucleo
- [[2026-10-15_trilha_e_board]] — skill `/trilha` (marcos, sequencia, bloqueios nativos, progresso), molde `BOARD.md` e formularios de issue
- [[2026-10-15_skills_3d]] — fork de texto (Three.js, R3F, Blender) + skill propria `cad-parametrico`; anatomy, cad-agent, Atlas, code-buddy fora
- [[2026-10-15_fontes_frontend]] — Refero, Arc e Cult UI nas 4 skills de design via `_shared/fontes-frontend.md`; vetados do Cult; hook lista so pastas com `SKILL.md`
- [[2026-10-15_classificacao_sonnet_e_plano_l_xl]] — `explorer` em Sonnet propoe o tamanho (vale o maior entre ele e a label); `Plan` opus e advisor so em L/XL; M com lista de fatias da sessao; plano fora do chat
- [[2026-10-15_padroes_halcyon]] — 54 skills e 5 agentes dos repos `modern-*` copiados do GitHub por script com `padroes-lock.json`; guardrail em `_shared/padroes-*.md`; marketplace nao publicado; `java-clean-architecture-scaffolding` como base Java
- [[2026-10-18_statusline_issue]] — statusline com issue da sessao, status do board (cache de 60 s renovado em segundo plano), modelo, esforco, contexto e tokens da sessao inteira (subagentes e advisor, lidos dos transcripts); hook + `/issue` gravam por `session_id`
- [[2026-10-26_progresso_shell]] — plugin `progresso-shell` em `.claude/skills/`: progresso de testes e shell na linha de status embaixo do prompt (`Testes 4/12`, `Shell 45%`) via `tee` num log; so Bash; permissao no modo padrao nao provada
- [[2026-10-18_issue_entrega_e_estados]] — `/issue` v1.2: testes unitarios por fatia alem do portao, In progress ao iniciar, PR `Refs #N` para a branch de origem, squash apos o CI, Done (prova toda automatizada) ou In review depois do merge via `issue.js mover`, URL da issue no fim
- [[2026-10-21_beui]] — beUI como quarta fonte de frontend (terceiro registry): controles com motion, UI de agente, React Native; skill e MCP dele fora; quatro itens vetados
- [[2026-10-18_economia_de_contexto]] — `ECONOMIA.md` (menos chamadas, contexto menor, modelo pela tarefa); hook de 5,3 KB para 0,7 KB sem a lista de skills; perguntas e alternativas escalam pelo tamanho
- [[2026-10-15_galerias_de_secao]] — degrau "galeria da secao" no passo 2 (navbar, footer, CTA, 404, bento, motion); scrolltide so como ficha, pago e sem redistribuicao
