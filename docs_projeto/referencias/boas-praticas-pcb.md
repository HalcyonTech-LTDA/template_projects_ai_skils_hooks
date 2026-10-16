---
title: Boas praticas de projeto de circuitos e PCB — normas, app notes e checklists
source: https://www.ipc.org/
type: referencia
status: aprovado
created: 2026-10-12
updated: 2026-10-12
verificado_em: 2026-10-12
tags: [referencia, pcb, eletronica, boas-praticas, tema/hardware]
---

# Boas praticas de projeto de circuitos e PCB

Levantamento para o capitulo de circuitos/PCB da skill de mecatronica. Convencao de confianca usada abaixo:

- **[lido]** = o texto da pagina foi lido (via WebFetch, que resume; trechos entre aspas vem do resumo e **nao foram conferidos com `curl`**).
- **[snippet]** = so vi resultado de busca/resumo, sem abrir a fonte.
- **[secundaria]** = nao e a norma/fabricante; e terceiro reproduzindo.
- **[nao lido]** = a fonte primaria existe mas nao consegui ler o corpo (PDF binario, timeout, paywall).

Normas IPC sao pagas. **Nenhuma norma IPC foi lida na fonte.** Todo numero de norma abaixo vem de fonte secundaria e deve ser conferido antes de virar regra "dura" na skill.

## 1. Normas IPC

| Norma | O que governa | Fonte |
|---|---|---|
| IPC-2221 (B; ha rev. C de dez/2023) | Projeto generico de PCB, inclui tabela 6-1 de espacamento eletrico por tensao | https://pcbsync.com/ipc-2221/ [secundaria] cita C = dez/2023; https://resources.altium.com/p/using-an-ipc-2221-calculator-for-high-voltage-design [secundaria] |
| IPC-2152 (2009) | Capacidade de corrente de condutor; substitui os graficos da 2221 | https://pcdandf.com/pcdesign/index.php/2009-archive-articles/5305-the-new-ipc-2152 [snippet], https://circuitsassembly.com/ca/editorial/menu-new-indust-prod/17617-ipc-releases-ipc-2152-standard.html [snippet] |
| IPC-7351B | Padroes de land pattern (footprint), niveis de densidade | https://docs.jitx.com/en/latest/jitxlib-standard/jitxlib.landpatterns.ipc.html [snippet, secundaria] |
| IPC-A-610 | Aceitabilidade visual do conjunto montado | https://www.circuitassembly.com/j-std-001-explained/ [snippet, secundaria] |
| J-STD-001 | Requisitos de processo/materiais de soldagem | idem |
| IPC-2581 (rev. C, nov/2020) | Formato XML unico de dados de fabricacao/montagem | https://www.electronics.org/news-release/ipc-releases-ipc-2581-revision-c-generic-requirements-printed-board-assembly-products [snippet]; sumario gratis: https://www.ipc.org/TOC/IPC-2581C-toc.pdf |

### 1.1 IPC-2221 — espacamento eletrico (Tabela 6-1)

Valores em mm, tensao DC ou pico AC entre condutores. Fonte unica lida: https://philipmcgaw.com/creepage-and-clearance/ [lido, **secundaria**, legenda "IPC-2221B Conductor spacing requirements"]. Consistente com a leitura parcial de https://pcbsync.com/ipc-2221/ (via busca) para B1/B2/B4 em 0-30 V, 301-500 V e formulas acima de 500 V. Nao consegui ler a norma.

| V | B1 interno | B2 externo sem cobertura (0-3050 m) | B4 externo c/ revestimento polimerico permanente | A5 conformal |
|---|---|---|---|---|
| 0-15 | 0,05 | 0,1 | 0,05 | 0,13 |
| 16-30 | 0,05 | 0,1 | 0,05 | 0,13 |
| 31-50 | 0,1 | 0,6 | 0,13 | 0,13 |
| 51-100 | 0,1 | 0,6 | 0,13 | 0,13 |
| 101-150 | 0,2 | 0,6 | 0,4 | 0,4 |
| 151-170 | 0,2 | 1,25 | 0,4 | 0,4 |
| 171-250 | 0,2 | 1,25 | 0,4 | 0,4 |
| 251-300 | 0,2 | 2,5 | 0,4 | 0,4 |
| 301-500 | 0,25 | 2,5 | 0,8 | 0,8 |
| >500 | V x 0,0025 | V x 0,005 | V x 0,00305 | V x 0,00305 |

(B3, acima de 3050 m: 0,1 / 0,1 / 0,6 / 1,5 / 3,2 / 3,2 / 6,4 / 12,5 / 12,5 mm nas mesmas faixas, mesma fonte.)

Ressalvas verificaveis:
- Outras fontes divergem na fronteira das faixas do B2 (ex.: allpcb diz 0,6 mm em 31-100 V e 1,25 mm em 101-250 V, o que **conflita** com a tabela acima em 101-150 V): https://www.allpcb.com/allelectrohub/the-ultimate-guide-to-calculating-clearance-between-traces-on-your-pcb [lido]. Por isso a tabela acima precisa de conferencia na norma.
- A rev. C (2023) reformula colunas e o passo acima de 500 V; o artigo da Altium cita o exemplo B1 = 0,25 mm + 0,0025 mm/V acima de 500 V: https://resources.altium.com/p/using-an-ipc-2221-calculator-for-high-voltage-design [lido, parcial: tabelas sao imagem].
- A tabela e isolacao **funcional**; nao substitui creepage/clearance de norma de seguranca (IEC 62368-1/60664-1). Pcbsync: "Use the invoked standard and its definitions instead of a copied generic voltage table" [lido]. A Altium e a pcbsync dizem que certificador nao aceita a 6-1 como tabela de seguranca [snippet].
- O espacamento e o minimo **acabado**, depois da tolerancia de fabricacao (pcbsync, mesma pagina).

### 1.2 IPC-2152 — corrente de trilha

- Escopo: "determining the appropriate sizes of internal and external conductors as a function of the current-carrying capacity required and acceptable conductor temperature rise" [snippet]: https://circuitsassembly.com/ca/editorial/menu-new-indust-prod/17617-ipc-releases-ipc-2152-standard.html
- O grafico de condutor interno da 2221 "was not based on testing internal PCB conductors"; testes mostram aumento de temperatura proximo entre interno e externo [snippet]: https://pcdandf.com/pcdesign/index.php/2009-archive-articles/5305-the-new-ipc-2152
- A 2152 considera condutividade termica, vias, dissipacao, material/espessura da placa e presenca de planos de cobre [snippet, mesma fonte].
- Implicacao para a skill (**inferencia nossa**): nao dimensionar trilha interna pelo grafico da 2221; usar calculadora 2152 e validar com margem.

### 1.3 IPC-7351B

- Tres geometrias por familia: protrusao maxima (nivel A, "Most"), mediana (B, "Nominal"), minima (C, "Least"); sufixo M/N/L no nome do footprint [snippet, secundaria]: https://docs.jitx.com/en/latest/jitxlib-standard/jitxlib.landpatterns.ipc.html
- O mesmo codigo da JITX alerta que os rotulos A/B/C das tabelas 3-25/3-26 sao niveis de *producibility*, nao de densidade (nao misturar).
- Para a skill (**inferencia**): padrao B; A para prototipo/solda manual; C so com processo qualificado.

### 1.4 IPC-A-610 x J-STD-001

- A-610 = criterio de aceitacao do conjunto pronto; J-STD-001 = requisitos de processo. Classes 1, 2, 3 compartilhadas (Classe 2 = eletronica dedicada comum; Classe 3 = alta confiabilidade) [snippet, secundaria]: https://www.circuitassembly.com/j-std-001-explained/ e https://pcbsync.com/ipc-a-610/
- As fontes divergem sobre a revisao vigente da J-STD-001 (uma diz J/2024, outra H). **Nao citar letra de revisao sem conferir no IPC.**

### 1.5 IPC-2581

- Rev. C, publicada nov/2020; XML unico com dados para ferramental, fabricacao, montagem e inspecao; norma paga (~200 EUR na DIN Media) [snippet]: https://www.dinmedia.de/en/standard/ipc-2581c/377809275
- Pratico (**inferencia**): Gerber+drill+pick&place continua o que JLCPCB/PCBWay pedem; 2581 e opcional.

### 1.6 Calculadoras de largura de trilha

- **KiCad PCB Calculator**: "Track Width ... calculates the trace width for printed circuit board conductors for a given current and temperature rise. It uses formulas from IPC-2221 (formerly IPC-D-275)." Aba "Electrical Spacing" traz tabela por faixa de tensao e campo para >500 V [lido]: https://docs.kicad.org/9.0/en/pcb_calculator/pcb_calculator.html . **Atencao**: e formula 2221, nao 2152.
- **Saturn PCB Toolkit**: calcula corrente de trilha e via por IPC-2152 [snippet]; pagina oficial citada: saturnpcb.com/pcb_toolkit (nao abri); versao vigente nao confirmada (fontes dao 6.64, 7.12, 8.47). https://pcdandf.com/pcdesign/index.php/editorial/menu-new-indust-prod/14858-saturn-pcb-delivers-pcb-design-toolkit-v-7-12
- **Sierra Circuits (Proto Express)**: calculadora web IPC-2152 [snippet]: https://www.protoexpress.com/resources/current-carrying-capacity-calculator/
- Cadence community: 2221 e 2152 dao so estimativa; para certeza, simulacao de queda IR [snippet]: https://community.cadence.com/cadence_technology_forums/pcb-design/f/pcb-design/41084/calculating-trace-current

## 2. Desacoplamento e integridade de alimentacao

| MCU/IC | Regra | Fonte |
|---|---|---|
| STM32F4 (AN4488 rev. 7, out/2018) | VDD: 1 capacitor ceramico/tantalo para o encapsulamento (min. 4,7 uF, tip. 10 uF) + 100 nF ceramico por pino VDD. VDDA: 100 nF ceramico + 1 uF. VCAP1/VCAP2 com regulador ligado: 2 x 2,2 uF ESR < 2 ohm (ou 1 x 4,7 uF se so VCAP1 existe). VBAT sem bateria: 100 nF a VDD. Capacitores o mais perto possivel dos pinos. | https://www.st.com/resource/en/application_note/dm00115714-getting-started-with-stm32f4xxxx-mcu-hardware-development-stmicroelectronics.pdf [snippet de busca com aspas literais; WebFetch deu timeout, nao li o PDF] |
| Outras familias STM32 | A mesma familia de notas existe por serie: AN4938 (H74x/H75x, rev. 7 out/2024), AN4555 (L4), AN5096 (**STM32G0**, nao H7), AN4661 (F7), AN4467 (L0). Cada serie tem valores proprios; consultar a da serie. | https://www.st.com/resource/en/application_note/an4938-getting-started-with-stm32h74xig-and-stm32h75xig-hardware-development-stmicroelectronics.pdf , https://www.st.com/resource/en/application_note/an5096-getting-started-with-stm32g0-series-hardware-development-stmicroelectronics.pdf [snippets] |
| STM32 osciladores | AN2867 "Oscillator design guide for STM8AF/AL/S, STM32 MCUs and MPUs"; tem secoes "PCB design guidelines" e "PCB design examples" (so TOC visto). Rev. 24 (fev/2026) segundo a busca. | https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm32-microcontrollers-stmicroelectronics.pdf [snippet] |
| ESP32-S3 (Espressif Hardware Design Guidelines) | Layout recomendado de 4 camadas: L1 sinais+componentes, L2 GND ("No signal traces here"), L3 alimentacao (com GND sob RF/cristal), L4 poucos sinais sem componentes. Alimentacao nas camadas internas "(not the ground layer)". 10 uF antes da entrada do chip (+ opcional 0,1 ou 1 uF em paralelo); 10 uF em cada um dos pinos 2 e 3 (VDD3P3 analogico/RF); "Place appropriate decoupling capacitors at the rest of the power pins" com vias de GND junto ao pad de cada capacitor. Pad de GND inferior com no minimo 9 vias. Trilha principal 3,3 V >= 25 mil. | https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html [lido via resumo; nao conferido literalmente. A pagina nao tem secoes numeradas] |
| ESP32-S3 reset | CHIP_PU nao pode flutuar; RC tipico 10 kohm / 1 uF; strapping GPIO0/3/45/46; pull-up em GPIO0 e sem capacitor grande nele. | https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html [snippet] |
| RP2040 | Guia oficial "Hardware design with RP2040" (RP-008279-DS): secoes 2.1.1 Input supply, 2.1.2 Decoupling capacitors, 2.1.3 Internal voltage regulator, 2.2 Flash storage, 2.3 Crystal oscillator, 2.7 Making a PCB. **Nao consegui ler o corpo** (PDF binario). Resumo de busca (nao confirmado): 100 nF por pino de alimentacao, perto dos pinos; 1 uF perto de VREG_IN e VREG_OUT. | https://pip.raspberrypi.com/documents/RP-008279-DS-hardware-design-with-rp2040.pdf [nao lido]; titulos de secao via https://pip-assets.raspberrypi.com/categories/814-rp2040/documents/RP-008279-DS-2-hardware-design-with-rp2040.pdf |
| Geral (ADI MT-101 "Decoupling Techniques", rev. 0, mar/2009) | Capacitores o mais perto do CI, ligados a plano de GND de baixa impedancia por via/trilha curta; ferrite opcional em serie. | https://www.analog.com/en/resources/package-resources.html (lista MT-101); espelho lido so em snippet: https://escies.org/download/webDocumentFile?id=62177 [snippet] |

Texto literal da ST sobre pares VDD/VSS e ponto de ambiguidade: usuarios no forum da ST discutem se o 4,7-10 uF e por pacote ou por par; a leitura majoritaria e por pacote: https://community.st.com/t5/stm32-mcus-products/how-supply-stm32f446ret6/m-p/635436 [snippet, forum, nao e fonte normativa].

Nao achei: valores numericos de desacoplamento do guia RP2040 em fonte primaria lida; texto de AN2867 sobre layout.

## 3. Aterramento, retorno de corrente, EMC, buck

- **Plano de GND continuo / nao dividir**: Bogatin, "never add a split or gap in the return path"; a corrente de retorno em alta frequencia segue o caminho de menor indutancia sob o sinal [snippet; artigo "The Case for Split Ground Planes" reproduzido no blog da Teledyne LeCroy]: https://blog.teledynelecroy.com/2023/01/signal-return-paths-signal-and-power.html . Nuance da mesma fonte: a lacuna reduz so ~40% do ruido indutivo no vizinho, "a small impact".
- **AGND/DGND de conversores**: ADI diz que os dois pinos devem ir ao mesmo GND analogico do sistema (juntos no pacote); TI diz igual: https://www.analog.com/en/analog-dialogue/raqs/raq-issue-9.html [WebFetch deu timeout; so snippet], https://ti.com/lit/slyt499 [snippet], ADI MT-031 (Kester/Bryant/Byrne, rev. A, out/2008): https://wcm-cce.cldnet.analog.com/media/en/training-seminars/tutorials/mt-031.pdf [snippet, so introducao]. Particionar posicao dos componentes (analogico/digital/potencia) em vez de dividir o plano (Ott, via resumo Autodesk): https://www.autodesk.com/products/fusion-360/blog/everyday-app-note-successfully-design-mixed-signal-pcb-partitioning/ [snippet, secundaria].
- **Stack-up 4 camadas**: Espressif recomenda Sinal/GND/Alimentacao/Sinal (ver secao 2). Henry Ott, *Electromagnetic Compatibility Engineering* (Wiley, 2009): nas camadas de sinal ao lado de plano o retorno flui no plano adjacente; 4 camadas reduz radiacao ~20 dB vs. 2 camadas; paginas 630-631 sobre troca de plano de referencia: https://www.allaboutcircuits.com/technical-articles/common-layer-stack-ups-for-a-four-layer-board/ [snippet, secundaria que reproduz figuras do livro]; a pagina 630-631 vem de post de forum (https://www.fpgarelated.com/showthread/comp.arch.fpga/90328-3.php), **nao verificado no livro**. Nao tenho o livro; nao afirmar "Ott diz X" sem abri-lo.
- **Buck, loop de entrada** (TI LMR36006, SNVSB48C, secao 11.1) [lido via resumo]: "the traces in this loop must be wide and short, and the loop area as small as possible"; "Place the input capacitor(s) as close as possible to the VIN and GND terminals"; "Use at least one ground plane in one of the middle layers"; "Keep the copper area connecting the SW pin to the inductor as short and wide as possible"; divisor de realimentacao junto ao pino FB e longe do no SW. https://www.ti.com/document-viewer/lit/html/SNVSB48C/layout-guidelines-snvsay71410
  Mesma orientacao em LM61440/LM60440-Q1 (menores capacitores mais perto dos pinos; plano VIN em camada inferior reduz a area): https://ti.com/document-viewer/LM61440/datasheet/GUID-B3BC1FF3-222C-4456-916C-6A98740CD6F4 [snippet].
- **Guarda de cristal**: Espressif (pagina de layout do ESP32-S3) [lido via resumo]: cristal a >= 2,0 mm do pino de clock, vias de GND em volta da trilha, sem vias nas trilhas do cristal, sem sinais rapidos sob o cristal, capacitores de carga dos dois lados. https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html . ST: AN2867 (nao lido).
- Nao achei: texto de Ott/Bogatin lido diretamente (livros); app note TI/ADI dedicada so a layout de buck (usei secoes de layout de datasheet).

## 4. Protecoes tipicas

- **Rele/solenoide, diodo de roda livre**: o diodo simples retarda a abertura da armadura e pode reduzir a vida do contato; TE recomenda diodo reverso com zener em serie (ou resistor) para melhor dinamica de liberacao: https://www.te.com/en/products/relays-and-contactors/electromechanical-relays/intersection/relay-coil-suppression-dc-relays.html [snippet]. Numeros de tempo de queda ("5-10x") vem de blog sem fonte: **nao usar**.
- **Inversao de polaridade, P-MOSFET**: TI SLVAE57B (fev-out/2021), secao 4.1 "Reverse Battery Protection using P-Channel MOSFET"; o diodo de corpo conduz brevemente na partida, com polaridade invertida o Vgs sobe e o MOSFET desliga; o MOSFET nao bloqueia corrente reversa da carga para a entrada (diferente de Schottky); controlador de diodo ideal (LM74500-Q1 + N-MOSFET) tem menor perda: https://www.ti.com/document-viewer/lit/html/SLVAE57B/GUID-067BD522-C287-4D5A-953C-E454F360AC9F [lido: so sumario; corpo da 4.1 so por snippet]. Titulo da nota nao confirmado. Projeto da rede de gate (zener de clamp de Vgs) **nao encontrado** em texto lido; ver a nota.
- **TVS/ESD em conector**: ROHM "PCB layout for TVS diodes" e "Selection method and usage of TVS diodes": TVS entre o conector e o CI, VRWM acima da tensao maxima da linha, layout ruim anula a protecao: https://fscdn.rohm.com/en/products/databook/applinote/discrete/diodes/pcb_layout_for_tvs_diodes_an-e.pdf , https://fscdn.rohm.com/en/products/databook/applinote/discrete/diodes/selection_method_and_usage_of_tvs_diodes_an-e.pdf [snippets]. "Dentro de 5 mm do conector" e regra de blog, **nao norma**: https://www.nextpcb.com/blog/tvs-diode-pcb-design-layout-guide . Nexperia/Littelfuse/TI: **nao achei** nota especifica nesta busca.
- **Fusivel/PTC, snubber, isolamento galvanico, filtros de entrada**: **nao pesquisei com profundidade** nesta rodada (sem fonte lida).
- **RS-485**: terminacao de 120 ohm em cada extremo; polarizacao failsafe: receptor deve dar nivel alto para VAB >= +200 mV e baixo para <= -200 mV; exemplo com cabo 120 ohm, 5 V +/-5 %: ~528 ohm para 0,25 V, ou 510 ohm pull-up em A e pull-down em B [snippet] — TI SLYT080 (PDF baixado era binario, titulo/autor **nao confirmados**): https://ti.com/lit/pdf/SLYT080 ; TI SLYT514 diz que transceptores modernos dispensam bias externo: https://ti.com/lit/pdf/slyt514 ; Renesas AN1986 "External fail-safe biasing of RS-485 networks": https://renesas.com/en/document/apn/an1986-external-fail-safe-biasing-rs-485-networks [snippet]. Conferir sempre no datasheet do transceptor.
- **CAN**: terminacao tipica 120 ohm em cada extremo; terminacao dividida = dois resistores de 60 ohm com capacitor ao GND no ponto medio, tipicamente 4,7 nF a 100 nF; fC = 1/(2 pi R C) e filtro de modo comum; resistores casados; so nos dois nos das pontas. TI SLLSEQ7F (TCAN33x) e guias SLLU321/SLLU342/SLLU355 [snippet]: https://www.ti.com/document-viewer/lit/html/SLLSEQ7F/GUID-753E3F93-C6B5-4FC4-AA63-25356C79C1B0 , https://ti.com/document-viewer/lit/html/SLLU342/GUID-66A85562-8D39-4690-95BD-CE0F775CA31A . As notas SLLA270/SLLA337 que eu queria **nao foram encontradas**.

## 5. Drivers de motor

- **DRV8871/DRV8872 (TI, SLVSCY9B, secao 10.1 Layout Guidelines)** [lido via resumo]: "The bulk capacitor should be placed to minimize the distance of the high-current path through the motor driver device."; "The connecting metal trace widths should be as wide as possible, and numerous vias should be used when connecting PCB layers."; "Small-value capacitors should be ceramic, and placed closely to device pins."; "The device thermal pad should be soldered to the PCB top-layer ground plane."; "Multiple vias should be used to connect to a large bottom-layer ground plane." https://www.ti.com/document-viewer/DRV8871/datasheet/layout-guidelines-slvscy83135
  Valor do capacitor de bulk: o datasheet remete a teste de sistema, nao a regra fixa (resumo de terceiro, nao confirmado).
- **TMC2209**: datasheet oficial nao lido. Fonte terciaria (wiki): pad exposto e GND, ligar a plano por tantas vias termicas quanto possivel, sense resistor perto do pino: https://wiki.adom.inc/ray/tmc2209 [secundaria]. **Nao usar como citacao**; abrir o datasheet ADI/Trinamic.
- **A4988/A3983 (Allegro)**: pad soldado em cobre exposto, vias termicas, sense resistors com retorno de baixa impedancia e ponto estrela sob o CI; via mirror alldatasheet: https://html.alldatasheet.net/html-pdf/551113/ALLEGRO/A3983SLPTR/2115/7/A3983SLPTR.html [snippet, secundaria]. Datasheet A4988 oficial nao lido. DRV8833 **nao pesquisado**.

## 6. DFM / DFT / DFA

- **JLCPCB capacidades** [lido via resumo, https://jlcpcb.com/capabilities/Capabilities]: trilha/espacamento minimo 0,10/0,10 mm (1 oz, 1-2 camadas) e 0,09/0,09 mm (multicamada); silkscreen largura >= 0,15 mm, altura de texto 40 mil (1,0 mm); cobre a borda >= 0,2 mm (fresado) e >= 0,4 mm (V-cut); anel anular PTH >= 0,20 mm; furo minimo 0,15 mm.
- **JLCPCB painelizacao** [snippet]: V-cut atravessa o painel inteiro; 2 mm minimo entre V-cuts paralelos; angulo 25 graus; nao ha V-cut em 0,4 mm; borda de processo 3-5 mm: https://jlcpcb.com/help/article/PCB-Panelization , https://jlcpcb.com/blog/v-cut-panelization-standards . Fiducial: centro a >= 3,85 mm da borda (JLCPCB SMT).
- **Fiduciais** (Advanced Circuits, [lido via resumo], https://www.advancedpcb.com/en-us/resources/blog/fiducials): globais 1,0-2,0 mm, locais 0,5-1,0 mm; abertura de mascara 2-4 mm / 1-2 mm; 3 globais nao colineares; 2 locais por componente critico (fine pitch <= 0,5 mm); em cobre, nao so silkscreen; "While IPC does not mandate specific fiducial dimensions", confirmar com o montador.
- **Orientacao de polarizados, test points, numeracao de referencia, marcacao de revisao, distancia componente-borda**: **nao achei** fonte primaria com numero nesta rodada. Os itens sao praticas comuns; a skill deve apresentar como recomendacao nossa, sem citar norma.
- PCBWay e Sierra Circuits DFM: **nao abertos** (so aparecem em outras buscas).

## 7. Checklists publicos

- Altium, "Schematic Design Review Checklist" (estilo, legibilidade, folha de rosto, BOM): https://resources.altium.com/p/schematic-review-checklist [snippet].
- Cadence, revisao de projetos open source: comparar com o esquema de referencia do fabricante do CI; "Just because a design has been open-sourced doesn't mean the design is totally correct": https://resources.pcb.cadence.com/blog/design-reviews-for-open-source-pcb-projects [snippet].
- UWaterloo Rocketry / UWARG, "How to do Design Reviews" (revisao por folha, template, verificacao de calculos do buck contra datasheet): https://uwarg-docs.atlassian.net/wiki/spaces/EL/pages/2173468893 [snippet].
- Espressif, Schematic Checklist (por chip, oficial): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html [snippet].
- Template de revisao por risco (alimentacao, GND, EMI, termica, test points, DFM): https://www.jotform.com/form-templates/preview/261052603638049/classic&nofs&disableSmartEmbed=1 [snippet, baixa autoridade].
- Nao achei um checklist canonico e neutro; o melhor caminho e montar o nosso a partir dos itens acima.

## O que NAO foi verificado (para o proximo passo)

1. Tabela 6-1 da IPC-2221: so fonte secundaria; B2 em 101-150 V diverge entre fontes.
2. RP2040: corpo do guia nao lido.
3. AN4488: citacoes via snippet de busca, nao li o PDF.
4. Ott e Bogatin: livros nao abertos.
5. TMC2209, A4988, DRV8833: datasheets oficiais nao lidos.
6. Fusivel/PTC, snubber, isoladores digitais, filtros de entrada: sem pesquisa.
7. DFA/DFT numericos (test point, borda, polarizado): sem fonte.
