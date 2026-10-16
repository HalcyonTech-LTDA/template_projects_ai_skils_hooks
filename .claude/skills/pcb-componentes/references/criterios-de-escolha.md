# Criterios de escolha de componentes

As folgas abaixo sao **pratica de engenharia adotada pela Halcyon**, nao numero de norma. Quando o
datasheet ou uma norma do produto pedir mais, vale o mais restritivo.

## 1. Folga (derating) por tipo de peca

| Peca | Regra | Por que |
|---|---|---|
| Resistor | Potencia dissipada <= 50% da nominal; tensao <= nominal do encapsulamento | Temperatura e deriva; resistor 0603 tipico e 0,1 W |
| Capacitor ceramico (MLCC) | Tensao nominal >= 2x a de trabalho; X7R/X5R para filtro e desacoplamento; C0G para temporizacao e cristal | Perda de capacitancia por DC bias, pior em encapsulamento pequeno |
| Capacitor eletrolitico | Tensao >= 1,5x; temperatura 105 C; ripple de corrente conferido | Vida util cai com temperatura e ripple |
| Diodo | Tensao reversa >= 1,5x a maxima vista; corrente media com folga de 50% | Transientes de comutacao |
| MOSFET | Vds >= 1,5x a tensao do barramento (2x com carga indutiva); Vgs maximo respeitado com margem; Rds(on) especificado na tensao de gate real (logic level para 3,3 V) | Picos de comutacao; MOSFET "4,5 V" meio aberto com 3,3 V esquenta |
| Regulador linear | Dissipacao (Vin - Vout) x I dentro do encapsulamento com a temperatura ambiente maxima | SOT-223 sem cobre dissipa pouco mais de 1 W |
| Regulador chaveado | Corrente de saida nominal >= 1,3x o pico; Vin maximo acima do transiente da fonte | Margem para pico de motor e para variacao da fonte |
| Conector | Corrente por pino com folga de 50%; tensao nominal; ciclos de insercao | Contato aquece antes de falhar |
| Fusivel / PTC | Corrente de disparo acima do pico normal e abaixo da capacidade da trilha e do conector | Fusivel protege a fiacao, nao o circuito |
| TVS | VRWM >= tensao maxima normal da linha; tensao de grampeamento abaixo do maximo absoluto do que protege | TVS abaixo da tensao de trabalho conduz sempre |

## 2. Encapsulamento

| Situacao | Escolha |
|---|---|
| Montagem SMT pela JLCPCB | Passivos 0603; CIs SOIC/SOT/TSSOP/QFN conforme necessidade |
| Montagem manual de prototipo | Passivos 0805; evitar QFN sem pad acessivel; nada abaixo de 0603 |
| Potencia (driver, regulador) | Encapsulamento com pad termico (PowerPAD, SO-8 com pad, TO-252) e vias termicas |
| Conector de campo (cabo externo) | Borne de parafuso ou conector com trava; THT para esforco mecanico |

Limites da montagem JLC (ficha, via resumo): Economic aceita minimo 0402 e passo de CI 0,4 mm;
Standard vai a 0201 e 0,35 mm.

## 3. Comprabilidade

- **Ciclo de vida:** Active em Mouser ou DigiKey. NRND e EOL so com justificativa escrita e plano de
  substituicao; Obsolete nunca. "Active" nao garante fornecimento — peca de fonte unica pode parar.
- **Segunda fonte:** para peca critica, anote um equivalente drop-in (mesmo encapsulamento e
  pinagem) no campo de observacao da BOM. Passivos padrao tem dezenas de fontes; CI especifico nao.
- **Estoque:** pelo menos 10x a quantidade do lote planejado no fornecedor escolhido. Parametro do
  projeto — ajuste ao volume real.
- **Padronizacao:** reuse o mesmo valor e encapsulamento sempre que possivel (todos os 100 nF iguais,
  todos os pull-ups de 10 k iguais). Menos linhas na BOM, menos pecas Extended, menos erro de montagem.

## 4. Pecas recorrentes em mecatronica (pontos de partida, conferir estoque na hora)

Estes sao **candidatos** comuns para iniciar a busca, nao recomendacao fechada. Sempre confirme com
`buscar_lcsc.py`/`buscar_distribuidor.py` e com o datasheet.

| Funcao | Candidatos para comecar a busca | Observacao |
|---|---|---|
| Buck 12-24 V → 3,3/5 V, ate ~1 A | AP63203 / AP63205 (Diodes), TPS54202 / TPS563200 (TI), MP1584 (MPS) | Conferir Vin max contra transiente da fonte |
| LDO 5 → 3,3 V baixa corrente | AMS1117-3.3, AP2112K-3.3, XC6206 | AMS1117 exige capacitor de saida com ESR adequado |
| Protecao de inversao | P-MOSFET (ex.: AO3401A, ate ~30 V com clamp de Vgs) ou controlador de diodo ideal (LM74500-Q1) | Vgs maximo de MOSFET pequeno costuma ser +-12 V: zener de clamp |
| MCU com Wi-Fi/BLE | ESP32-S3-WROOM-1 (modulo certificado) | Antena na borda com area de exclusao |
| MCU sem radio | STM32G0/G4, RP2040 | Guia de hardware do fabricante por serie |
| Driver de motor DC escovado | DRV8871 (ate ~3,6 A pico, 45 V), DRV8833 (dois motores pequenos) | Pad termico e capacitor de volume |
| Driver de motor de passo | TMC2209 (silencioso, UART), DRV8825, A4988 | Datasheet oficial para layout termico |
| Acionamento de rele/solenoide | MOSFET N logic level (ex.: AO3400A) + diodo de roda livre | Ver supressao na skill pcb-esquematico |
| RS-485 | MAX3485 / SP3485 (3,3 V), THVD1450 | Terminacao e polarizacao conforme a rede |
| CAN | TCAN1042, SN65HVD230 | Terminacao dividida nas pontas |
| USB-serial | CH340C, CP2102N | CH340C dispensa cristal |
| ESD em USB/dados | USBLC6-2SC6, TPD2E2U06 | |
| TVS em entrada 12/24 V | SMBJ15A/SMBJ28A (VRWM acima da tensao normal) | Conferir corrente de surto esperada |

## 5. Sinais de alerta numa peca

- Datasheet so em chines ou sem secao de valores maximos absolutos.
- Fabricante sem distribuidor autorizado ocidental (Mouser/DigiKey/Farnell) — dificil achar segunda fonte.
- Estoque concentrado num unico vendedor de marketplace.
- Encapsulamento proprietario que nao existe na biblioteca do KiCad nem no `easyeda2kicad`.
