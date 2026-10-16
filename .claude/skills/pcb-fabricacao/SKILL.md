---
name: pcb-fabricacao
description: Gera e libera o pacote de fabricacao de uma placa KiCad 10 para a JLCPCB — Gerber e furacao, BOM e CPL (pick-and-place) no formato da JLC, BOM completa com MPN, PDF do esquematico, STEP, render — e aplica o portao de liberacao (ERC e DRC zerados, BOM completa, revisao humana registrada, portao extra de alta tensao) antes de gravar a revisao em releases/. Use ao exportar gerbers, gerar BOM ou CPL, pedir placa ou montagem SMT, "manda pra JLC", "pacote de fabricacao", "liberar a revisao", conferir rotacao de componentes, estimar custo de fabricacao ou registrar um pedido.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, AskUserQuestion
version: 1.0
---

# /pcb-fabricacao — pacote verificado e liberacao registrada

Parte da familia `pcb-*` (roteiro em `pcb-projeto`). Scripts em `.claude/skills/pcb-projeto/scripts/`.

**Pre-condicao:** DRC sem erros com paridade (`pcb-layout`). Exportar Gerber de placa com violacao e
mandar defeito para a fabrica com selo de "pronto".

## Fluxo

1. **Pacote de trabalho**
   ```bash
   S=.claude/skills/pcb-projeto/scripts
   python $S/exportar_fab.py hardware/<placa> --rev A
   ```
   Escreve em `hardware/<placa>/fab/rev-A/` (ignorado pelo git):

   | Arquivo | Para que |
   |---|---|
   | `<placa>-rev-A-gerber.zip` | Gerber (X2, Protel, mm, mascara subtraida da serigrafia) + `.gbrjob` + furacao Excellon (`PTH.drl` e `NPTH.drl`) — upload na JLC |
   | `<placa>-rev-A-bom-jlc.csv` | `Comment, Designator, Footprint, JLCPCB Part #`, agrupada por valor + footprint + LCSC |
   | `<placa>-rev-A-cpl-jlc.csv` | `Designator, Mid X, Mid Y, Rotation, Layer` em mm, `Layer` = `Top`/`Bottom` |
   | `<placa>-rev-A-bom.csv` | BOM completa: item, valor, referencias, quantidade, footprint, MPN, fabricante, LCSC, Mouser, DigiKey, datasheet |
   | `<placa>-rev-A-esquematico.pdf` | Revisao e documentacao |
   | `<placa>-rev-A-mapa-furos-PTH.pdf` / `-NPTH.pdf` | Conferencia da furacao (fora do zip, para o upload nao ler como camada) |
   | `<placa>-rev-A.step`, `render-top.png`, `render-bottom.png` | Mecanica e conferencia visual (se falharem, viram aviso) |
   | `manifesto.json` | SHA-256 de cada arquivo, versao do KiCad, data, comandos |

   Exemplo real da BOM JLC: `10k,"R1,R2,R3,R5,R6",R_0603_1608Metric,C25804`. O zip nao e
   reproduzivel byte a byte (o Gerber X2 grava a data de criacao): o hash vale para o arquivo enviado,
   nao para uma reexportacao.
2. **Conferencia visual** — abra os renders e os Gerbers (visualizador online da JLC no upload, ou
   GerbView do KiCad). Procure: serigrafia sobre pad, contorno fechado, furos presentes, mascara nos
   lugares certos, texto da revisao.
3. **Portao 2**
   ```bash
   python $S/portao_liberacao.py hardware/<placa> \
     --checklist "docs_projeto/<Projeto>/03_Hardware/Eletronica/Gerber/<placa>_RevA_Liberacao_Fabricacao.md"
   ```
   Bloqueia (codigo != 0) e diz por que, se faltar qualquer um:
   - ERC sem erros nem avisos e DRC sem erros com paridade, com o `.kicad_dru` validado (roda tudo
     de novo — nao confia em execucao anterior). Paridade e conexao faltando bloqueiam em **qualquer**
     severidade: no KiCad 10.0.0 footprint faltando e campo do simbolo diferente do footprint saem
     como aviso. Editou um campo no esquematico? Atualize a placa antes de liberar. Os demais avisos
     de DRC nao bloqueiam, mas saem listados para a pessoa justificar na nota;
   - `tensao_max_v` finito na spec do projeto (`null`, ausente ou nao numerico bloqueia) e a revisao
     da spec igual a pedida;
   - severidades do `.kicad_pro`: regra critica de ERC/DRC rebaixada para aviso ou `ignore` bloqueia
     (senao a violacao some do relatorio); rebaixamentos menores e exclusoes saem listados e vao para
     o manifesto;
   - todo componente montado com `MPN` e `LCSC` — ou com o campo `Sem_LCSC` dizendo o motivo (peca
     soldada a mao ou comprada fora): ela fica na BOM completa e sai da BOM e do CPL da JLC;
   - a nota de liberacao (`type: gate`, `gate: liberacao`) **desta placa e desta revisao** com
     `status: aprovado`, `revisores` preenchido e nenhum item em aberto (`- [ ]`, `1. [ ]` ou dentro de
     callout; `- [x] N/A` sem motivo conta como aberto). A nota do portao 1 nao serve;
   - **alta tensao** (gatilhos em `pcb-projeto/references/alta-tensao.md`: tensao acima do limite DC
     ou AC, redes `HV` na spec ou na netlist): nota `gate: alta-tensao` aprovada, arquivo diferente da
     de liberacao, e regras `HV` validas no `.kicad_dru` com `clearance` e `creepage`.

   O agente prepara a nota, cola a evidencia e percorre o checklist com a pessoa. **Quem marca
   `aprovado` e preenche `revisores` e a pessoa.** Se o portao bloquear por falta de aprovacao, diga
   isso e pare — nao edite a nota para passar.
4. **Liberacao**
   ```bash
   python $S/exportar_fab.py hardware/<placa> --rev A --liberar --checklist "<mesma nota>"
   ```
   Roda o portao e, so se passar, copia o conjunto de fabricacao para
   `hardware/<placa>/releases/rev-A/` com `manifesto.json` (SHA-256 de cada arquivo, versao do KiCad,
   data). E esse zip que vai para a fabrica.
5. **Pedido** — parametros e armadilhas em `references/pedido-jlcpcb.md`. Registre numero do pedido,
   custo e prazo na nota de liberacao e em `08_Producao/Custos_BOM/`.
6. **Depois do pedido** — revisao congelada. Sugira ao usuario o commit e a tag
   `hw-<placa>-rev-a` (commitar e decisao dele) e abra a nota de bring-up em `Prototipagem/Rev_A/`.

## Armadilhas que o DRC nao pega

- **Rotacao no CPL:** a origem e a rotacao zero de alguns footprints do KiCad nao batem com as da
  biblioteca da JLC. O preview 3D do pedido mostra; corrija ali ou ajuste a rotacao do componente e
  regenere. Confira **todo** componente polarizado (diodo, LED, CI, eletrolitico).
- **Peca Extended e falta de estoque:** o upload da BOM mostra o que falta. Troque pela Basic
  equivalente (`buscar_lcsc.py --basic`) e regenere a partir da spec, nao edite o CSV.
- **DNP x `Sem_LCSC`:** DNP e "nao montado" — sai de todas as BOMs e do CPL. Peca que vai na placa
  mas nao pela JLC (borne soldado a mao, peca consignada) leva o campo `Sem_LCSC` com o motivo: fica
  na BOM completa (para compra) e sai da BOM/CPL da JLC — mesmo que tenha `LCSC` (comum em simbolo
  importado pelo `easyeda2kicad`); o `Sem_LCSC` vence. Peca marcada "excluir dos arquivos de posicao"
  no KiCad tambem sai da BOM e do CPL da JLC (sem coordenada a JLC nao monta) e fica na BOM completa.
- **Spec do projeto desatualizada:** o portao le `hardware/<placa>/spec/<placa>.json`. Gerar o
  esquematico a partir de uma spec de fora deixa a do projeto como esqueleto (`tensao_max_v: null`) e
  o portao bloqueia. A spec usada fica dentro do projeto.
- **Numero do pedido na serigrafia:** a JLC imprime um codigo na placa; escolha a posicao
  ("specify location" com o texto `JLCJLCJLCJLC` na serigrafia) ou pague para remover.
- **Imposto:** compra como empresa paga regime diferente de pessoa fisica (ver `pcb-componentes`).

## Alternativa manual

O plugin Fabrication Toolkit (bennymeg, v5.3+ com suporte ao KiCad 10) gera Gerber, BOM e CPL no
formato da JLC por um botao na GUI e le o mesmo campo `LCSC`. Serve para conferir o `exportar_fab.py`
ou para quem prefere a GUI. A liberacao pelo portao continua obrigatoria.

## Referencias

- `references/pedido-jlcpcb.md` — parametros do pedido, montagem Economic x Standard, custos, PCBWay.
- Ficha: `docs_projeto/referencias/componentes-e-fabricacao-pcb.md`.
- Comandos `kicad-cli` usados por baixo: `docs_projeto/referencias/kicad-cli-e-formatos.md`.
