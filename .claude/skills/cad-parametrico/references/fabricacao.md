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
