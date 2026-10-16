"""Geometria do esquematico: biblioteca (Y para cima) -> folha (Y para baixo).

Convencao do KiCad conferida contra o demo `pic_programmer` (rotacoes 0/90/180/270 e espelhos):
- ponto da biblioteca (x, y) vira (x, -y) na folha;
- `(at X Y R)` gira R graus no sentido anti-horario **como se ve na tela**;
- `(mirror x)` espelha em torno do eixo X (inverte Y), `(mirror y)` em torno do eixo Y (inverte X);
  o espelho vem **depois** da rotacao.
- O `(at x y ang)` de um pino e a ponta de conexao; `ang` aponta da ponta para o corpo.
"""

import math
from dataclasses import dataclass

GRADE = 1.27
_DIRECOES = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}    # angulo na folha -> vetor (Y para baixo)


@dataclass(frozen=True)
class Orientacao:
    rotacao: int = 0        # 0, 90, 180 ou 270
    espelho: str = None     # None, 'x' ou 'y'


def na_grade(v, grade=GRADE):
    """Arredonda para o multiplo mais proximo da grade (evita 101.60000000001)."""
    return round(round(v / grade) * grade, 4)


def _girar_tela(x, y, graus):
    """Gira (x, y) da folha no sentido anti-horario da tela (Y para baixo)."""
    r = math.radians(graus)
    c, s = round(math.cos(r)), round(math.sin(r))
    return x * c + y * s, -x * s + y * c


def transformar(x, y, orient=Orientacao()):
    """Deslocamento na folha de um ponto da biblioteca, relativo a origem do simbolo."""
    fx, fy = _girar_tela(x, -y, orient.rotacao)
    if orient.espelho == "x":
        fy = -fy
    elif orient.espelho == "y":
        fx = -fx
    return fx + 0.0, fy + 0.0


def posicao_pino(pino, origem, orient=Orientacao()):
    """Ponta de conexao absoluta do pino na folha."""
    dx, dy = transformar(pino.x, pino.y, orient)
    return round(origem[0] + dx, 4), round(origem[1] + dy, 4)


def direcao_para_fora(pino, orient=Orientacao()):
    """Vetor unitario (folha) que sai da ponta do pino para longe do corpo."""
    r = math.radians(pino.angulo)
    vx, vy = transformar(-round(math.cos(r)), -round(math.sin(r)), orient)
    return int(vx), int(vy)


def angulo_da_direcao(vetor):
    """Vetor da folha -> angulo de texto/label (0 direita, 90 cima, 180 esquerda, 270 baixo)."""
    for ang, v in _DIRECOES.items():
        if v == tuple(vetor):
            return ang
    raise ValueError(f"direcao fora dos eixos: {vetor}")


def vetor_do_angulo(ang):
    return _DIRECOES[int(ang) % 360]
