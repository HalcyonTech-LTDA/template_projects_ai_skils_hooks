# Regras de fabricacao — pontos de partida

Valores tipicos para **calibrar**, nao norma. Variam com impressora, fatiador, material e
fornecedor. Quando o usuario tiver numero proprio (peca de teste, datasheet), ele vence.

## FDM, bico 0,4 mm, camada 0,2 mm

| Item | Partida | Nota |
|---|---|---|
| Parede de gabinete | 2,0 mm | Minimo pratico ~1,2 mm (3 perimetros). Multiplo da largura de linha (~0,45) |
| Fundo / tampo | 1,6 a 2,0 mm | >= 8 camadas |
| Folga de encaixe deslizante | 0,3 a 0,4 mm por lado | Tampa que entra no corpo |
| Folga de encaixe justo | 0,15 a 0,2 mm por lado | Imprimir teste antes |
| Folga PCB no gabinete | 0,5 mm por lado | Placa com tolerancia de corte |
| Furo vertical | +0,2 a +0,3 mm no diametro | Furo sai menor que o desenhado |
| Furo horizontal | formato gota (teardrop) | Topo do furo cede sem suporte |
| Saliencia sem suporte | ate 45 graus | Acima disso, chanfro em vez de filete na face de baixo |
| Ponte sem suporte | ate ~10 mm | Mais que isso, redesenhar |
| Texto em relevo | >= 0,6 mm de traco, 0,4 mm de altura | |
| Snap-fit | gancho com 1,0 a 1,5 mm de espessura, deflexao pequena | Fragil em PLA; prefira PETG |

## Fixacao

| Item | Partida | Nota |
|---|---|---|
| Passagem M2 / M2,5 / M3 | 2,4 / 2,9 / 3,4 mm | Encaixe normal |
| Furo para rosca direta M3 no plastico | 2,5 a 2,8 mm | Poucas montagens; inserto e melhor |
| Inserto termico M3 | ~4,0 a 4,2 mm, profundidade = inserto + 0,5 | **Ler o datasheet do inserto**; muda por fabricante |
| Parede ao redor do inserto | >= 1,6 mm | |
| Suporte (standoff) de PCB | diametro externo >= furo + 2 x 1,6 mm | Altura = folga sob a placa (componentes THT do lado de baixo) |
| Cabeca de parafuso embutida | rebaixo = cabeca + 0,4 mm | |
| Rosca engajada em plastico | ~2x o diametro do parafuso | Menos que isso espana |
| Pilar (boss) de parafuso direto | diametro externo 2,5 a 3x o parafuso | Plastico em volta = diametro do parafuso |

### Parafuso metrico — medidas de norma (mm)

Passagem media (ISO 273) e broca de rosca. Cabeca allen pela ISO 4762. Em plastico impresso,
o furo de rosca entra com a folga de furo vertical da tabela de FDM acima.

| Rosca | Cabeca allen | Passagem | Furo para rosca |
|---|---|---|---|
| M1.6 | 3,0 | 1,8 | 1,25 |
| M2 | 3,8 | 2,4 | 1,6 |
| M2.5 | 4,5 | 2,9 | 2,05 |
| M3 | 5,5 | 3,4 | 2,5 |
| M4 | 7 | 4,5 | 3,3 |
| M5 | 8,5 | 5,5 | 4,2 |
| M6 | 10 | 6,6 | 5 |

- Escolha: M2/M2.5 para placa e peca fina, M3 para o que fica na mao ou na mesa, M4+ para
  carga. **O furo de montagem da placa decide**: o parafuso cuja passagem e a mais proxima
- Cabecas: allen ISO 4762 (padrao), abaulada ISO 7380 (M3+), escareada ISO 10642 (M3+),
  panela Phillips ISO 7045 (ate M8), sextavada ISO 4017. Porca ISO 4032, arruela ISO 7089
- **So comprimento comercial** (6, 8, 10, 12, 16, 20...). Conta de baixo da cabeca; na
  escareada, do topo da cabeca
- Origem do parafuso no codigo = onde a cabeca assenta. Furo de passagem, furo de rosca e
  rebaixo usam a mesma origem: um posicionamento serve para os tres cortes
- Porca cativa: alojamento sextavado (entre-faces + folga) para nao girar
- Nome da peca leva a medida: "Parafusos da tampa, M3 x 8". Pedido de "maior" sem numero
  → pergunte qual, dizendo quanto mede cada

Fonte das regras de pilar e da tabela: `docs_projeto/referencias/enclose.md`.

## Orientacao de impressao

- Defina a face que vai na mesa ao desenhar: e a face plana maior, e a referencia das cotas
- Forca de camada e fraca no eixo Z: gancho e pino nao devem ser impressos em pe
- Rebaixo para cabeca de parafuso na face da mesa gera saliencia; use camada de sacrificio
  (0,2 mm) e fure depois

## Resina (SLA/MSLA)

- Folga deslizante ~0,1 a 0,2 mm por lado; parede minima ~1,0 mm
- Peca oca precisa de furo de dreno (>= 2 mm) para nao reter resina
- Peca encolhe na cura; conferir em peca de teste

## Usinagem CNC

- Canto interno tem raio da fresa: nunca canto vivo interno; raio >= 1 mm por padrao
- Profundidade de bolso ate ~3 a 4x o diametro da fresa
- Tolerancia vai no desenho (STEP + PDF cotado), nao no modelo

## Corte laser (chapa)

- Kerf (largura do corte) ~0,1 a 0,2 mm; compensar em encaixe
- Encaixe macho-femea com folga negativa pequena para pressao, testar em retalho
