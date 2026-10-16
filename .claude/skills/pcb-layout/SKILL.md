---
name: pcb-layout
description: Faz o layout de PCB no KiCad 10 — placa criada a partir do esquematico, contorno e furos, posicionamento por bloco funcional, stack-up de 2 ou 4 camadas, net classes e largura de trilha pela corrente, regras de DRC da JLCPCB (.kicad_dru), planos de terra, vias termicas, isolacao de alta tensao, roteamento dos sinais simples com Freerouting e DRC com paridade de esquematico. Use ao posicionar componentes, rotear, definir regras de projeto, largura de trilha, stack-up, plano de GND, antena, layout de buck ou de driver de motor, rodar DRC, "faz a placa", "roteia", "arruma o layout".
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, AskUserQuestion
version: 1.0
---

# /pcb-layout — posicionar com criterio, rotear o simples, provar com DRC

Parte da familia `pcb-*` (roteiro em `pcb-projeto`). Scripts em `.claude/skills/pcb-projeto/scripts/`.
Os dois scripts SWIG (`pcb_do_esquematico.py`, `rotear.py`) rodam no **Python do KiCad**; o
`diagnostico.py` imprime o caminho dele (`$KPY` abaixo).

**Pre-condicao:** portao 1 aprovado (nota de revisao do esquematico com `status: aprovado`). Layout
em cima de esquematico nao revisado e retrabalho contratado.

## Divisao de trabalho (decisao do projeto)

| Quem | O que |
|---|---|
| Agente | Placa a partir do esquematico, contorno, furos, net classes, regras JLC, posicionamento por bloco, planos de GND, roteamento dos **sinais simples** com Freerouting, DRC |
| Pessoa | Revisao do posicionamento, roteamento de **potencia** (net class `Power`), **alta tensao** (`HV`), USB e outros pares diferenciais, RF/antena, analogico sensivel, no de chaveamento de buck, cristal |

O Freerouting nao sabe o que e laco de corrente, retorno, impedancia nem isolacao. Ele liga pontos.
Por isso o `rotear.py` deixa `Power` e `HV` fora por padrao, e o resultado dele sempre passa por olho
humano no portao 2.

## Fluxo

1. **Placa a partir do esquematico**
   ```bash
   S=.claude/skills/pcb-projeto/scripts
   "$KPY" $S/pcb_do_esquematico.py hardware/<placa>/<placa>.kicad_sch \
     --spec hardware/<placa>/spec/<placa>.json -o hardware/<placa>/<placa>.kicad_pcb \
     --largura 80 --altura 60 --furos M3
   ```
   Footprints ligados aos simbolos pelo uuid, como a GUI faz (o "Update PCB from Schematic" deve
   continuar funcionando depois; nao testado na GUI), agrupados por bloco da spec, conectores na
   borda, modulo de radio com a antena em balanco, contorno retangular, furos de fixacao, net classes
   da spec, regras JLC e zonas de GND nas duas faces (alivio termico em pad passante, ligacao cheia
   em SMD). Placa que ja tem **qualquer** item (footprint, trilha, contorno ou furo desenhado a mao)
   so e refeita com `--sobrescrever` — e ai perde tudo. O posicionamento e ponto
   de partida: nao gira pecas, nao cola o desacoplamento nos pinos, nao fecha o laco do buck. Contorno nao retangular ou com recortes da caixa: desenhe na GUI em
   `Edge.Cuts` ou importe o DXF da mecanica.
2. **Posicionamento** — o mais importante do layout; o roteamento herda as qualidades e os defeitos
   dele. Regras em `references/posicionamento-e-roteamento.md`. Primeiro o que e fixado pela mecanica
   (conectores, furos, LEDs, botoes, antena), depois os blocos de potencia, depois o MCU e o resto.
   Gere imagem para conferir: `kicad-cli pcb render --side top -o fab/top.png <placa>.kicad_pcb`.
   **Peca a revisao do posicionamento a pessoa antes de rotear.**
3. **Potencia e criticos (pessoa)** — a pessoa roteia `Power`, `HV`, pares diferenciais, antena,
   buck e cristal na GUI, ou dita ao agente exatamente o caminho. O `rotear.py` trava as trilhas que
   ja existem antes de chamar o Freerouting e so importa dele as redes que ainda tinham ligacao
   faltando — o trabalho da pessoa fica intacto. **Limite medido:** com cobre ja travado o
   Freerouting fecha pior. Rotear sinais primeiro e potencia depois deixou 2 ligacoes de `+12V_SYS`
   abertas no exemplo; potencia primeiro e sinais depois deixou o `BST_BUCK` aberto. O `rotear.py`
   lista o que ficou e sai com 1. Saidas: a pessoa fecha a ligacao na GUI; ou abre espaco no
   posicionamento e roda de novo; ou roteia tudo numa passada (`--ignorar-classes ""`, que fechou o
   exemplo com DRC sem erros) e a pessoa **refaz** a potencia por cima — nunca aceite potencia do
   Freerouting sem revisar largura, laco e vias.
4. **Sinais simples (agente)**
   ```bash
   "$KPY" $S/rotear.py hardware/<placa>/<placa>.kicad_pcb            # exclui Power e HV
   "$KPY" $S/rotear.py hardware/<placa>/<placa>.kicad_pcb --ignorar-classes Power,HV,USB
   ```
   Exporta Specctra DSN, roda o Freerouting sem interface, importa o SES e reenche as zonas. Exige
   Java e o jar do Freerouting (`FREEROUTING_JAR`); detalhes e limites em `references/freerouting.md`.
5. **DRC com paridade**
   ```bash
   python $S/verificar.py drc hardware/<placa>/<placa>.kicad_pcb --paridade
   python $S/verificar.py dru hardware/<placa>/<placa>.kicad_dru
   ```
   **Pronto = zero erros** com zonas reenchidas e paridade com o esquematico (nenhum footprint
   sobrando ou faltando, nenhuma rede divergente), e o `.kicad_dru` aceito pelo KiCad (`dru` —
   arquivo invalido e descartado em silencio). "Unconnected items" e erro: placa com ratsnest
   pendente nao esta pronta. **Avisos** (quase sempre de serigrafia) o `verificar.py drc` lista; cada
   um e corrigido, ou excluido no KiCad com comentario, ou justificado na nota do portao 2. Exemplo
   real: a serigrafia da antena do ESP32-S3 em balanco fora da placa gera `silk_edge_clearance` — e
   proposital. `--estrito` reprova tambem por aviso, para quem quiser zero absoluto.
6. **Revisao do layout** — o checklist de layout esta na nota de liberacao do portao 2
   (`<placa>_Rev<R>_Liberacao_Fabricacao.md`). Percorra item por item e anote; quem aprova e uma pessoa.

## Regras padrao (JLCPCB, com folga)

O projeto nasce com `<placa>.kicad_dru` copiado de `assets/kicad/jlc-2camadas.kicad_dru` ou
`jlc-4camadas.kicad_dru`. Os valores de board e das net classes ficam acima do minimo da JLC — placa
no limite da fabrica e placa com rendimento pior. Tabela completa, larguras por corrente e stack-up em
`references/regras-e-stackup.md`.

| Item | Padrao do projeto | Minimo JLC (2026-10-12) |
|---|---|---|
| Trilha / espaco (board) | 0,15 / 0,15 mm | 0,10 / 0,10 mm |
| Net class `Default` | 0,25 mm / 0,2 mm | — |
| Net class `Power` | 0,8 mm / 0,3 mm (ajuste pela corrente) | — |
| Net class `HV` | 1,0 mm / 2,5 mm (ponto de partida; ver alta tensao) | — |
| Via | furo 0,3 / diametro 0,6 mm | 0,15 / 0,25 mm |
| Anel de furo de componente (2 camadas) | >= 0,18 mm | 0,18 mm absoluto, 0,25 recomendado |
| Via ↔ trilha / furo ↔ furo | 0,2 / 0,25 mm | 0,2 / 0,2 mm |
| Cobre ↔ borda | 0,3 mm | 0,2 mm fresado, 0,4 mm V-cut |
| Serigrafia | texto >= 1,0 mm, linha >= 0,15 mm | mesmos |

## Alta tensao

Se a placa tem a net class `HV`, concatene `assets/kicad/alta-tensao.kicad_dru` ao `.kicad_dru` do
projeto, siga `pcb-projeto/references/alta-tensao.md` e nunca deixe o Freerouting rotear `HV`.

## Referencias

- `references/regras-e-stackup.md` — capacidades da JLC, largura por corrente (formula da IPC-2221),
  vias, stack-up de 2 e 4 camadas, impedancia, `.kicad_dru` comentado.
- `references/posicionamento-e-roteamento.md` — posicionamento por bloco, buck, driver de motor,
  modulo de radio, cristal, USB, conectores, planos, DFM.
- `references/freerouting.md` — instalacao, o que ele roteia bem e mal, parametros, como revisar.
- Fichas: `docs_projeto/referencias/boas-praticas-pcb.md` e `componentes-e-fabricacao-pcb.md`.
