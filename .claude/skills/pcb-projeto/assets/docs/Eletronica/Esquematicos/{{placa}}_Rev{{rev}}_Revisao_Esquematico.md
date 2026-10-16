---
title: {{placa}} Rev {{rev}} · Revisao do esquematico (portao 1)
type: gate
gate: esquematico
status: rascunho
created: {{data}}
updated: {{data}}
project: {{projeto}}
module: 03_Hardware
layer: hardware
placa: {{placa}}
revisao: {{rev}}
revisores: []
date:
tags: [gate, layer/hardware, module/hardware]
---

# {{placa}} Rev {{rev}} · Revisao do esquematico

Portao 1: o layout so comeca com esta nota em `status: aprovado`, `revisores` preenchido por quem
revisou (pessoa, nao o agente) e nenhum item `- [ ]` em aberto. Item que nao se aplica:
`- [x] N/A — motivo`.

## Evidencia automatica

- Comando: `python .claude/skills/pcb-projeto/scripts/verificar.py erc hardware/{{placa}}/{{placa}}.kicad_sch --estrito`
- Comando: `python .claude/skills/pcb-projeto/scripts/verificar.py netlist hardware/{{placa}}/{{placa}}.kicad_sch --spec hardware/{{placa}}/spec/{{placa}}.json`
- Resultado (cole o resumo):
- PDF do esquematico:

## Checklist

### Geral

- [ ] Title block com projeto, placa, revisao, data e empresa
- [ ] ERC estrito zerado (sem erro nem aviso); cada aviso aceito foi excluido no KiCad e esta justificado em "Achados"
- [ ] Netlist confere com a spec (`verificar.py netlist`)
- [ ] Todo componente com Valor, Footprint, Datasheet, MPN, Fabricante e LCSC (ou DNP justificado)
- [ ] Redes com nome significativo; nenhuma rede que sai de um bloco com nome automatico `Net-(...)`

### Alimentacao

- [ ] Orcamento de potencia fecha com margem de 30% ou mais em cada trilho
- [ ] Faixa de entrada de cada regulador cobre a tensao minima, maxima e transientes da fonte
- [ ] Dissipacao de cada regulador calculada e aceitavel para o encapsulamento
- [ ] Protecao de entrada: fusivel ou PTC, inversao de polaridade e TVS se a alimentacao vem de cabo externo
- [ ] Capacitores de entrada e saida dos reguladores como o datasheet pede (valor, dieletrico, tensao com folga para a perda por DC bias)
- [ ] Desacoplamento: capacitor local em cada pino de alimentacao de CI e capacitor de volume por trilho

### MCU e logica

- [ ] Reset/EN com o circuito do guia do fabricante (ex.: ESP32-S3: RC 10 k / 1 uF no CHIP_PU)
- [ ] Pinos de strapping/boot no estado correto na partida; botao de BOOT quando o MCU pede
- [ ] Interface de gravacao e depuracao acessivel (UART, SWD ou USB)
- [ ] Pinagem dos perifericos conferida no datasheet (TX/RX cruzados, pinos com funcao fixa, ADC no pino certo)
- [ ] Pull-ups de I2C presentes uma unica vez no barramento (2,2 k a 10 k conforme velocidade e capacitancia)
- [ ] Niveis logicos compativeis (3,3 V x 5 V); tolerancia a 5 V confirmada no datasheet quando usada
- [ ] Pinos nao usados tratados como o datasheet manda; flag de nao conectado so onde o pino e realmente livre

### Potencia e cargas

- [ ] Toda carga indutiva (rele, solenoide, motor, bobina) com supressao de transiente adequada
- [ ] Driver de motor: corrente de pico, limite de corrente (ILIM/sense) e capacitor de volume conferidos
- [ ] MOSFET: Vgs maximo respeitado, acionamento total na tensao do GPIO (logic level), dissipacao por Rds(on)
- [ ] MOSFET acionado por GPIO com resistor de gate e pull-down para estado definido na partida

### Interfaces externas

- [ ] Todo conector externo com protecao ESD/TVS e contra curto ou sobretensao coerente com o que se liga nele
- [ ] RS-485/CAN com terminacao e polarizacao definidas (jumper se a posicao na rede variar)
- [ ] USB-C como device com resistores de 5,1 k nos CC e ESD nos dados
- [ ] Pinagem de cada conector documentada (numero do pino, sinal, vista)

### Alta tensao

- [ ] N/A ou nota `{{placa}}_Rev{{rev}}_Aprovacao_Alta_Tensao.md` aberta e em andamento

### Documentacao

- [ ] Diagrama de blocos e orcamento de potencia atualizados
- [ ] Calculos (divisores, RC, corrente de LED, ILIM, realimentacao do buck) escritos como texto no esquematico ou nesta nota

## Achados da revisao

| # | Achado | Acao | Resolvido |
|---|---|---|---|
| 1 | | | |
