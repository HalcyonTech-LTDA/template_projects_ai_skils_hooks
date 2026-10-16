---
name: pcb-esquematico
description: Cria, edita e revisa esquematicos eletricos (.kicad_sch) no KiCad 10 a partir de uma especificacao JSON do circuito, com ERC e prova de conectividade pela netlist, e traz circuitos de referencia de mecatronica (entrada protegida, buck/LDO, ESP32-S3, STM32, RP2040, drivers de motor, rele e solenoide, entrada isolada, 4-20 mA, RS-485, CAN, USB-C, I2C). Use para desenhar ou gerar esquematico, diagrama eletrico, ligar componentes, montar "o circuito de" alguma funcao, rodar ERC, conferir netlist, revisar esquematico existente ou preparar a revisao do portao 1.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebFetch, AskUserQuestion
version: 1.0
---

# /pcb-esquematico — da spec ao .kicad_sch provado

Parte da familia `pcb-*` (roteiro em `pcb-projeto`; pecas em `pcb-componentes`). Scripts em
`.claude/skills/pcb-projeto/scripts/`.

## Como o esquematico nasce

O agente **nao desenha fio por fio**. Ele escreve a spec do circuito (`hardware/<placa>/spec/<placa>.json`:
componentes, redes, blocos) e o `gerar_esquematico.py` produz o `.kicad_sch` no estilo
**label por pino**: cada pino ganha um fio curto terminado num label com o nome da rede, ou num
simbolo de power (GND, +3V3, +12V). Componentes ficam agrupados por bloco funcional, cada bloco numa
regiao com titulo.

Por que assim: e o estilo que fica legivel **e** e verificavel mecanicamente. Fio roteado entre
simbolos gerado por maquina vira emaranhado e esconde ligacao errada; label por pino deixa cada
conexao escrita com o nome da rede, e a netlist prova que a ligacao existe.

## Fluxo

1. **Pecas decididas** pela `pcb-componentes` (MPN, LCSC, footprint e pinagem conferidos).
2. **Circuito de cada bloco** a partir do circuito de aplicacao do datasheet e de
   `references/circuitos-de-referencia.md`. Valores calculados (divisor, RC, limite de corrente)
   ficam anotados em `notas` do bloco na spec.
3. **Escreva a spec** — contrato completo em `references/spec-json.md`. Pontos que mais erram:
   - Pino por **numero** sempre que houver nomes repetidos (`U1.GND` liga todos os GND; e o que se
     quer para alimentacao, nao para sinal).
   - Todo pino sem ligacao tem de estar em `nao_conectar` — o gerador falha de proposito se nao
     estiver, para nao esconder pino esquecido.
   - Pad exposto (EP) ligado a rede que o datasheet manda.
   - `pwr_flag` nas redes que entram por conector (o ERC precisa saber quem alimenta a rede).
4. **Gere e verifique:**
   ```bash
   S=.claude/skills/pcb-projeto/scripts
   python $S/gerar_esquematico.py hardware/<placa>/spec/<placa>.json -o hardware/<placa>/<placa>.kicad_sch
   python $S/verificar.py erc hardware/<placa>/<placa>.kicad_sch --estrito
   python $S/verificar.py netlist hardware/<placa>/<placa>.kicad_sch --spec hardware/<placa>/spec/<placa>.json
   ```
   **Pronto = ERC sem erros nem avisos (`--estrito`) e netlist batendo com a spec.** Sem `--estrito`
   o `verificar.py erc` so reprova por erro. Aviso que for aceito de proposito vira exclusao no KiCad
   (janela do ERC → excluir, com comentario) e entra na nota de revisao com o motivo — assim o
   `--estrito` continua zerado e o aceite fica escrito. ERC sozinho nao prova nada: dois labels com o
   mesmo nome errado passam no ERC. A comparacao da netlist exportada pelo `kicad-cli` com a spec e
   que mostra que cada rede tem exatamente os pinos declarados (e os componentes e footprints).
5. **PDF para revisao humana:**
   ```bash
   kicad-cli sch export pdf hardware/<placa>/<placa>.kicad_sch -o <03_Hardware>/Eletronica/Esquematicos/<placa>_Rev<R>.pdf
   ```
6. **Portao 1.** Preencha a evidencia na nota `<placa>_Rev<R>_Revisao_Esquematico.md` e percorra o
   checklist dela item por item, anotando achados. Quem aprova e uma pessoa. O checklist e a fonte
   unica das verificacoes de esquematico — leia-o em
   `.claude/skills/pcb-projeto/assets/docs/Eletronica/Esquematicos/` se a nota ainda nao existir.

## Convencoes de desenho

- **Nomes de rede:** trilhos com sinal e tensao (`+12V`, `+3V3`, `VMOT`); sinais em MAIUSCULAS com
  sublinhado e funcao (`UART0_TX`, `I2C_SDA`, `MOTOR_IN1`, `EN_BUCK`). Sinal ativo em baixo com
  sufixo `_N` (`RESET_N`). TX/RX nomeados do ponto de vista do MCU.
- **Referencias por bloco:** numere em sequencia dentro de cada bloco (entrada R1-R9, MCU R10-R29...)
  quando a placa tiver mais de ~30 componentes; ajuda a achar na placa.
- **Fluxo da esquerda para a direita:** entrada a esquerda, carga a direita; alimentacao em cima.
- **Title block** com projeto, placa, revisao, data e empresa (vem da spec).
- **Valores com unidade e o que importa:** `100nF 50V X7R`, `10k 1%`, `22uF 25V`.

## Editar esquematico existente

Antes de mexer, leia o `README.md` da placa para saber o modo:

- **Modo spec:** edite a spec e regenere. Nunca edite o `.kicad_sch` a mao nesse modo — a proxima
  geracao apaga. O `gerar_esquematico.py` recusa sobrescrever um arquivo salvo pela GUI (`generator`
  diferente de `pcbkit`); `--sobrescrever` forca — so use com o modo manual descartado de proposito.
- **Modo manual** (alguem ja editou na GUI): nao regenere. Para mudanca pequena, edite o S-expression
  com cuidado (nunca reaproveite `uuid`; nunca apague `lib_symbols` em uso) ou peca a pessoa para
  fazer na GUI; depois ERC e netlist de novo. Para mudanca grande, proponha a edicao na GUI e
  descreva exatamente o que ligar.

Revisar esquematico de terceiro: rode ERC, exporte a netlist (`kicad-cli sch export netlist`) e o PDF,
e percorra o checklist do portao 1; confira cada CI contra o circuito de aplicacao do datasheet.

## Limites desta versao do gerador

- Folha unica (sem hierarquia). Placa que nao cabe numa folha A3 legivel deve virar modo manual com
  folhas hierarquicas feitas na GUI, ou ser dividida em placas.
- Posicionamento por bloco em grade: legivel, nao artistico. Quem quiser o desenho bonito arruma na
  GUI — e passa para o modo manual.

## Referencias

- `references/spec-json.md` — contrato completo da spec, com exemplo.
- `references/circuitos-de-referencia.md` — blocos de mecatronica com valores de partida e fonte.
- `references/formato-kicad-sch.md` — o que o KiCad 10 exige no arquivo (para editar a mao com seguranca).
- Ficha de boas praticas com fontes: `docs_projeto/referencias/boas-praticas-pcb.md`.
