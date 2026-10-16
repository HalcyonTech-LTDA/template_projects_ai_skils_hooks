# Formato .kicad_sch do KiCad 10 (para editar a mao com seguranca)

Conferido no KiCad 10.0.0 contra os demos regravados com `kicad-cli sch upgrade` e contra o que o
`gerar_esquematico.py` escreve (ERC zero e netlist batendo). Depois de qualquer edicao a mao:
`verificar.py erc` e `verificar.py netlist` de novo.

## Cabecalho e ordem dos nos

```
(kicad_sch
	(version 20260306) (generator "eeschema") (generator_version "10.0")
	(uuid "12cbfc9c-c0f6-5f82-a650-aeb64e94fcee")      <- uuid da folha raiz
	(paper "A3")
	(title_block (title "...") (date "2026-10-12") (rev "A") (company "...") (comment 1 "..."))
	(lib_symbols ...)
	junction* no_connect* wire* label* text* rectangle* symbol*
	(sheet_instances (path "/" (page "1")))
	(embedded_fonts no)
)
```

- `version` maior que a do KiCad instalado: o `kicad-cli` recusa (`falha ao ler o esquematico`,
  saida 3; testado com `20990101`). Versao antiga ele le e regrava com `kicad-cli sch upgrade`.
- `generator` pode ser qualquer string (o pcbkit grava `"pcbkit"`).
- Strings sempre entre aspas; palavras-chave e booleanos sem aspas: `(hide yes)`, `(dnp no)`.

## uuid

- Todo no grafico e toda instancia tem `(uuid "...")` proprio. **Nunca copie um bloco sem trocar os
  uuids**: uuid repetido corrompe a ligacao com a placa e o KiCad pode descartar o item.
- O uuid da instancia de simbolo e o elo com o footprint: na placa, `(path "/<uuid do simbolo>")`.
  Trocar esse uuid faz o "Atualizar PCB" tratar o componente como novo.
- O gerador usa uuid5 (projeto + ref + unidade): regenerar a mesma spec mantem os uuids.

## lib_symbols

Copia **achatada** de cada simbolo usado, com o nome completo `"Lib:Nome"`; as subunidades ficam com o
nome curto (`(symbol "R_0_1" ...)`, `(symbol "R_1_1" ...)`). Derivado (`extends`) precisa ser achatado
antes (pinos e desenho do pai, propriedades do filho) — `bibliotecas.no_embutido` faz isso.
Se a copia diverge da biblioteca, o ERC acusa `lib_symbol_mismatch` (aviso). Nunca apague uma entrada
ainda usada por alguma instancia: o simbolo vira um "??" e perde os pinos.

## Instancia de simbolo

```
(symbol (lib_id "Device:R") (at 330.2 180.34 90) (unit 1) (body_style 1)
	(exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no)
	(uuid "551b0125-037a-59fc-a311-60edfc0807c9")
	(property "Reference" "R7" (at 326.39 175.006 90) (show_name no) (do_not_autoplace no)
		(effects (font (size 1.27 1.27)) (justify left)))
	(property "Value" "1k" (at 326.39 177.038 90) ...)
	(property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 330.2 180.34 0) (hide yes) ...)
	(property "Datasheet" "..." ...) (property "Description" "..." ...)
	(property "MPN" "0603WAF1001T5E" ... (hide yes) ...) (property "LCSC" "C21190" ...)
	(pin "1" (uuid "...")) (pin "2" (uuid "..."))
	(instances (project "placa-exemplo"
		(path "/12cbfc9c-c0f6-5f82-a650-aeb64e94fcee" (reference "R7") (unit 1))))
)
```

- `instances/project` = nome do `.kicad_pro` (sem extensao); `path` = `"/<uuid da folha raiz>"`.
  Com `path` apontando para outro uuid, o `kicad-cli` 10.0.0 ainda exportou netlist e ERC sem acusar
  nada (testado): o erro passa despercebido ate a GUI ou a placa. Confira o `path` a olho.
- `(at x y angulo)` das propriedades e **absoluto** na folha. O angulo do texto e somado a rotacao do
  simbolo: num simbolo a 90 ou 270 graus, `angulo 90` aparece na horizontal.
- `dnp yes` marca nao montado (sai da BOM e do CPL). Um `(pin "n" (uuid))` por pino da unidade.
- Campos extras (MPN, LCSC, Fabricante) vao para a netlist em `(fields ...)` e para a BOM.

## Geometria

- Biblioteca tem Y para cima; folha tem Y para baixo: pino `(at x y)` vira `(X + x, Y - y)`.
- `(at X Y R)` gira R graus anti-horario na tela; `(mirror x)` inverte Y, `(mirror y)` inverte X,
  aplicado depois da rotacao. O `(at)` do pino e a ponta de conexao; o angulo aponta para o corpo.
- Tudo que conecta (ponta de pino, fio, label, no_connect) na grade de 1,27 mm; fora dela o ERC da
  `endpoint_off_grid` e a ligacao pode nao fechar.

## Fio, label, power, PWR_FLAG, no_connect

```
(wire (pts (xy 31.75 36.83) (xy 31.75 34.29)) (stroke (width 0) (type default)) (uuid "..."))
(label "MOTOR_IN1" (at 27.94 137.16 180) (effects (font (size 1.27 1.27)) (justify right bottom)) (uuid "..."))
(no_connect (at 30.48 144.78) (uuid "..."))
```

- Conexao e por coincidencia de ponto: a ponta do fio (ou o ponto do label) tem de cair exatamente
  na ponta do pino. O gerador poe um fio de 2,54 mm por pino e o label/power na outra ponta.
- Label local vale so na folha; na netlist sai com prefixo: `/MOTOR_IN1`.
- Power e um simbolo (`lib_id "power:GND"`, `Reference "#PWR02"` oculta) cujo pino unico liga a rede
  global com o nome do Value; na netlist sai sem prefixo: `GND`. No 10 o simbolo embutido tem
  `(power global)` logo apos o nome.
- `power:PWR_FLAG` (`#FLG01`) diz ao ERC que a rede e alimentada. Precisa em rede que so tem
  `power_in` e passivos: entrada por conector, fonte de MOSFET, saida de buck pela bobina.
- `no_connect` na ponta do pino: o ERC deixa de acusar `pin_not_connected`.
- Pinos ocultos empilhados no mesmo ponto (GND do DRV8871 pinos 1/7/9, GND do ESP32-S3-WROOM-1
  pinos 1/40/41) sao ligados juntos por um unico fio; nao de redes diferentes a eles.

## Texto e moldura

```
(text "Driver de motor DC (DRV8871)" (exclude_from_sim no) (at 222.25 101.6 0) (effects (font (size 2.54 2.54) (bold yes)) (justify left bottom)) (uuid "..."))
(rectangle (start 12.7 12.7) (end 214.63 95.25) (stroke (width 0) (type dash)) (fill (type none)) (uuid "..."))
```

Texto com varias linhas usa `\n` dentro da string. Moldura e texto nao entram na netlist nem no ERC.

## Armadilhas encontradas

- Copiar e colar um simbolo no arquivo sem trocar `uuid` e os `(pin ... (uuid))`.
- Renomear a pasta/arquivo do projeto sem atualizar `(project "...")` das instancias.
- Editar o desenho de um simbolo so na `lib_symbols`: o ERC acusa `lib_symbol_mismatch`; mude na
  biblioteca do projeto e atualize pelo editor.
- Mudar so o `length` de um pino na copia embutida nao dispara `lib_symbol_mismatch`.
- O `kicad-cli sch export svg` escreve cada texto como traco (`<g class="stroked-text">`) com
  coordenadas absolutas: da para conferir sobreposicao de textos por script.
- Modo spec: nao edite o `.kicad_sch` gerado; a proxima geracao apaga a edicao.
