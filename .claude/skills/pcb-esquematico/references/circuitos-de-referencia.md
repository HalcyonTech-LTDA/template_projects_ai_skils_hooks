# Circuitos de referencia para mecatronica

Pontos de partida, nao circuito final. **O datasheet da peca escolhida vence sempre** — em especial o
circuito de aplicacao tipico e a secao de layout. Origem de cada valor:

- **[ficha]** — fonte citada em `docs_projeto/referencias/boas-praticas-pcb.md` (lida via resumo em
  2026-10-12; conferir o original antes de virar regra dura).
- **[datasheet]** — o valor depende da peca; tire do datasheet dela.
- **[pratica]** — pratica de engenharia adotada pela Halcyon, sem norma especifica por tras.

## Indice

1. Entrada de alimentacao protegida (12/24 V)
2. Conversao: buck e LDO
3. ESP32-S3-WROOM-1
4. STM32
5. RP2040
6. Motor DC com DRV8871
7. Motor de passo
8. Rele, solenoide e carga indutiva
9. Entrada digital isolada 24 V
10. Entrada 4-20 mA
11. RS-485
12. CAN
13. USB-C (device, USB 2.0)
14. I2C, botoes, LEDs, NTC

---

## 1. Entrada de alimentacao protegida (12/24 V)

Ordem dos elementos, do borne para dentro: **fusivel/PTC → protecao de inversao → TVS → capacitor de
volume**.

- **Fusivel ou PTC** em serie com o positivo. Corrente de disparo acima do pico normal da placa (motor
  partindo) e abaixo da capacidade de trilha e conector. [pratica]
- **Inversao de polaridade com P-MOSFET** [ficha: TI SLVAE57B, secao 4.1]:
  - Dreno no positivo de entrada, fonte para o lado da carga, gate ao GND por resistor (10 k a 100 k).
  - Com polaridade certa, o diodo de corpo conduz na partida, a fonte sobe, Vgs fica negativo e o
    MOSFET satura. Invertida, Vgs fica positivo e ele desliga.
  - **Zener de clamp entre gate e fonte** (catodo na fonte) quando a tensao de entrada pode passar do
    Vgs maximo do MOSFET — MOSFET SOT-23 pequeno costuma ter Vgs max de +-12 V, e 12 V nominal com
    tolerancia ja passa. Zener de 10 V e o resistor de gate limitando a corrente do zener. [pratica]
  - O P-MOSFET nao bloqueia corrente reversa da carga para a entrada (o Schottky bloqueia). Para
    corrente alta, controlador de diodo ideal com N-MOSFET (ex.: LM74500-Q1) perde menos. [ficha]
  - Alternativa simples para corrente baixa: diodo Schottky em serie (perde ~0,3-0,5 V). [pratica]
- **TVS** do positivo protegido ao GND: VRWM acima da tensao normal maxima, tensao de grampeamento
  abaixo do maximo absoluto do regulador. [ficha: ROHM]
- **Capacitor de volume** (eletrolitico ou polimero, 47-220 uF, tensao >= 1,5x) perto do ponto em que
  a corrente se divide entre regulador e driver de motor. [pratica]

Redes sugeridas: `+12V` (borne), `VIN_PROT` (apos fusivel), `+12V_SYS` (apos protecao).

## 2. Conversao: buck e LDO

**Buck** (12/24 V → 5 ou 3,3 V) [datasheet + ficha TI LMR36006 sec. 11.1]:
- Siga o circuito de aplicacao do datasheet: capacitores de entrada ceramicos colados em VIN/GND,
  capacitor de bootstrap, indutor (valor e corrente de saturacao do datasheet), capacitores de saida,
  divisor de realimentacao se a versao for ajustavel.
- Corrente de saida nominal >= 1,3x o pico do trilho. [pratica]
- No esquematico, anote em `notas` do bloco: frequencia, indutor escolhido, ripple esperado.
- Layout (vai para `pcb-layout`): laco de entrada minimo, no SW curto, FB longe do SW.

**LDO** (5 → 3,3 V, ou pos-regulacao de trilho analogico):
- Dissipacao `(Vin - Vout) x I`. Acima de ~0,5 W em SOT-23/SOT-89 ou ~1 W em SOT-223 sem area de
  cobre, troque por buck. [pratica]
- Capacitores de entrada e saida como o datasheet pede; alguns LDO (AMS1117) exigem faixa de ESR no
  capacitor de saida. [datasheet]

## 3. ESP32-S3-WROOM-1

[ficha: Espressif ESP32-S3 Hardware Design Guidelines — layout e schematic checklist]
- **Alimentacao 3,3 V:** 10 uF + 100 nF junto ao pino 3V3 do modulo; trilho capaz de picos de
  transmissao Wi-Fi (o buck deve aguentar ~500 mA de pico com folga). [ficha + pratica]
- **EN (CHIP_PU):** pull-up de 10 k ao 3V3 e 1 uF ao GND (atraso de partida); nunca flutuando. [ficha]
- **Boot:** GPIO0 com pull-up (10 k) e botao para GND (BOOT); sem capacitor grande no GPIO0. Botao de
  RESET no EN para GND e conveniente. [ficha + pratica]
- **Strapping pins** (GPIO0, GPIO3, GPIO45, GPIO46): nao acione cargas que forcem nivel nesses pinos
  durante a partida. [ficha]
- **Gravacao:** UART0 (U0TXD/U0RXD) num header com GND, 3V3, EN e GPIO0, ou USB nativo (GPIO19 D-,
  GPIO20 D+) direto ao conector USB-C com ESD. Confira os numeros de pino no simbolo do modulo.
  [datasheet]
- **Antena:** modulo na borda da placa, area de exclusao do datasheet sem cobre em nenhuma camada
  (vai para `pcb-layout`).

## 4. STM32

[ficha: ST AN4488 para STM32F4; cada serie tem a sua — AN5096 (G0), AN4555 (L4), AN4661 (F7),
AN4938 (H74x/75x)]
- VDD: 100 nF por pino VDD + um capacitor de volume (4,7-10 uF) por encapsulamento (F4). [ficha]
- VDDA: 100 nF + 1 uF; filtro com ferrite opcional se o ADC importa. [ficha]
- VCAP (series com regulador interno de nucleo, F4/F7): capacitores com o valor e ESR do datasheet. [ficha]
- NRST: capacitor de 100 nF ao GND (o pull-up e interno); botao opcional. [pratica + datasheet]
- BOOT0: pull-down de 10 k (partida pela flash), com jumper ou botao para o bootloader. [pratica]
- SWD: header com SWDIO, SWCLK, NRST, 3V3 e GND (Tag-Connect ou 2x5 1,27 mm). [pratica]
- Cristal HSE: capacitores de carga `CL1 = CL2 = 2 x (CL_cristal - C_parasita)`, com C_parasita de
  2-5 pF; AN2867 para margem de ganho. [pratica + ficha AN2867]

## 5. RP2040

[ficha: guia "Hardware design with RP2040" (RP-008279-DS) — corpo nao lido na pesquisa; **conferir
no guia** antes de usar os valores]
- 100 nF por pino de alimentacao (IOVDD, DVDD) junto aos pinos; capacitores no regulador interno
  (VREG_IN/VREG_VOUT) conforme o guia.
- Flash QSPI externa (o RP2040 nao tem flash), cristal de 12 MHz, resistores em serie no USB conforme
  o guia.
- Botao BOOTSEL (QSPI_SS ao GND) para gravar via USB.

## 6. Motor DC com DRV8871

[ficha: TI SLVSCY9B, secao 10.1; datasheet para os valores]
- VM: capacitor de volume (eletrolitico, tensao >= 1,5x VM) e 100 nF ceramico colados nos pinos.
  O datasheet remete o valor de volume a teste de sistema; 47-100 uF e partida comum. [ficha + pratica]
- ILIM: resistor ao GND define o limite de corrente pela equacao do datasheet — calcule e anote em
  `notas`. [datasheet]
- IN1/IN2 em GPIOs com PWM; estado de partida definido (pull-down) para o motor nao girar no boot.
  [pratica]
- Pad termico (PowerPAD) ao GND com varias vias para plano grande (vai para `pcb-layout`). [ficha]
- Saidas OUT1/OUT2 ao borne do motor; capacitor de 100 nF nos terminais do motor reduz ruido de
  escova (no motor, nao na placa, quando possivel). [pratica]

## 7. Motor de passo

TMC2209, DRV8825, A4988: siga o circuito de aplicacao do datasheet oficial (resistores de sense,
capacitores de VM e de carga interna, pinos de microstep). A pesquisa nao leu os datasheets
oficiais — nao use valores de wiki ou modulo de terceiros. Pontos fixos: [pratica]
- Capacitor de volume grande em VM (motor de passo devolve energia na desaceleracao).
- Resistores de sense de baixa indutancia, retorno de corrente curto ao GND do driver.
- Nunca desconecte o motor com o driver energizado (documente no manual).

## 8. Rele, solenoide e carga indutiva

- **Acionamento low-side:** N-MOSFET logic level (Rds(on) especificado em Vgs = 2,5 ou 3,3 V), resistor
  de gate de 47-100 ohm e pull-down de 10-100 k no gate. [pratica]
- **Supressao obrigatoria:** diodo em antiparalelo com a bobina (catodo no positivo). Diodo simples
  atrasa a abertura do rele e reduz a vida do contato; para abertura rapida use diodo + zener em serie
  (ou resistor), conforme a TE. [ficha: TE relay coil suppression]
- **Lado do contato:** carga AC indutiva no contato pede snubber RC ou varistor no contato; carga de
  rede no contato e alta tensao — ver portao em `pcb-projeto`. [pratica]
- Rele com isolacao bobina-contato especificada quando o contato chaveia rede. [pratica]

## 9. Entrada digital isolada 24 V (sensor industrial, fim de curso)

[pratica]
- Resistor serie dimensionado para 3-5 mA no LED do optoacoplador na tensao nominal; potencia do
  resistor com folga (24 V x 5 mA = 120 mW → resistor 0805/1206).
- Diodo em antiparalelo com o LED do opto (protege contra inversao) ou opto bidirecional.
- Lado do MCU: pull-up e capacitor pequeno de filtro; o GND do lado de campo **nao** se liga ao GND
  logico (senao a isolacao some).
- TVS no lado de campo se o cabo for longo.

## 10. Entrada 4-20 mA

[pratica]
- Resistor shunt de precisao (0,1%) ao GND: 150 ohm da 0,6-3,0 V, compativel com ADC de 3,3 V.
  Potencia: 20 mA^2 x 150 = 60 mW (use folga).
- Resistor serie + TVS/diodos de clamp antes do ADC; RC de filtro antialiasing.
- Fonte de alimentacao do loop (24 V) com limite de corrente se o sensor for 2 fios.

## 11. RS-485

[ficha: TI SLYT080/SLYT514, Renesas AN1986]
- Transceptor de 3,3 V (MAX3485/SP3485/THVD1450); DE e /RE ligados juntos num GPIO.
- Terminacao de 120 ohm **so nas duas pontas** da rede — use jumper ou chave se a placa puder estar
  no meio do barramento.
- Polarizacao failsafe: transceptor moderno com failsafe interno dispensa; senao, pull-up em A e
  pull-down em B dimensionados para garantir >= 200 mV com a terminacao (exemplo da ficha: ~510-560 ohm
  com 5 V). Confira no datasheet do transceptor.
- TVS para RS-485 nas linhas A/B no conector.

## 12. CAN

[ficha: TI SLLSEQ7F e guias SLLU3xx]
- Transceptor CAN (TCAN1042, SN65HVD230 para 3,3 V).
- Terminacao **dividida** nas pontas: dois resistores de 60 ohm casados e capacitor de 4,7-100 nF do
  ponto medio ao GND (filtro de modo comum). Jumper se a posicao variar.
- ESD/TVS nas linhas CANH/CANL.

## 13. USB-C (device, USB 2.0)

[pratica + datasheet do conector]
- CC1 e CC2 **cada um** com seu resistor de 5,1 k ao GND (um resistor compartilhado nao funciona com
  cabo C-C).
- ESD (USBLC6-2 ou similar) em D+/D- junto ao conector; as duas fileiras de D+/D- do conector
  ligadas entre si.
- VBUS com capacitor (ate ~10 uF no conector, limite da especificacao USB) e TVS se a placa puder
  receber surto.
- Blindagem: ao GND direto ou por RC (1 M em paralelo com 4,7 nF) — escolha e anote. [pratica]

## 14. I2C, botoes, LEDs, NTC

- **I2C:** pull-ups uma vez por barramento — 4,7 k a 100 kHz, 2,2 k a 400 kHz como partida; recalcule
  pela capacitancia do barramento. Cabo longo pede buffer (P82B715) ou outra interface. [pratica]
- **Botao:** pull-up (interno ou 10 k) + RC de debounce (10 k / 100 nF) se o firmware nao debounce;
  TVS/ESD se o botao for externo a caixa. [pratica]
- **LED indicador:** `R = (Vcc - Vf) / I`; 2 mA ja e visivel em LED moderno; ex.: 3,3 V, LED vermelho
  (Vf ~2 V), 2 mA → 680 ohm. [pratica]
- **NTC:** divisor com resistor fixo igual a resistencia do NTC na temperatura de interesse; RC de
  filtro antes do ADC; referencia do divisor no mesmo trilho de referencia do ADC. [pratica]
