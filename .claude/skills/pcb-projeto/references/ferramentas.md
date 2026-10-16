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
