---
title: Familia de skills pcb-* para projeto de circuitos e PCB no KiCad 10
type: decisao
status: aprovado
created: 2026-10-12
updated: 2026-10-12
project: template_projetos
tags: [decisao, skills, hardware, kicad, tema/hardware]
---

# 2026-10-12 — Familia de skills `pcb-*` (KiCad 10)

## O que mudou

1. Cinco skills novas em `.claude/skills/` (50 → 55): `pcb-projeto` (porta de entrada: fases,
   portoes, pastas, alta tensao), `pcb-componentes`, `pcb-esquematico`, `pcb-layout`, `pcb-fabricacao`.
2. Toolkit unico em `.claude/skills/pcb-projeto/scripts/` (pacote `pcbkit`, so biblioteca padrao do
   Python; dois scripts rodam no Python do KiCad por causa do SWIG `pcbnew`), com testes `unittest`.
3. Assets: projeto KiCad modelo com net classes, `.kicad_dru` da JLCPCB (2 e 4 camadas) e de alta
   tensao, modelos de nota de hardware (diagrama de blocos, portao 1, portao 2, bring-up, aprovacao de
   alta tensao) e a spec da placa de exemplo usada na prova ponta a ponta.
4. Quatro fichas novas em `docs_projeto/referencias/`: `kicad-cli-e-formatos`, `kicad-mcp-e-skills`,
   `componentes-e-fabricacao-pcb`, `boas-praticas-pcb`.
5. `SKILLS.md` secao 7, `MCPS.md` secao 4.1 (MCP de KiCad como experimental), `CONVENCOES.md` (tipos
   `diagrama` e `simulacao`; properties `revisores`, `placa`, `revisao`, `fabricante`, `tensao_max_v`,
   `norma_seguranca`), READMEs de `docs_Template_Projeto/03_Hardware/` e vizinhos, `CLAUDE.md`.

## Decisoes do usuario

| Tema | Escolha |
|---|---|
| Estrutura | Familia de skills (contra a recomendacao de uma skill so com referencias) |
| Fabricante padrao | JLCPCB + LCSC |
| Fontes de componente | LCSC/JLC Basic + Mouser/DigiKey |
| Aceite | ERC/DRC zero + pacote de fabricacao + revisao humana registrada |
| Layout | Agente posiciona e roteia sinais simples com Freerouting; potencia, alta tensao, USB, RF com a pessoa |
| Alta tensao | Permitida com portao obrigatorio |
| Pastas | Fonte KiCad em `hardware/<placa>/`; notas em `03_Hardware/` |
| Entrega | So no template, sem commit, sem propagar para os derivados |

## Decisao de arquitetura (delegada ao agente)

**Nucleo = `kicad-cli` 10 + esquematico gerado em S-expression + SWIG `pcbnew` so onde o CLI nao
alcanca.** Motivos verificados:

- O KiCad 10 nao tem API headless de esquematico. A IPC API cobre so o editor de PCB e exige a GUI
  aberta; plugins de esquematico e modo headless chegam no KiCad 11 (dev-docs, ficha
  `kicad-mcp-e-skills`).
- `kicad-cli` 10 faz ERC, DRC (com paridade), netlist, BOM, Gerber, furacao, posicao, PDF, STEP e
  render, com codigo de saida confiavel. Nao faz "Update PCB from Schematic" nem Specctra DSN — dai o
  SWIG, isolado em `pcbkit/swig/`.
- O esquematico gerado usa **label por pino**: legivel e verificavel pela netlist exportada.

## Alternativas descartadas

- **MCP de KiCad no nucleo** (`mixelpixx/KiCAD-MCP-Server`, ~244 tools; `oaslananka/kicad-mcp-pro`,
  ~241): toda tool entra no prompt de toda sessao; contraria a regra de 3 a 6 MCPs do `MCPS.md`. O
  `mixelpixx` so promete KiCad 9+. Registrado como experimental no `MCPS.md` 4.1.
- **Vendorizar `aklofas/kicad-happy`** (MIT, 11 skills de analise): descricoes "ALWAYS trigger"
  colidem com a familia e sao ~100 mil linhas nao revisadas. Fica como plugin opcional de revisao
  (SKILLS.md secao 7).
- **SKiDL** para gerar esquematico: suporta o 10, mas a qualidade do desenho gerado nao foi
  verificada e acrescenta dependencia. **kiutils/kicad-skip**: parados e com relatos de arquivo
  corrompido. **circuit-synth/atopile**: outra stack.

## O que a verificacao mostrou (e mudou o plano)

- Bibliotecas de simbolo do KiCad 10 sao pastas `Lib.kicad_symdir/` com um arquivo por simbolo.
  Versoes de formato: sch 20260306, pcb 20260206, sym 20251024, mod 20260206.
- `.kicad_dru` invalido e **descartado em silencio** (DRC sai 0 sem aplicar regra nenhuma). Dai o
  `verificar.py dru` com regra-canario, usado tambem pelo portao.
- A ficha da JLC misturava anel de via e de furo de componente; a pagina relida separa: via 0,15/0,25
  mm; PTH 0,18 mm (2 camadas). Via-trilha 0,2 mm, furo-furo 0,2 mm, NPTH minimo 0,5 mm.
- jlcsearch: busca por texto devolve resultado irrelevante e so indexa peca com estoque na JLC; por
  codigo e confiavel. `buscar_lcsc.py` cai na API de detalhe da LCSC quando o codigo nao esta no indice.
- `easyeda2kicad` 1.0.1 funciona com o KiCad 10 depois de `sym/fp upgrade`, mas os tipos eletricos
  dos pinos vem errados — etapa de importacao assistida, nao fonte de verdade.

## Prova ponta a ponta

Executada em 2026-10-12 nesta maquina (KiCad 10.0.0, Freerouting 2.5.0 jar, Java 26), numa pasta
limpa com espaco e `&` no caminho, so com os scripts da familia, sobre a placa de exemplo
(`assets/exemplo/placa-exemplo.json`: entrada 12 V protegida, buck AP63203, ESP32-S3-WROOM-1,
DRV8871, gravacao UART, LED — 31 componentes, 6 blocos, 19 redes, codigos LCSC conferidos):

| Passo | Resultado |
|---|---|
| `novo_projeto.py --docs` | projeto e notas de 03_Hardware criados |
| `gerar_esquematico.py` | `.kicad_sch` gerado |
| `verificar.py erc --estrito` | 0 erros, 0 avisos |
| `verificar.py netlist` | 19 redes com exatamente os pinos da spec |
| `pcb_do_esquematico.py` | 31 footprints ligados, paridade vazia |
| `rotear.py` padrao (copia) | sinais roteados; 14 ligacoes de `Power` deixadas para a pessoa |
| `rotear.py --ignorar-classes ""` | 0 ligacoes faltando |
| `verificar.py drc --paridade` | **0 erros**; 2 avisos de serigrafia da antena em balanco (propositais) |
| `verificar.py dru` | `.kicad_dru` aceito |
| `exportar_fab.py` | zip (9 camadas + 2 furacoes), BOM e CPL JLC, BOM completa, PDF, STEP, renders |
| `portao_liberacao.py` com nota em rascunho | BLOQUEADO (status, revisores, 25 itens abertos) |
| Nota aprovada (simulacao no scratchpad) + `--liberar` | `releases/rev-A/` com manifesto SHA-256 |
| `--liberar` de novo | recusado: revisao congelada |

Suite final: 368 testes `unittest` (2 pulados: rede real). A prova foi refeita depois das correcoes
da revisao, com o mesmo resultado.

## Revisao independente

O `reviewer` (Opus, so leitura) achou 7 defeitos que **bloqueavam a entrega**, todos no portao de
liberacao e quase todos reproduzidos: qualquer nota aprovada servia (inclusive a do portao 1 como
liberacao e a de liberacao como aprovacao de alta tensao); net class `HV` nao detectada com padrao
regex ou classe composta (`HV,Power`); severidades rebaixadas no `.kicad_pro` sumiam com violacoes do
relatorio; `revisores: null` contava como revisor; itens `1. [ ]` e em callout passavam; regra HV
conferida so pelo texto; tensao negativa ou NaN escapava. Mais 10 achados menores (sobrescrever
esquematico editado na GUI, `Sem_LCSC` ignorado com LCSC presente, `--saida` forjando release, path
traversal em `--rev`, limite AC de 42,4 Vpk, entre outros).

Todos corrigidos com teste que falhava antes (fatias 5A e 5B). Na conferencia final apareceram mais
tres, tambem corrigidos: `verificar.py drc --paridade` aprovava placa com footprint faltando (no
10.0.0 a paridade sai como aviso); peca fora do arquivo de posicao ficava na BOM da JLC sem
coordenada; `clearance_mm: 3,2` (virgula decimal) na nota HV era ignorado em silencio.

**Fica em aberto (decisao do usuario):** o portao humano depende de o agente nao escrever
`status: aprovado` nem `revisores` numa nota `type: gate`. Isso esta nas skills como regra, mas nada
impede tecnicamente. Mitigacao possivel: um hook `PreToolUse` que nega Edit/Write que introduza
`status: aprovado` em nota de gate.

**Limites medidos** (documentados nas skills): o posicionamento automatico e ponto de partida (nao
gira pecas nem fecha o laco do buck); com cobre ja travado o Freerouting pode nao fechar ligacoes
(rotear em duas etapas deixou 2 ligacoes abertas); busca por texto do jlcsearch nao e confiavel;
chamadas autenticadas a Mouser/DigiKey nao foram testadas (sem chave); upload real na JLC nao foi
feito; a "Update PCB from Schematic" da GUI nao foi testada sobre a placa gerada.

## Consequencias

- **KiCad 11** remove o SWIG: `pcb_do_esquematico.py` e `rotear.py` terao de migrar para a IPC API.
- Numeros marcados "conferir" nas fichas (IPC-2221 B2 em 101-150 V, taxas da JLC, imposto de
  importacao como PJ) nao viraram regra dura.
- Os projetos derivados **nao** receberam a familia; a propagacao e o commit ficam a criterio do
  usuario. Ao propagar, copiar as cinco pastas juntas.
