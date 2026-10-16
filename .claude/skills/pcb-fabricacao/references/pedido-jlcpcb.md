# Pedido na JLCPCB

Verificado em 2026-10-12 (ficha `docs_projeto/referencias/componentes-e-fabricacao-pcb.md`, leitura
resumida das paginas da JLC). Precos mudam: confira no carrinho.

## 1. Placa nua

| Parametro | Padrao da familia | Quando mudar |
|---|---|---|
| Camadas | 2 | 4 com radio integrado no chip, USB de alta velocidade, ADC sensivel, densidade |
| Material / espessura | FR-4, 1,6 mm | Mais fina so por restricao mecanica |
| Cobre externo | 1 oz | 2 oz com corrente alta que nao cabe em largura |
| Acabamento | HASL sem chumbo | ENIG com passo fino (<= 0,5 mm), QFN/BGA, ou contatos de borda |
| Cor da mascara | Verde | Outras cores podem aumentar prazo |
| Impedancia controlada | Nao | Sim so com 4 camadas e trilhas calculadas para o stack-up da JLC |
| Numero do pedido | "Specify location" com `JLCJLCJLCJLC` na serigrafia | Remover tem custo |
| Gerber | O zip do `releases/rev-<R>/` | — |

Configuracao de Gerber que o `exportar_fab.py` segue (guias da JLC para KiCad; a pesquisa achou
versoes para 8, 9 e para BOM/CPL do 10.0.3, sem guia de Gerber especifico do 10): formato 4.6 em mm,
extensoes Protel, X2, atributos de netlist, escala 1:1, sem marcas de furo, mascara subtraida da
serigrafia; furacao Excellon em mm, origem absoluta, PTH e NPTH em arquivos separados;
`Edge.Cuts` obrigatoria. Os mapas de furo saem em PDF fora do zip.

## 2. Montagem SMT

| | Economic | Standard |
|---|---|---|
| Menor passivo | 0402 | 0201 |
| Menor passo de CI | 0,4 mm | 0,35 mm |
| Placas | 2 a 50 | 2 a 80.000 |
| Tamanho de placa | 10x10 a 470x500 mm | minimo 70x70 mm |
| Taxa por peca Extended | ~US$ 3 (Preferred isenta) | ~US$ 1,53 (Basic e Extended) |
| Setup (aprox.) | ~US$ 8 | ~US$ 26 por face |

- Economic so face superior segundo terceiros (nao confirmado na pagina da JLC). Na duvida, coloque
  todo SMD em cima.
- Componentes THT (bornes, headers) podem ser montados a parte (taxa propria) ou soldados a mao. O
  que for soldado a mao leva o campo `Sem_LCSC` com o motivo (sai da BOM/CPL da JLC, fica na BOM
  completa para compra). **Nao use DNP para isso**: DNP tira a peca de todas as BOMs.
- Upload: zip Gerber + `bom-jlc.csv` + `cpl-jlc.csv`. Confira no preview: peca certa em cada
  posicao, rotacao, polaridade, face.

## 3. Custo total (o que somar)

Placa + stencil (se montagem manual com pasta) + montagem (setup + taxas Extended + pecas) + frete +
**imposto de importacao como pessoa juridica** (ver `pcb-componentes/references/fontes-e-apis.md`).
Registre a estimativa e o realizado em `08_Producao/Custos_BOM/`.

## 4. PCBWay (alternativa)

Quando a peca nao existe na LCSC ou a montagem precisa ser turnkey por MPN (a PCBWay compra pelo
MPN), minimo de 5 placas montadas. Capacidades de placa nua parecidas (1-14 camadas, trilha 0,1 mm,
furo a partir de 0,15 mm). O mesmo zip de Gerber serve; a BOM completa (`<placa>-rev-<R>-bom.csv`, com
MPN) e o arquivo de BOM a enviar. Formato exato de CPL da PCBWay: confira no upload.

## 5. Fabricas nacionais

Para placa nua de prototipo com prazo curto, existem fabricas brasileiras (PCB Brasil, Micropress,
Circuibras e outras — lista na ficha). Capacidades e precos **nao verificados**: peca as regras de
projeto antes e ajuste o `.kicad_dru`. Montagem SMT nacional de lote pequeno nao foi encontrada.
