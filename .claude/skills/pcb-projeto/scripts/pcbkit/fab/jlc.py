"""BOM e CPL (pick-and-place) no formato da montagem SMT da JLCPCB.

Formato conferido em 2026-10-12 na pagina da JLC "How to generate the BOM and Centroid file from
KiCad" (https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad,
escrita para o KiCad 10.0.3):
- BOM (.csv, .xls ou .xlsx): `Comment, Designator, Footprint, JLCPCB Part #`;
- CPL: `Designator, Mid X, Mid Y, Rotation, Layer`, coordenadas em milimetros. A pagina renomeia a
  coluna `Side` do KiCad para `Layer`; os valores `Top`/`Bottom` sao os do Fabrication Toolkit e do
  modelo de CPL da JLC.

So entram componentes montados pela JLC: nao DNP, na BOM, com codigo LCSC e sem `Sem_LCSC` (que vence
o `LCSC`); no CPL, tambem sem `exclude_from_pos_files` (`bom.Componente`).
A rotacao e a do KiCad: a diferenca para a biblioteca da JLC se confere no preview do pedido.
"""

import csv
from pathlib import Path

from . import bom

CABECALHO_BOM = ["Comment", "Designator", "Footprint", "JLCPCB Part #"]
CABECALHO_CPL = ["Designator", "Mid X", "Mid Y", "Rotation", "Layer"]
LADOS = {"top": "Top", "bottom": "Bottom"}


def para_jlc(comps):
    return [c for c in comps if c.montado_pela_jlc]


def nome_footprint(footprint):
    """'Resistor_SMD:R_0603_1608Metric' -> 'R_0603_1608Metric'."""
    return footprint.split(":", 1)[-1]


def linhas_bom(comps):
    grupos = bom.agrupar(para_jlc(comps), lambda c: (c.valor, c.footprint, c.lcsc))
    return [[g[0].valor, bom.refs(g), nome_footprint(g[0].footprint), g[0].lcsc] for g in grupos]


def escrever_bom(caminho, comps):
    return bom.escrever_csv(caminho, CABECALHO_BOM, linhas_bom(comps))


def ler_pos(caminho):
    """CSV do `kicad-cli pcb export pos --format csv --units mm`: Ref,Val,Package,PosX,PosY,Rot,Side."""
    with Path(caminho).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _numero(texto):
    return f"{float(texto):.4f}"


def _rotacao(texto):
    graus = float(texto) % 360
    return f"{graus:g}"


def _lado(texto):
    lado = LADOS.get(texto.strip().lower())
    if lado is None:
        raise ValueError(f"lado desconhecido no arquivo de posicao: {texto!r}")
    return lado


def linhas_cpl(posicoes, comps):
    """(linhas, sem_posicao): uma linha por componente do CPL (`bom.Componente.no_cpl`) que esta no arquivo
    de posicao; `sem_posicao` lista os que deveriam estar e nao estao (ex.: peca fora da placa)."""
    alvo = {c.ref for c in comps if c.no_cpl}
    linhas, vistos = [], set()
    for p in sorted(posicoes, key=lambda p: bom.ordem_ref(p["Ref"])):
        if p["Ref"] in alvo:
            vistos.add(p["Ref"])
            linhas.append([p["Ref"], _numero(p["PosX"]), _numero(p["PosY"]), _rotacao(p["Rot"]), _lado(p["Side"])])
    return linhas, sorted(alvo - vistos, key=bom.ordem_ref)


def escrever_cpl(caminho, posicoes, comps):
    linhas, sem_posicao = linhas_cpl(posicoes, comps)
    bom.escrever_csv(caminho, CABECALHO_CPL, linhas)
    return sem_posicao
