"""Resumo do relatorio de DRC do kicad-cli: por tipo, conexoes faltando por rede e por net class.

A descricao dos itens vem no idioma da instalacao ("Ilha 2 [/+12V_SYS] de Q1 no F.Cu"), mas a
rede aparece sempre entre colchetes: e so isso que se le dela.
"""

import collections
import re

from . import regras

_REDE = re.compile(r"\[([^\]]*)\]")


def rede_do_item(descricao):
    m = _REDE.search(descricao or "")
    return m.group(1) if m else None


def _rede_da_violacao(v):
    for item in v.get("items", []):
        rede = rede_do_item(item.get("description"))
        if rede:
            return rede
    return None


def _violacao(v):
    return {"tipo": v.get("type"), "severidade": v.get("severity"), "descricao": v.get("description"),
            "itens": [i.get("description") for i in v.get("items", [])]}


def desconectados_por_rede(rel):
    return dict(sorted(collections.Counter(_rede_da_violacao(v) or "?" for v in rel.nao_conectados).items()))


def desconectados_por_classe(rel, dados_pro):
    """Conexoes faltando agrupadas pela net class da rede (pelo netclass_patterns do .kicad_pro). Rede
    que casa padroes de duas classes fica na composta, como o KiCad mostra (`HV,Power`)."""
    contagem = collections.Counter()
    for rede, n in desconectados_por_rede(rel).items():
        contagem[regras.classe_da_rede(dados_pro, rede) if dados_pro else regras.CLASSE_PADRAO] += n
    return dict(sorted(contagem.items()))


def reprova(resumo, estrito=False):
    """Mesmo criterio do portao: erro reprova; paridade e conexao faltando reprovam em qualquer
    severidade (no KiCad 10.0.0 `missing_footprint` e cia. sao `warning` por padrao: um footprint
    faltando passaria); aviso so reprova com `estrito`."""
    if resumo["erros"] or resumo["desconectados"] or resumo["paridade"]:
        return True
    return bool(estrito and resumo["avisos"])


def resumir(rel, dados_pro=None):
    todas = rel.violacoes + rel.nao_conectados + rel.paridade
    por_tipo = collections.Counter((v.get("type"), v.get("severity")) for v in todas)
    return {"erros": rel.erros, "avisos": rel.avisos,
            "por_tipo": [{"tipo": t, "severidade": s, "quantidade": n} for (t, s), n in sorted(por_tipo.items())],
            "desconectados": len(rel.nao_conectados),
            "desconectados_por_rede": desconectados_por_rede(rel),
            "desconectados_por_classe": desconectados_por_classe(rel, dados_pro),
            "paridade": [_violacao(v) for v in rel.paridade],
            "violacoes": [_violacao(v) for v in rel.violacoes]}
