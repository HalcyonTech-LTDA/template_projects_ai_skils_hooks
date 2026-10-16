# Fontes de componentes, APIs e importacao

Tudo verificado em 2026-10-12 por leitura resumida das paginas (ficha
`docs_projeto/referencias/componentes-e-fabricacao-pcb.md`). Numero de custo e imposto: **confira na
pagina antes de virar orcamento**.

## 1. JLCPCB / LCSC

| Categoria | Custo de montagem | Observacao |
|---|---|---|
| Basic | Sem taxa por peca | Ja carregada nas maquinas |
| Preferred (Extended) | Sem taxa de feeder **so** na montagem Economic | Lista muda; filtre no site |
| Extended | Cerca de US$ 3 por peca unica (FAQ: 3; tabela: 3,07 Economic, 1,53 Standard) | Conte quantas a BOM tem |

Busca:
- `buscar_lcsc.py` usa o jlcsearch (tscircuit), nao oficial e sem chave.
- Site oficial: https://jlcpcb.com/parts ; so Basic: https://jlcpcb.com/parts/basic_parts
- jlcparts (yaqwsx), busca parametrica no navegador: https://yaqwsx.github.io/jlcparts/

LCSC nao tem API publica oficial.

## 2. Mouser e DigiKey

| | Mouser | DigiKey |
|---|---|---|
| API | Search API v1, chave gratuita por e-mail (conta My Mouser) | Product Information v4, app no portal developer.digikey.com |
| Credencial | `MOUSER_API_KEY` | `DIGIKEY_CLIENT_ID`, `DIGIKEY_CLIENT_SECRET` (OAuth2 client credentials) |
| Limites | ~30 chamadas/min, 1.000/dia, 50 resultados por chamada (via resumo) | 120/min, 1.000/dia (HTTP 429 ao exceder) |
| Entrega no Brasil | Frete fixo de ~US$ 35, Incoterm FCA, impostos na entrega (nao conferido: pagina deu timeout) | Frete fixo de US$ 40, Incoterm CPT: impostos por conta do comprador |
| Via revenda nacional | — | Karimex: preco final em reais com frete e impostos (aceitar CNPJ: nao verificado) |

Onde colocar a chave: bloco `env` de `.claude/settings.local.json` (ignorado pelo git). Politica de
segredo do template em `docs_projeto/MCPS.md`, secao 6.

Nexar/Octopart (agregador, OAuth2, GraphQL): plano Evaluation gratis ate 100 pecas casadas. Util para
comparar varios distribuidores de uma vez; nao implementado nos scripts.

## 3. Importacao como pessoa juridica

- A isencao de ate US$ 50 do Remessa Conforme e de **pessoa fisica**. Para PJ, a Receita (pagina
  atualizada em 2026-05-19) diz: imposto de importacao de 60% mais ICMS de 17% a 20%, mesmo em site
  certificado e abaixo de US$ 50.
- MP 1.357/2026 (maio) e PLV 13/2026 (sancionado em 2026-09-10) mexeram nas faixas para PF; a imprensa
  fala em reduzir a faixa maior para 30%, mas **nao ha confirmacao de que vale para PJ**.
- Consequencia pratica: compre consolidado (frete fixo dilui), prefira revenda nacional com preco
  final (Karimex) quando o prazo importa, e coloque imposto no custo da BOM em
  `08_Producao/Custos_BOM`. Confirme o regime com o contador.

## 4. Brasil: lojas e fabricas

Lojas (para bancada e reposicao; nao como fonte da BOM de producao):

| Loja | Perfil |
|---|---|
| Bau da Eletronica | Mais ampla: CIs, transistores, resistores SMD 0402-1210 |
| Eletrogate, Soldafria, MakerHero (ex-FilipeFlop) | Maker: modulos, ESP32, basicos |
| Multcomercial | Varejo geral, loja fisica |

Fabricas de PCB nacionais (prototipo; capacidades e precos nao verificados): PCB Brasil, Griffus,
Micropress, Luchtec, Circuito Impresso PRO, Circuibras. **Montagem SMT de lote pequeno no Brasil nao
foi encontrada** — por isso o padrao da familia e a JLCPCB.

## 5. Quando usar o quê

| Situacao | Fonte |
|---|---|
| Placa montada pela JLC | LCSC (Basic > Preferred > Extended) |
| Prototipo montado a mao, com pressa | Revenda nacional com preco final ou loja nacional; DigiKey/Mouser se o prazo permitir |
| Conferir ciclo de vida e datasheet oficial | Mouser/DigiKey, sempre |
| Peca que a LCSC nao tem | DigiKey/Mouser; montagem pela PCBWay (turnkey por MPN) ou consignada |
