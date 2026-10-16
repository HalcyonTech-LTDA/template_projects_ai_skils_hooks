"""Serializa o Desenho no formato .kicad_sch do KiCad 10 (ver "## Oraculo" no handoff).

UUIDs sao deterministicos (uuid5 de projeto + chave do objeto): regenerar a mesma spec mantem o
uuid de cada simbolo, que e o elo com o footprint na placa (`(path "/<uuid do simbolo>")`).
"""

import uuid

from .. import bibliotecas, modelos
from ..sexpr import Simbolo as S, filho, salvar_arquivo

FONTE = 1.27
_JUSTIFY_LABEL = {0: ("left", "bottom"), 90: ("left", "bottom"), 180: ("right", "bottom"), 270: ("right", "bottom")}


class Uuids:
    """uuid5 por chave; chave repetida e erro de programacao (uuid duplicado no arquivo)."""

    def __init__(self, semente):
        self.ns = uuid.uuid5(uuid.NAMESPACE_URL, f"pcbkit:{semente}")
        self.usadas = set()

    def __call__(self, *chave):
        k = "/".join(str(c) for c in chave)
        if k in self.usadas:
            raise ValueError(f"chave de uuid repetida: {k}")
        self.usadas.add(k)
        return str(uuid.uuid5(self.ns, k))


def uuid_do_simbolo(projeto, ref, unidade=1):
    """Uuid que o gerador da a instancia `ref`/`unidade` (para a fatia de placa e para testes)."""
    return str(uuid.uuid5(uuid.uuid5(uuid.NAMESPACE_URL, f"pcbkit:{projeto}"), f"sym/{ref}/{unidade}"))


# --- nos basicos -------------------------------------------------------------------

def _efeitos(tamanho=FONTE, justify=None, negrito=False):
    fonte = [S("font"), [S("size"), tamanho, tamanho]]
    if negrito:
        fonte.append([S("bold"), S("yes")])
    no = [S("effects"), fonte]
    if justify:
        no.append([S("justify")] + [S(j) for j in justify])
    return no


def _prop(nome, valor, x, y, oculto=False, justify=None, angulo=0):
    no = [S("property"), nome, valor, [S("at"), x, y, angulo]]
    if oculto:
        no.append([S("hide"), S("yes")])
    return no + [[S("show_name"), S("no")], [S("do_not_autoplace"), S("no")], _efeitos(FONTE, justify)]


def _fio(x1, y1, x2, y2, u):
    return [S("wire"), [S("pts"), [S("xy"), x1, y1], [S("xy"), x2, y2]],
            [S("stroke"), [S("width"), 0], [S("type"), S("default")]], [S("uuid"), u]]


def _label(nome, x, y, ang, u):
    return [S("label"), nome, [S("at"), x, y, ang], _efeitos(FONTE, _JUSTIFY_LABEL[ang]), [S("uuid"), u]]


def _nc(x, y, u):
    return [S("no_connect"), [S("at"), x, y], [S("uuid"), u]]


def _texto(texto, x, y, tamanho, negrito, u):
    just = ("left", "bottom") if negrito else ("left", "top")
    return [S("text"), texto, [S("exclude_from_sim"), S("no")], [S("at"), x, y, 0],
            _efeitos(tamanho, just, negrito), [S("uuid"), u]]


def _moldura(c, u):
    return [S("rectangle"), [S("start"), c.x1, c.y1], [S("end"), c.x2, c.y2],
            [S("stroke"), [S("width"), 0], [S("type"), S("dash")]], [S("fill"), [S("type"), S("none")]],
            [S("uuid"), u]]


# --- instancias de simbolo ------------------------------------------------------------

def _cabeca_instancia(lib_id, x, y, rot, unidade, dnp, u):
    return [S("symbol"), [S("lib_id"), lib_id], [S("at"), x, y, rot], [S("unit"), unidade],
            [S("body_style"), 1], [S("exclude_from_sim"), S("no")], [S("in_bom"), S("yes")],
            [S("on_board"), S("yes")], [S("in_pos_files"), S("yes")], [S("dnp"), S("yes" if dnp else "no")],
            [S("uuid"), u]]


def _pinos_e_caminho(simbolo, unidade, ref, ctx, chave):
    nums = []
    for p in simbolo.pinos:
        if p.unidade in (0, unidade) and p.corpo in (0, 1) and p.numero not in nums:
            nums.append(p.numero)
    pinos = [[S("pin"), n, [S("uuid"), ctx.uuids("pin", chave, unidade, n)]] for n in nums]
    caminho = [S("instances"), [S("project"), ctx.nome_projeto,
                                [S("path"), f"/{ctx.uuid_raiz}", [S("reference"), ref], [S("unit"), unidade]]]]
    return pinos + [caminho]


def _campos_extra(comp):
    props = comp.simbolo.propriedades
    datasheet = comp.campos.get("Datasheet") or props.get("Datasheet", "")
    extra = [("Footprint", comp.footprint), ("Datasheet", datasheet), ("Description", props.get("Description", ""))]
    return extra + [(k, v) for k, v in comp.campos.items() if k != "Datasheet"]


def _instancia_componente(inst, ctx):
    it, comp = inst.item, inst.item.componente
    no = _cabeca_instancia(comp.lib_id, inst.x, inst.y, inst.rotacao, it.unidade, comp.dnp,
                           ctx.uuids("sym", comp.ref, it.unidade))
    ang = angulo_campo(inst.rotacao)
    for nome, valor in (("Reference", comp.ref), ("Value", comp.valor)):
        x, y, just = inst.campos[nome]
        no.append(_prop(nome, valor, x, y, justify=_justify_campo(just, inst.rotacao), angulo=ang))
    no += [_prop(k, v, inst.x, inst.y, oculto=True) for k, v in _campos_extra(comp)]
    return no + _pinos_e_caminho(comp.simbolo, it.unidade, comp.ref, ctx, comp.ref)


def angulo_campo(rotacao):
    """O KiCad gira o texto do campo junto com o simbolo: em simbolo de 90/270 graus, angulo 90 fica horizontal."""
    return 90 if rotacao in (90, 270) else 0


def _justify_campo(just, rotacao):
    return (just,)


def _instancia_especial(simbolo, ref, x, y, rot, valor, valor_xy, ctx, chave, valor_oculto=False):
    """Simbolo de power ou PWR_FLAG: Reference oculta, Value no ponto calculado."""
    no = _cabeca_instancia(simbolo.lib_id, x, y, rot, 1, False, ctx.uuids("sym", chave, 1))
    no.append(_prop("Reference", ref, x, y, oculto=True))
    vx, vy, just = valor_xy
    no.append(_prop("Value", valor, vx, vy, oculto=valor_oculto, justify=(just,) if just else None,
                    angulo=angulo_campo(rot)))
    no += [_prop(k, simbolo.propriedades.get(k, ""), x, y, oculto=True) for k in ("Footprint", "Datasheet", "Description")]
    return no + _pinos_e_caminho(simbolo, 1, ref, ctx, chave)


class _Contexto:
    def __init__(self, nome_projeto, uuids, uuid_raiz):
        self.nome_projeto, self.uuids, self.uuid_raiz = nome_projeto, uuids, uuid_raiz
        self.n_pwr = self.n_flg = 0

    def ref_power(self):
        self.n_pwr += 1
        return f"#PWR{self.n_pwr:02d}"

    def ref_flag(self):
        self.n_flg += 1
        return f"#FLG{self.n_flg:02d}"


# --- arquivo ------------------------------------------------------------------------

def _lib_symbols(desenho):
    simbolos = {}
    for inst in desenho.instancias:
        simbolos[inst.item.simbolo.lib_id] = inst.item.simbolo
    for pw in desenho.powers:
        simbolos[pw.simbolo.lib_id] = pw.simbolo
    return [S("lib_symbols")] + [bibliotecas.no_embutido(simbolos[k]) for k in sorted(simbolos)]


def _simbolos(desenho, ctx):
    nos = []
    for inst in desenho.instancias:
        if inst.item.componente is not None:
            nos.append(_instancia_componente(inst, ctx))
        else:
            x, y, just = inst.campos.get("Value", (inst.x, inst.y, None))
            nos.append(_instancia_especial(inst.item.simbolo, ctx.ref_flag(), inst.x, inst.y, 0, "PWR_FLAG",
                                           (x, y, just), ctx, inst.item.chave))
    for i, pw in enumerate(desenho.powers):
        nos.append(_instancia_especial(pw.simbolo, ctx.ref_power(), pw.x, pw.y, pw.rotacao, pw.rede,
                                       (pw.valor_xy[0], pw.valor_xy[1], None), ctx, f"pwr{i}"))
    return nos


def _graficos(desenho, uuids):
    nos = [_nc(x, y, uuids("nc", i)) for i, (x, y) in enumerate(desenho.ncs)]
    nos += [_fio(*f, uuids("fio", i)) for i, f in enumerate(desenho.fios)]
    nos += [_label(n, x, y, a, uuids("label", i)) for i, (n, x, y, a) in enumerate(desenho.labels)]
    nos += [_texto(t, x, y, s, b, uuids("texto", i)) for i, (t, x, y, s, b) in enumerate(desenho.textos)]
    nos += [_moldura(c, uuids("moldura", i)) for i, c in enumerate(desenho.molduras)]
    return nos


def _bloco_titulo(dados, data, origem):
    no = modelos.bloco_titulo(dados["titulo"], data, dados["revisao"], dados.get("empresa", ""))
    no.append([S("comment"), 1, f"Gerado pelo pcbkit de {origem} (modo spec)"])
    return no


def esquematico(circuito, desenho, nome_projeto, data, origem="spec"):
    """Arvore S-expression do .kicad_sch. `nome_projeto` = nome do .kicad_pro (stem do arquivo)."""
    uuids = Uuids(circuito.projeto)
    raiz = uuids("raiz")
    ctx = _Contexto(nome_projeto, uuids, raiz)
    arvore = modelos.esquematico_vazio(circuito.dados["titulo"], data, circuito.dados["revisao"],
                                       circuito.dados.get("empresa", ""), desenho.folha, uuid_raiz=raiz)
    arvore[arvore.index(filho(arvore, "title_block"))] = _bloco_titulo(circuito.dados, data, origem)
    arvore[arvore.index(filho(arvore, "lib_symbols"))] = _lib_symbols(desenho)
    pos = arvore.index(filho(arvore, "sheet_instances"))
    arvore[pos:pos] = _graficos(desenho, uuids) + _simbolos(desenho, ctx)
    return arvore


def escrever(caminho, arvore):
    salvar_arquivo(caminho, arvore)
