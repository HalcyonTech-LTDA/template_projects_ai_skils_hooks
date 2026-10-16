# build123d — idiomas e armadilhas

Dois modos: **builder** (`with BuildPart() as p:`) e **algebra** (`peca = Box(...) - Cylinder(...)`).
Escolha um por arquivo. Algebra fica mais legivel em funcoes pequenas por feature.

## Alinhamento

Primitivas nascem centradas na origem. Para apoiar na mesa (Z = 0):

```python
Box(c, l, a, align=(Align.CENTER, Align.CENTER, Align.MIN))
```

Esquecer o `align` e a causa mais comum de furo deslocado em metade da altura.

## Casca (gabinete aberto em cima)

```python
with BuildPart() as corpo:
    Box(c, l, a, align=(Align.CENTER, Align.CENTER, Align.MIN))
    topo = corpo.faces().sort_by(Axis.Z)[-1]
    offset(amount=-PAREDE, openings=topo)
```

## Furos em posicoes da placa

```python
with BuildPart() as p:
    ...
    with Locations(*[(x - cx, y - cy, z_topo) for x, y in FUROS_PCB]):
        Hole(radius=3.4 / 2, depth=PAREDE)
```

Converta as coordenadas da placa para a origem da peca **num lugar so** (uma funcao), nao
espalhado pelo codigo.

## Seletores

- `faces().sort_by(Axis.Z)[-1]` = face mais alta; `[0]` = mais baixa
- `edges().filter_by(Axis.Z)` = arestas verticais (para filete de canto)
- Filete depois dos furos pode falhar; filete antes, furo depois

## Exportacao

```python
export_step(peca, "peca.step")   # fabricacao, revisao em CAD
export_stl(peca, "peca.stl")     # fatiador
```

STEP preserva geometria exata; STL e malha. Entregue os dois quando a peca vai para fora.

## Verificacao por codigo

```python
assert peca.is_valid()
print(peca.bounding_box().size)  # Vector(c, l, a) em mm
print(round(peca.volume, 1))     # mm3; > 0
```

## Ambiente

`uv add build123d` (Python 3.10+). A primeira instalacao baixa o OCCT (~centenas de MB).
Visualizacao interativa e opcional (`ocp_vscode`); nao e requisito para gerar o arquivo.
A API ainda muda entre versoes menores: confira a versao instalada antes de usar idioma
desta pagina que falhar.
