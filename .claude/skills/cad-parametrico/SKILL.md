---
name: cad-parametrico
description: Modelagem CAD parametrica por codigo para pecas que vao ser fabricadas — gabinete de placa, suporte, tampa, encaixe, peca para impressora 3D ou usinagem — com build123d (padrao), OpenSCAD ou CadQuery, cotas em milimetro e exportacao STEP/STL/3MF. Use quando o usuario pedir peca, gabinete, case, enclosure, suporte, furacao, modelo para imprimir, STL, STEP, 3MF, OpenSCAD, build123d ou CadQuery. Nao use para cena 3D de site (three-best-practices / r3f-best-practices) nem para asset artistico (blender-scripting).
---

# CAD parametrico

Peca de fabricacao e um programa: parametros no topo, uma funcao por feature, exportacao no
fim. O agente escreve o codigo; quem gera o arquivo e o interpretador do projeto. Esta skill
e **so instrucional** — nao traz script, servidor nem container.

## 1. Escolha da ferramenta

| Situacao | Ferramenta | Por que |
|---|---|---|
| Padrao, peca nova | **build123d** | Python puro, kernel OCCT, exporta STEP de verdade, seletores de face/aresta |
| Projeto ja em OpenSCAD, ou peca so de primitivas CSG | **OpenSCAD** | Sem dependencia Python; sem STEP nativo e sem filete real |
| Projeto ja em CadQuery | **CadQuery** | Mesmo kernel do build123d; nao migre sem pedido |

Leia o que o projeto ja usa (`pyproject.toml`, `*.scad`, `*.py` com `import build123d`)
antes de escolher. Nunca misture duas na mesma peca.

## 2. Antes do codigo — perguntas obrigatorias

Sem estes dados a peca sai errada; pergunte o que faltar:

1. **Processo**: FDM, resina (SLA), usinagem CNC, corte laser. Muda folga e parede
2. **Peca de origem**: placa (dimensoes, furos de fixacao, conectores, componente mais alto),
   arquivo STEP do fabricante, desenho cotado. Nao invente cota de conector
3. **Fixacao**: parafuso (M2/M2.5/M3), inserto termico, encaixe por pressao, snap-fit
4. **Material** e ambiente (temperatura, UV, umidade): PLA deforma acima de ~55 C
5. **Formato de entrega**: STEP para fabricar/revisar, STL ou 3MF para fatiar

## 3. Estrutura do codigo

```python
"""Gabinete da placa X. Unidade: mm."""
from build123d import *

# --- parametros (unico lugar com numero magico) ---
PCB = (60.0, 40.0, 1.6)        # comprimento, largura, espessura
FOLGA_PCB = 0.5                # por lado
PAREDE = 2.0
ALTURA_LIVRE = 18.0            # componente mais alto + margem
FUROS_PCB = [(3.5, 3.5), (56.5, 3.5), (3.5, 36.5), (56.5, 36.5)]

def casco() -> Part: ...
def suportes(base: Part) -> Part: ...
def recortes(corpo: Part) -> Part: ...

def gabinete() -> Part:
    return recortes(suportes(casco()))

if __name__ == "__main__":
    peca = gabinete()
    export_step(peca, "gabinete.step")
    export_stl(peca, "gabinete.stl")
```

Regras:
- **Uma funcao por feature** (casco, suporte, recorte, tampa). Nada de `main()` de 200 linhas
- Toda cota derivada de parametro: `largura = PCB[1] + 2 * (FOLGA_PCB + PAREDE)`
- Origem e eixo declarados no docstring (ex.: canto inferior esquerdo da placa em 0,0)
- Tampa e corpo sao funcoes separadas que compartilham os mesmos parametros
- Nome de arquivo exportado = nome da peca; nao sobrescreva arquivo de outra peca

Idiomas build123d que o agente costuma errar estao em `references/build123d.md`.

## 4. Regras de fabricacao

Numeros de partida para FDM com bico 0,4 mm, folgas de encaixe, furos, insertos, saliencias
e o que muda em resina e CNC: `references/fabricacao.md`. Leia antes de fixar
`PAREDE`, folgas e diametros. Sao **pontos de partida para calibrar**, nao norma — a
impressora do usuario vence a tabela.

## 5. Verificacao antes de entregar

1. Se o interpretador estiver disponivel no projeto, rode o script e confira por codigo:
   `peca.is_valid()`, `peca.bounding_box().size` contra as cotas esperadas e
   `peca.volume > 0`. Mostre os numeros ao usuario
2. Confira cada furo e recorte contra a fonte da cota (datasheet, desenho, STEP da placa).
   Cota sem fonte e declarada como **suposicao** na entrega
3. Se o interpretador nao estiver disponivel, **diga isso** e entregue o comando exato para o
   usuario rodar (`uv run gabinete.py`, `openscad -o peca.stl peca.scad`). Nao afirme que a
   peca e valida sem ter rodado
4. Para impressao, recomende imprimir **so a regiao critica** (um canto com furo e encaixe)
   antes da peca inteira

## 6. O que nao fazer

- Nao suba servidor CAD que execute codigo recebido por HTTP (padrao do `cad-agent`; ver
  `docs_projeto/referencias/skill3d-cad-agent.md`)
- Nao gere malha (STL) como fonte de verdade: a fonte e o script; STL e saida
- Nao use unidade implicita. Blender trabalha em metro, OpenSCAD e build123d em mm
- Nao copie modelo de terceiro (Thingiverse, Printables) sem conferir a licenca
