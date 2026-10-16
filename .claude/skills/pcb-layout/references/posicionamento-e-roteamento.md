# Posicionamento e roteamento

Origem: **[ficha]** = `docs_projeto/referencias/boas-praticas-pcb.md`; **[datasheet]** = siga a secao
de layout da peca; **[pratica]** = pratica adotada pela Halcyon.

## Ordem de posicionamento

1. **Fixados pela mecanica:** contorno, furos de fixacao, conectores (na borda, com o lado de encaixe
   para fora), botoes, LEDs, display, antena. Confira contra o desenho da caixa antes de seguir.
2. **Potencia:** entrada e protecao junto ao conector de alimentacao; buck; driver de motor junto ao
   conector do motor. O caminho de corrente alta deve ser curto e nao passar pela regiao do MCU.
3. **MCU/modulo** e seus satelites (desacoplamento, cristal, reset, boot).
4. **Interfaces** (transceptores RS-485/CAN, USB, ESD) colados aos seus conectores.
5. **O resto** (LEDs, pull-ups, test points), sem atrapalhar os anteriores.

Agrupar por bloco funcional e o ponto de partida do `pcb_do_esquematico.py`; o ajuste fino e humano.

## Por bloco

### Desacoplamento [ficha: ST AN4488, ADI MT-101, Espressif]
- Capacitor pequeno (100 nF) o mais perto possivel do pino de alimentacao, do mesmo lado do CI.
- Via de GND direto no pad do capacitor ao plano; trilha curta e larga, sem via no meio do caminho
  entre capacitor e pino.
- Capacitor de volume do trilho perto do ponto de entrada da alimentacao naquele bloco.

### Buck [ficha: TI LMR36006 sec. 11.1]
- **Laco de entrada minimo:** capacitor de entrada colado em VIN e GND do CI. E o laco de corrente
  pulsada; area dele = ruido irradiado.
- No de chaveamento (SW → indutor) curto e largo o suficiente, sem area de cobre a mais (e antena).
- Divisor de realimentacao junto ao pino FB, longe do SW e do indutor; trilha de FB fina e curta.
- Plano de GND solido sob o conversor, com vias proximas aos pads de GND.

### Driver de motor [ficha: TI DRV8871 sec. 10.1]
- Capacitor de volume e ceramico perto de VM, minimizando o caminho de corrente alta pelo driver.
- Pad termico soldado ao plano de GND da face superior, com varias vias para um plano grande na
  face inferior. Area de cobre e o dissipador.
- As vias termicas sob o pad exposto ligam **cheio** a zona, sem alivio — alivio ali corta o caminho
  do calor. O `pcb_do_esquematico.py` forca isso em todo pad passante com o mesmo numero de um pad
  SMD do footprint (padrao dos footprints `..._ThermalVias`); confira se voce trocar o footprint.
- Trilhas de VM e saidas largas (net class `Power`), varias vias nas trocas de camada.
- Resistor de sense/limite (ILIM) com retorno curto ao GND do driver.

### Modulo de radio (ESP32-S3-WROOM-1) [ficha: Espressif]
- Antena na borda da placa, de preferencia projetando para fora ou na quina.
- **Area de exclusao do datasheet sem cobre em nenhuma camada**, sem componentes, sem trilha, sem
  zona — inclua uma keepout zone no KiCad.
- Pad de GND do modulo com muitas vias ao plano (a Espressif pede no minimo 9 no pad do chip; no
  modulo, siga o datasheet dele).
- Nada metalico (parafuso, conector, bateria) perto da antena.

### Cristal [ficha: Espressif; ST AN2867]
- Colado no MCU (trilhas curtas), capacitores de carga dos dois lados, cercado por GND com vias.
- Nenhum sinal passando por baixo nem perto; nenhuma via nas trilhas do cristal.

### USB [pratica]
- D+ e D- como par diferencial (mesmo comprimento, paralelos, juntos), sem via se possivel, por cima
  de plano de GND continuo. USB 2.0 full speed tolera muito; high speed pede impedancia de 90 ohm.
- ESD colado ao conector, antes de qualquer outra coisa no caminho.

### Conectores de campo (cabo externo) [ficha: ROHM TVS; pratica]
- TVS/ESD entre o conector e o CI protegido, perto do conector, com retorno curto ao GND.
- Furos de fixacao do conector e alivio mecanico; borne de parafuso THT para corrente alta.

## Roteamento

- Rotear primeiro: potencia e GND (zonas), pares diferenciais, cristal, sinais analogicos. Depois os
  digitais lentos (aqui entra o Freerouting).
- Trilha de sinal sobre plano continuo; troca de camada de sinal rapido acompanhada de via de GND
  proxima (o retorno tambem troca de camada).
- Cantos a 45 graus (estetica e consistencia; em frequencia de mecatronica nao ha ganho eletrico).
- Evite trilhas paralelas longas entre potencia chaveada e sinal sensivel.
- Zonas: GND nas duas faces em placa de 2 camadas, com alivio termico (thermal relief) nos pads
  passantes (THT) para a solda pegar e ligacao cheia nos pads SMD e de dissipacao — e como o
  `pcb_do_esquematico.py` cria as zonas. Se o DRC acusar `starved_thermal` (raio do alivio bloqueado),
  abra espaco em volta do pad em vez de trocar para ligacao cheia.

## DFM, DFA e DFT [ficha: JLCPCB, Advanced Circuits; resto pratica]

- **Serigrafia:** referencia legivel de cada componente (>= 1 mm de altura), fora dos pads; marca de
  pino 1, catodo e polaridade visivel depois de montado; nome da placa, revisao e data.
- **Fiduciais** em montagem SMT com passo fino: 3 globais nao colineares (1-2 mm de cobre, abertura de
  mascara de 2-4 mm), longe da borda.
- **Test points** em cada trilho de alimentacao, GND e sinais de depuracao (UART, SWD), acessiveis com
  ponta de prova.
- **Distancia da borda:** componentes a 1 mm ou mais da borda fresada (mais se a placa for em painel
  com V-cut); nada de componente alto colado ao conector.
- **Orientacao:** componentes iguais na mesma orientacao quando possivel (montagem e inspecao).
- **Painel:** a JLC paneliza se pedido; painel proprio (KiKit) so com motivo.
