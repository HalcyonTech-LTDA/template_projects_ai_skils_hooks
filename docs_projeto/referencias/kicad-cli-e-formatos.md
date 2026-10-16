---
title: KiCad 10 — kicad-cli, jobsets, formato de arquivo e KLC
source: https://docs.kicad.org/
type: referencia
status: aprovado
created: 2026-10-12
updated: 2026-10-12
verificado_em: 2026-10-12
tags: [referencia, kicad, cli, eletronica, tema/hardware]
---

# KiCad 10 — kicad-cli, jobsets, formato de arquivo e KLC

Aviso de método: o texto das paginas foi lido via WebFetch, que devolve **resumo** e pode errar detalhes. Onde a frase abaixo esta entre aspas, ela veio do resumo e **nao foi conferida com curl**. Confira com `kicad-cli <cmd> --help` local antes de gravar numa skill. A pagina KLC (klc.kicad.org) devolveu 403 ao WebFetch; o que consta dela veio de snippets de busca.

## 1. kicad-cli 10

Fonte: https://docs.kicad.org/10.0/en/cli/cli.html (existe; as flags abaixo sao da doc 10.0). Comparacao com 9.0: https://docs.kicad.org/9.0/en/cli/cli.html

Subcomandos de `pcb export` na doc 10: `3dpdf, brep, drill, dxf, gencad, gerbers, glb, hpgl (nao funcional no 10.0), ipc2581, ipcd356, odb, pdf, ply, pos, ps, stats, step, stl, stpz, u3d, svg, vrml, xao`. `sch export`: `bom, dxf, hpgl (nao funcional), netlist, pdf, postscript, python-bom, svg`. `pcb`: `drc, export, import, render, upgrade`.

Convencoes (via resumo): listas de camadas separadas por virgula sem espaco (`F.Cu,B.Cu`); nomes canonicos como `F.Cu`, `B.Cu`, `In.1`, `F.Fab`; nomes definidos pelo usuario sao testados primeiro. Lista completa de nomes canonicos: nao verificado. Exit code de `--exit-code-violations`: 0 sem violacoes, 5 com violacoes.

### sch erc
Flags: `-o`, `-D/--define-var`, `--format report|json`, `--units mm|in|mils`, `--severity-all/-error/-warning/-exclusions`, `--exit-code-violations`.
```
kicad-cli sch erc --format json --severity-all --exit-code-violations -o erc.json projeto.kicad_sch
```

### pcb drc
Flags: `-o`, `-D`, `--format report|json`, `--all-track-errors`, `--schematic-parity`, `--units`, `--severity-*`, `--exit-code-violations`, `--refill-zones`, `--save-board`. `--save-board` so salva se `--refill-zones` tambem for usado (via resumo). Na doc 9.0, `--save-board` nao aparece (via resumo); `--refill-zones` nao constou na lista resumida da 9.0, nao verificado.
```
kicad-cli pcb drc --schematic-parity --refill-zones --format json --severity-all --exit-code-violations -o drc.json placa.kicad_pcb
```

### pcb export gerbers
Flags: `-o <dir>`, `-l/--layers`, `--cl/--common-layers`, `--drawing-sheet`, `-D`, `--erd/--exclude-refdes`, `--ev/--exclude-value`, `--ibt/--include-border-title`, `--sp`, `--hdnp`, `--sdnp`, `--cdnp`, `--no-x2`, `--no-netlist`, `--subtract-soldermask`, `--disable-aperture-macros`, `--use-drill-file-origin`, `--precision 5|6`, `--no-protel-ext`, `--check-zones`, `--variant`, `--board-plot-params` (usa os parametros de plot Gerber salvos na placa; ignora as flags de camada? nao verificado).
```
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts -o fab/gerber/ placa.kicad_pcb
kicad-cli pcb export gerbers --board-plot-params -o fab/gerber/ placa.kicad_pcb
```
Os nomes `F.Silkscreen` etc. nao foram confirmados na doc; use `kicad-cli pcb export gerbers --help` para a lista local.

### pcb export drill
Flags: `-o <dir>`, `--format excellon|gerber`, `--drill-origin absolute|plot`, `--excellon-zeros-format decimal|suppressleading|suppresstrailing|keep`, `--excellon-oval-format alternate|route`, `-u/--excellon-units mm|in`, `--excellon-mirror-y`, `--excellon-min-header`, `--excellon-separate-th`, `--generate-map`, `--generate-report`, `--report-path`, `--generate-tenting`, `--map-format pdf|gerberx2|ps|dxf|svg`, `--gerber-precision`.
```
kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format pdf -o fab/gerber/ placa.kicad_pcb
```

### pcb export pos
Flags: `-o <arquivo>`, `--side front|back|both`, `--format ascii|csv|gerber`, `--units in|mm` (padrao **in**), `--bottom-negate-x`, `--use-drill-file-origin`, `--smd-only`, `--exclude-fp-th`, `--exclude-dnp`, `--gerber-board-edge`, `--variant`.
```
kicad-cli pcb export pos --format csv --units mm --side both --smd-only --exclude-dnp --use-drill-file-origin -o fab/pos.csv placa.kicad_pcb
```

### sch export bom
Flags: `-o`, `--variant`, `--preset`, `--format-preset`, `--fields`, `--labels`, `--group-by`, `--sort-field`, `--sort-asc`, `--filter`, `--exclude-dnp`, `--field-delimiter`, `--string-delimiter`, `--ref-delimiter`, `--ref-range-delimiter`, `--keep-tabs`, `--keep-line-breaks`. `--include-excluded-from-bom` e obsoleta e sem efeito no 10.0.
```
kicad-cli sch export bom --fields "Reference,Value,Footprint,${QUANTITY},LCSC" --labels "Ref,Valor,Footprint,Qtd,LCSC" --group-by "Value,Footprint" --exclude-dnp -o fab/bom.csv projeto.kicad_sch
```
Sintaxe de `${QUANTITY}` em `--fields`: nao verificada nesta pesquisa.

### sch export netlist
`--format kicadsexpr` (padrao) `|kicadxml|cadstar|orcadpcb2|spice|spicemodel|pads|allegro`, `--variant`, `-o`.
```
kicad-cli sch export netlist --format kicadxml -o projeto.xml projeto.kicad_sch
```

### pcb export ipc2581 / odb
- ipc2581: `-o`, `--drawing-sheet`, `-D`, `--precision` (6), `--compress`, `--version B|C` (C padrao), `--units mm|in`, `--bom-col-int-id`, `--bom-col-mfg-pn`, `--bom-col-mfg`, `--bom-col-dist-pn`, `--bom-col-dist`, `--bom-rev`, `--variant`.
- odb: `-o`, `--drawing-sheet`, `-D`, `--precision` (2), `--compression none|zip|tgz` (zip padrao), `--units`, `--variant`.
```
kicad-cli pcb export ipc2581 --version C --bom-col-int-id Reference --bom-col-mfg-pn MPN -o fab/placa.xml placa.kicad_pcb
kicad-cli pcb export odb --compression zip -o fab/placa-odb.zip placa.kicad_pcb
```

### pcb render
`-o` obrigatorio (`.png/.jpg/.jpeg`), `-w/--width` (1600), `--height` (900; a doc grafa `-h`, que colide com ajuda, prefira `--height`), `--side top|bottom|left|right|front|back`, `--background default|transparent|opaque`, `--quality basic|high|user`, `--preset`, `--use-board-stackup-colors`, `--floor`, `--perspective`, `--zoom`, `--pan`, `--pivot`, `--rotate`, `--light-*`, `--variant`.
```
kicad-cli pcb render --side top --quality high --background transparent -o render-top.png placa.kicad_pcb
```

### Outros uteis
```
kicad-cli pcb export step --help
kicad-cli sch export pdf -o docs/esquematico.pdf projeto.kicad_sch
kicad-cli pcb upgrade --force placa.kicad_pcb
kicad-cli sch upgrade projeto.kicad_sch
kicad-cli version --format about
```
`sch upgrade` nao atualiza folhas filhas (via resumo).

### Jobsets
- Doc CLI: `kicad-cli jobset run [--help] [--stop-on-error] [--file JOB_FILE] [--output OUTPUT] INPUT_FILE`, onde `INPUT_FILE` e o `.kicad_pro`. Sem `--output`, **todos** os destinos sao gerados e o ID de cada um e impresso. `--output` aceita descricao (precisa ser unica, senao nada roda) ou ID (chave `id` no `.kicad_jobset`). Sem `--stop-on-error`, os jobs seguem apos falha. Fonte: https://docs.kicad.org/10.0/en/cli/cli.html
```
kicad-cli jobset run -f producao.kicad_jobset --stop-on-error projeto.kicad_pro
kicad-cli jobset run -f producao.kicad_jobset --output "Gerbers" projeto.kicad_pro
```
- Criacao na UI: File > New Jobset File... no gerenciador de projetos; jobs com `+`; destinos `Folder` ou `Archive` (zip); variaveis `${PROJECTNAME}`, `${CURRENT_DATE}`; saida montada numa pasta temporaria (`${JOBSET_OUTPUT_WORK_PATH}`) e movida so se todos os jobs terminarem. Tipos de job: PCB (3D, stats, drill, DXF, GenCAD, Gerbers, IPC-2581, ODB++, PDF, pos, PS, SVG, DRC, render), Schematic (DXF, netlist, PDF, PS, SVG, BOM, ERC), Special (copiar arquivos, comando de shell). Fonte: https://docs.kicad.org/10.0/en/kicad/kicad.html (via resumo).
- Formato do arquivo: a doc de usuario nao descreve a sintaxe. Pelo codigo-fonte (via resumo, nao conferida) e **JSON** (nlohmann), com listas `jobs` e `outputs`; job tem `id, type, description, settings`; destino tem `id, type ("folder"|"archive"), only, description, settings`; `jobsFileSchemaVersion = 1`. Fonte: https://raw.githubusercontent.com/KiCad/kicad-source-mirror/10.0/common/jobs/jobset.cpp . **Nao ha esquema publicado**: gere o jobset pela UI e versione o arquivo; nao o escreva a mao.

## 2. Novidades do KiCad 10 para automacao

- Lancamento: 20/03/2026 (10.0.0). Pontuais ate 10.0.6 (ago/2026) e 10.0.5 em 22/07. Fontes: https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/ , https://www.kicad.org/blog/2026/08/KiCad-10.0.6-Release/
- Anuncio oficial cita: variantes de design (mesmo esquematico, BOM diferente), design blocks no editor de PCB, editor grafico de regras DRC (grava no mesmo `.kicad_dru`), sugestoes de correcao de DRC, exportacao 3D PDF, codigos de barras, hachura, importadores Allegro/PADS/gEDA, modelos 3D oficiais so em STEP. O anuncio **nao** fala de CLI, jobsets, IPC nem SWIG (via resumo). Fonte: URL do anuncio acima.
- No CLI (comparando as docs 9.0 e 10.0, via resumo): `--variant` existe so no 10 (bom, netlist, pos, gerbers, ipc2581, odb, render, pdf...). So no 10: `pcb drc --save-board`, `pcb import`, `pcb export 3dpdf/u3d/stpz`. Ja existiam no 9: `--board-plot-params`, `--exclude-dnp`, `ipc2581 --version`, `odb --compression`, `jobset run`, `xao/brep`. Fontes: https://docs.kicad.org/10.0/en/cli/cli.html e https://docs.kicad.org/9.0/en/cli/cli.html .
- SWIG: continua embutido no 10; deprecado desde o 9.0, remocao planejada para o KiCad 11 (versao antiga da pagina dizia 10). Fonte: busca em https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/ (snippet; texto da pagina nao conferido).
- IPC API: no 9 e 10 so conversa com a GUI em execucao e **nao exporta/plota**; modo headless via `kicad-cli` e plugins no editor de esquematico so no KiCad 11. "Users of previous versions may make use of `kicad-cli` called from plugins to automate plotting/exporting tasks." Fonte: https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/ (via resumo).
- Consequencia para a skill (inferencia): automacao headless no 10 = `kicad-cli` + edicao de texto dos arquivos S-expression; nao ha API para editar esquematico.

## 3. Formato S-expression

Fontes: https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html , .../sexpr-schematic/index.html , .../sexpr-pcb/index.html , .../sexpr-symbol-lib/index.html (via resumo).

Regras gerais: tokens minusculos; strings UTF-8 entre aspas; unidades em mm sem notacao exponencial; resolucao 1 nm em placa/footprint (ate 6 casas) e 0,0001 mm em esquematico/simbolo (4 casas).

**Numero de versao no 10** (codigo-fonte, branch 10.0, via resumo):
- Esquematico e simbolos (`kicad_sch`): `20260306` ("Variant in_bom semantics corrected"). Fonte: https://raw.githubusercontent.com/KiCad/kicad-source-mirror/10.0/eeschema/sch_file_versions.h
- Placa (`kicad_pcb`): `20260206` ("Fix barcode and variant attribute serialization"). Fonte: https://raw.githubusercontent.com/KiCad/kicad-source-mirror/10.0/pcbnew/pcb_io/kicad_sexpr/pcb_io_kicad_sexpr.h
- A pagina de formato da dev-docs nao traz o valor literal da versao. Confirme abrindo e salvando um arquivo no KiCad 10 local. Versao de `.kicad_sym` e `.kicad_mod` no 10: nao verificado (o sym compartilha o header do esquematico, inferencia).

**`.kicad_sch` topo** (ordem da dev-docs): `(kicad_sch (version V) (generator G) [(generator_version "10.0")] (uuid U) (paper "A4") (lib_symbols ...) junction/no_connect/bus_entry/wire/bus/polyline/text/label/global_label/hierarchical_label/symbol/sheet ... (sheet_instances (path "/" (page "1"))))`. `generator_version` existe desde a versao 20231120; `sheet_instances`/`paper` nao constam como topo na pagina resumida; `paper` esta na secao comum. Nao use `eeschema` como `generator` em ferramenta de terceiros.
Sintaxes literais da pagina:
```
(symbol "LIB:NOME" (at X Y ANGLE) (unit N) (in_bom yes) (on_board yes) (uuid ...) (property "Reference" "R1" ...) (pin "1" (uuid ...))
  (instances (project "NOME" (path "/<uuid-folha-raiz>" (reference "R1") (unit 1)))))
(wire (pts (xy X1 Y1) (xy X2 Y2)) (stroke (width 0) (type default)) (uuid ...))
(junction (at X Y) (diameter 0) (color 0 0 0 0) (uuid ...))
(label "NET" (at X Y ANGLE) (effects ...) (uuid ...))
(global_label "NET" (shape input) (at X Y ANGLE) (effects ...) (uuid ...))
```
Exigencias para abrir sem erro: **nao verificado na fonte oficial**. Inferencias a validar com `kicad-cli sch upgrade` e `sch erc`: um `uuid` unico por objeto; `lib_symbols` com a definicao de cada `lib_id` usado; o `path` em `instances` deve bater com o uuid da folha raiz; simbolos de energia sao simbolos `power:` com `lib_symbols` embutido.

**`.kicad_pcb`** (dev-docs): cabecalho `(kicad_pcb (version V) (generator G))` primeiro; depois, em qualquer ordem, `general` (com `thickness`), `page`, `layers`, `setup`, `net`, `footprint`, `gr_*`, `segment/via/arc`, `zone`, `group`. Obrigatorios: header, `general`, `layers`, `setup`, `net`. Sintaxes: `(net 0 "")`, `(segment (start X Y) (end X Y) (width W) (layer "F.Cu") (net N) (uuid U))`, `(via (at X Y) (size D) (drill D) (layers "F.Cu" "B.Cu") (net N) (uuid U))`. A dev-docs usa `tstamp`; versoes novas usam `uuid` (inferencia, nao verificado). Lembrete: o 10 tem `generator_version`.

**`.kicad_pro`**: arquivo de projeto compartilhado entre esquematico e placa (JSON, conforme conhecimento previo; a doc consultada nao diz o formato). `.kicad_prl` e local (visibilidade de camadas), nao precisa ser versionado. `sym-lib-table` e `fp-lib-table`: global (no diretorio de configuracao do usuario) e opcional por projeto (na pasta do projeto). Projeto exige `.kicad_pro`, esquematico raiz e placa com o mesmo nome base; uma placa por projeto. Fonte: https://docs.kicad.org/10.0/en/kicad/kicad.html (via resumo). Sintaxe interna das tabelas: nao verificado.

## 4. KiCad Library Conventions (KLC)

Fonte oficial: https://klc.kicad.org (403 ao WebFetch; textos abaixo vem de snippets de busca, **nao conferidos**). Revisao 3.0.60 (2026-01-30) alterou a F5.3: https://klc.kicad.org/history

- S4.1 (https://klc.kicad.org/symbol/s4/s4.1/): pinos na grade de 100 mil (2,54 mm); comprimento minimo 100 mil, aumentando em passos de 50 mil conforme o numero do pino (2 caracteres 100 mil, 3 caracteres 150 mil); maximo 300 mil; todos os pinos do simbolo com mesmo comprimento (exceto discretos simples); numeros de pino unicos; nomes batendo com o datasheet.
- S3.1 (https://klc.kicad.org/symbol/s3/s3.1.html): origem no centro do simbolo simetrico. S3.2: texto de 50 mil.
- F5.3 courtyard (https://klc.kicad.org/footprint/f5/f5.3.html): retangulo na camada `F.CrtYd`, linha de 0,05 mm, grade de 0,01 mm; folga padrao **0,25 mm**; **0,15 mm** para pecas menores que 1,5 mm (texto exato revisado em 2026, conferir); conectores +0,5 mm; capacitores de lata e cristais 0,5 mm; BGA 1,0 mm.
- F3.x nomenclatura SMD: `[Prefixo]_[tamanho imperial]_[tamanho metrico]Metric_[modificadores]`, ex. `R_0603_1608Metric`, `C_1206_3216Metric` (https://klc.kicad.org/footprint/f3/f3.1).
- Fab: `F.Fab`/`B.Fab` sao camadas de documentacao para montagem (snippet de foruns, nao KLC). Regras F5.1 (silk), F5.2 (fab), grade de pads, origem: **nao verificado**.
- Densidade IPC-7351 e estrutura das bibliotecas oficiais: nao verificado.
- Modelos 3D: no 10 as bibliotecas oficiais trazem so STEP (https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/); a variavel de caminho e versionada, `${KICAD10_3DMODEL_DIR}` (forum, secundario: https://forum.kicad.info/t/3dview-in-kicad9-to-kicad10/67943). Nada no KLC e obrigatorio fora da submissao as bibliotecas oficiais (forum, secundario).

## 5. Regras de DRC customizadas (`.kicad_dru`)

Fonte: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html (secao "Custom design rules"; via resumo). O arquivo fica ao lado do `.kicad_pro`, com o mesmo nome base (inferencia).

```
(version 1)
(rule <nome>
    [(severity error|warning|ignore|exclusion)]
    [(layer <camada>|outer|inner)]
    [(condition "<expressao>")]
    (constraint <tipo> [(min X)] [(opt X)] [(max X)]))
```
- Comentarios com `#`. As regras sao avaliadas **de tras para frente**: coloque as especificas depois das gerais.
- Tipos: `annular_width, assertion, bridged_mask, clearance, connection_width, courtyard_clearance, creepage, diff_pair_gap, diff_pair_uncoupled, disallow, edge_clearance, hole_clearance, hole_size, hole_to_hole, length, min_resolved_spokes, physical_clearance, physical_hole_clearance, silk_clearance, skew, solder_mask_expansion, solder_paste_abs_margin, solder_paste_rel_margin, text_height, text_thickness, thermal_relief_gap, thermal_spoke_width, track_angle, track_segment_length, track_width, via_count, via_dangling, via_diameter, zone_connection`.

Exemplos (os cinco primeiros literais da doc; o ultimo e adaptado por mim e **nao testado**):
```
(version 1)
# Clearance for 400V nets to anything else
(rule HV
    (condition "A.hasNetclass('HV')")
    (constraint clearance (min 1.5mm)))

(rule "clearance_outer"
    (layer outer)
    (constraint clearance (min 0.25mm)))

(rule "BGA neckdown"
    (constraint track_width (min 0.2mm) (opt 0.25mm))
    (constraint clearance (min 0.05mm) (opt 0.08mm))
    (condition "A.intersectsCourtyard('U3')"))

(rule "Max Drill Hole Size PTH"
    (constraint hole_size (max 6.35mm))
    (condition "A.Pad_Type == 'Through-hole'"))

(rule "ignore_left"
    (constraint via_dangling)
    (condition "A.enclosedByArea('dangling vias allowed')")
    (severity ignore))

# ADAPTADO, nao testado: largura minima por net class
(rule "Power width"
    (condition "A.hasNetclass('Power')")
    (constraint track_width (min 0.5mm)))
```
- Exemplo de classe de componente com `courtyard_clearance`: na mesma pagina.
- Alta tensao entre duas nets de classes diferentes: um tutorial de terceiros usa prefixo comum nos nomes de netclass e curinga (`'HV*'` com `==`); nao verificado no 10 — teste no DRC. Fonte secundaria: https://forum.kicad.info/t/how-to-handle-net-classes-for-high-voltage-without-false-drc-errors/68593
- Ajuda embutida: Board Setup > Custom Rules > Syntax help.
- Rodar: `kicad-cli pcb drc` aplica o `.kicad_dru` do projeto (inferencia, nao verificado).

## Nao encontrado / nao verificado
- Texto literal da KLC (403) e lista completa de regras.
- Esquema do `.kicad_jobset` alem das chaves do codigo-fonte; exemplo de arquivo real.
- Nomes canonicos exatos de camadas para `--layers` (confira com `--help`).
- ~~Estrutura minima valida de `.kicad_sch`/`.kicad_pcb` testada abrindo no KiCad 10.~~ Resolvido: ver "Conferido na maquina".
- Formato `.kicad_pro` e `fp-lib-table` na doc oficial.
- ~~Versao de `.kicad_mod` no 10.~~ Resolvido: 20260206.

## Conferido na maquina (oraculo, 2026-10-12)

Medido no KiCad **10.0.0** instalado (Windows 11) pela familia de skills `pcb-*`, abrindo demos
regravados com `kicad-cli sch/pcb upgrade` e arquivos gerados pelos scripts. Substitui os "nao
verificado" acima no que se refere a estes pontos. Detalhe pratico em
`.claude/skills/pcb-esquematico/references/formato-kicad-sch.md` e
`.claude/skills/pcb-layout/references/freerouting.md`.

| Ponto | Resultado |
|---|---|
| Versao de formato | `.kicad_sch` 20260306; `.kicad_pcb` 20260206; `.kicad_sym` 20251024; `.kicad_mod` 20260206 |
| `version` maior que a instalada | `kicad-cli` recusa ("falha ao ler"), saida 3 |
| Bibliotecas de simbolo oficiais | Pastas `Lib.kicad_symdir/` com **um arquivo por simbolo** (22.712 arquivos); `extends` aponta para outro arquivo da mesma pasta |
| `sym-lib-table` global | Em `%APPDATA%/kicad/10.0/`, uma unica entrada `(type "Table")` apontando para `share/kicad/template/sym-lib-table` |
| Instancia de simbolo | `instances/project` = nome do `.kicad_pro`; `path` = `"/<uuid da folha raiz>"`. `path` errado nao e acusado nem por ERC nem por netlist |
| Footprint ↔ simbolo | No `.kicad_pcb`, `path` = `"/<uuid do simbolo>"` (sem o uuid da raiz), `sheetname "/"` |
| Redes na placa | Pelo nome, `(net "GND")`; nao ha tabela de redes no topo. Label local aparece como `/REDE` |
| Ids de camada de cobre | F.Cu 0, B.Cu 2, In1.Cu 4, In2.Cu 6 |
| `netclass_patterns` do `.kicad_pro` | E **regex** ancorado e sensivel a maiusculas; todas as classes que casam se aplicam (`(class "HV,Power")` na netlist) |
| `.kicad_dru` invalido | **Descartado em silencio**: erro de sintaxe, condicao invalida ou falta de `(version 1)` → DRC sai 0 sem aplicar regra. Dois `(version 1)` no arquivo concatenado sao aceitos |
| Ordem das regras `.kicad_dru` | Vale a **ultima** regra que casa, mesmo mais ampla |
| `rule_severities` no `.kicad_pro` | `"ignore"` some com a violacao do JSON mesmo com `--severity-all` (DRC e ERC) |
| Paridade com o esquematico | `missing_footprint` e cia. saem como **warning** por padrao: footprint faltando nao e erro |
| SWIG no Python do KiCad | `pcbnew` 10.0.0 tem `ExportSpecctraDSN`, `ImportSpecctraSES`, `FootprintLoad`, `ZONE_CONNECTION_THT_THERMAL` |
| Freerouting 2.5.0 | `-mp` e `-inc` obsoletos (usar `--router.autorouter.max_passes` e `--router.autorouter.ignore_net_classes`); build nativo `freerouting-cli` trava no headless; telemetria ligada por padrao |
