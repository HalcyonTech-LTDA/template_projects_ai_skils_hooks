# Scripts da familia pcb-* (KiCad 10)

Toolkit unico das skills `pcb-projeto`, `pcb-componentes`, `pcb-esquematico`, `pcb-layout` e
`pcb-fabricacao`. Toda a logica fica no pacote `pcbkit/` (biblioteca padrao do Python, sem
dependencias); os scripts sao a linha de comando.

## Como rodar

```bash
# Python do sistema (3.10+), a partir da raiz do repositorio
python .claude/skills/pcb-projeto/scripts/<script>.py ...

# Scripts SWIG (pcbnew): so no Python embarcado do KiCad. O diagnostico imprime o caminho.
"C:/Program Files/KiCad/10.0/bin/python.exe" .claude/skills/pcb-projeto/scripts/<script>.py ...
```

Convencoes de todos os scripts: `--json` troca a saida humana por JSON; codigo de saida diferente
de 0 em falha; caminhos com espaco, `&` e acento funcionam (passe entre aspas).

## Catalogo

| Script | Uso | Saida |
|---|---|---|
| `diagnostico.py [--json]` | Versao do KiCad, `kicad-cli`, Python do KiCad com `pcbnew`, pastas de biblioteca, Java, jar do Freerouting (`FREEROUTING_JAR`), `uvx`/`easyeda2kicad`, presenca (nunca o valor) de `MOUSER_API_KEY`, `DIGIKEY_CLIENT_ID`, `DIGIKEY_CLIENT_SECRET` | 0 nucleo pronto; 1 falta `kicad-cli` ou `pcbnew` |
| `novo_projeto.py <dir-hardware> --nome <placa> [--camadas 2\|4] [--rev A] [--projeto NOME] [--titulo T] [--empresa E] [--alta-tensao] [--docs <dir 03_Hardware>]` | Cria `<dir-hardware>/<placa>/`: `.kicad_pro` (net classes Default/Power/HV), `.kicad_dru` JLC (+ regras HV com `--alta-tensao`), `.kicad_sch`/`.kicad_pcb` vazios, `sym-lib-table`/`fp-lib-table` para `bibliotecas/`, `spec/<placa>.json`, `.gitignore`, `README.md`. `--docs` copia `assets/docs/**/*.md` trocando `{{placa}}`, `{{projeto}}`, `{{rev}}`, `{{data}}` no caminho e no conteudo; com `--alta-tensao` copia tambem `assets/opcionais/` para `Eletronica/Gerber/`. Nunca sobrescreve | 0 criado; 1 projeto ja existe ou nome invalido; 2 uso, `--rev` ou `--projeto` invalido (caminho, `..`, nome reservado do Windows) |
| `buscar_biblioteca.py simbolo <termo>` | Busca simbolo por nome, descricao e palavras-chave nas bibliotecas instaladas (+ do projeto com `--projeto <dir>`) | 0 achou; 1 nada; 2 uso ou KiCad ausente |
| `buscar_biblioteca.py footprint <termo>` | Idem para footprint (nome, `descr`, `tags`) | idem |
| `buscar_biblioteca.py pinos <Lib:Simbolo>` | Pinos (numero, nome, tipo eletrico, unidade, posicao, orientacao, comprimento), footprint sugerido e filtro; resolve `extends` | 0; 1 simbolo ou biblioteca inexistente |
| `buscar_biblioteca.py pads <Lib:Footprint>` | Numeros dos pads do footprint (conferir contra os pinos) | idem |
| `buscar_lcsc.py <termo ou Cxxxx> [--basic] [--json] [--limite N]` | Peca LCSC/JLCPCB pelo jlcsearch (nao oficial, sem chave): codigo, MPN, encapsulamento, estoque, preco, Basic/Preferred. Codigo sem resultado cai no detalhe da LCSC | 0 achou; 1 sem resultado; 2 uso; 3 rede/HTTP/formato |
| `buscar_distribuidor.py mouser\|digikey <termo ou MPN> [--json] [--limite N] [--modo auto\|keyword\|partnumber] [--site US] [--moeda USD]` | APIs oficiais da Mouser e DigiKey: MPN, fabricante, estoque, preco, ciclo de vida, datasheet | 0 achou; 1 sem resultado; 2 sem chave ou uso errado; 3 rede/HTTP/formato |
| `gerar_esquematico.py <spec.json> -o <placa>.kicad_sch [--projeto DIR] [--sobrescrever] [--json]` | Esquematico a partir da spec (estilo label por pino, blocos como regioes da folha, uuids estaveis entre geracoes). Valida a spec inteira antes: ref duplicada, componente fora de bloco ou em dois, simbolo/footprint/pino inexistente, rede com um pino, pino em duas redes, pino sem rede fora de `nao_conectar`, pinos empilhados em redes diferentes. Recusa sobrescrever `.kicad_sch` salvo pela GUI (`generator` diferente de `pcbkit`) sem `--sobrescrever` | 0 gerado; 1 spec invalida (lista todos os erros) ou esquematico salvo pela GUI; 2 uso ou KiCad ausente |
| `verificar.py erc <sch> [--relatorio R] [--estrito] [--json]` | ERC pelo `kicad-cli` (`--severity-all`), resumo por tipo | 0 sem erro; 1 erro (ou aviso com `--estrito`); 2 uso/KiCad |
| `verificar.py netlist <sch> --spec <spec.json> [--projeto DIR] [--json]` | Exporta a netlist e prova que cada rede da spec tem exatamente os pinos declarados; relata redes faltando, pinos sobrando/faltando, redes inesperadas, componentes e footprints divergentes | 0 bate; 1 diverge; 2 uso, spec invalida ou KiCad |
| `verificar.py drc <pcb> [--paridade] [--estrito] [--relatorio R] [--json]` | DRC pelo `kicad-cli` (`--severity-all --refill-zones`; a placa em disco nao muda), resumo por tipo, conexoes faltando por rede e por net class; `--paridade` = `--schematic-parity` (footprint faltando/sobrando, rede divergente) | 0 sem erro; 1 erro, conexao faltando ou paridade em qualquer severidade (footprint faltando sai como aviso no 10.0.0); demais avisos so com `--estrito`; 2 uso/KiCad |
| `verificar.py dru <arquivo.kicad_dru> [--pro P] [--json]` | Prova que o `kicad-cli` aceita o `.kicad_dru` (regra-canario: arquivo invalido e descartado em silencio pelo DRC); usa o `.kicad_pro` de mesmo nome se existir | 0 aceito; 1 rejeitado; 2 uso/KiCad |
| `pcb_do_esquematico.py <sch> --spec <spec.json> -o <pcb> [--largura MM --altura MM] [--furos M3\|nenhum] [--projeto DIR] [--sobrescrever] [--json]` | **(SWIG)** Netlist pelo `kicad-cli`; net classes da spec no `.kicad_pro` vizinho (`netclass_patterns` com o nome como a placa ve: `/REDE` para label, `REDE` para power; sem `.kicad_pro`/`.kicad_dru`, copia os modelos e avisa); footprints ligados aos simbolos (path = uuid do simbolo), redes nos pads, posicionamento por bloco, contorno, furos M3 nos cantos, zonas de GND em F.Cu e B.Cu preenchidas. Tamanho automatico (passos de 5 mm) sem `--largura/--altura` | 0 gravada; 1 spec invalida, nao cabe (diz o tamanho minimo) ou placa ja tem itens (footprint, trilha, zona, desenho; exige `--sobrescrever`); 2 uso, KiCad ausente ou fora do Python do KiCad |
| `rotear.py <pcb> [--ignorar-classes Power,HV] [--passes N] [--threads N] [--timeout S] [--manter-intermediarios] [--json]` | **(SWIG)** Freerouting sem interface (jar, `FREEROUTING_JAR`): trava e preserva as trilhas existentes, exporta DSN sem planos, roteia sem fanout, so importa do SES as redes com ligacao faltando (DRC numa copia sem zonas) e fora das classes ignoradas (re-rodar numa placa roteada nao duplica cobre; sem pendencia nem chama o Freerouting), importa, alarga o neckdown abaixo da trilha minima (desfaz se violar regra), reenche zonas, grava e mede o que ficou sem ligar por net class. Padrao ignora `Power` e `HV`; `""` roteia tudo. Rede em duas classes (classe composta `HV,Power` no DSN) e ignorada se qualquer parte for pedida; a flag do Freerouting so leva os nomes simples e a composta e tirada pelo filtro do SES. Detalhes em `pcb-layout/references/freerouting.md` | 0 ligou todas as classes nao ignoradas sem erro de regra; 1 sobrou conexao fora das ignoradas, erro de regra ou Freerouting falhou; 2 uso, Freerouting/Java/KiCad ausente ou fora do Python do KiCad |
| `exportar_fab.py <dir-projeto> [--rev A] [--saida DIR] [--json]` | Pacote de trabalho em `<dir-projeto>/fab/rev-<R>/` (ou `--saida`, recusada dentro de `releases/`): `<placa>-rev-<R>-gerber.zip` (Gerber 4.6 mm, Protel, X2, zonas conferidas, mascara subtraida da serigrafia; furacao Excellon mm absoluta com PTH e NPTH separados), `-bom-jlc.csv` (`Comment,Designator,Footprint,JLCPCB Part #`), `-cpl-jlc.csv` (`Designator,Mid X,Mid Y,Rotation,Layer`, mm, `Top`/`Bottom`), `-bom.csv` (BOM completa), `-esquematico.pdf`, `-mapa-furos-PTH.pdf`/`-NPTH.pdf`, `<placa>-rev-<R>.step`, `render-top.png`, `render-bottom.png` e `manifesto.json`. STEP e render sao opcionais (falha vira aviso) | 0 gerado; 1 exportacao falhou; 2 uso, `--saida` dentro de `releases/` ou KiCad ausente |
| `exportar_fab.py <dir-projeto> --rev A --liberar --checklist <nota> [--aprovacao-hv <nota>]` | Recusa se `releases/rev-<R>/` ja existe; roda o portao e, so se passar, gera o pacote e copia zip, BOM JLC, CPL JLC, BOM completa e PDF para `releases/rev-<R>/` com `manifesto.json` (SHA-256 e tamanho de cada arquivo, versao do KiCad, data, comandos do kicad-cli com caminhos relativos, nota, revisores, avisos de DRC, severidades rebaixadas e exclusoes do `.kicad_pro`). `--rev` precisa ser a `revisao` da spec | 0 liberado; 1 portao bloqueou ou release ja existe; 2 uso |
| `portao_liberacao.py <dir-projeto> --checklist <nota> [--aprovacao-hv <nota>] [--rev A] [--json]` | Portao 2, tudo de novo: ERC sem erros nem avisos; DRC sem erros com paridade e zonas reenchidas (paridade e conexao faltando **bloqueiam em qualquer severidade**: no 10.0.0 `missing_footprint` sai como aviso; os demais **avisos sao listados e nao bloqueiam**); nenhuma regra critica de ERC/DRC rebaixada no `.kicad_pro` (`rule_severities`; rebaixamentos nao criticos e exclusoes sao listados); `.kicad_dru` aceito (regra-canario); `revisao` e `tensao_max_v` declarados na spec (`tensao_max_v` e o pico; nao finito bloqueia; negativo vale o modulo) e `--rev` igual a `revisao` da spec; `MPN` e `LCSC` em todo componente montado (falta de LCSC aceita com motivo no campo `Sem_LCSC`); nota de liberacao com `type: gate`, `gate: liberacao`, `placa` e `revisao` do projeto, `status: aprovado`, `revisores` e nenhum item aberto (`- [x] N/A — motivo` conta; N/A sem motivo nao). Alta tensao (`tensao_max_v` > 60 V, ou > 42,4 V com `tensao_ac: true`; valor ausente; rede na net class `HV`, inclusive composta ou por padrao regex; redes `HV` na spec): nota `gate: alta-tensao` `<placa>_Rev<R>_Aprovacao_Alta_Tensao.md` ao lado da nota (ou `--aprovacao-hv`, nunca o mesmo arquivo da nota de liberacao) aprovada, e regras HV validas (`pcbkit/regra_hv.py`) de `clearance` e `creepage` >= 2,5 mm (ou o `clearance_mm`/`creepage_mm` do frontmatter da nota HV, se maior) | 0 liberado; 1 bloqueado; 2 uso, projeto invalido ou KiCad ausente |

**Busca de peca LCSC: a busca por texto do jlcsearch e pouco confiavel** (em 2026-10-12 devolveu
itens sem relacao com o termo e so indexa pecas com estoque). O caminho e: **MPN** (datasheet,
Mouser ou DigiKey) → **codigo LCSC** (site da JLC/LCSC ou busca "<MPN> LCSC") →
`buscar_lcsc.py <Cxxxx>` para confirmar. Confira sempre em `https://jlcpcb.com/partdetail/<Cxxxx>`.

Importar simbolo/footprint de uma peca LCSC que nao existe nas bibliotecas do KiCad:
`uvx easyeda2kicad --full --lcsc_id=<Cxxxx> --project-relative --output <projeto>/lcsc` (o
`--output` e prefixo, e o modelo 3D so resolve com `lcsc.3dshapes/` na raiz do projeto) seguido de
`kicad-cli sym upgrade` e `kicad-cli fp upgrade`, registrando `lcsc` no `sym-lib-table` e no
`fp-lib-table` do projeto e corrigindo os tipos eletricos dos pinos (ver
`pcb-componentes/references/simbolos-e-footprints.md`).

**Campos de componente lidos pela fab** (da netlist do esquematico): `MPN`, `Fabricante`
(← `Manufacturer`), `LCSC` (← `LCSC Part`, `LCSC Part #`, `JLCPCB Part #`), `Mouser`, `DigiKey`,
`Datasheet` e `Sem_LCSC` (motivo de nao ter codigo LCSC: fica na BOM completa, sai da BOM/CPL da JLC).
DNP e "excluir da BOM" tiram o componente de todas as BOMs e do CPL. A rotacao do CPL e a do KiCad:
confira no preview da JLC.

## pcbkit

| Modulo | Responsabilidade |
|---|---|
| `ambiente.py` | Acha o KiCad (`KICAD_CLI`/`KICAD_DIR` → `C:/Program Files/KiCad/<maior versao>` → PATH), Python do KiCad, pastas de biblioteca (`KICAD10_*_DIR`), config do usuario, Java, Freerouting, `uvx` |
| `sexpr.py` | Parser/serializador S-expression (round-trip; `Simbolo` = atomo sem aspas); `carregar_todos(..., comentarios=True)` le `.kicad_dru` |
| `bibliotecas.py` | `sym-lib-table`/`fp-lib-table` (projeto vence global; global `type "Table"` aninhada), `.kicad_sym` e `.kicad_symdir`, `extends` achatado, pinos, busca |
| `kicad_cli.py` | ERC/DRC/netlist/upgrade pelo `kicad-cli`, leitura do relatorio JSON, `validar_dru` (regra-canario: o `kicad-cli` descarta `.kicad_dru` invalido em silencio) |
| `modelos.py` | `.kicad_sch`, `.kicad_pcb`, `.kicad_sym` e tabelas de biblioteca vazios no formato do KiCad 10 |
| `console.py` | UTF-8 no console do Windows, saida JSON |
| `netlist.py` | Le a netlist `kicadsexpr` (redes, pinos, componentes e a net class de cada rede, `(class "HV,Power")` separada em lista) e compara com a spec (`/REDE` de label local = `REDE` da spec) |
| `esquematico/` | `spec.py` (validacao e resolucao `REF.pino`), `geometria.py` (biblioteca -> folha), `caixas.py` (caixas e texto), `posicionamento.py` (blocos, itens, fios/labels/power), `escritor.py` (`.kicad_sch`, uuid5 por projeto+ref+unidade) |
| `regras.py` | Net classes da spec no `.kicad_pro` (`classes`, `netclass_patterns`), copia de `.kicad_pro`/`.kicad_dru` modelo, classes de uma rede pelo padrao como o KiCad 10 casa (curinga `*`/`?` ou regex, ancorado, sensivel a maiusculas; duas classes = composta `HV,Power`) |
| `drc.py` | Resumo do relatorio de DRC: por tipo, conexoes faltando por rede (lida entre colchetes na descricao) e por net class (inclusive composta) |
| `freerouting.py` | Linha de comando do Freerouting 2.5.0 (flags reais, telemetria desligada, dados fora do perfil), execucao com timeout, resumo do log, leitura de classes do DSN, `sem_planos`, `filtrar_sessao` |
| `projeto.py` | Arquivos de `hardware/<placa>/` (placa = stem do unico `.kicad_pro`), leitura da spec |
| `nota.py` | Nota de portao: frontmatter (escalar, lista em linha ou em bloco, comentario `#` cortado, `null`/`~`/`""`/`[]` vazios, campo repetido bloqueia), itens abertos (`-`/`*`/`+`/numerados, em callout `>`, qualquer caixa que nao seja `[x]`) fora de bloco de codigo (cerca fecha com o mesmo marcador e comprimento >= o de abertura; cerca sem fechamento bloqueia), `N/A` sem motivo (sem diferenciar maiusculas), criterio de aprovacao |
| `portao.py` | Portao de liberacao: verificacoes puras (ERC, DRC, severidades, `.kicad_dru`, revisao e tensao da spec, BOM, notas por papel `gate`, alta tensao, regras HV) e `rodar()` que chama o kicad-cli |
| `severidades.py` | `rule_severities` e exclusoes de ERC/DRC do `.kicad_pro` (o kicad-cli os aplica mesmo com `--severity-all`): padrao do KiCad 10.0.0, regras criticas que nao podem ser rebaixadas, rebaixamentos e exclusoes listados |
| `regra_hv.py` | Regras da net class `HV` no `.kicad_dru`: condicao aceita, severity, layer, minimo em mm/mil/in, e regra posterior que anula a HV (o KiCad usa a ultima regra que casa) |
| `fab/` | `bom.py` (componentes da netlist com fallbacks de campo, BOM completa), `jlc.py` (BOM e CPL da JLC), `pacote.py` (exportacoes pelo kicad-cli, zip, conferencia de camadas), `manifesto.py` (SHA-256, versao, comandos) |
| `swig/` | So no Python do KiCad (o `__init__` nao importa `pcbnew`): `placa.py` (footprints ligados aos simbolos, redes nos pads, contorno, furos, zonas), `specctra.py` (DSN/SES preservando trilhas existentes, neckdown), `posicionamento.py` (geometria pura, roda e e testada no Python do sistema) |

## Testes

```bash
python -m unittest discover -s .claude/skills/pcb-projeto/scripts/tests
```

Os testes que precisam do KiCad sao pulados se o `kicad-cli` nao for encontrado. Os que rodam o
`kicad-cli` levam alguns segundos cada (DRC). O teste de rede real do `buscar_lcsc` so roda com
`PCB_TESTES_REDE=1`. Os de `pcb_do_esquematico.py`/`rotear.py` (`test_pcb_kicad.py`) rodam o Python
do KiCad por subprocesso (pulam sem `pcbnew`); os de roteamento pulam sem `FREEROUTING_JAR` e Java
(cerca de 1 minuto a mais com eles).
