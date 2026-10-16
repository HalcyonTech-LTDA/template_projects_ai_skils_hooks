---
title: KiCad — servidores MCP, skills prontas e bibliotecas Python
source: https://github.com/mixelpixx/KiCAD-MCP-Server
type: referencia
status: aprovado
created: 2026-10-12
updated: 2026-10-12
verificado_em: 2026-10-12
tags: [referencia, kicad, mcp, eletronica, tema/hardware]
---

# KiCad — servidores MCP, skills prontas e bibliotecas Python

Pesquisa feita em 2026-10-12 para decidir como uma skill do Claude Code deve projetar circuitos/PCBs no KiCad 10.0.0 (Windows 11, `kicad-cli` 10, Python embarcado com `pcbnew` SWIG, `kipy` nao instalado). Numeros de estrelas e datas vieram da API publica do GitHub (`api.github.com/repos/...`) e do JSON do PyPI (`pypi.org/pypi/<pkg>/json`) lidos em 2026-10-12, via WebFetch (que resume a pagina: tratar como "via resumo, nao conferido byte a byte"). O que nao foi verificado esta marcado.

## 1. Resumo executivo

- **O KiCad 10 NAO traz MCP nem IA oficial.** A nota de lancamento nao menciona Python, IPC, SWIG nem IA (https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/, via resumo). Nenhum MCP oficial encontrado.
- **A IPC API do KiCad 9 e 10 so cobre o editor de PCB e exige o KiCad aberto.** Citacoes literais (https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/, via resumo): "KiCad 9 and 10 only support IPC API plugins in the PCB Editor."; "The IPC API in KiCad 9 and 10 only supports communication with a running instance of the KiCad GUI."; "KiCad 11 adds support for plugins in the Schematic Editor."; "Support for running in headless mode through `kicad-cli` was added for KiCad 11."
- **SWIG `pcbnew`: remocao planejada para o KiCad 11.** "The SWIG-based Python bindings in KiCad are deprecated as of KiCad 9.0 and will be removed in a future version." / "The current plan is to remove the SWIG bindings in KiCad 11.0." (https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/, via resumo). Um relato de forum diz que o nightly 10.99 ja nao traz Python nem SWIG (https://forum.kicad.info/t/kicad-10-99-win-missing-python-exe/71638, nao conferido na fonte). Conclusao: nao construir nada novo em cima de SWIG.
- **Para esquematico no KiCad 10 nao existe API de edicao viva.** Todo gerador/editor de `.kicad_sch` trabalha em arquivo (S-expression), por parser proprio ou lib.
- **MCPs existem e sao muitos, mas caros em contexto**: mixelpixx 244 tools; oaslananka/kicad-mcp-pro 241 tools. Qualidade do esquematico gerado: mixelpixx faz fios reais por injecao de S-expression; ha defeitos abertos (ver 3.1).
- **Skills prontas reaproveitaveis**: `aklofas/kicad-happy` (MIT, 11 skills, KiCad 5-10, mas so ANALISA/REVISA, nao gera). Geracao: nenhuma skill madura encontrada; `circuit-synth` (MIT) e a mais proxima mas sem KiCad 10 documentado.
- **Recomendacao**: ver secao 6 (abordagem hibrida: skill + `kicad-cli` + gerador em Python/arquivo, MCP so opcional com perfil reduzido).

## 2. Matriz comparativa

### 2.1 Servidores MCP

| Projeto | Estrelas | Ultimo push | Licenca | KiCad 10? | Mecanismo | Tools | Esquematico com fios? | Roteamento | JLCPCB |
|---|---|---|---|---|---|---|---|---|---|
| mixelpixx/KiCAD-MCP-Server | 2658 | 2026-10-01 (release v2.8.2, 2026-09-25) | MIT | Parcial: README diz "KiCAD 9.0 or higher"; issue #420 aberta (cabecalho de biblioteca de simbolos escrito como KiCad 9) | SWIG + IPC (kipy, experimental) hibrido + kicad-skip + injecao S-expr + kicad-cli | 244 (README) | Sim, fios reais por S-expr, `connect_to_net`, labels, hierarquia | Sim, Freerouting (Java 21+ ou Docker) | Sim (libs locais + JLCSearch) |
| oaslananka/kicad-mcp-pro | 124 | 2026-10-12 (PyPI 4.3.0) | MIT | Sim, alvo principal (10.0.6 verificado; 10.0.7 em qualificacao) | kicad-cli + IPC (KiCad aberto) + parser de arquivo | 241 (com perfis `schematic_only`, `minimal`, `pcb_only`...) | Sim: `sch_*` (symbols, wires, labels, `sch_build_circuit` com auto_layout) | Opcional `[freerouting]` | nao verificado |
| lucatib/kicad-mcp | 2 | 2026-10-11 (repo criado 2026-08-07) | MIT | Sim (10.0.6, so Windows) | venv do Python do KiCad: pcbnew + kipy + kicad-cli + parse de `.kicad_sch` | 23 listadas na Glama (README cita mais) | Gera esquematico de pinout de firmware (`create_pinout_schematic`); fios nao verificado | `route_nets` citado no README, nao verificado | nao verificado |
| lamaalrajih/kicad-mcp | 525 | 2025-10-17 | MIT | Nao: "KiCad 9.0 or higher", sem commits desde out/2025 | kicad-cli + analise de arquivo | nao informado | Nao (analise, DRC, BOM, netlist) | Nao | Nao |
| Seeed-Studio KiCad MCP | nao verificado | nao verificado | nao verificado | README diz 9.0+ (via Glama) | analise/validacao | nao verificado | Nao desenha; alerta que fios podem nao conectar de verdade | nao | nao |

### 2.2 Skills / agentes

| Projeto | Estrelas | Ultimo push | Licenca | Faz | KiCad | Reaproveitavel? |
|---|---|---|---|---|---|---|
| aklofas/kicad-happy | 1377 | 2026-10-06 | MIT | 11 skills de ANALISE: kicad, spice, emc, datasheets, bom, digikey, mouser, lcsc, element14, jlcpcb, pcbway. Nao gera nem edita arquivos | 5 a 10 ("Full") | Sim, copiar/instalar via `/plugin marketplace add`; scripts Python sem dependencia obrigatoria e sem exigir KiCad |
| circuit-synth/circuit-synth | 285 | 2026-03-08 (PyPI 0.12.1, 2026-01-09) | MIT | Circuito em Python gera `.kicad_pro/.sch/.pcb`; agentes e skills de Claude Code | README: 8.0+; KiCad 10 nao mencionado | Parcial; sem commits ha 7 meses |
| diodeinc/pcb | 458 | 2026-10-12 | MIT | Toolchain "Zener" (linguagem propria) + skills (spice-sim, component-search...) | nao verificado | So se aceitar a linguagem Zener |
| american-embedded/kistack | 396 | 2026-09-24 | Sem licenca clara (NOASSERTION) | Skills de esquematico, revisao de PCB, BOM, exports, Gerber | nao informado | Nao copiar sem licenca |
| l3wi/claude-eda | 19 | 2026-01-01 | Sem licenca | Sistema Claude Code para EDA com KiCad | nao verificado | Nao |
| atopile/atopile | 3987 | 2026-06-13 | MIT | Linguagem `.ato` que atualiza `.kicad_pcb`; sem integracao de agente documentada | nao especificado | Outra stack (nao e skill) |

### 2.3 Bibliotecas Python

| Lib | Versao / data | Licenca | Formato KiCad 10? | Observacao |
|---|---|---|---|---|
| kicad-python (kipy, IPC) | 0.8.0 / 2026-08-30 | MIT | 0.7.1 e citada como par do KiCad 10 por terceiros; 0.8.0 nao verificado contra 10 | Instala-se com `pip install kicad-python`, importa-se como `kipy`; so PCB, KiCad aberto |
| SKiDL | 2.3.0 / 2026-07-28 | MIT | Sim: "KiCad 5 through 10"; suporte a 10 adicionado na 2.3.0 (via resumo do PyPI) | Gera netlist e esquematico (6-10) |
| kicad-sch-api | 0.5.6 / 2025-11-19 | MIT | README: abre em KiCad 7/8; 9/10 nao verificado | Tem MCP proprio de 15 tools |
| kiutils | 1.4.8 / 2024-02-02 | GPLv3 | Nao: ultima release anterior ao KiCad 9; PR #128 (2026-04, validado no 10.0.1) ainda e PR | Repo parado (push 2024-07) |
| kicad-skip | 0.2.5 / 2024-02-16 | LGPLv2+ | Nao verificado; sem push desde 2024-05 | Manipula S-expr de sch/pcb/netlist |
| KiKit | 1.8.1 / 2026-08-05 | MIT | versoes do KiCad nao informadas no PyPI | Panelizacao, fabricacao; usa pcbnew (SWIG) - nao verificado |
| KiBot | 1.9.1 / 2026-07-28 | GPLv3 | versoes nao informadas no PyPI | Automacao de exports/CI; roda sobre kicad-cli/pcbnew |

## 3. Achados — MCPs

### 3.1 mixelpixx/KiCAD-MCP-Server
- Repo: https://github.com/mixelpixx/KiCAD-MCP-Server. API: 2658 estrelas, 365 forks, MIT, push 2026-10-01, 16 itens abertos (https://api.github.com/repos/mixelpixx/KiCAD-MCP-Server). Releases v2.8.2 (2026-09-25), v2.8.1, v2.8.0 (2026-09-24), v2.7.0 (2026-08-20) (https://api.github.com/repos/mixelpixx/KiCAD-MCP-Server/releases).
- README (https://raw.githubusercontent.com/mixelpixx/KiCAD-MCP-Server/main/README.md, via resumo): pre-requisito "KiCAD 9.0 or higher"; Windows 10/11 "Fully supported with automated setup" por `setup-windows.ps1`; Node 18+, Python 3.11+; 244 tools registradas (184 indexadas para busca); "Discovery doesn't reduce context, since every tool schema is still sent to the client"; fios reais por injecao de S-expression; Freerouting via Java 21+ ou Docker; JLCPCB via bibliotecas locais e JLCSearch (download completo 3-5 GB, 40-60 min).
- O README informa que o autor reescreveu o projeto em Rust como "Konnect", plugin nativo KiCad 10 via IPC, 171 tools, AGPL-3.0, onde "new development happens". O repo Python/TS segue MIT e mantido. Konnect nao foi inspecionado por mim.
- Issues abertas lidas (https://api.github.com/repos/mixelpixx/KiCAD-MCP-Server/issues): #420 simbolo-lib escrito com token KiCad 9 (reporter diz que trocar para o valor do 10 funciona no 10.0.6); #379 bug de regex truncando `lib_symbols` (pode deixar dados orfaos no arquivo); #407 tools com parametros declarados e nunca lidos e seis tools sem rota Python; #345 `search_tools` omite 75 de 216 tools; #406 colisao de courtyard por bounding box com falso positivo; #453 race condition na subida do Python. Nenhuma issue aberta sobre fios de esquematico. Nao verifiquei issues fechadas.

### 3.2 oaslananka/kicad-mcp-pro
- Repo: https://github.com/oaslananka/kicad-mcp-pro (a Glama lista como Valxyria/kicad-mcp-pro; essa URL do GitHub deu 404). 124 estrelas, MIT, push 2026-10-12, criado 2026-05-31, 16 itens abertos (https://api.github.com/repos/oaslananka/kicad-mcp-pro). PyPI 4.3.0, `requires_python >=3.13` (https://pypi.org/pypi/kicad-mcp-pro/json). Atencao: a Glama diz Python 3.12+; o PyPI diz 3.13+ — vale o PyPI.
- Glama (https://glama.ai/mcp/servers/Valxyria/kicad-mcp-pro, via resumo): 241 tools; KiCad 10 alvo principal, 9.x "best-effort"; exports por kicad-cli, edicao ao vivo por IPC (KiCad aberto); `sch_*` cobre simbolos, fios, labels, barramentos, `sch_build_circuit` com `auto_layout`; instalacao `uvx kicad-mcp-pro`; perfis de tools reduzem a superficie.
- Issues/PRs: foco em teste de evidencia do KiCad 10.0.7 no Windows (#1246, #1181; "Keeps 10.0.6 as the last verified version"), bug de ingestao hierarquica (#1141: leitura so da raiz de um projeto de 1000+ componentes deu 7 componentes). Maioria dos itens abertos e infraestrutura/pesquisa (https://api.github.com/repos/oaslananka/kicad-mcp-pro/issues). Release mais recente: versoes divergem entre espelhos; PyPI e a fonte.

### 3.3 lucatib/kicad-mcp
- https://github.com/lucatib/kicad-mcp: 2 estrelas, MIT, 0 issues, criado 2026-08-07, push 2026-10-11 (https://api.github.com/repos/lucatib/kicad-mcp). Glama (https://glama.ai/mcp/servers/ehue1ojo5a, via resumo): Windows-only, verificado no KiCad 10.0.6 com kicad-python 0.7.1; "KiCad 10 has no schematic IPC API, so schematic tools use `kicad-cli` and direct `.kicad_sch` parsing"; `run_kicad_script` executa Python arbitrario com os privilegios do usuario. Muito novo e quase sem uso.

### 3.4 lamaalrajih/kicad-mcp
- https://github.com/lamaalrajih/kicad-mcp: 525 estrelas, MIT, ultimo push 2025-10-17, 24 issues abertas (https://api.github.com/repos/lamaalrajih/kicad-mcp). README: KiCad 9+, analise/DRC/BOM/netlist, passos de instalacao orientados a macOS/Linux. Nao gera esquematico. Parado ha ~12 meses.

### 3.5 Outros vistos (nao avaliados a fundo)
Busca no GitHub (https://api.github.com/search/repositories?q=kicad+mcp&sort=updated) lista 223 repos: ProductOfAmerica/mcp-server-kicad (13 estrelas, "100+ tools"), salitronic/eda-agent (244 estrelas, foco Altium), mo9652962-ai/circuit-agent, havamal-65/KiCad-MCP, entre outros. Todos pequenos; nao verificados. A Glama tambem lista "KiCad Copilot" (npm v0.1.0, schematic por linguagem natural, KiCad 9 ou 10) em https://socket.dev/npm/package/kicad-copilot-mcp — nao verificado.

## 4. Achados — skills e agentes

- **kicad-happy**: https://github.com/aklofas/kicad-happy. 1377 estrelas, MIT, push 2026-10-06, 6 issues (https://api.github.com/repos/aklofas/kicad-happy). README (https://raw.githubusercontent.com/aklofas/kicad-happy/main/README.md, via resumo): tabela de suporte "KiCad 10" com Schematic, PCB e Gerber "Full"; 11 skills; "zero required dependencies" e nao exige KiCad instalado; instala por `/plugin marketplace add` / `/plugin install` no Claude Code. Descrito como analise: nunca menciona gerar ou modificar arquivos KiCad. E o melhor candidato a reaproveitar (revisao de esquematico, BOM, sourcing LCSC/JLCPCB).
- **circuit-synth**: https://github.com/circuit-synth/circuit-synth, 285 estrelas, MIT, push 2026-03-08, 19 issues (API). README (https://raw.githubusercontent.com/circuit-synth/circuit-synth/main/README.md, via resumo): agentes `circuit-architect`, `circuit-synth`, `simulation-expert`, `component-search`; skills `circuit-patterns`, `component-search`, `kicad-integration`; "KiCad 8.0+"; sem rotulo de maturidade; README nao diz como as conexoes viram fios. PyPI 0.12.1 (2026-01-09), Python >=3.12 (https://pypi.org/pypi/circuit-synth/json). Gerador via kicad-sch-api; KiCad 10 nao verificado.
- **diodeinc/pcb**: https://github.com/diodeinc/pcb, 458 estrelas, MIT, push 2026-10-12. Ecossistema da linguagem Zener; skills listadas em https://www.vibeindex.ai/skills/diodeinc/pcb/spice-sim (indice de terceiro). Nao avaliado.
- **american-embedded/kistack**: https://github.com/American-Embedded/kistack, 396 estrelas, licenca "NOASSERTION"; README sem licenca nem versao do KiCad; instala com `npx skills add American-Embedded/kistack`. Nao copiar sem licenca.
- **l3wi/claude-eda**: https://github.com/l3wi/claude-eda, 19 estrelas, sem licenca, parado desde 2026-01.
- **atopile**: https://github.com/atopile/atopile, 3987 estrelas, MIT, push 2026-06-13. Alternativa "circuito como codigo" propria, atualiza `.kicad_pcb`; sem integracao de agente no README (https://raw.githubusercontent.com/atopile/atopile/main/README.md, via resumo). Versao do KiCad nao especificada.
- Skills citadas por indices de terceiros e NAO verificadas no GitHub: `telagod/code-abyss` (operating-kicad-eda, 17 tools MCP), `virajrungta` review (KiCad 9), `major-ai-skills` kicad (https://app.unpkg.com/major-ai-skills@2.3.0/files/skills/kicad/SKILL.md). Indices: https://www.vibeindex.ai/, https://claudemarketplaces.com/.
- **Nao encontrado**: skill oficial da Anthropic para KiCad; (nao verifiquei o repo anthropics/skills nem awesome-claude-skills diretamente).

## 5. Achados — bibliotecas Python

- **kicad-python / kipy**: https://pypi.org/pypi/kicad-python/json — 0.8.0, 2026-08-30, MIT, Python >=3.9, deps jsonschema/protobuf/pynng. Importa-se como `kipy` (modulo; nao e pacote separado no PyPI, segundo o que o JSON mostrou). Forum: com 0.7.1 em KiCad 10.0.5 campos customizados de footprint nao eram lidos (https://forum.kicad.info/t/kicad-10-customized-symbol-fields-missing-in-kicad-python-0-7-1/70731, so titulo/resumo). Relato de terceiros: cada instancia do KiCad tem um socket; comandos de board so funcionam se o editor de PCB for dono do socket (Glama, nao conferido).
- **SKiDL**: https://pypi.org/pypi/skidl/json — 2.3.0, 2026-07-28, MIT, "KiCad 5 through 10; schematic generation 6-10; KiCad 10 added in 2.3.0 (`KICAD10`)" (via resumo). Melhor candidato para gerar netlist/esquematico em codigo no KiCad 10. Qualidade visual do esquematico gerado: nao verificada.
- **kicad-sch-api**: https://pypi.org/pypi/kicad-sch-api/json — 0.5.6, 2025-11-19, MIT, "exact format preservation", "open in KiCAD 7/8" (README), MCP de 15 tools. Sem release em 11 meses; 9/10 nao verificado.
- **kiutils**: https://pypi.org/pypi/kiutils/json — 1.4.8, 2024-02-02, GPLv3, "KiCad 6.0 and up". Issues: https://api.github.com/repos/mvnmgrx/kiutils/issues. #120 (KiCad 8.0.4): salva esquematico errado (propriedades ocultas viram visiveis); #113 "Broken as of KiCAD 8?". PR #128 (2026-04-19, validado no 10.0.1) segue como PR. Evitar para 9/10.
- **kicad-skip**: https://pypi.org/pypi/kicad-skip/json — 0.2.5, 2024-02-16, LGPLv2+, "kicad 7+". Repo https://github.com/psychogenic/kicad-skip: 231 estrelas, push 2024-05-26, 28 issues. Parado. (O mixelpixx ainda o usa e contorna limites por injecao de S-expr.)
- **KiKit**: https://pypi.org/pypi/kikit/json — 1.8.1, 2026-08-05, MIT. **KiBot**: https://pypi.org/pypi/kibot/json — 1.9.1, 2026-07-28, GPLv3. Versoes de KiCad suportadas NAO constam no PyPI; nao verifiquei documentacao. Servem para panelizacao e automacao de exports/CI, nao para criar esquematico.
- **IPC API — resumo para KiCad 10**: so editor de PCB; exige GUI aberta; sem plot/export; esquematico e headless so no KiCad 11 (https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/). Um slide de status do projeto lista "IPC support for schematic editor API" sob recursos do esquematico da v10 (https://www.nextpcb.com/uploads/attach/blog/1.%20Seth%20Hillbrand%20-%20KiCad%20Project%20Status.pdf, so snippet de busca) — contradiz a documentacao oficial; prevalece a documentacao.

## 6. Recomendacao

1. **Nao depender de SWIG `pcbnew`** como caminho principal: deprecado desde o 9, remocao planejada no 11 (e ja ausente no nightly 10.99 segundo relato).
2. **Base da skill: `kicad-cli` 10** (ERC, DRC, netlist, BOM, Gerber, PDF/SVG, render). Nao exige GUI, ja instalado, estavel e documentado. Fonte do "tool call" dentro da skill: comandos Bash.
3. **Geracao de esquematico por codigo**: SKiDL 2.3.0 (declara KiCad 10) para o fluxo "circuito em Python -> netlist -> esquematico". Edicao fina de `.kicad_sch` existente: S-expression direto, mas validada sempre por `kicad-cli sch erc` e abrindo/exportando para detectar corrupcao. Evitar kiutils/kicad-skip (paradas).
4. **PCB**: netlist -> `.kicad_pcb` via KiCad GUI (Update PCB from Schematic) ou scripts; leitura/edicao viva por `kipy` so se o usuario aceitar KiCad aberto e instalar `kicad-python`; roteamento por Freerouting (DSN/SES) e um passo separado.
5. **MCP: opcional, nao no nucleo.** Custo de contexto (241-244 tools) vai contra a regra de 3 a 6 MCPs do template. Se quiser testar: `oaslananka/kicad-mcp-pro` com perfil `schematic_only` ou `minimal` (mira KiCad 10 e instala por `uvx`, mas exige Python >=3.13) ou `mixelpixx` (mais usado, MIT, tem JLCPCB+Freerouting, mas README so promete 9+ e tem issues abertas sobre o formato 10). Em qualquer caso avaliar numa copia de projeto.
6. **Reaproveitar**: `kicad-happy` (MIT, KiCad 10 "Full") como skill de revisao/BOM/sourcing em vez de reescrever; adaptar a parte de geracao a partir de ideias do circuit-synth (MIT) se necessario.
7. **Teste de aceitacao sugerido** (nao executado aqui): gerar um circuito simples (LED + resistor + regulador), rodar `kicad-cli sch erc`, exportar netlist e PDF, abrir no KiCad 10.0.0 e conferir se os fios conectam de verdade.

## 7. Armadilhas

- A versao instalada e 10.0.0; varios projetos foram verificados no 10.0.6/10.0.7. Diferencas entre patch releases nao foram avaliadas; considerar atualizar o KiCad.
- Contagens de tools divergem entre fontes: mixelpixx diz 244 no README e 216 na issue #345 (https://api.github.com/repos/mixelpixx/KiCAD-MCP-Server/issues).
- Versao de Python: kicad-mcp-pro pede >=3.13 (PyPI), o Python embarcado do KiCad pode ser mais antigo — versao do Python embarcado no 10.0.0 nao verificada.
- Esquematico gerado por LLM/automacao: o Seeed MCP avisa que fios podem nao formar conexao eletrica de verdade (via Glama, https://glama.ai/mcp/servers/mx8hlhuzi9, nao conferido). Sempre validar com ERC.
- `run_kicad_script` (lucatib) e tools similares executam Python arbitrario com os privilegios do usuario.
- `kipy` nao instalado: `pip install kicad-python` (modulo `kipy`); em KiCad 9/10 a IPC API tem que estar habilitada e o editor de PCB aberto.
- Estrelas e datas mudam; indices (vibeindex, claudemarketplaces, glama) sao de terceiros e divergem (ex.: kicad-happy 172 vs 846 vs 1377 estrelas conforme a fonte; vale a API do GitHub).
- Nao verificado: Konnect (Rust/AGPL), Seeed MCP, KiCad Copilot, repos anthropics/skills e awesome-claude-skills, compatibilidade KiKit/KiBot com KiCad 10, versao exata do Python embarcado.
