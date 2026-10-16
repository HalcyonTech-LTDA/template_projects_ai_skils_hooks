---
title: Componentes e fabricacao de PCB — JLCPCB, LCSC, distribuidores e Brasil
source: https://jlcpcb.com/capabilities/pcb-capabilities
type: referencia
status: aprovado
created: 2026-10-12
updated: 2026-10-12
verificado_em: 2026-10-12
tags: [referencia, pcb, componentes, fabricacao, tema/hardware]
---

# Componentes e fabricacao de PCB

Pesquisa feita em 2026-10-12 para a skill de KiCad 10 (mecatronica: sensores, MCU, drivers, fontes).

**Aviso de metodo.** A ferramenta de leitura de paginas devolve resumos, nao o texto bruto. Nao foi possivel rodar `curl` nesta sessao. Por isso nada abaixo e citacao literal conferida: todo trecho entre aspas e "via resumo, nao conferido". Numeros que decidem custo (taxa extended, imposto de importacao) devem ser reconferidos na pagina antes de entrar em regra da skill. Tudo "visto em 2026-10-12".

## 1. JLCPCB / LCSC

### 1.1 Basic, Preferred, Extended e custo

- Basic: pecas de uso frequente (resistor/capacitor chip) que ficam carregadas na pick-and-place, sem custo de mao de obra. Fonte: https://jlcpcb.com/help/article/pcb-assembly-faqs
- Extended: o operador monta o alimentador (feeder) manualmente. A FAQ diz que cada componente extended custa US$ 3. Fonte: https://jlcpcb.com/help/article/pcb-assembly-faqs
- Preferred Extended: pecas que eram Basic e hoje sao Extended (Preferred). "Isentas da taxa de feeder loading" na montagem **Economic**. Fonte: https://jlcpcb.com/help/article/pcb-assembly-faqs (via resumo). Ou seja, **Preferred ainda existe**, mas a isencao so vale em Economic (ver 1.4: Economic = so face superior, ate 50 pcs).
- Tabela de custo (US$, sujeita a cambio): https://jlcpcb.com/help/article/pcb-assembly-price (via resumo, nao conferida)
  - Setup: Economic 8,18; Standard 25,56 (1 face) / 51,12 (2 faces)
  - Stencil: Economic 1,53; Standard 8,21 / 16,42
  - Feeder loading: Economic Extended 3,07; Standard Basic/Extended 1,53 cada
  - Handling Standard: a partir de 14,93
- Divergencia: a FAQ diz US$ 3 por extended; a tabela diz 3,07 (Economic). Tratar como "cerca de US$ 3". Paginas antigas (Q&A, carrinho) citam US$ 1,5 por peca no Standard, coerente com a tabela.
- Promocoes mudam: fontes de terceiros dizem que a JLC as vezes isenta a taxa de um subconjunto de extended. Nao verificado em fonte oficial.
- Lista atual de pecas Preferred: **nao verificada**. Consultar https://jlcpcb.com/parts/basic_parts e o filtro da biblioteca.

### 1.2 Como buscar pecas

- Site oficial: https://jlcpcb.com/parts (biblioteca; so listado, nao li o conteudo).
- jlcparts (yaqwsx), nao oficial: UI em https://yaqwsx.github.io/jlcparts/ , baixa a base no navegador (IndexedDB) e consulta localmente; busca parametrica e por texto, links para datasheet e LCSC. Repo: https://github.com/yaqwsx/jlcparts . Frequencia de atualizacao: nao informada. Nao ha dump pronto para usuario final (so via workflow de desenvolvedor).
- jlcsearch (tscircuit), nao oficial, "JLCPCB In-Stock Parts Engine": https://jlcsearch.tscircuit.com . A pagina nao documenta API. Um guia de terceiros diz que o servico tem API publica sem autenticacao (https://glama.ai/mcp/servers/@mixelpixx/KiCAD-MCP-Server/blob/d2723bc29207c942bc93083131e2ac2a8d1a82d5/docs/JLCPCB_USAGE_GUIDE.md). Termos: nao encontrados.
- API oficial JLCPCB: uma pagina de terceiros afirma que `api.jlcpcb.com` existe e que o acesso depende de analise (historico de pedidos/perfil). Nao confirmado em fonte oficial. https://claudeskills.info/skills/aklofas/kicad-happy/jlcpcb/
- API publica oficial da LCSC: **nao encontrada**.

### 1.3 easyeda2kicad

- Repo: https://github.com/uPesy/easyeda2kicad.py
- PyPI: versao **1.0.1, de 2026-04-06**, Python >= 3.9. https://pypi.org/project/easyeda2kicad/
- README: suporta "KiCad v6 e superior"; v5 nao. KiCad 9 e 10 **nao sao citados** — nao ha confirmacao de teste com o KiCad 10. Tratar como "provavelmente funciona, nao verificado"; validar footprint e simbolo importados antes de rotear.
- Instalar: `pip install easyeda2kicad`. No Windows, usar o prompt do KiCad e `python -m easyeda2kicad`.
- Uso: `easyeda2kicad --full --lcsc_id=C2040` (simbolo + footprint + 3D); varios IDs: `--lcsc_id C2040 C20197`. Flags: `--symbol`, `--footprint`, `--3d`, `--output <pasta>`, `--overwrite`, `--project-relative` (modelo 3D relativo a `${KIPRJMOD}`), `--custom-field "Chave:Valor"` (util para gravar `LCSC Part #`), `--use-cache`. Saida padrao: `~/Documents/Kicad/easyeda2kicad/`.

### 1.4 Capacidades de fabricacao (pagina de capacidades, via resumo)

Fonte: https://jlcpcb.com/capabilities/pcb-capabilities
- Trilha/espaco minimo: 1-2 camadas, 1 oz: 0,10/0,10 mm (4/4 mil). Multicamada, 1 oz: 0,09/0,09 mm (3,5/3,5 mil).
- Furo minimo de via: 0,15 mm (2 camadas e multicamada). 0,1 mm so para placa <= 1 mm com ENIG/OSP. 1 camada: 0,3 mm (so NPTH).
- Anel anular PTH: 2 camadas: recomendado 0,25 mm, minimo absoluto 0,18 mm. Multicamada: recomendado 0,20 mm, minimo absoluto 0,15 mm.
- Camadas: 1 a 32.
- Espessura: 0,4 a 4,5 mm; opcoes padrao 0,4/0,6/0,8/1,0/1,2/1,6/2,0 mm. A FAQ cita outra faixa (0,4 a 3,2 mm): confirmar antes de pedir.
- Impedancia controlada: a partir de 4 camadas; tolerancia padrao +-10% (FAQ cita +-5% sob pedido).
- Montagem (https://jlcpcb.com/capabilities/pcb-assembly-capabilities , via resumo): Economic: pacote minimo 0402, passo minimo de CI 0,4 mm, BGA 0,5 mm, placa 10x10 a 470x500 mm, 2 a 50 pcs. Standard: pacote minimo 0201, passo 0,35 mm, BGA 0,3 mm, placa minima 70x70 mm, 2 a 80.000 pcs. A FAQ diz que Economic exige painelizacao acima de 30 pecas (https://jlcpcb.com/help/article/pcb-assembly-faqs). Nota: a busca de terceiros informa que Economic e so face superior; isso nao apareceu nas paginas lidas (nao verificado).

### 1.5 BOM e CPL para a montagem JLC

Fonte: https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad ("How To Export BOM and CPL Files From KiCad 10", via resumo).
- BOM (.csv/.xls/.xlsx), no minimo: `Comment`, `Designator`, `Footprint`, `JLCPCB / LCSC Part #`.
- CPL: `Designator`, `Mid X`, `Mid Y`, `Rotation`, `Layer`, em mm.
- Metodo recomendado pela JLC: plugin **Fabrication Toolkit** (Plugin and Content Manager). Gera pasta `production` com Gerbers, `bom.csv` e `positions.csv` ja no formato JLC. Opcoes: "Apply automatic component translations" e "Apply automatic fill for all zones".
- Fabrication Toolkit (bennymeg): https://github.com/bennymeg/Fabrication-Toolkit . Pagina de releases (via resumo): **v5.3.0 "Added KiCad 10 support"**, v5.3.1 corrige "Duplicate footprint in KiCad 10", ambos em 15 de maio (ano nao mostrado na pagina). https://github.com/bennymeg/Fabrication-Toolkit/releases
- Campo no simbolo: o plugin le "LCSC Part #", "LCSC Part", "LCSC PN", "JLCPCB Part Number", e, como fallback, "LCSC", "JLC", "MPN". Depois de editar o esquematico, atualizar o PCB (F8).
- Alternativa por script (kicad-cli, docs https://docs.kicad.org/10.0/en/cli/cli.html , via resumo):
  - `kicad-cli pcb export pos --format csv --units mm --side both --exclude-dnp --smd-only <placa>.kicad_pcb`
  - `kicad-cli sch export bom --fields "Value,Reference,Footprint,LCSC Part #" --labels "Comment,Designator,Footprint,LCSC Part #" --group-by "Value,Footprint,LCSC Part #" --exclude-dnp <esq>.kicad_sch`
  - Os cabecalhos do `.pos` do KiCad (`Ref, PosX, PosY, Rot, Side`) precisam virar `Designator, Mid X, Mid Y, Rotation, Layer`; o valor de `Side` (top/bottom) tambem precisa ser conferido contra o que a JLC espera. Inferencia, nao testado. `--include-excluded-from-bom` esta obsoleta no KiCad 10.
  - A pagina da JLC nao menciona kicad-cli.

### 1.6 Gerber / furacao recomendados pela JLC para KiCad

Fonte: https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9 (passos escritos para KiCad 9.0.4; a JLC nao publicou guia de Gerber especifico para KiCad 10 que eu tenha achado). Via resumo:
- Gerber: formato 4.6 em mm; "Use Protel filename extensions"; "Use extended X2 format"; "Include netlist attributes"; plot mode Filled; escala 1:1; drill marks None; regenerar zonas antes de plotar.
- Camadas minimas 2 camadas: F/B Cu, F/B Mask, F/B Silkscreen, Edge.Cuts (obrigatoria). Paste so se for montagem SMT. Multicamada: todas as camadas internas.
- Furacao: Excellon, mm, origem absoluta, zeros em formato decimal, "alternate drill mode for oval holes", PTH e NPTH em arquivos separados (caixa desmarcada).
- Zipar Gerber e drill juntos, nomes em ingles.
- Guias antigos (KiCad 5-8) pedem tambem "Subtract soldermask from silkscreen".

### 1.7 Conferencia da sessao principal (2026-10-12)

Releitura direta de https://jlcpcb.com/capabilities/pcb-capabilities para fixar as regras de DRC:
- **Via** e **furo de componente (PTH)** tem minimos diferentes. Via: furo 0,15 mm / diametro
  0,25 mm em 2 camadas e multicamada (preferido furo >= 0,2 mm; diametro 0,1-0,15 mm maior que o
  furo). O anel de 0,18 mm (2 camadas) / 0,15 mm (multicamada) do item 1.4 vale para **PTH**.
- Pad-pad SMD de redes diferentes 0,15 mm; via-via (furo a furo) 0,2 mm; via-trilha 0,2 mm.
- NPTH minimo 0,5 mm. Serigrafia: linha >= 0,15 mm, texto >= 1,0 mm.

Esses numeros estao nos `.kicad_dru` da skill `pcb-projeto` (`assets/kicad/`), com folga.

### 1.8 Busca de pecas por script (teste de 2026-10-12)

- jlcsearch: busca por **codigo** LCSC confiavel; busca por **texto** devolve resultado irrelevante e
  o indice so contem peca com estoque na JLC (`C25804` e `AP63203` voltaram vazios). Causa no codigo
  do `tscircuit/jlcsearch`: filtro fixo `stock > 0`.
- API web da LCSC `https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=<C>` (nao documentada):
  responde por codigo com MPN, fabricante, encapsulamento, estoque **da LCSC** e escada de preco.
  A busca por palavra-chave da mesma API devolve 403.
- `easyeda2kicad` 1.0.1 funciona com o KiCad 10.0.0 depois de `kicad-cli sym/fp upgrade`, mas os
  tipos eletricos dos pinos vem errados e o footprint nao segue a KLC. Detalhes na skill
  `pcb-componentes` (`references/simbolos-e-footprints.md`).

## 2. PCBWay (resumo)

- Capacidades: https://www.pcbway.com/capabilities.html (via resumo) — 1 a 14 camadas; trilha/espaco 0,1 mm (4 mil); furo CNC 0,15 a 6,0 mm; anel anular minimo 0,15 mm; espessura 0,2 a 3,2 mm; cobre externo 1 a 8 oz; acabamentos HASL, ENIG, OSP, ouro duro, prata, estanho, ENEPIG; impedancia so no nivel Advanced (+-10%).
- Montagem: https://www.pcbway.com/assembly-capabilities.html (via resumo) — passivos ate 01005/0201/0402, BGA 0,3 mm, SMT/THT/misto, consignado, turnkey ou parcial, **minimo 5 pecas**, prazo de 24 h a algumas semanas, placa 10x10 a 250x500 mm. Precos de montagem nao estao na pagina.

## 3. Brasil

### 3.1 Importacao: o ponto central e que a Halcyon e CNPJ

- A regra "ate US$ 50 sem imposto federal" vale para **pessoa fisica**. Pagina da Receita (atualizada em 2026-05-19, via resumo): para pessoa juridica "nao importa se voce comprou de site certificado no Remessa Conforme"; cobra-se **60% de Imposto de Importacao** mais **ICMS de 17% a 20%** conforme o estado, na chegada, antes da entrega. https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/manuais/remessas-postal-e-expressa/problemas-frequentes/encomendas-com-valor-ate-us-50-00
- Regime geral PJ: RTS com aliquota unica de 60% ate US$ 3.000 (resumo de busca; nao li a pagina do RTS): https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/manuais/despacho-de-importacao/topicos-1/remessa-postal-internacional-rpi-e-remessa-expressa-re/remessa-postal-internacional-rpi/com-pagamento-do-imposto/regime-de-tributacao-simplificada-rts
- Mudancas em 2026 (todas sobre o que a imprensa relata; texto da lei nao localizado):
  - MP 1.357/2026 (12/05/2026): zera o II para compras PF de ate US$ 50 no Remessa Conforme; faixa US$ 50-3.000 "permanece em 60%" com deducao de US$ 30. https://www12.senado.leg.br/noticias/materias/2026/05/13/medida-provisoria-zera-taxa-das-blusinhas-para-importacoes-de-ate-us-50
  - PLV 13/2026 sancionado em 2026-09-10: a imprensa diz que a faixa maior cai de 60% para 30%. Fontes divergem se o teto e US$ 3 mil ou R$ 3 mil. https://www.diariodepernambuco.com.br/politica/2026/09/11723566-presidente-lula-sanciona-isencao-da-taxa-das-blusinhas-em-compras-ate-uss-50.html e https://www12.senado.leg.br/noticias/audios/2026/09/fim-da-taxa-das-blusinhas-e-sancionado
  - **Nao verificado** se a reducao para 30% alcanca pessoa juridica nem se substitui o texto da pagina da Receita acima. Confirmar com contador/despachante.
- ICMS: a pagina da Receita de 2026 diz 17% a 20%. Confirmacao de aliquota 2026 pelo Confaz: **nao verificada** (so achei fontes de 2023/2024, que citam Convenio ICMS 81/2023 com 17% e proposta de 20% a partir de 2025-04-01).
- Remessas ao Brasil exigem CNPJ/CPF do destinatario (resumo de busca de guia da DHL: https://www.dhl.com/discover/en-br/ship-with-dhl/import-with-dhl/customs-clearance-and-restrictions).
- JLCPCB/LCSC: Incoterm e tributos de entrega no Brasil **nao verificados**.

### 3.2 Mouser e DigiKey no Brasil

- DigiKey Brasil: frete fixo de **US$ 40 por pedido**; Incoterm **CPT**, ou seja, tributos e impostos por conta do comprador (nao e DDP). Prazo de 1 a 5 dias. Limite de frete gratis: nao encontrado. https://www.digikey.com.br/pt/help-support/delivery-information/delivery-time-and-cost (via resumo)
- DigiKey via **Karimex** (parceiro autorizado): precos em reais ja com frete internacional, desembaraco, taxas e impostos locais; pagamento em ate 10x no cartao, desconto de 5% a vista e 10% em boleto/PIX; pedido em karimex.com.br/digikey. https://www.digikey.com.br/pt/resources/authorized-reseller (via resumo). Isso funciona como DDP na pratica; se o cadastro aceita CNPJ e o catalogo e o completo: nao verificado.
- Mouser Brasil: so por resumo de busca — telefone local, frete fixo de US$ 35 por FedEx/DHL/UPS, e uma FAQ que indica Incoterm FCA com impostos cobrados na entrega (o oposto de DDP). As paginas `br.mouser.com/help/contact-us/mouser-faqs` e `mouser.com/localoffice-br/` deram timeout e **nao foram conferidas**. https://www.mouser.com/localoffice-br/ e https://br.mouser.com/help/contact-us/mouser-faqs
- Limite de frete gratis Mouser/DigiKey em R$: nao encontrado.
- Inferencia (nao e da fonte): com 60% de II + ICMS sobre importacao direta de PJ, os caminhos realistas sao Karimex (preco final em R$), distribuidor nacional ou consolidar compras para ficar abaixo do frete fixo.

### 3.3 Lojas e distribuidores nacionais

Classificacao a partir da home de cada loja em 2026-10-12 (via resumo):
- Eletrogate (Contagem/MG por DDD 31): maker. Arduino, ESP32/ESP8266, drivers de motor, componentes basicos. STM32 e SMD nao aparecem. https://www.eletrogate.com
- Bau da Eletronica (DDD 11): mais amplo. Transistores, CIs (reguladores, optoacopladores, drivers), diodos, **resistores SMD 0402/0603/0805/1206/1210**, microcontroladores AVR/PIC/8051. Tamanho do catalogo nao informado. https://www.baudaeletronica.com.br
- Soldafria (Ichip Tecnologia, DDD 11): maker/varejo, ESP32, componentes basicos, ferramentas. https://www.soldafria.com.br
- Multcomercial (DDD 11, loja fisica): varejo geral; componentes, motores, ferramentas, audio. Catalogo SMD nao evidente. https://www.multcomercial.com.br
- Mamute Eletronica: o site e `https://www.mamuteeletronica.com.br/` (listado em material da USP), mas o acesso deu 403; **nao classificado**. Nao confundir com Mega Mamute (varejo de informatica).
- FilipeFlop: pagina deu 403. Segundo TecMundo (2023-02), a FilipeFlop virou **MakerHero** (rebranding, Florianopolis/SC; representante oficial da Raspberry Pi no Brasil). Fonte unica: https://www.tecmundo.com.br/mercado/260253-makerhero-nova-marca-representante-oficial-da-raspberry-pi-brasil.htm . Perfil: maker.
- Saravati: citada na lista da USP junto de MakerHero; nao pesquisada.
- Arrow Brasil: so achei enderecos de escritorio em Sao Paulo (https://www.arrow.com/fr-fr/support/contact-support/find-an-arrow-office); venda de componentes avulsos para pequenas empresas: **nao verificada**. Farnell/Newark Brasil: **nao encontrado**.
- Opoen (opoen.com.br): citada em um forum sem data como a melhor loja local e "ainda fraca"; nao verifiquei.

### 3.4 Fabricas de PCB no Brasil (paginas proprias, via resumo)

- PCB Brasil, cotacao online, prototipos de 1 ou 2 faces com vias metalizadas, lotes de 5 ou 10, FR4 1,6 mm, HASL, stencil SMT: https://pcbbrasil.com.br/ e https://pcbbrasil.com.br/prototipos
- Griffus PCB: foco em prototipo, diz ate 8 h para dupla face e 10 dias normal (conteudo parece antigo): https://www.griffuspcb.com.br/
- Micropress: face simples, dupla e multicamada, desde 1986, ISO 9001: https://www.micropress.com.br/fabricacao-placas-circuito-impresso
- Luchtec (Guarulhos/SP): simples e dupla face, orcamento por formulario: https://www.luchtec.com.br/
- Circuito Impresso PRO: dupla face metalizada, minimo 10 pecas, 16 dias uteis: https://www.circuitoimpressopro.com.br/
- Circuibras (Araucaria/PR): alta complexidade, IATF 16949, planos para prototipo; oferece stencil SMT, montagem nao confirmada: https://www.circuibras.com.br
- Montagem SMT de lote pequeno no Brasil: **nao encontrei fornecedor confirmado**. Sanmina Campinas aparece como EMS de grande porte (https://www.sanmina.com/wp-content/uploads/2016/05/2450_campinas_pcba.pdf), nao prototipagem. Precos e capacidades (camadas, trilha minima) dessas fabricas: nao verificados. Descartei listas do blog bestpcbs.com por ser SEO de um concorrente.

## 4. APIs de busca de componentes

- **Nexar / Octopart**: OAuth 2.0 (client id e secret no portal https://portal.nexar.com , citado por resultado de busca). Planos (https://nexar.com/compare-plans , via resumo): Evaluation gratis, ate 100 pecas casadas; Standard ate 2.000; Pro ate 15.000; Enterprise sob consulta. A pagina nao traz precos nem limite de chamadas. No Evaluation aparecem lifecycle, datasheets, specs e ECAD; no Standard esses campos nao estao incluidos. Um outro resultado falava em 1.000 chamadas/mes: conflita, trate como nao confirmado. https://nexar.com/api
- **DigiKey API v4**: limites de Product Information: 120/min e 1.000/dia (docs, via busca) — https://developer.digikey.com/documentation . Excedido: HTTP 429; cabecalhos `X-RateLimit-Limit/Remaining`. Token de acesso dura 30 min, refresh 90 dias; precisa de Client ID e de assinar um produto de API. https://developer.digikey.com/faq . **Contradicao**: a documentacao principal diz que so authorization code (3 pernas) e permitido; a pagina de recursos diz que Product Information v4 usa fluxo 2-legged (https://developer.digikey.com/resources). Para script, testar client credentials primeiro. Cabecalhos de locale (`x-digikey-locale-*`) existem; valores para Brasil: nao encontrados.
- **Mouser Search API**: chave gratuita enviada por e-mail apos cadastro na conta My Mouser; ate 50 resultados por chamada, 30 chamadas/min, 1.000/dia; termos permitem pedir aumento. https://www.mouser.com/en/api-search/ e https://www.mouser.com/en/apiterms/ (numeros via resumo de busca; a pagina deu timeout na leitura direta).
- **LCSC**: sem API publica oficial encontrada. Opcoes: jlcparts e jlcsearch (nao oficiais) ou API JLCPCB com acesso restrito (item 1.2).
- Para usar por script: Nexar = client id/secret + token OAuth + GraphQL; DigiKey = app no portal, client id/secret, token; Mouser = chave em query string. (Detalhes de transporte e formato: nao verificados.)

## 5. Regras para escolher peca facil de comprar

Fontes de guia sao blogs de fabricantes e de ferramentas, nao norma. O que e inferencia esta marcado.
- Ciclo de vida: categorias Active, NRND, Last Time to Buy, EOL, Obsolete; NRND nao tem significado uniforme entre fabricantes, entao ler a politica do fabricante e os PCNs; filtrar NRND/EOL/Obsoleto na captura do esquematico; "Active" nao garante fornecimento (fonte unica pode parar a producao). https://resources.altium.com/p/component-selection-long-product-lifecycles e https://www.protoexpress.com/kb/how-to-watch-out-for-eol-and-obs-pcb-components/ (via resumo)
- Segunda fonte: multi-sourcing e alternativas drop-in validadas protegem contra EOL; biblioteca padronizada permite trocar. Mesma fonte.
- Valores: IEC 60063 define as series E; E12 (10%) e E24 (5%). A serie nao garante que o valor exista no encapsulamento, potencia e tolerancia desejados. https://www.bestpcbs.com/blog/2026/07/common-resistor-values/ (blog de fabricante, fraca como fonte)
- Encapsulamentos: o que a fonte diz — 0402 pede microscopio e mao firme em solda manual; foruns recomendam 0805 para montagem manual, 0603 para pick-and-place simples, 0402 para maquinas melhores. https://www.eevblog.com/forum/manufacture/using-0402-when-plenty-of-room-for-0603/ e https://www.nextpcb.com/blog/mlcc-0402-vs-0201-vs-0603-size-selection-guide . Nao achei guia de fabricante com a regra SOIC vs QFN.
- Dado da JLC que sustenta a regra (item 1.4): Economic aceita no minimo 0402 e passo de CI 0,4 mm; Standard vai a 0201 e 0,35 mm.
- Inferencia para a skill (nao e de nenhuma fonte unica): passivos em 0603 por padrao (0805 se for solda manual); 0402 so por falta de espaco; preferir Basic/Preferred da JLC; CIs em SOIC/SOT/TSSOP antes de QFN/BGA; so afirmar "facil de comprar" depois de checar estoque e ciclo de vida na API; estoque minimo e numero de fontes: **nenhuma fonte achada com valor recomendado** — definir como parametro configuravel da skill.

## Pontos nao verificados (resumo)

- Texto literal de qualquer pagina (so resumos). Nao rodei `curl`.
- Paginas Mouser Brasil e Mouser API (timeout); valores de frete e limites vem de resumo de busca.
- Se o II de 30% do PLV 13/2026 vale para PJ; teto US$ x R$ 3 mil; ICMS 2026 pelo Confaz.
- Incoterm de LCSC/JLCPCB para o Brasil; lista atual de Preferred; promocoes de taxa extended.
- Compatibilidade do easyeda2kicad com KiCad 10; ano do release 5.3.x do Fabrication Toolkit.
- Precos e limites de chamadas pagos do Nexar; locale do Brasil na API DigiKey.
- Capacidade, preco e prazo das fabricas brasileiras; montagem SMT nacional de lote pequeno; Arrow/Farnell/Newark Brasil; Mamute, Saravati, Opoen.
- Se Economic PCBA e so face superior (afirmado so por terceiro).
