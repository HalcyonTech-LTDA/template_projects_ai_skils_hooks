"""Caixas delimitadoras na folha (mm, Y para baixo) e tamanho estimado de texto.

A largura do texto e uma estimativa da fonte de traco do KiCad (conferida contra o SVG exportado
pelo kicad-cli): basta para nao sobrepor, nao para medir.
"""

import math
from dataclasses import dataclass

from . import geometria as g
from ..sexpr import etiqueta, filho, filhos

LARGURA_CARACTERE = 0.92        # fracao da altura da fonte por caractere (com folga)


@dataclass
class Caixa:
    x1: float
    y1: float
    x2: float
    y2: float

    @classmethod
    def de_pontos(cls, pontos):
        xs = [p[0] for p in pontos]
        ys = [p[1] for p in pontos]
        return cls(min(xs), min(ys), max(xs), max(ys))

    @property
    def largura(self):
        return self.x2 - self.x1

    @property
    def altura(self):
        return self.y2 - self.y1

    def uniao(self, outra):
        if outra is None:
            return self
        return Caixa(min(self.x1, outra.x1), min(self.y1, outra.y1), max(self.x2, outra.x2), max(self.y2, outra.y2))

    def deslocar(self, dx, dy):
        return Caixa(self.x1 + dx, self.y1 + dy, self.x2 + dx, self.y2 + dy)

    def expandir(self, m):
        return Caixa(self.x1 - m, self.y1 - m, self.x2 + m, self.y2 + m)

    def cruza(self, outra):
        return self.x1 < outra.x2 and outra.x1 < self.x2 and self.y1 < outra.y2 and outra.y1 < self.y2


def uniao(caixas):
    caixas = [c for c in caixas if c is not None]
    if not caixas:
        return None
    total = caixas[0]
    for c in caixas[1:]:
        total = total.uniao(c)
    return total


def largura_texto(texto, tamanho=1.27):
    linhas = str(texto).split("\n")
    return max(len(l) for l in linhas) * tamanho * LARGURA_CARACTERE


def altura_texto(texto, tamanho=1.27):
    return (str(texto).count("\n") + 1) * tamanho * 1.6


def caixa_texto(texto, x, y, tamanho=1.27, angulo=0, horizontal="center", vertical="center"):
    """Caixa de um texto ancorado em (x, y) com a justificacao do KiCad (left/center/right, top/center/bottom)."""
    w, h = largura_texto(texto, tamanho), altura_texto(texto, tamanho)
    x1 = {"left": 0, "center": -w / 2, "right": -w}[horizontal]
    y1 = {"top": 0, "center": -h / 2, "bottom": -h}[vertical]
    cantos = [(x1, y1), (x1 + w, y1), (x1, y1 + h), (x1 + w, y1 + h)]
    if angulo % 180 == 90:
        cantos = [(cy, -cx) for cx, cy in cantos]     # texto vertical le de baixo para cima
    return Caixa.de_pontos([(x + cx, y + cy) for cx, cy in cantos])


# --- desenho de simbolo de biblioteca ---------------------------------------------------

def _pontos_grafico(no):
    tag = etiqueta(no)
    if tag in ("polyline", "bezier"):
        return [(p[1], p[2]) for p in filhos(filho(no, "pts") or [], "xy")]
    if tag == "rectangle":
        s, e = filho(no, "start"), filho(no, "end")
        return [(s[1], s[2]), (e[1], e[2])]
    if tag == "circle":
        c, r = filho(no, "center"), filho(no, "radius")
        return [(c[1] - r[1], c[2] - r[1]), (c[1] + r[1], c[2] + r[1])]
    if tag == "arc":
        return [(n[1], n[2]) for n in (filho(no, "start"), filho(no, "mid"), filho(no, "end")) if n]
    return []


def _unidade_do_no(nome, unidade):
    partes = str(nome).rsplit("_", 2)
    if len(partes) < 3 or not partes[1].isdigit():
        return True
    return int(partes[1]) in (0, unidade) and partes[2] in ("0", "1")


def caixa_corpo(simbolo, unidade=1, orient=g.Orientacao()):
    """Desenho + pinos (ponta e base) da unidade, relativo a origem do simbolo na folha."""
    pontos = []
    for sub in filhos(simbolo.no, "symbol"):
        if _unidade_do_no(sub[1], unidade):
            for gr in sub[2:]:
                pontos += _pontos_grafico(gr) if isinstance(gr, list) else []
    for p in simbolo.pinos:
        if p.unidade in (0, unidade) and p.corpo in (0, 1):
            r = math.radians(p.angulo)
            pontos += [(p.x, p.y), (p.x + p.comprimento * round(math.cos(r)), p.y + p.comprimento * round(math.sin(r)))]
    if not pontos:
        return Caixa(-1.27, -1.27, 1.27, 1.27)
    return Caixa.de_pontos([g.transformar(x, y, orient) for x, y in pontos])
