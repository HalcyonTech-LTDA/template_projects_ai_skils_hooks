---
title: Hardware — _Template_Projeto
area: Hardware
tags: [readme, template, projeto]
project: _Template_Projeto
created: 2026-04-22
updated: 2026-10-12
created_by:
updated_by:
module: 01_Projetos
type: readme
status: aprovado
---

# Hardware

Eletronica (diagrama de blocos, esquematicos, layout, BOM, fabricacao), mecanica e prototipagem.

> Template. Ao duplicar para um novo projeto, substituir `project: _Template_Projeto` pelo nome real e popular as subpastas.

## Como o hardware e feito: familia de skills `pcb-*`

O projeto de placas usa **KiCad 10** e cinco skills do Claude Code, que vivem em `.claude/skills/`
do repositorio (catalogo e precedencia em [[../../SKILLS|SKILLS.md]], secao 7):

| Fase | Skill | Prova de pronto | Nota nesta pasta |
|---|---|---|---|
| Requisitos e arquitetura | `pcb-projeto` | Diagrama de blocos e orcamento de potencia fechados | `Eletronica/Esquematicos/<placa>_Diagrama_de_Blocos.md` |
| Componentes | `pcb-componentes` | MPN, LCSC, datasheet e footprint conferidos | — (campos na spec) |
| Esquematico | `pcb-esquematico` | ERC zero e netlist igual a spec | **Portao 1:** `Eletronica/Esquematicos/<placa>_Rev<R>_Revisao_Esquematico.md` |
| Layout | `pcb-layout` | DRC sem erros com paridade de esquematico (avisos justificados) | (checklist dentro da nota do portao 2) |
| Fabricacao | `pcb-fabricacao` | `portao_liberacao.py` passa | **Portao 2:** `Eletronica/Gerber/<placa>_Rev<R>_Liberacao_Fabricacao.md` |
| Bring-up | `pcb-projeto` | Trilhos e blocos testados | `Prototipagem/Rev_<R>/<placa>_Rev<R>_Bring_Up.md` |

Para comecar uma placa, peca ao Claude "projetar a placa de ..." (a `pcb-projeto` dispara) ou rode:

```bash
python .claude/skills/pcb-projeto/scripts/diagnostico.py
python .claude/skills/pcb-projeto/scripts/novo_projeto.py hardware --nome <placa> \
  --docs "docs_projeto/<Projeto>/03_Hardware"
```

O segundo comando cria a fonte KiCad em `hardware/<placa>/` e as notas acima nesta pasta.

## Onde cada coisa fica

| Conteudo | Local | Versionado |
|---|---|---|
| Fonte KiCad (`.kicad_pro/sch/pcb/dru`), spec JSON, bibliotecas do projeto | `hardware/<placa>/` na raiz do repositorio | Sim |
| Saidas de trabalho (Gerber, BOM, renders) | `hardware/<placa>/fab/` | Nao |
| Pacote liberado para a fabrica, com manifesto SHA-256 | `hardware/<placa>/releases/rev-<R>/` | Sim |
| Diagrama de blocos, PDF do esquematico, notas de revisao | `03_Hardware/Eletronica/` (esta pasta) | Sim |
| STEP da placa para a caixa | `03_Hardware/Mecanica/CAD_3D/` | Sim |
| Bring-up e achados por revisao | `03_Hardware/Prototipagem/Rev_<R>/` | Sim |
| Custo de BOM por volume, fornecedores, pedido | `08_Producao/` | Sim |
| Datasheets e app notes usados | `10_Referencias/Hardware/` (links) | Sim |

A fonte KiCad fica fora do vault de notas de proposito: arquivo gerado e binario nao poluem o
Obsidian, e o que a equipe le (diagrama, PDF, revisoes) fica aqui.

## Regras que valem para toda placa

- **Dois portoes humanos.** Layout so comeca com o portao 1 aprovado; pedido so sai com o portao 2
  aprovado. Notas `type: gate` com `status: aprovado`, `revisores` preenchido por pessoa e nenhum
  item `- [ ]` em aberto. O agente prepara e verifica; nunca aprova.
- **Alta tensao** (rede 127/220 VAC, acima de 60 V DC ou acima de 42,4 V de pico em AC): portao
  extra com nota de aprovacao de alta tensao — e a primeira pergunta e se um modulo AC-DC
  certificado nao resolve.
- **Revisao liberada e congelada.** Mudanca abre a revisao seguinte (`Rev_B`), com o bring-up da
  anterior listando o porque.
- **Fabricante padrao:** JLCPCB com pecas LCSC (Basic primeiro); Mouser/DigiKey para prototipo e
  ciclo de vida.

Fichas de apoio (normas, capacidades da JLC, importacao, `kicad-cli`) em
[[../../referencias/README|docs_projeto/referencias/]], secao "Eletronica e PCB".
