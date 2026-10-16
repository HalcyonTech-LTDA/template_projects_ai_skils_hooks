# Spec do circuito (JSON)

Fonte do esquematico no modo spec: `hardware/<placa>/spec/<placa>.json`. Lida por
`gerar_esquematico.py` (gera o `.kicad_sch`), `verificar.py netlist` (prova a conectividade),
`pcb_do_esquematico.py` (blocos e net classes na placa) e `portao_liberacao.py` (tensao maxima).

Exemplo completo e testado ponta a ponta: `.claude/skills/pcb-projeto/assets/exemplo/placa-exemplo.json`.

## Campos de topo

| Campo | Tipo | Obrigatorio | Uso |
|---|---|---|---|
| `projeto` | string | Sim | Nome da placa (slug), vai para o title block |
| `titulo` | string | Sim | Titulo legivel do esquematico |
| `revisao` | string | Sim | Letra da revisao (`A`) |
| `empresa` | string | Nao | Title block (padrao: vazio) |
| `folha` | string | Nao | `A4`, `A3`, `A2`, `A1` (padrao `A3`) |
| `tensao_max_v` | numero | Sim | Maior tensao presente na placa, **valor de pico**. Acima de 60 (DC) aciona o portao de alta tensao |
| `tensao_ac` | booleano | Nao | `true` quando a maior tensao e alternada: o limite de alta tensao cai para 42,4 V de pico |
| `blocos` | lista | Sim | Regioes do desenho, na ordem em que aparecem |
| `componentes` | lista | Sim | Um item por componente |
| `redes` | objeto | Sim | Nome da rede → lista de pinos |
| `pwr_flag` | lista | Nao | Redes que recebem PWR_FLAG (alimentacao que entra por conector) |
| `nao_conectar` | lista | Nao | Pinos deliberadamente sem ligacao (recebem flag de nao conectado) |
| `classes_de_rede` | objeto | Nao | Net classes para o layout (largura, clearance) |

## `blocos`

```json
{"id": "entrada", "titulo": "Entrada 12 V e protecao",
 "componentes": ["J1", "F1", "Q1", "D1", "R1", "D2", "C1"],
 "notas": "Q1 AO3401A contra inversao: dreno na entrada, fonte na carga, gate ao GND por R1 10k.\nD1 zener 10 V limita Vgs a -10 V (Vgs max do Q1 e +-12 V)."}
```

Todo componente aparece em exatamente um bloco. `notas` vira texto no desenho, junto do bloco — e o
lugar dos calculos.

## `componentes`

```json
{
  "ref": "U2",
  "simbolo": "Regulator_Switching:AP63203WU",
  "valor": "AP63203WU",
  "footprint": "Package_TO_SOT_SMD:TSOT-23-6",
  "campos": {
    "MPN": "AP63203WU-7",
    "Fabricante": "Diodes Incorporated",
    "LCSC": "C780769",
    "Datasheet": "https://www.diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf"
  },
  "dnp": false
}
```

- `simbolo` e `footprint` **sempre** confirmados com `buscar_biblioteca.py` (nunca de memoria);
  `buscar_biblioteca.py pinos <Lib:Simbolo>` e `pads <Lib:Footprint>` mostram os nomes e numeros
  reais para usar nas redes.
- `campos` aceita qualquer chave; as lidas pela fabricacao sao `MPN`, `Fabricante`, `LCSC`, `Mouser`,
  `DigiKey`, `Datasheet`. Os codigos acima sao os do exemplo, confirmados com `buscar_lcsc.py` em
  2026-10-12 — estoque muda: confirme de novo antes de usar.
- O gerador recusa: simbolo de power declarado como componente (use a rede), componente sem
  footprint, referencia duplicada.
- `dnp: true` marca o componente como nao montado (sai de todas as BOMs e do CPL, fica no desenho e
  na placa).
- Peca montada fora da JLC (soldada a mao, consignada): `"Sem_LCSC": "motivo"` em `campos`. Fica na
  BOM completa e sai da BOM/CPL da JLC; o `MPN` continua obrigatorio.

## `redes`

Trecho do exemplo (nomes e numeros reais dos simbolos do KiCad 10):

```json
"redes": {
  "+12V":      ["J1.1", "F1.1"],
  "VIN_FUSE":  ["F1.2", "Q1.D"],
  "Q1_GATE":   ["Q1.G", "D1.A", "R1.1"],
  "+12V_SYS":  ["Q1.S", "D1.K", "D2.1", "C1.1", "U2.IN", "U2.EN", "U3.VM"],
  "SW_BUCK":   ["U2.SW", "C4.2", "L1.1"],
  "GND":       ["J1.2", "R1.2", "U2.GND", "U1.1", "U1.40", "U1.41", "U3.1", "U3.7", "U3.9"]
}
```

Como `REF.pino` e resolvido:

1. Por **numero** de pino (`U1.40`, `U3.9` — o pad exposto do DRV8871). Use numero sempre que houver
   ambiguidade.
2. Se nenhum numero casar, por **nome** (`U2.IN`, `Q1.G`). Nome que casa varios pinos liga **todos**
   e o gerador avisa — correto para alimentacao, perigoso para sinal. O nome e o do simbolo, nao o do
   datasheet: no AP63203WU a entrada chama `IN` (nao `VIN`); no ESP32-S3-WROOM-1 os GPIOs chamam
   `IO4`, `IO7` (nao `GPIO4`). Confira com `buscar_biblioteca.py pinos`.
3. Pinos ocultos empilhados no mesmo ponto (GND do DRV8871 em 1/7/9, do ESP32 em 1/40/41) recebem um
   fio so; o gerador recusa a spec se eles estiverem em redes diferentes.

Rede com nome de simbolo da biblioteca `power` (`GND`, `+3V3`, `+5V`, `+12V`, `+24V`, `VCC`...) e
desenhada com o simbolo de power; as demais com label local. Uma rede com um pino so e erro (rede
pendurada); o gerador recusa.

## `pwr_flag`

O ERC acusa "pino de entrada de alimentacao nao alimentado" (`power_pin_not_driven`) quando uma rede
tem entradas de alimentacao e nenhum pino do tipo saida de alimentacao. Isso acontece sempre que quem
alimenta a rede e um pino **passivo** ou um conector:

- rede que chega por borne ou conector (`+12V`, `GND`);
- rede depois de um componente passivo no caminho de potencia: a fonte do MOSFET de protecao
  (`+12V_SYS`), a saida de um buck que passa pela bobina (`+3V3`), depois de um fusivel ou ferrite.

Liste essas redes aqui (o exemplo usa `+12V`, `GND`, `+12V_SYS` e `+3V3`) e escreva o motivo nas
`notas` do bloco. O que nao se faz: PWR_FLAG numa rede que deveria ser alimentada por uma saida de
alimentacao de verdade (pino `power_out` de um LDO, por exemplo) e nao esta — ai o erro do ERC e real
e o PWR_FLAG o esconde.

## `nao_conectar`

```json
"nao_conectar": ["U1.17", "U1.18", "U3.NC"]
```

Pino sem rede e fora desta lista faz o gerador **falhar** listando os pinos. E de proposito: NC
automatico esconde pino esquecido.

## `classes_de_rede`

```json
"classes_de_rede": {
  "Power": {"redes": ["+12V", "VIN_FUSE", "+12V_SYS", "MOTOR_A", "MOTOR_B"], "largura_mm": 0.8, "clearance_mm": 0.3},
  "HV":    {"redes": [], "largura_mm": 1.0, "clearance_mm": 2.5}
}
```

Redes fora de qualquer classe ficam em `Default` (trilha 0,25 mm, clearance 0,2 mm no modelo do
projeto). Largura de `Power` pela corrente — ver `pcb-layout`. O `rotear.py` deixa as classes
`Power` e `HV` fora do Freerouting por padrao.
