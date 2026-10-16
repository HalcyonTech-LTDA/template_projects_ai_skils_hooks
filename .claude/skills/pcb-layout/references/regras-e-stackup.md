# Regras de projeto, largura de trilha e stack-up

## 1. Capacidades da JLCPCB (conferidas na pagina em 2026-10-12)

Fonte: https://jlcpcb.com/capabilities/pcb-capabilities

| Item | 1-2 camadas | Multicamada |
|---|---|---|
| Trilha / espaco minimo (1 oz) | 0,10 / 0,10 mm | 0,09 / 0,09 mm |
| Via minima (furo / diametro) | 0,15 / 0,25 mm (preferido furo >= 0,2) | 0,15 / 0,25 mm |
| Anel de furo de componente (PTH) | 0,18 mm absoluto, 0,25 recomendado | 0,15 absoluto, 0,20 recomendado |
| Pad ↔ pad SMD (redes diferentes) | 0,15 mm | 0,15 mm |
| Via ↔ via (furo a furo) / via ↔ trilha | 0,2 / 0,2 mm | 0,2 / 0,2 mm |
| Cobre ↔ borda | 0,2 mm fresado; 0,4 mm V-cut | idem |
| Furo NPTH minimo | 0,5 mm | 0,5 mm |
| Serigrafia | linha >= 0,15 mm; texto >= 1,0 mm | idem |
| Impedancia controlada | — | a partir de 4 camadas, +-10% |

Os padroes do projeto (tabela no SKILL.md) ficam acima desses minimos. Va ao minimo so com motivo
(passo fino de CI, BGA) e por regra localizada, nunca baixando o board inteiro.

Excecao ja incluida nos `.kicad_dru` (regra `jlc_furo_via_termica_footprint`): vias termicas que
vem **dentro do footprint** (pad dissipador do ESP32-S3-WROOM-1, do DRV8871) podem ter furo de
0,2 mm — acima do minimo de 0,15 mm da JLC. Sem ela, o footprint oficial do modulo gera erros de
furo contra o minimo de 0,3 mm do projeto.

## 2. Largura de trilha pela corrente

Pela formula da IPC-2221 (a mesma usada pela calculadora do KiCad), cobre externo de 1 oz (35 um):

| Corrente | Elevacao de 10 C | Elevacao de 20 C |
|---|---|---|
| 0,5 A | 0,12 mm | — |
| 1 A | 0,30 mm | 0,20 mm |
| 2 A | 0,78 mm | 0,51 mm |
| 3 A | 1,37 mm | 0,90 mm |
| 5 A | 2,77 mm | 1,82 mm |

Calculado com `I = 0,048 x dT^0,44 x A^0,725` (A em mil^2). E **estimativa**:

- A IPC-2152 substituiu os graficos da 2221 e considera planos de cobre, vias e espessura da placa; o
  grafico de condutor interno da 2221 nao foi baseado em teste de condutor interno (ficha). Para
  trilha de potencia definitiva use uma calculadora 2152 (Saturn PCB Toolkit, Sierra Circuits) e
  deixe margem.
- Trilha interna dissipa pior: pela 2221, precisa de cerca de 2,6x a area da externa para a mesma
  elevacao. Evite potencia em camada interna sem calcular.
- Trilha curta entre um pad pequeno e um plano esquenta menos que o calculo; trilha longa em placa
  fechada numa caixa esquenta mais. Elevacao de 10 C e o padrao conservador da familia.
- **Vias:** varias vias em paralelo em toda troca de camada de potencia. A aba "Via Size" da
  calculadora do KiCad estima a corrente por via; na falta de calculo, uma via de 0,3 mm por ampere
  e regra conservadora comum. [pratica]

## 3. Stack-up

**2 camadas (padrao, 1,6 mm, 1 oz):**
- Componentes e sinais em F.Cu; B.Cu quase toda GND (zona), com poucos sinais curtos de travessia.
- Plano de GND da face de baixo continuo sob os sinais rapidos e sob o MCU; cada travessia de sinal
  em B.Cu corta o plano — mantenha curtas e perpendiculares entre si.
- Zonas de GND nas duas faces (o `pcb_do_esquematico.py` cria as duas), costuradas por vias
  (stitching) a cada poucos milimetros nas bordas e em volta das areas ruidosas. **A costura e
  manual**: nenhum script coloca essas vias.

**4 camadas (quando ha radio integrado no chip, USB de alta velocidade, ADC sensivel ou densidade):**
- Sinal / GND / Alimentacao / Sinal, como recomenda a Espressif para o ESP32-S3: L2 so GND, sem
  trilha; L3 alimentacao (com GND sob RF e cristal); L4 poucos sinais. [ficha]
- Cada camada de sinal fica adjacente a um plano: o retorno da corrente corre no plano logo abaixo.
- Impedancia controlada (USB 90 ohm diferencial, RF 50 ohm) so a partir de 4 camadas na JLC; use a
  calculadora de impedancia da JLC com o stack-up escolhido no pedido.

## 4. Planos e retorno de corrente

- **Nao divida o plano de GND** sob sinais. A corrente de retorno de alta frequencia corre no plano
  logo abaixo da trilha; uma fenda obriga o retorno a contornar e vira antena. [ficha: Bogatin]
- Conversores com AGND e DGND: os dois pinos no mesmo GND, junto ao chip. Separe por **posicao**
  (analogico de um lado, digital do outro, potencia em outro), nao cortando o plano. [ficha: ADI, TI]
- Corrente alta de motor e de buck nao deve atravessar a regiao do analogico nem do MCU no caminho
  de volta ao conector de entrada — posicione para que o laco de potencia fique local.

## 5. `.kicad_dru` (regras customizadas)

Sintaxe (KiCad 10): `(version 1)` e regras `(rule "nome" (condition "...") (constraint tipo (min X)))`.
As regras sao avaliadas de tras para frente: **a especifica vai depois da geral**. Exemplos que o
modelo da familia usa:

```
(version 1)

(rule "JLC via-trilha"
  (condition "A.Type == 'Via' && B.Type == 'Track'")
  (constraint clearance (min 0.2mm)))

(rule "HV clearance"
  (condition "A.hasNetclass('HV') || B.hasNetclass('HV')")
  (constraint clearance (min 2.5mm))
  (constraint creepage (min 2.5mm)))
```

O arquivo real esta em `.claude/skills/pcb-projeto/assets/kicad/`.

**Armadilha verificada no KiCad 10.0.0:** `.kicad_dru` com erro de sintaxe, condicao invalida ou sem
`(version 1)` e **descartado em silencio** — o DRC roda, sai com codigo 0 e simplesmente nao aplica
nenhuma regra do arquivo. Rodar o DRC nao prova que a regra vale. Depois de qualquer edicao, valide:

```bash
python .claude/skills/pcb-projeto/scripts/verificar.py dru hardware/<placa>/<placa>.kicad_dru
```

O `verificar.py dru` acrescenta uma regra-canario numa copia e confere que o DRC a aplicou; se nao
aplicou, o arquivo foi descartado. O `portao_liberacao.py` faz a mesma checagem.
