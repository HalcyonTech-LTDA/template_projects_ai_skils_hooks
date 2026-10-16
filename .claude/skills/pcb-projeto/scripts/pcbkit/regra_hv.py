"""Regras da net class `HV` no `.kicad_dru`: quais valem como isolacao de alta tensao e quais a anulam.

Regra HV valida: condicao exatamente `A.hasNetclass('HV')` ou `A.hasNetclass('HV') || B.hasNetclass('HV')`
(espacos nao importam), sem `(severity ...)` diferente de `error` e sem `(layer ...)`. `clearance` e
`creepage` podem estar na mesma regra ou em regras separadas (como no `assets/kicad/alta-tensao.kicad_dru`).
`hasNetclass('HV')` tambem casa a classe composta (`HV,Power`): medido no 10.0.0, as regras do asset
acusam violacoes nas redes `/MOTOR_A`/`/MOTOR_B` quando elas estao em `HV` e em `Power`.

Precedencia medida no KiCad 10.0.0: quando duas regras casam, vale a ULTIMA do arquivo, mesmo que a
condicao dela seja mais ampla (`A.Type == 'Track'` depois de uma regra de 5 mm derruba o minimo para o
dela). Por isso uma regra posterior que redefine `clearance`/`creepage` abaixo do minimo anula a HV.
"""

import re

from . import sexpr

RESTRICOES = ("clearance", "creepage")
MINIMO_MM = 2.5
_CONDICOES = {"A.hasNetclass('HV')", "A.hasNetclass('HV')||B.hasNetclass('HV')",
              "B.hasNetclass('HV')||A.hasNetclass('HV')"}
_MEDIDA = re.compile(r"^\s*([0-9]*\.?[0-9]+)\s*(mm|mil|in|um)?\s*$")
_POR_MM = {"mm": 1.0, None: 1.0, "mil": 0.0254, "in": 25.4, "um": 0.001}


def medida_mm(texto):
    """'2.5mm' -> 2.5; '100mil' -> 2.54; sem unidade = mm; outra coisa -> None."""
    m = _MEDIDA.match(str(texto))
    return float(m.group(1)) * _POR_MM[m.group(2)] if m else None


def _minimo_mm(restricao):
    for item in restricao[2:]:
        if isinstance(item, list) and sexpr.etiqueta(item) == "min" and len(item) > 1:
            return medida_mm(item[1])
    return None


def regras(arvore_dru):
    return [r for r in arvore_dru or [] if isinstance(r, list) and sexpr.etiqueta(r) == "rule"]


def nome(regra):
    return str(regra[1]) if len(regra) > 1 and not isinstance(regra[1], list) else "?"


def defeitos(regra):
    """Por que uma regra nao serve de regra HV (lista vazia = serve)."""
    saida = []
    if re.sub(r"\s+", "", str(sexpr.valor(regra, "condition", ""))) not in _CONDICOES:
        saida.append("condicao diferente de \"A.hasNetclass('HV')\" ou "
                     "\"A.hasNetclass('HV') || B.hasNetclass('HV')\"")
    sev = sexpr.valor(regra, "severity")
    if sev is not None and str(sev) != "error":
        saida.append(f"severity {sev} (precisa ser error ou ausente)")
    if sexpr.filho(regra, "layer") is not None:
        saida.append("restrita a uma camada (layer)")
    return saida


def restricoes(regra):
    """{tipo: minimo em mm ou None} das restricoes `clearance`/`creepage` da regra."""
    saida = {}
    for r in sexpr.filhos(regra, "constraint"):
        tipo = str(r[1]) if len(r) > 1 else ""
        if tipo in RESTRICOES:
            saida[tipo] = _minimo_mm(r)
    return saida


def minimos(arvore_dru):
    """{'clearance': 2.5, 'creepage': 2.5}: maior minimo por restricao nas regras HV validas."""
    achadas = {}
    for regra in regras(arvore_dru):
        if defeitos(regra):
            continue
        for tipo, minimo in restricoes(regra).items():
            if minimo:
                achadas[tipo] = max(minimo, achadas.get(tipo, 0))
    return achadas


def _enfraquece(regra, tipo, minimo):
    valor = restricoes(regra).get(tipo, False)
    return valor is not False and ((valor or 0) < minimo or sexpr.filho(regra, "layer") is not None
                                   or str(sexpr.valor(regra, "severity", "error")) != "error")


def sobrepostas(arvore_dru, tipo, minimo):
    """Nomes das regras DEPOIS da ultima regra HV valida de `tipo` (>= `minimo`) que redefinem `tipo`
    abaixo do minimo, rebaixadas ou por camada: elas vencem a regra HV."""
    lista = regras(arvore_dru)
    validas = [i for i, r in enumerate(lista) if not defeitos(r) and (restricoes(r).get(tipo) or 0) >= minimo]
    if not validas:
        return []
    return [nome(r) for r in lista[validas[-1] + 1:] if _enfraquece(r, tipo, minimo)]


def nao_contam(arvore_dru):
    """Regras que citam HV mas nao valem como regra HV, com o motivo (para a mensagem)."""
    return [f"regra '{nome(r)}' nao conta: {'; '.join(d)}" for r in regras(arvore_dru)
            if "HV" in str(sexpr.valor(r, "condition", "")) and restricoes(r) and (d := defeitos(r))]
