---
name: pcb-componentes
description: Escolhe componentes eletronicos faceis de comprar e confere simbolo, footprint e datasheet para o KiCad 10 — LCSC/JLCPCB Basic primeiro, Mouser e DigiKey para prototipo e ciclo de vida, busca nas bibliotecas instaladas, importacao por codigo LCSC (easyeda2kicad), segunda fonte, derating e armadilhas de pinagem. Use ao escolher ou trocar uma peca, montar ou revisar a BOM, procurar footprint ou simbolo, achar codigo LCSC ou MPN equivalente, perguntar "qual regulador/MOSFET/driver/conector usar", estimar custo de BOM ou importacao de componentes.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebFetch, WebSearch, AskUserQuestion
version: 1.0
---

# /pcb-componentes — peca certa, comprável e com footprint conferido

Parte da familia `pcb-*` (roteiro geral em `pcb-projeto`). Scripts em
`.claude/skills/pcb-projeto/scripts/`.

Uma peca so entra na spec do esquematico com **cinco coisas confirmadas**: requisito eletrico
atendido com folga, datasheet lido, compra possivel (estoque e ciclo de vida), simbolo e footprint
existentes e com pinagem casada. O erro mais caro de uma placa nao e o de roteamento: e o footprint
com pino trocado ou a peca que some do mercado entre o prototipo e o lote.

## Ordem de preferencia de fonte

1. **LCSC Basic** (JLCPCB) — sem taxa de montagem por peca; e onde a montagem SMT da JLC e mais
   barata. Passivos, diodos, transistores e CIs comuns quase sempre tem Basic.
2. **LCSC Preferred / Extended com estoque alto** — Extended paga cerca de US$ 3 por peca unica na
   montagem (conferir na pagina de precos; ver ficha). Aceitavel para CI que nao tem Basic.
3. **Mouser / DigiKey** — prototipo de montagem manual, peca que a LCSC nao tem, e a referencia de
   ciclo de vida (Active/NRND/Obsolete) e datasheet oficial. Mesmo quando a peca vem da LCSC, o
   MPN deve existir em Mouser ou DigiKey: e a segunda fonte e a prova de que nao e peca obscura.

Lojas nacionais (Bau da Eletronica e similares) servem para bancada e reposicao de prototipo, nao
como fonte da BOM de producao.

## Fluxo

1. **Requisito.** Escreva o que a peca precisa atender antes de buscar: tensao e corrente com
   margem, encapsulamento aceitavel, temperatura, interface. Folgas em
   `references/criterios-de-escolha.md`.
2. **Busca — pelo MPN, depois pelo codigo LCSC.**
   ```bash
   S=.claude/skills/pcb-projeto/scripts
   python $S/buscar_distribuidor.py digikey "buck 3.3V 600mA"     # parametrica: acha o MPN
   python $S/buscar_distribuidor.py mouser DRV8871DDAR            # estoque, ciclo de vida, datasheet
   python $S/buscar_lcsc.py C780769                               # confirma o codigo LCSC
   python $S/buscar_lcsc.py C1525 --json
   ```
   - Busca parametrica e por texto: Mouser/DigiKey (`buscar_distribuidor.py`, exige chave) ou o
     catalogo da JLC/LCSC e o jlcparts no navegador. Com o MPN em maos, ache o codigo LCSC (pagina
     da LCSC/JLC ou busca web "`<MPN>` LCSC") e **confirme** com `buscar_lcsc.py <Cxxxx>`.
   - `buscar_lcsc.py` consulta o jlcsearch (nao oficial). Verificado em 2026-10-12: a busca por
     **codigo** e confiavel; a busca por **texto** devolve resultado irrelevante e so indexa peca com
     estoque na JLC. Para codigo fora do indice, o script cai na API de detalhe da LCSC: o resultado
     vem com `fonte: lcsc-detail`, `estoque_origem: lcsc` (estoque da LCSC, **nao** o da montagem JLC)
     e `classe: desconhecido` — nao trate como Basic nem como Extended. Confirme estoque, preco e
     Basic/Extended no site da JLC antes do pedido.
   - Chaves (`MOUSER_API_KEY`, `DIGIKEY_CLIENT_ID`/`_SECRET`) no bloco `env` do
     `.claude/settings.local.json` — nunca no repositorio. Sem chave, o script explica como obter.
     Codigos de saida dos dois: 0 achou, 1 sem resultado, 2 sem chave/uso, 3 rede/HTTP/formato.
3. **Datasheet.** Leia as secoes que importam: valores maximos absolutos, condicoes recomendadas,
   pinagem (vista de cima), circuito de aplicacao tipico, layout recomendado e land pattern. Guarde o
   link no campo `Datasheet`. Circuito de aplicacao do fabricante e o ponto de partida do
   esquematico — nao invente valores que o datasheet da.
4. **Simbolo e footprint.**
   ```bash
   python .claude/skills/pcb-projeto/scripts/buscar_biblioteca.py simbolo DRV8871
   python .claude/skills/pcb-projeto/scripts/buscar_biblioteca.py footprint "SOIC-8"
   python .claude/skills/pcb-projeto/scripts/buscar_biblioteca.py pinos Driver_Motor:DRV8871DDA
   ```
   Ordem: biblioteca oficial do KiCad → importacao pelo codigo LCSC (`easyeda2kicad`) para a
   biblioteca do projeto → desenho proprio seguindo a KLC. Detalhes e armadilhas em
   `references/simbolos-e-footprints.md`.
5. **Casamento de pinagem.** Compare numero de pino do simbolo com numero de pad do footprint **e**
   com o datasheet. Simbolo generico (`Device:Q_PMOS_GSD`, por exemplo) carrega a ordem no nome;
   ela tem de bater com a do encapsulamento da peca escolhida.
6. **Registro.** Preencha os campos do componente na spec:

| Campo | Exemplo | Obrigatorio |
|---|---|---|
| `valor` | `10k`, `100nF 50V X7R`, `AP63203WU` | Sim |
| `footprint` | `Resistor_SMD:R_0603_1608Metric` | Sim |
| `Datasheet` | URL do fabricante | Sim |
| `MPN` | `0603WAF1002T5E` | Sim |
| `Fabricante` | `UNI-ROYAL` | Sim |
| `LCSC` | `C25804` | Sim se montado pela JLC |
| `Mouser` / `DigiKey` | numero do distribuidor | Recomendado |
| `Sem_LCSC` | `borne soldado a mao` | So quando a peca vai na placa mas nao pela montagem JLC |

`exportar_fab.py` e o `portao_liberacao.py` leem esses nomes de campo exatamente assim.

## Regras rapidas

- Passivos em **0603** por padrao; **0805** se a montagem for manual; 0402 so por falta de espaco
  (a montagem Economic da JLC aceita 0402 no minimo).
- CI em SOIC, SOT ou TSSOP antes de QFN; QFN so com pad termico necessario ou sem alternativa; BGA
  fora de questao em placa de 2 camadas sem motivo forte.
- Valores da serie E24 para resistor e E6/E12 para capacitor — e o que tem estoque.
- Capacitor ceramico perde capacitancia com tensao DC aplicada: tensao nominal de pelo menos o dobro
  da de trabalho e dieletrico X7R/X5R para desacoplamento e filtro.
- Ciclo de vida **Active** em pelo menos um distribuidor grande; NRND so com justificativa escrita.
- Estoque: pelo menos 10 vezes o necessario para o lote planejado (parametro do projeto — ajuste).
- Modulo certificado (radio, AC-DC) antes de circuito discreto equivalente.

## Brasil: custo de importacao

A Halcyon compra como **pessoa juridica**: a isencao de ate US$ 50 e de pessoa fisica. Pela pagina
da Receita (atualizada em 2026-05-19), PJ paga imposto de importacao de 60% mais ICMS mesmo abaixo
de US$ 50. A lei de setembro de 2026 que reduz a faixa maior para 30% **nao foi confirmada para PJ**.
DigiKey entrega com frete fixo de US$ 40 e impostos por conta do comprador; a Karimex revende DigiKey
com preco final em reais. Detalhes e o que falta confirmar em `references/fontes-e-apis.md` —
confirme com o contador antes de transformar em orcamento.

## Referencias

- `references/criterios-de-escolha.md` — folgas (derating) por tipo de peca, encapsulamentos,
  ciclo de vida, segunda fonte, pecas de mecatronica recorrentes.
- `references/simbolos-e-footprints.md` — bibliotecas oficiais, KLC, `easyeda2kicad`, criacao de
  simbolo/footprint proprio, armadilhas de pinagem.
- `references/fontes-e-apis.md` — JLCPCB/LCSC, Mouser, DigiKey, Nexar, lojas e fabricas no Brasil,
  importacao.
- Ficha completa: `docs_projeto/referencias/componentes-e-fabricacao-pcb.md`.
