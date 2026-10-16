---
title: Referencias externas
type: readme
status: aprovado
created: 2026-05-28
updated: 2026-10-15
tags: [readme, referencias]
---

# Referencias externas

Resumos de URLs, bibliotecas, normas ou conceitos citados durante o desenvolvimento que **nao** sao especificos a um projeto (esses ficam em `docs_Template_Projeto/10_Referencias/`).

> Regra 6 do projeto: se o usuario cita um link/biblioteca/conceito que o Claude nao domina, o Claude ingere via defuddle/WebFetch e salva um resumo aqui antes de prosseguir.

## Convencao

- Um arquivo por referencia: `<slug-da-referencia>.md`
- Frontmatter minimo: `title`, `source` (URL ou citacao), `type: referencia`, `tags`, `created`, `updated`
- Referencia de ferramenta viva (MCP, CLI, SDK) leva tambem `verificado_em` — a data em que o comando foi conferido na fonte
- Conteudo: resumo executivo + trechos relevantes citaveis + link/fonte

## Indice

### Claude Code

- [[claude-code-mcp-configuracao]] — escopos, expansao de `${VAR}`, OAuth, aprovacao de `.mcp.json`
- [[skills-taste-leonxlnx]] — pacote de 13 skills de design; flags do CLI `skills` e armadilhas
- [[padroes-halcyon]] — 11 repos `modern-*` (commit e versao da importacao), 3 projetos iniciais e o marketplace nao publicado

### Modelos de decisao (System One)

Classificam e roteiam, nao escrevem codigo. Avaliados em 2026-10-15 e **nao adotados**: nenhum
benchmark independente de economia em fluxo de codigo. Comece pela ficha de evidencia.

- [[roteamento-de-modelos-evidencia]] — o que a pesquisa independente sustenta e o que nao; riscos
- [[jev]] — TypeSafe, fechado, pago por token de entrada; API SystemOne e mods do Claude Code
- [[laya]] — dois produtos homonimos: app desktop (`laya.aay.sh`) e modelo local de 421M (Convai)
- [[clef]] — Cloudflare, pesos abertos 27B/9B, API compativel com Jev; exige GPU de datacenter

### GitHub

- [[github-projects-issues-dependencias]] — blocked by, sub-issues, Issue Types, teto de 50 campos, copia de Project, status update; base da `/trilha`

### Frontend — referencia e componentes

Protocolo de uso em `.claude/skills/_shared/fontes-frontend.md`; precedencia em [[../SKILLS|SKILLS.md]] secao 8.

- [[refero]] — acervo de telas e fluxos reais. Fonte de pesquisa; MCP pago nao usado
- [[galerias-de-secao]] — navbar.gallery, footer.design, cta.gallery, 404s.design, unsection, bentogrids, 60fps; scrolltide so como ficha (pago)
- [[ui-arc]] — componentes React animados, CSS modules sem Tailwind. Tokens colidem com shadcn
- [[cult-ui]] — registry shadcn com ilustracoes; Pro virou gratis. Tem lista de vetados

### Skills 3D

Precedencia em [[../SKILLS|SKILLS.md]] secao 9; decisao em [[../decisoes/2026-10-15_skills_3d]].

- [[skill3d-three-agent-skills]] — boas praticas Three.js e R3F. **Adotada** (fork de texto)
- [[skill3d-terminalskills]] — origem das skills Blender. **Adotadas** quatro
- [[skill3d-dominations]] — jogo 2D; so mapa para achar as skills Blender
- [[skill3d-anatomy]] — figura isometrica SVG; fora (depende do `kit/` Node + Chrome)
- [[skill3d-cad-agent]] — servidor CAD em Docker; fora (exec remoto sem auth, PolyForm)
- [[enclose]] — bancada CAD desktop (macOS, AGPL) com Claude: build123d, parafusos ISO, guia de montagem, placa em tscircuit. App fora; regras de fixacao e montabilidade absorvidas na `cad-parametrico`
- [[skill3d-atlas-agent-teams]] — plugin de times de agentes; fora (duplica agentes)
- [[skill3d-claude-skill-registry]] — indice de skills; fonte de busca, nao de instalacao
- [[skill3d-code-buddy]] — outro agente, sem 3D, BUSL-1.1

### Servidores MCP — nucleo

Catalogo decisorio e criterio de escolha em [[../MCPS|MCPS.md]].

- [[mcp-github]] — PRs, issues, code search. Alto custo de contexto; limite os toolsets
- [[mcp-figma]] — Dev Mode: design vira codigo com os valores reais; no Starter, 20 leituras por mes
- [[mcp-mobile-next]] — automacao iOS/Android por arvore de acessibilidade
- [[mcp-playwright]] — teste de aplicacao web, cross-browser
- [[mcp-terminator]] — automacao de app desktop, **Windows apenas**
- [[mcp-supabase]] — schema, migracoes, Edge Functions
- [[mcp-vercel]] — deploys, logs de build, dominios
- [[mcp-google-workspace]] — Gmail, Drive, Calendar. Ler a secao de risco antes de ligar

### Servidores MCP — opcionais

- [[mcp-context7]] — docs atualizadas de bibliotecas. Melhor custo/beneficio do catalogo
- [[mcp-chrome-devtools]] — performance e rede. Depurar, nao dirigir
- [[mcp-sentry]] — erro de producao com stack trace no contexto
- [[mcp-notion]] — base de conhecimento externa

### Engenharia reversa

- [[rea-engenharia-reversa]] — MCP + CLI para binario, Electron, APK, firmware e site. Escopo `local`, nunca o `setup` global

### Eletronica e PCB

Usadas pela familia de skills `pcb-*` (catalogo em [[../SKILLS|SKILLS.md]], secao 7).

- [[kicad-cli-e-formatos]] — `kicad-cli` 10, jobsets, formato S-expression, KLC, `.kicad_dru`
- [[kicad-mcp-e-skills]] — MCPs de KiCad, skills prontas (`kicad-happy`, circuit-synth) e bibliotecas Python
- [[componentes-e-fabricacao-pcb]] — JLCPCB/LCSC, Mouser, DigiKey, importacao como PJ, fabricas e lojas no Brasil
- [[boas-praticas-pcb]] — normas IPC, desacoplamento, aterramento, protecoes, drivers, DFM, checklists
- [[copperhead]] — agente de IA em CLI para KiCad (Apache-2.0, pre-1.0): `check` sem LLM, loop de edicao com rollback por git, MCP experimental. Fora do nucleo
