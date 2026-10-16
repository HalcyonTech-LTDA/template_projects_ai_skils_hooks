"""Specctra DSN/SES pelo SWIG `pcbnew` (so no Python do KiCad 10), preservando trilhas existentes.

Medido no 10.0.0 com o Freerouting 2.5.0: o KiCad exporta trilha travada (locked) como
`(wire ... (type fix))`, que o Freerouting nao mexe nem devolve no SES, e o ImportSpecctraSES apaga as
trilhas e vias da placa SALVO as travadas antes de trazer as da sessao. Entao: travar o que ja
existe, exportar, rotear, importar, tirar copias identicas as preservadas (se uma versao futura
devolver a fiada fixa no SES) e destravar so o que foi travado aqui.
"""

from . import exigir_pcbnew

pcbnew = exigir_pcbnew()


def exportar_dsn(board, caminho):
    if not pcbnew.ExportSpecctraDSN(board, str(caminho)):
        raise RuntimeError(f"pcbnew nao exportou o DSN {caminho}")


def importar_ses(board, caminho):
    if not pcbnew.ImportSpecctraSES(board, str(caminho)):
        raise RuntimeError(f"pcbnew nao importou o SES {caminho}")


def travar_existentes(board):
    """Trava trilhas e vias ainda destravadas; devolve os uuids travados aqui."""
    travadas = []
    for t in board.GetTracks():
        if not t.IsLocked():
            t.SetLocked(True)
            travadas.append(t.m_Uuid.AsString())
    return travadas


def destravar(board, uuids):
    uuids = set(uuids)
    for t in board.GetTracks():
        if t.m_Uuid.AsString() in uuids:
            t.SetLocked(False)


def _chave(t):
    """Igualdade geometrica de trilha (pontas em qualquer ordem) ou via."""
    rede, camada = t.GetNetname(), t.GetLayer()
    if t.GetClass() == "PCB_VIA":
        return ("via", rede, t.GetPosition().x, t.GetPosition().y)
    a, b = (t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)
    return ("trilha", rede, camada, min(a, b), max(a, b), t.GetWidth())


def remover_copias(board, preservadas):
    """Tira trilhas/vias identicas a uma preservada (uuid em `preservadas`). Devolve quantas tirou."""
    preservadas = set(preservadas)
    originais = {_chave(t) for t in board.GetTracks() if t.m_Uuid.AsString() in preservadas}
    copias = [t for t in board.GetTracks() if t.m_Uuid.AsString() not in preservadas and _chave(t) in originais]
    for t in copias:
        board.Delete(t)
    return len(copias)


def alargar_finas(board):
    """Trilhas mais finas que a minima da placa passam para a minima. Devolve {uuid: largura original}."""
    minimo = board.GetDesignSettings().m_TrackMinWidth
    finas = {}
    for t in board.GetTracks():
        if t.GetClass() == "PCB_TRACK" and t.GetWidth() < minimo:
            finas[t.m_Uuid.AsString()] = t.GetWidth()
            t.SetWidth(minimo)
    return finas


def restaurar_larguras(board, larguras):
    for t in board.GetTracks():
        if t.m_Uuid.AsString() in larguras:
            t.SetWidth(larguras[t.m_Uuid.AsString()])


def trilha_minima_um(board):
    """Trilha minima da placa (regras do .kicad_pro), em micrometros."""
    return pcbnew.ToMM(board.GetDesignSettings().m_TrackMinWidth) * 1000


def contar(board):
    """(trilhas, vias) na placa."""
    vias = sum(1 for t in board.GetTracks() if t.GetClass() == "PCB_VIA")
    return len(board.GetTracks()) - vias, vias
