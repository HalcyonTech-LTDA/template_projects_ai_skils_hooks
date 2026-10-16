"""Posicionamento: cada bloco vira uma regiao da folha; componentes em grade dentro do bloco.

Estilo "label por pino": cada ponta de pino ganha um fio curto (FIO mm) para fora do corpo,
terminado num label local ou num simbolo de power; pino em `nao_conectar` ganha o X de nao
conectado na propria ponta. PWR_FLAG vira um item a mais no bloco do primeiro pino da rede.

Tudo aqui e geometria pura (sem S-expression): o `escritor` so serializa o `Desenho`.
Coordenadas na grade de 1,27 mm; nenhuma caixa de item se sobrepoe (empacotamento em prateleiras).
"""

import textwrap
from dataclasses import dataclass, field

from . import geometria as g
from .caixas import Caixa, caixa_corpo, caixa_texto, largura_texto, uniao

FIO = 2.54              # comprimento do fio de cada pino
FONTE = 1.27
FONTE_TITULO = 2.54
FOLGA = 2.54            # entre itens e em volta do conteudo do bloco
FOLGA_BLOCO = 5.08      # entre blocos
LARGURA_MIN_BLOCO = 101.6
MARGEM = 12.7           # da borda da folha
ALTURA_LEGENDA = 40.64  # faixa de baixo reservada ao title block
FOLHAS_MM = {"A4": (297, 210), "A3": (420, 297), "A2": (594, 420), "A1": (841, 594)}


@dataclass
class Terminacao:
    tipo: str           # 'label', 'power' ou 'nc'
    rede: str = ""
    simbolo: object = None  # SimboloLib de power


@dataclass
class Item:
    chave: str          # ref do componente ou '#FLG:<rede>'
    simbolo: object     # SimboloLib
    unidade: int
    terminacoes: dict   # numero do pino -> Terminacao
    componente: object = None   # spec.Componente (None para PWR_FLAG)
    valor: str = ""
    rotacao: int = 0

    @property
    def orient(self):
        return g.Orientacao(self.rotacao)


def terminacao(circuito, chave):
    nome = circuito.rede_do_pino.get(chave)
    if nome is None:
        return Terminacao("nc")
    rede = circuito.redes[nome]
    return Terminacao("power", nome, rede.power) if rede.power else Terminacao("label", nome)


def itens_do_componente(circuito, comp):
    """Um item por unidade do simbolo."""
    itens = []
    for u in range(1, comp.simbolo.unidades + 1):
        terms = {p.numero: terminacao(circuito, (comp.ref, p.numero))
                 for p in comp.pinos() if p.unidade in (0, u)}
        if terms:
            itens.append(Item(comp.ref, comp.simbolo, u, terms, comp, comp.valor, rotacao_preferida(comp, terms)))
    return itens


def rotacao_preferida(comp, terms):
    """Dois pinos na vertical (R, C, L...) deitam (90 graus) quando nenhum vai a simbolo de power:
    os labels ficam horizontais. Com power, fica em pe (power em cima e embaixo, o desenho classico)."""
    pinos = [p for p in comp.pinos() if p.numero in terms]
    verticais = len(pinos) == 2 and all(p.x == 0 and p.angulo in (90, 270) for p in pinos)
    tem_power = any(t.tipo == "power" for t in terms.values())
    return 90 if verticais and not tem_power else 0


def _itens_flag(circuito, simbolo_flag):
    """bloco -> [Item PWR_FLAG], no bloco do primeiro componente da rede."""
    por_bloco = {}
    for rede in circuito.redes.values():
        if not rede.pwr_flag:
            continue
        bloco = circuito.componentes[rede.pinos[0][0]].bloco
        term = Terminacao("power", rede.nome, rede.power) if rede.power else Terminacao("label", rede.nome)
        numero = simbolo_flag.pinos[0].numero
        por_bloco.setdefault(bloco, []).append(Item(f"#FLG:{rede.nome}", simbolo_flag, 1, {numero: term},
                                                    None, "PWR_FLAG"))
    return por_bloco


def blocos_com_itens(circuito, simbolo_flag):
    flags = _itens_flag(circuito, simbolo_flag)
    saida = []
    for b in circuito.blocos:
        itens = [it for ref in b.refs for it in itens_do_componente(circuito, circuito.componentes[ref])]
        saida.append((b, itens + flags.get(b.id, [])))
    return saida


# --- primitivas do desenho -------------------------------------------------------

@dataclass
class Instancia:
    item: Item
    x: float
    y: float
    rotacao: int = 0
    campos: dict = field(default_factory=dict)   # 'Reference'/'Value' -> (x, y, justify)


@dataclass
class Power:
    simbolo: object
    rede: str
    x: float
    y: float
    rotacao: int
    valor_xy: tuple


@dataclass
class Desenho:
    folha: str
    instancias: list = field(default_factory=list)
    powers: list = field(default_factory=list)
    fios: list = field(default_factory=list)       # (x1, y1, x2, y2)
    labels: list = field(default_factory=list)     # (nome, x, y, angulo)
    ncs: list = field(default_factory=list)        # (x, y)
    textos: list = field(default_factory=list)     # (texto, x, y, tamanho, negrito)
    molduras: list = field(default_factory=list)   # Caixa
    avisos: list = field(default_factory=list)


# --- geometria de um item (origem em 0,0) ---------------------------------------------

def pontos_de_conexao(item):
    """[(pos, direcao, terminacao)] um por ponto distinto (pinos empilhados viram um so)."""
    vistos, saida = set(), []
    for p in item.simbolo.pinos:
        if p.unidade not in (0, item.unidade) or p.corpo not in (0, 1) or p.numero not in item.terminacoes:
            continue
        pos = g.posicao_pino(p, (0, 0), item.orient)
        if pos in vistos:
            continue
        vistos.add(pos)
        saida.append((pos, g.direcao_para_fora(p, item.orient), item.terminacoes[p.numero]))
    return saida


def orientacao_power(simbolo, direcao):
    """Rotacao do simbolo de power para o corpo dele seguir a direcao do fio."""
    pino = simbolo.pinos[0]
    for rot in (0, 90, 180, 270):
        dx, dy = g.direcao_para_fora(pino, g.Orientacao(rot))
        if (-dx, -dy) == tuple(direcao):
            return rot
    return 0


def _power(term, x, y, direcao):
    rot = orientacao_power(term.simbolo, direcao)
    corpo = caixa_corpo(term.simbolo, 1, g.Orientacao(rot)).deslocar(x, y)
    alcance = max(abs(corpo.x1 - x), abs(corpo.x2 - x)) if direcao[0] else max(abs(corpo.y1 - y), abs(corpo.y2 - y))
    meio = largura_texto(term.rede) / 2 if direcao[0] else FONTE * 0.8
    dist = alcance + 0.635 + meio
    vx, vy = x + direcao[0] * dist, y + direcao[1] * dist
    if direcao[0]:
        vy -= FONTE * 0.8       # fio na horizontal: texto acima da linha, como os labels (pino vizinho a 2,54 mm)
    texto = caixa_texto(term.rede, vx, vy)
    return Power(term.simbolo, term.rede, x, y, rot, (round(vx, 3), round(vy, 3))), corpo.uniao(texto)


def _label(nome, x, y, direcao):
    ang = g.angulo_da_direcao(direcao)
    horiz = "right" if ang in (180, 270) else "left"
    return (nome, x, y, ang), caixa_texto(nome, x, y, FONTE, ang % 180, horiz, "bottom").expandir(0.4)


def _terminar(desenho_local, pos, direcao, term):
    """Desenha a terminacao de um ponto e devolve a caixa ocupada."""
    if term.tipo == "nc":
        desenho_local.ncs.append(pos)
        return Caixa(pos[0] - 0.8, pos[1] - 0.8, pos[0] + 0.8, pos[1] + 0.8)
    x2, y2 = pos[0] + direcao[0] * FIO, pos[1] + direcao[1] * FIO
    desenho_local.fios.append((pos[0], pos[1], x2, y2))
    fio = Caixa.de_pontos([pos, (x2, y2)])
    if term.tipo == "power":
        pw, caixa = _power(term, x2, y2, direcao)
        desenho_local.powers.append(pw)
    else:
        lb, caixa = _label(term.rede, x2, y2, direcao)
        desenho_local.labels.append(lb)
    return fio.uniao(caixa)


def _linhas_campos(item):
    if item.componente is None:
        return [("Value", item.valor)] if item.valor else []
    return [("Reference", item.chave), ("Value", item.valor)]


def _candidatos_campos(corpo, linhas):
    """Posicoes (x, y_topo, justify) para o bloco de texto de Reference/Value, em ordem de preferencia."""
    h = len(linhas) * FONTE * 1.6
    meio = (corpo.y1 + corpo.y2) / 2 - h / 2
    return [(corpo.x2 + 1.27, meio, "left"), (corpo.x1 - 1.27, meio, "right"),
            (corpo.x1, corpo.y1 - 1.27 - h, "left"), (corpo.x2, corpo.y1 - 1.27 - h, "right"),
            (corpo.x1, corpo.y2 + 1.27, "left"), (corpo.x2, corpo.y2 + 1.27, "right")]


def _caixas_campos(linhas, x, y_topo, justify):
    saida = []
    for i, (nome, texto) in enumerate(linhas):
        y = y_topo + (i + 0.5) * FONTE * 1.6
        saida.append((nome, x, y, justify, caixa_texto(texto, x, y, FONTE, 0, justify, "center")))
    return saida


def _posicionar_campos(item, corpo, obstaculos):
    """Reference e Value onde nao cruzam pino, fio ou label; senao, acima de tudo."""
    linhas = _linhas_campos(item)
    if not linhas:
        return {}, None
    for x, y, just in _candidatos_campos(corpo, linhas):
        cx = _caixas_campos(linhas, x, y, just)
        if not any(c[4].cruza(o) for c in cx for o in obstaculos):
            return {c[0]: (c[1], c[2], c[3]) for c in cx}, uniao([c[4] for c in cx])
    tudo = uniao(obstaculos)
    cx = _caixas_campos(linhas, tudo.x1, tudo.y1 - 1.27 - len(linhas) * FONTE * 1.6, "left")
    return {c[0]: (c[1], c[2], c[3]) for c in cx}, uniao([c[4] for c in cx])


def desenhar_item(item):
    """Desenho local do item (origem 0,0) e a caixa que ele ocupa."""
    local = Desenho("")
    corpo = caixa_corpo(item.simbolo, item.unidade, item.orient)
    obst = [corpo]
    for pos, direcao, term in pontos_de_conexao(item):
        obst.append(_terminar(local, pos, direcao, term))
    campos, caixa_campos = _posicionar_campos(item, corpo, obst)
    local.instancias.append(Instancia(item, 0.0, 0.0, item.rotacao, campos))
    return local, uniao(obst + [caixa_campos])


# --- empacotamento ---------------------------------------------------------------------

def _prateleiras(tamanhos, largura_max, folga):
    """Posicoes (x, y) de cada retangulo (w, h) em linhas da esquerda para a direita."""
    pos, x, y, altura_linha = [], 0.0, 0.0, 0.0
    for w, h in tamanhos:
        if x > 0 and x + w > largura_max:
            x, y, altura_linha = 0.0, y + altura_linha + folga, 0.0
        pos.append((x, y))
        x += w + folga
        altura_linha = max(altura_linha, h)
    return pos


def _arredondar_acima(v, grade=g.GRADE):
    return g.na_grade(v + grade / 2 - 1e-6, grade) if v % grade else v


def _deslocar(local, dx, dy, destino):
    for inst in local.instancias:
        campos = {k: (x + dx, y + dy, j) for k, (x, y, j) in inst.campos.items()}
        destino.instancias.append(Instancia(inst.item, inst.x + dx, inst.y + dy, inst.rotacao, campos))
    for pw in local.powers:
        destino.powers.append(Power(pw.simbolo, pw.rede, pw.x + dx, pw.y + dy, pw.rotacao,
                                    (pw.valor_xy[0] + dx, pw.valor_xy[1] + dy)))
    destino.fios += [(a + dx, b + dy, c + dx, d + dy) for a, b, c, d in local.fios]
    destino.labels += [(n, x + dx, y + dy, a) for n, x, y, a in local.labels]
    destino.ncs += [(x + dx, y + dy) for x, y in local.ncs]
    destino.textos += [(t, x + dx, y + dy, s, b) for t, x, y, s, b in local.textos]
    destino.molduras += [m.deslocar(dx, dy) for m in local.molduras]


def _notas(texto, largura):
    colunas = max(20, int(largura / (FONTE * 0.92)))
    linhas = []
    for par in str(texto).split("\n"):
        linhas += textwrap.wrap(par, colunas) or [""]
    return "\n".join(linhas)


def _conteudo(feitos, largura):
    """Posicoes dos itens em prateleiras e a largura/altura realmente ocupadas."""
    tamanhos = [(_arredondar_acima(c.largura), _arredondar_acima(c.altura)) for _, c in feitos]
    pos = _prateleiras(tamanhos, largura, FOLGA * 2)
    w = max((x + tw for (x, _), (tw, _) in zip(pos, tamanhos)), default=0)
    h = max((y + th for (_, y), (_, th) in zip(pos, tamanhos)), default=0)
    return pos, w, h


def _largura_bloco(bloco, feitos, alvo):
    largura_max = max([alvo] + [c.largura for _, c in feitos])
    _, w, _ = _conteudo(feitos, largura_max)
    titulo = largura_texto(bloco.titulo, FONTE_TITULO)
    notas = min(largura_texto(bloco.notas), alvo) if bloco.notas else 0
    return max(w, titulo, notas, LARGURA_MIN_BLOCO / 2)


def montar_bloco(bloco, feitos, alvo=LARGURA_MIN_BLOCO):
    """Desenho do bloco (origem no canto superior esquerdo da moldura) e o tamanho (w, h).
    `feitos` = [desenhar_item(it)]; `alvo` = largura preferida do conteudo."""
    largura = _largura_bloco(bloco, feitos, alvo)
    pos, _, _ = _conteudo(feitos, largura)
    topo = FOLGA + FONTE_TITULO * 1.6
    desenho = Desenho("")
    desenho.textos.append((bloco.titulo, FOLGA, FOLGA + FONTE_TITULO, FONTE_TITULO, True))
    fundo = topo
    for (local, caixa), (x, y) in zip(feitos, pos):
        dx, dy = g.na_grade(FOLGA + x - caixa.x1), g.na_grade(topo + FOLGA + y - caixa.y1)
        _deslocar(local, dx, dy, desenho)
        fundo = max(fundo, caixa.y2 + dy)
    if bloco.notas:
        notas = _notas(bloco.notas, largura)
        desenho.textos.append((notas, FOLGA, fundo + FOLGA, FONTE, False))
        fundo += FOLGA + notas.count("\n") * FONTE * 1.6 + FONTE * 2
    w, h = _arredondar_acima(largura + 2 * FOLGA), _arredondar_acima(fundo + FOLGA)
    desenho.molduras.append(Caixa(0, 0, w, h))
    return desenho, (w, h)


def _horizonte(tamanhos, largura_max, folga):
    """Empacotamento 'mais baixo, depois mais a esquerda' (skyline): cada retangulo vai para o x
    em que fica mais alto na folha; a ordem da spec decide o desempate."""
    perfil = [(0.0, largura_max, 0.0)]          # segmentos (x1, x2, y do fundo ocupado)
    pos = []
    for w, h in tamanhos:
        melhor = None
        for x, _, _ in perfil:
            if x + w > largura_max + 1e-6 and x > 0:
                continue
            y = max(sy for sx1, sx2, sy in perfil if sx1 < x + w and sx2 > x)
            if melhor is None or (y, x) < melhor:
                melhor = (y, x)
        y, x = melhor
        pos.append((x, y))
        perfil = _subir_perfil(perfil, x, x + w + folga, y + h + folga)
    return pos


def _subir_perfil(perfil, x1, x2, y):
    novo = []
    for sx1, sx2, sy in perfil:
        if sx2 <= x1 or sx1 >= x2:
            novo.append((sx1, sx2, sy))
            continue
        if sx1 < x1:
            novo.append((sx1, x1, sy))
        if sx2 > x2:
            novo.append((x2, sx2, sy))
    novo.append((x1, x2, y))
    return sorted(novo)


LARGURAS_ALVO = (101.6, 127.0, 152.4, 177.8, 203.2, 254.0)


def _tentar(folha, blocos_feitos, alvo):
    largura_folha, altura_folha = FOLHAS_MM[folha]
    feitos = [montar_bloco(b, f, alvo) for b, f in blocos_feitos]
    pos = _horizonte([t for _, t in feitos], largura_folha - 2 * MARGEM, FOLGA_BLOCO)
    total = Desenho(folha)
    for (desenho, _), (x, y) in zip(feitos, pos):
        _deslocar(desenho, g.na_grade(MARGEM + x), g.na_grade(MARGEM + y), total)
    ocupado = uniao(total.molduras)
    return total, (ocupado.y2 if ocupado else 0)


def montar(folha, blocos_itens):
    """blocos_itens: [(spec.Bloco, [Item])]. Devolve o Desenho da folha inteira.
    Tenta varias larguras de bloco e fica com a de menor altura total."""
    blocos_feitos = [(b, [desenhar_item(it) for it in its]) for b, its in blocos_itens]
    tentativas = [_tentar(folha, blocos_feitos, alvo) for alvo in LARGURAS_ALVO]
    total, _ = min(tentativas, key=lambda t: t[1])
    largura_folha, altura_folha = FOLHAS_MM[folha]
    _conferir_folha(total, largura_folha, altura_folha)
    return total


def _conferir_folha(desenho, largura, altura):
    ocupado = uniao(desenho.molduras)
    if ocupado and (ocupado.x2 > largura - MARGEM or ocupado.y2 > altura - MARGEM - ALTURA_LEGENDA):
        desenho.avisos.append(
            f"o desenho ocupa {ocupado.x2:.0f} x {ocupado.y2:.0f} mm e passa da area util da folha {desenho.folha} "
            f"({largura} x {altura} mm, menos margem e legenda); use folha maior ou divida a placa")
