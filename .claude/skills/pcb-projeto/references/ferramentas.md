# Ferramentas: o que a familia usa, o que ficou de fora e por que

Fatos com fonte nas fichas `docs_projeto/referencias/kicad-mcp-e-skills.md` e
`docs_projeto/referencias/kicad-cli-e-formatos.md` (verificadas em 2026-10-12).

## O nucleo: `kicad-cli` + scripts proprios

| Precisa de | Como a familia faz | Por que |
|---|---|---|
| ERC, DRC, netlist, BOM, Gerber, furacao, posicao, PDF, STEP, render | `kicad-cli` 10 | Oficial, headless, codigo de saida confiavel com `--exit-code-violations` |
| Criar o esquematico | `gerar_esquematico.py` escreve o `.kicad_sch` em S-expression | O KiCad 10 nao tem API de esquematico. A IPC API cobre so PCB e exige a GUI aberta; plugin de esquematico e modo headless so no KiCad 11 |
| Criar a placa a partir do esquematico | `pcb_do_esquematico.py` com o `pcbnew` (SWIG) do Python do KiCad | O "Update PCB from Schematic" (F8) nao existe no CLI do 10 |
| Rotear sinais simples | `rotear.py`: Specctra DSN → Freerouting → SES, via SWIG | `kicad-cli pcb export` nao tem DSN no 10 |
| Achar simbolo/footprint | `buscar_biblioteca.py` nas bibliotecas instaladas | Evita `lib_id` inventado, o erro mais comum de agente |
| Achar peca comprável | `buscar_lcsc.py` (jlcsearch, sem chave), `buscar_distribuidor.py` (Mouser/DigiKey, com chave) | Estoque, preco e ciclo de vida reais |

Os scripts usam so a biblioteca padrao do Python. Os dois SWIG rodam no Python do KiCad
(`<KiCad>/bin/python.exe`); o `diagnostico.py` imprime o caminho.

## Risco conhecido: KiCad 11

O SWIG `pcbnew` foi deprecado no KiCad 9 e a remocao esta planejada para o KiCad 11. Quando o 11
sair, `pcb_do_esquematico.py` e `rotear.py` precisam migrar para a IPC API (`kicad-python`/`kipy`),
que no 11 ganha modo headless pelo `kicad-cli` e cobertura do editor de esquematico. Tudo que e
`kicad-cli` e formato de arquivo continua valendo. O codigo SWIG esta isolado em
`scripts/pcbkit/swig/` justamente para essa troca ser local.

## MCP de KiCad: opcional, fora do nucleo

| Servidor | Situacao em 2026-10-12 |
|---|---|
| `mixelpixx/KiCAD-MCP-Server` | O mais usado (~2,6 mil estrelas, MIT). ~244 tools; README promete KiCad 9+, issue aberta sobre simbolo gravado com token do 9. Tem fios de esquematico, Freerouting e busca JLCPCB |
| `oaslananka/kicad-mcp-pro` | Mira o KiCad 10. ~241 tools com perfis (`minimal`, `schematic_only`). Exige Python 3.13+ (`uvx`) |
| `lamaalrajih/kicad-mcp` | So analise; parado desde 2025-10 |

Ficou fora do nucleo porque toda tool de MCP ligado entra no prompt de toda sessao, usada ou nao, e
240 tools contrariam a regra de 3 a 6 servidores do `docs_projeto/MCPS.md`. Os scripts entregam o
mesmo resultado sem custo de contexto e com prova pelo `kicad-cli`.

Quando faz sentido ligar: sessao exploratoria em que a pessoa quer conversar com a placa aberta na
GUI. Use o `kicad-mcp-pro` com perfil `minimal`, em escopo `local`, e desligue ao terminar.

## `aklofas/kicad-happy`: plugin opcional de revisao profunda

Conjunto de 11 skills (MIT) de **analise**: revisao de esquematico e layout, SPICE, EMC, termica,
BOM e busca em DigiKey/Mouser/LCSC/element14. Nao gera nem edita arquivo. Ficou fora do template
porque as descricoes dela disputam gatilho com a familia (a skill `bom` diz "ALWAYS trigger" para
qualquer sourcing) e porque sao ~100 mil linhas que nao revisamos.

Quem quiser uma segunda opiniao antes do portao 2 pode instalar no escopo do usuario
(`/plugin marketplace add aklofas/kicad-happy`) e rodar a revisao dela sobre o projeto. Precedencia:
para gerar, editar, verificar e liberar, a familia `pcb-*` vence; `kicad-happy` so como revisao extra.

## `copperheadhq/copperhead`: agente de terceiros, referencia e verificacao extra

Agente de IA em CLI (TypeScript, Apache-2.0, v0.12.0 em 2026-10-15, criado em 2026-07) que edita
`.kicad_sch`/`.kicad_pcb` reais e roda ERC/DRC pelo `kicad-cli` ate passarem. Pede KiCad >= 8
(KiCad 10 e Windows nao verificados), Node >= 20, git e um backend de LLM proprio. Ficha:
`docs_projeto/referencias/copperhead.md`.

| Comando | Precisa de LLM? | Uso aqui |
|---|---|---|
| `copperhead check` | Nao (sem rede) | Segunda opiniao de ERC, DRC e drift antes dos portoes 1 e 2. Nao substitui os scripts da familia |
| `copperhead score schematic` | Nao | Nota de legibilidade do esquematico gerado, como sinal extra na revisao humana |
| `copperhead do` / `create` | Sim | **Nao usar** numa sessao com as skills `pcb-*`: e um segundo agente disputando a mesma tarefa, com custo de modelo proprio |
| MCP stdio | — | Experimental e instavel. Mesma regra dos MCPs de KiCad acima: escopo `local`, so exploracao |

Ficou fora do nucleo porque e pre-1.0, nao roteia (decisao do projeto), nao cobre fabricacao para a
JLC nem escolha de pecas no ROADMAP, e nao tem KiCad 10 confirmado. Precedencia: para gerar,
editar, verificar e liberar, a familia `pcb-*` vence.

Ideias que valem trazer para os scripts, sem copiar codigo: snapshot git antes de editar com
rollback automatico se ERC/DRC piorar, e uma nota de legibilidade do esquematico.

## Alternativas consideradas para gerar esquematico

- **SKiDL 2.3.0** (Python, MIT): suporta KiCad 5 a 10, gera netlist e esquematico. Descartado como
  padrao porque o desenho gerado nao foi verificado e adiciona dependencia; continua boa opcao para
  quem prefere descrever circuito em Python.
- **circuit-synth**: gera `.kicad_sch`/`.kicad_pcb` a partir de Python e traz agentes de Claude Code;
  README fala em KiCad 8+, sem commits desde 2026-03.
- **kiutils / kicad-skip**: parados desde 2024 e com relatos de arquivo corrompido a partir do KiCad 8.
  Nao usar.
- **atopile / diodeinc pcb (Zener)**: linguagens proprias de descricao de hardware; outra stack.

## Fabrication Toolkit (plugin da GUI)

O plugin `bennymeg/Fabrication-Toolkit` (v5.3+ com suporte ao KiCad 10) gera Gerber, BOM e CPL no
formato da JLC por um botao na GUI. E a alternativa manual ao `exportar_fab.py`; os dois leem o campo
`LCSC` do simbolo.
