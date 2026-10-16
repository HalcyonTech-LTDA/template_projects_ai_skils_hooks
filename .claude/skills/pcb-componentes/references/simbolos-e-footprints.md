# Simbolos e footprints no KiCad 10

## 1. De onde vem cada coisa (ordem de preferencia)

1. **Biblioteca oficial do KiCad** (instalada com ele; `buscar_biblioteca.py`). Segue a KiCad Library
   Convention (KLC), tem modelo 3D em STEP e e revisada pela comunidade.
2. **Importacao pelo codigo LCSC** com `easyeda2kicad` para a biblioteca do projeto
   (`hardware/<placa>/bibliotecas/`). Rapido e casado com a peca da JLC, mas **sem revisao**: confira
   pinagem e pads contra o datasheet antes de usar. Resultado do teste no KiCad 10 e comando
   recomendado: secao 4.
3. **Desenho proprio** seguindo a KLC, na biblioteca do projeto, quando nenhum dos dois existe.

Nunca escreva um `lib_id` de memoria: o nome tem de vir do `buscar_biblioteca.py`. Simbolo inexistente
faz o esquematico abrir com "?" e o ERC acusar.

## 2. Nomenclatura que a KLC usa (para buscar melhor)

- Footprint SMD de dois terminais: `<Prefixo>_<imperial>_<metrico>Metric`, ex.:
  `R_0603_1608Metric`, `C_0805_2012Metric`, `LED_0603_1608Metric`, `D_SOD-123`.
- CIs: nome do encapsulamento JEDEC, ex.: `SOIC-8_3.9x4.9mm_P1.27mm`,
  `TSSOP-20_4.4x6.5mm_P0.65mm`, `QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm`.
- Bibliotecas por familia: `Resistor_SMD`, `Capacitor_SMD`, `Package_SO`, `Package_TO_SOT_SMD`,
  `Package_DFN_QFN`, `Connector_*`, `TerminalBlock_*`, `RF_Module`, `MountingHole`, `TestPoint`.
- Simbolos genericos ficam em `Device` (`R`, `C`, `L`, `D`, `LED`, `Q_NMOS_GSD`...). Os de CI estao
  na biblioteca da familia (`Regulator_Switching`, `Driver_Motor`, `MCU_ST_STM32G0`...).

## 3. Armadilhas de pinagem (as que mais queimam placa)

| Armadilha | Como pegar |
|---|---|
| **SOT-23 de transistor/MOSFET**: a ordem G-S-D varia por fabricante | Use o simbolo com a ordem no nome (`Q_PMOS_GSD`, `Q_NMOS_GDS`...) igual a do datasheet da peca escolhida |
| **Diodo/LED**: catodo no pino 1 ou 2 conforme o footprint | Confira o pad marcado como K e a marcacao da serigrafia |
| **Regulador SOT-223**: a aba e saida (AMS1117) ou GND (outros) | Datasheet da peca, nao do "equivalente" |
| **Conector**: vista do lado do encaixe x vista de cima da placa | Desenhe a pinagem do cabo na nota de diagrama |
| **USB-C**: dezenas de variantes de footprint (so 2.0, 16 ou 24 pinos, montagem media) | Footprint exato do MPN escolhido |
| **Modulo de radio**: area de exclusao da antena faz parte do footprint | Footprint oficial do modulo; conferir com o datasheet |
| **Pad exposto (EP)**: numero do pad (ex.: 9 ou 33) precisa estar ligado a rede certa no simbolo | Pino EP no simbolo ligado a GND (ou ao que o datasheet manda) |
| **Variante de encapsulamento do mesmo CI** (DDA x DGN, PowerPAD x sem pad) | Sufixo do MPN casa com o sufixo do simbolo/footprint |

## 4. Importacao pelo codigo LCSC (`easyeda2kicad`)

Testado em 2026-10-12 com `easyeda2kicad` 1.0.1 (via `uvx`) e KiCad 10.0.0, com um resistor
(`C25804`) e um CI buck (`C780769`, AP63203WU-7). **Funciona como importacao assistida, nao como
fonte de verdade**: gera simbolo, footprint e modelo 3D que o KiCad 10 abre, mas o dado do EasyEDA
vem com defeitos que o agente precisa corrigir.

```bash
# --output e um PREFIXO, nao uma pasta: gera lcsc.kicad_sym, lcsc.pretty/ e lcsc.3dshapes/
uvx easyeda2kicad --full --lcsc_id=C780769 --project-relative --output hardware/<placa>/lcsc
kicad-cli sym upgrade hardware/<placa>/lcsc.kicad_sym     # formato antigo (2021) -> KiCad 10
kicad-cli fp upgrade  hardware/<placa>/lcsc.pretty
kicad-cli sym export svg hardware/<placa>/lcsc.kicad_sym -o fab/conferencia
kicad-cli fp  export svg hardware/<placa>/lcsc.pretty    -o fab/conferencia
```

Com `--project-relative` o modelo 3D fica `${KIPRJMOD}/lcsc.3dshapes/...`, por isso o prefixo vai na
**raiz do projeto** (`hardware/<placa>/lcsc`), nao em `bibliotecas/`. Varios codigos acumulam na mesma
biblioteca `lcsc`.

O que corrigir sempre, antes de usar a peca na spec:

1. **Tipo eletrico dos pinos.** O CI veio com todos os pinos `unspecified` e o resistor com `input`.
   Com isso o ERC fica cego para erro de alimentacao. Corrija no simbolo: `power_in`, `power_out`,
   `input`, `output`, `bidirectional`, `passive` conforme o datasheet.
2. **Registre a biblioteca.** O campo `Footprint` do simbolo vem como `lcsc:<nome>`: acrescente as
   entradas `lcsc` no `sym-lib-table` e no `fp-lib-table` do projeto, apontando para
   `${KIPRJMOD}/lcsc.kicad_sym` e `${KIPRJMOD}/lcsc.pretty`.
3. **Confira o footprint contra o land pattern do datasheet.** O nome nao segue a KLC
   (`TSOT-26_L2.9-W1.6-P0.95-LS2.8-BL`) e courtyard, mascara e pasta sao os do EasyEDA.
4. **Campos.** O importador grava `LCSC Part`, `MPN` e `Manufacturer` (com ideograma: `DIODES(美台)`)
   e deixa a descricao vazia. Na spec, preencha os campos da familia (`LCSC`, `MPN`, `Fabricante`) —
   eles vencem. `exportar_fab.py` aceita `LCSC Part` como alternativa, mas nao conte com isso.

Prefira sempre o simbolo/footprint oficial do KiCad quando existir (passivos, conectores comuns,
ESP32-S3, muitos reguladores e drivers). Reserve o `easyeda2kicad` para pecas que so existem no
catalogo LCSC.

## 5. Desenho proprio pela KLC (resumo; o site klc.kicad.org e a fonte)

Simbolo:
- Pinos na grade de 100 mil (2,54 mm), comprimento de 100 mil (passos de 50 mil), todos iguais.
- Nomes de pino iguais aos do datasheet; numeros unicos; tipo eletrico correto (power input, output,
  bidirectional, passive, no connect) — o ERC depende disso.
- Entradas a esquerda, saidas a direita, alimentacao em cima, GND embaixo.
- Campos: Reference, Value, Footprint, Datasheet, Description, e os da familia (MPN, Fabricante, LCSC).

Footprint:
- Origem no centro da peca (SMD) ou no pino 1 (conectores THT, conforme KLC).
- Camadas: cobre e mascara nos pads; `F.Fab` com o contorno real da peca e o texto de referencia;
  `F.SilkS` com contorno fora dos pads e marca de pino 1; `F.CrtYd` com linha de 0,05 mm e folga de
  0,25 mm em volta da peca (mais em conectores e cristais — ver KLC F5.3, revisada em 2026-01).
- Pads pelo land pattern recomendado do datasheet; na falta dele, IPC-7351 nivel nominal (B).
- Modelo 3D em STEP associado, com caminho relativo ao projeto (`${KIPRJMOD}/bibliotecas/3d/...`).

Verifique o footprint novo exportando o SVG (`kicad-cli fp export svg`) e comparando com o desenho do
datasheet antes de usar.
