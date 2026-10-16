"""Arquivos KiCad 10 vazios (validos para o kicad-cli) montados em S-expression.

Estrutura conferida contra os demos do KiCad 10.0.0 regravados com `kicad-cli ... upgrade`
(ver "## Oraculo" no handoff da skill).
"""

import uuid

from . import GERADOR, GERADOR_VERSAO, VERSAO_PCB, VERSAO_SCH, VERSAO_SYM
from .sexpr import Simbolo as S

# Camadas do KiCad 10: cobre com ids pares (F.Cu 0, B.Cu 2, In1.Cu 4, In2.Cu 6...).
_CAMADAS_TECNICAS = [
    (9, "F.Adhes", "user", "F.Adhesive"), (11, "B.Adhes", "user", "B.Adhesive"),
    (13, "F.Paste", "user", None), (15, "B.Paste", "user", None),
    (5, "F.SilkS", "user", "F.Silkscreen"), (7, "B.SilkS", "user", "B.Silkscreen"),
    (1, "F.Mask", "user", None), (3, "B.Mask", "user", None),
    (17, "Dwgs.User", "user", "User.Drawings"), (19, "Cmts.User", "user", "User.Comments"),
    (21, "Eco1.User", "user", "User.Eco1"), (23, "Eco2.User", "user", "User.Eco2"),
    (25, "Edge.Cuts", "user", None), (27, "Margin", "user", None),
    (31, "F.CrtYd", "user", "F.Courtyard"), (29, "B.CrtYd", "user", "B.Courtyard"),
    (35, "F.Fab", "user", None), (33, "B.Fab", "user", None),
]


def novo_uuid():
    return str(uuid.uuid4())


def _cabecalho(raiz, versao):
    return [S(raiz), [S("version"), versao], [S("generator"), GERADOR], [S("generator_version"), GERADOR_VERSAO]]


def bloco_titulo(titulo, data, rev, empresa):
    no = [S("title_block"), [S("title"), titulo], [S("date"), data], [S("rev"), rev]]
    if empresa:
        no.append([S("company"), empresa])
    return no


def esquematico_vazio(titulo, data, rev, empresa="", folha="A3", uuid_raiz=None):
    """Folha raiz sem componentes. `uuid_raiz` e o que entra em instances/path dos simbolos."""
    return _cabecalho("kicad_sch", VERSAO_SCH) + [
        [S("uuid"), uuid_raiz or novo_uuid()],
        [S("paper"), folha],
        bloco_titulo(titulo, data, rev, empresa),
        [S("lib_symbols")],
        [S("sheet_instances"), [S("path"), "/", [S("page"), "1"]]],
        [S("embedded_fonts"), S("no")],
    ]


def _camadas(n_cobre):
    if n_cobre not in (2, 4, 6):
        raise ValueError("numero de camadas de cobre deve ser 2, 4 ou 6")
    cobre = [[0, "F.Cu", S("signal")]]
    cobre += [[2 + 2 * i, f"In{i}.Cu", S("signal")] for i in range(1, n_cobre - 1)]
    cobre += [[2, "B.Cu", S("signal")]]
    tecnicas = [[i, nome, S(tipo)] + ([apelido] if apelido else []) for i, nome, tipo, apelido in _CAMADAS_TECNICAS]
    return [S("layers")] + cobre + tecnicas


def placa_vazia(n_cobre, titulo, data, rev, empresa="", espessura=1.6, folha="A4"):
    """Placa sem contorno nem footprints, com todas as camadas padrao habilitadas."""
    return _cabecalho("kicad_pcb", VERSAO_PCB) + [
        [S("general"), [S("thickness"), espessura], [S("legacy_teardrops"), S("no")]],
        [S("paper"), folha],
        bloco_titulo(titulo, data, rev, empresa),
        _camadas(n_cobre),
        [S("setup"), [S("pad_to_mask_clearance"), 0]],
        [S("embedded_fonts"), S("no")],
    ]


def biblioteca_simbolos_vazia():
    return _cabecalho("kicad_symbol_lib", VERSAO_SYM)


def tabela_bibliotecas(tipo, entradas):
    """tipo 'sym' ou 'fp'; entradas = [(nome, uri, descricao)]."""
    raiz = [S(f"{tipo}_lib_table"), [S("version"), 7]]
    for nome, uri, descr in entradas:
        raiz.append([S("lib"), [S("name"), nome], [S("type"), "KiCad"], [S("uri"), uri],
                     [S("options"), ""], [S("descr"), descr]])
    return raiz
