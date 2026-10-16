"""Posicionamento inicial por bloco da spec. Geometria pura: nao importa `pcbnew`.

E ponto de partida para revisao humana, nao layout final. Regras (todas explicaveis):
1. Dentro de cada bloco, as pecas que nao sao de borda sao empacotadas da maior para a menor,
   sempre no ponto livre mais acima e mais a esquerda (heuristica "bottom-left"), com
   `FOLGA_PECA` entre courtyards; a largura-alvo do bloco e ~1,25 x a raiz da area somada.
2. Os blocos entram na placa na ordem da spec, pela mesma heuristica, com `FOLGA_BLOCO` entre
   eles, `MARGEM` ate a borda e os cantos reservados aos furos de fixacao.
3. Pecas de borda: conector (`J*`) e modulo com area de exclusao (antena: footprint com area de
   regra que proibe footprints). Cada uma vai para a borda mais proxima do seu bloco; peca em bloco
   so de pecas de borda segue o bloco com que divide mais redes de sinal.
   Antena escolhe primeiro; conector nao divide borda com antena. A borda escolhida ganha uma faixa
   da profundidade da peca, e os blocos sao reempacotados no miolo que sobra; como isso muda onde
   os blocos caem, as bordas sao reescolhidas sobre o arranjo novo (ate 4 vezes) e fica o arranjo
   de menor soma de distancias bloco -> borda da sua peca.
4. Conector: lado comprido paralelo a borda e o corpo (lado mais longe dos pads, por onde entra o fio
   num borne horizontal) voltado para fora. Antena: a area de exclusao fica TODA fora da placa (a
   borda passa onde ela comeca; a antena do modulo fica em balanco, opcao recomendada pela
   Espressif). A peca desliza ao longo da borda ate o ponto livre mais proximo do centro do bloco.
Sem `largura`/`altura`, a placa cresce de 5 em 5 mm ate tudo caber.

Coordenadas em mm, origem no canto superior esquerdo da placa, y para baixo (como no KiCad).
"""

import math
from dataclasses import dataclass, field

FOLGA_PECA = 1.0        # courtyard a courtyard dentro do bloco
FOLGA_BLOCO = 3.0       # entre blocos (e entre bloco e faixa de conectores)
MARGEM = 2.0            # courtyard ate a borda da placa
MARGEM_CONECTOR = 0.5   # courtyard do conector ate a borda
FOLGA_CONECTOR = 1.0    # entre conectores na mesma borda
CANTO_FURO = 8.0        # quadrado reservado em cada canto para o furo M3 (centro a 4 mm das bordas)
PASSO_PLACA = 5.0
BORDAS = ("esquerda", "superior", "direita", "inferior")
REDE_GLOBAL = 8         # rede com mais pinos que isso (GND, +3V3) nao conta para "dividir sinal"


class ErroPosicionamento(ValueError):
    pass


@dataclass
class Peca:
    ref: str
    bloco: str
    caixas: dict            # rotacao (0, 90, 180, 270) -> (x0, y0, x1, y1) do courtyard relativo a origem
    pads: dict              # rotacao -> (x, y) centroide dos pads relativo a origem
    conector: bool = False
    redes: frozenset = frozenset()
    exclusao: dict = None   # rotacao -> caixa da area de exclusao (antena); a `caixa` ja vem sem ela
    corpos: dict = None     # rotacao -> caixa so do courtyard (sem o texto de referencia), para orientar

    @property
    def de_borda(self):
        return self.conector or self.exclusao is not None

    def corpo(self, rot=0):
        """Caixa que decide a orientacao na borda: o courtyard, sem o texto que entra na `caixa`."""
        return (self.corpos or self.caixas)[rot]

    def caixa(self, rot=0):
        return self.caixas[rot]

    def tamanho(self, rot=0):
        x0, y0, x1, y1 = self.caixas[rot]
        return x1 - x0, y1 - y0


@dataclass
class Posicao:
    x: float
    y: float
    rotacao: int = 0


@dataclass
class Resultado:
    largura: float
    altura: float
    posicoes: dict                              # ref -> Posicao (origem do footprint)
    blocos: dict                                # id -> (x0, y0, x1, y1)
    bordas: dict = field(default_factory=dict)  # ref do conector -> borda
    furos: list = field(default_factory=list)   # [(x, y)]
    avisos: list = field(default_factory=list)


# --- empacotamento -----------------------------------------------------------------

def _colide(a, b, folga):
    return a[0] < b[2] + folga and b[0] < a[2] + folga and a[1] < b[3] + folga and b[1] < a[3] + folga


def _candidatos(limite, ocupados, folga):
    pts = {(limite[0], limite[1])}
    for r in ocupados:
        pts |= {(r[2] + folga, r[1]), (r[0], r[3] + folga), (limite[0], r[3] + folga), (r[2] + folga, limite[1])}
    return sorted(pts, key=lambda p: (round(p[1], 6), round(p[0], 6)))


def empacotar(tamanhos, limite, obstaculos=(), folga=FOLGA_PECA):
    """Coloca retangulos (l, a), na ordem dada, no ponto livre mais acima e mais a esquerda dentro de
    `limite` (x0, y0, x1, y1; y1 pode ser inf). Devolve [(x, y)] dos cantos ou None se algum nao cabe."""
    ocupados, saida = list(obstaculos), []
    for l, a in tamanhos:
        for x, y in _candidatos(limite, ocupados, folga):
            r = (x, y, x + l, y + a)
            dentro = (x >= limite[0] - 1e-9 and y >= limite[1] - 1e-9
                      and r[2] <= limite[2] + 1e-9 and r[3] <= limite[3] + 1e-9)
            if dentro and not any(_colide(r, o, folga) for o in ocupados):
                ocupados.append(r)
                saida.append((x, y))
                break
        else:
            return None
    return saida


# --- blocos --------------------------------------------------------------------------

@dataclass
class _Bloco:
    id: str
    pecas: list                 # Pecas que nao sao conector, ordem de empacotamento
    locais: dict                # ref -> (x, y) do canto do courtyard dentro do bloco
    largura: float = 0.0
    altura: float = 0.0


def _montar_bloco(id_bloco, pecas):
    pecas = sorted(pecas, key=lambda p: (-p.tamanho()[1], -p.tamanho()[0], p.ref))
    if not pecas:
        return _Bloco(id_bloco, [], {})
    area = sum((l + FOLGA_PECA) * (a + FOLGA_PECA) for l, a in (p.tamanho() for p in pecas))
    alvo = max(max(p.tamanho()[0] for p in pecas), 1.25 * math.sqrt(area))
    cantos = empacotar([p.tamanho() for p in pecas], (0.0, 0.0, alvo, math.inf))
    locais = {p.ref: c for p, c in zip(pecas, cantos)}
    largura = max(c[0] + p.tamanho()[0] for p, c in zip(pecas, cantos))
    altura = max(c[1] + p.tamanho()[1] for p, c in zip(pecas, cantos))
    return _Bloco(id_bloco, pecas, locais, largura, altura)


def _cantos_furo(largura, altura, furos):
    if not furos:
        return []
    c = CANTO_FURO
    return [(0, 0, c, c), (largura - c, 0, largura, c), (0, altura - c, c, altura), (largura - c, altura - c, largura, altura)]


def _arranjar_blocos(blocos, largura, altura, margens, furos):
    """Regiao (x0, y0, x1, y1) de cada bloco com pecas, ou None se nao cabe."""
    com_pecas = [b for b in blocos if b.pecas]
    limite = (margens["esquerda"], margens["superior"], largura - margens["direita"], altura - margens["inferior"])
    obst = _cantos_furo(largura, altura, furos)
    cantos = empacotar([(b.largura, b.altura) for b in com_pecas], limite, obst, FOLGA_BLOCO)
    if cantos is None:
        return None
    return {b.id: (x, y, x + b.largura, y + b.altura) for b, (x, y) in zip(com_pecas, cantos)}


# --- conectores ------------------------------------------------------------------------

def _distancias(regiao, largura, altura):
    x0, y0, x1, y1 = regiao
    return {"esquerda": x0, "superior": y0, "direita": largura - x1, "inferior": altura - y1}


def _bloco_vizinho(conector, pecas, regioes):
    """Bloco (com regiao) que divide mais redes de sinal com o conector."""
    contagem = {}
    for p in pecas:
        if p.bloco in regioes and not p.de_borda:
            contagem[p.bloco] = contagem.get(p.bloco, 0) + len(conector.redes & p.redes)
    return max(sorted(contagem), key=lambda b: contagem[b]) if contagem else None


def _regiao_de_referencia(conector, pecas, regioes, largura, altura):
    bloco = conector.bloco if conector.bloco in regioes else _bloco_vizinho(conector, pecas, regioes)
    return regioes.get(bloco, (largura / 2, altura / 2, largura / 2, altura / 2))


def _exclusao_para_fora(peca, rot, borda):
    """A area de exclusao esta inteira do lado de fora do corpo, na direcao da borda?"""
    x0, y0, x1, y1 = peca.corpo(rot)
    ex0, ey0, ex1, ey1 = peca.exclusao[rot]
    return {"esquerda": ex1 <= x0 + 1e-6, "direita": ex0 >= x1 - 1e-6,
            "superior": ey1 <= y0 + 1e-6, "inferior": ey0 >= y1 - 1e-6}[borda]


def _rotacao_na_borda(peca, borda):
    """Antena: a rotacao que poe a exclusao para fora (None se nenhuma). Conector: lado comprido
    paralelo a borda e, entre as que servem, a que poe mais corpo alem dos pads para fora."""
    if peca.exclusao is not None:
        servem = [r for r in (0, 90, 180, 270) if _exclusao_para_fora(peca, r, borda)]
        return servem[0] if servem else None
    vertical = borda in ("esquerda", "direita")
    def para_fora(rot):
        x0, y0, x1, y1 = peca.corpo(rot)
        px, py = peca.pads[rot]
        return {"esquerda": px - x0, "direita": x1 - px, "superior": py - y0, "inferior": y1 - py}[borda]

    def em_pe(rot):
        x0, y0, x1, y1 = peca.corpo(rot)
        return (y1 - y0) >= (x1 - x0)
    servem = [r for r in (0, 90, 180, 270) if em_pe(r) == vertical]
    return max(servem or [0], key=lambda r: (round(para_fora(r), 3), -r))


def _profundidade(peca, borda):
    l, a = peca.tamanho(_rotacao_na_borda(peca, borda))
    return l if borda in ("esquerda", "direita") else a


def _escolher_bordas(de_borda, pecas, regioes, largura, altura):
    """Antenas primeiro; conector evita borda de antena. Borda sem rotacao valida e descartada."""
    bordas, de_antena = {}, set()
    for c in sorted(de_borda, key=lambda p: (p.exclusao is None, p.ref)):
        dist = _distancias(_regiao_de_referencia(c, pecas, regioes, largura, altura), largura, altura)
        validas = [b for b in BORDAS if _rotacao_na_borda(c, b) is not None]
        livres = [b for b in validas if c.exclusao is not None or b not in de_antena] or validas
        if not livres:
            raise ErroPosicionamento(f"{c.ref}: nenhuma rotacao poe a area de exclusao para fora da placa")
        bordas[c.ref] = min(livres, key=lambda b: dist[b])
        if c.exclusao is not None:
            de_antena.add(bordas[c.ref])
    return bordas


def _margens(conectores, bordas):
    m = {b: MARGEM for b in BORDAS}
    for c in conectores:
        b = bordas[c.ref]
        m[b] = max(m[b], _margem_borda(c) + _profundidade(c, b) + FOLGA_BLOCO)
    return m


def _margem_borda(peca):
    """Antena encosta na borda (a exclusao fica fora); conector fica a MARGEM_CONECTOR."""
    return 0.0 if peca.exclusao is not None else MARGEM_CONECTOR


def _caixa_na_borda(peca, borda, rot, centro, largura, altura):
    """Caixa absoluta da peca encostada na borda, centrada em `centro` ao longo dela."""
    l, a = peca.tamanho(rot)
    m = _margem_borda(peca)
    if borda == "esquerda":
        return (m, centro - a / 2, m + l, centro + a / 2)
    if borda == "direita":
        return (largura - m - l, centro - a / 2, largura - m, centro + a / 2)
    if borda == "superior":
        return (centro - l / 2, m, centro + l / 2, m + a)
    return (centro - l / 2, altura - m - a, centro + l / 2, altura - m)


def _deslizar(peca, borda, rot, alvo, largura, altura, ocupados):
    """Primeira posicao livre ao longo da borda, a partir do alvo e se afastando dele (passo 0,25 mm)."""
    comprimento = altura if borda in ("esquerda", "direita") else largura
    for i in range(int(comprimento / 0.25) * 2 + 1):
        centro = alvo + (i + 1) // 2 * 0.25 * (1 if i % 2 else -1)
        cx = _caixa_na_borda(peca, borda, rot, centro, largura, altura)
        dentro = cx[0] >= 0 and cx[1] >= 0 and cx[2] <= largura and cx[3] <= altura
        if dentro and not any(_colide(cx, o, FOLGA_CONECTOR) for o in ocupados):
            return cx
    return None


def _colocar_de_borda(de_borda, pecas, regioes, bordas, largura, altura, furos):
    posicoes, ocupados = {}, _cantos_furo(largura, altura, furos)
    for c in sorted(de_borda, key=lambda p: (p.exclusao is None, p.ref)):
        b = bordas[c.ref]
        rot = _rotacao_na_borda(c, b)
        x0, y0, x1, y1 = _regiao_de_referencia(c, pecas, regioes, largura, altura)
        alvo = (y0 + y1) / 2 if b in ("esquerda", "direita") else (x0 + x1) / 2
        cx = _deslizar(c, b, rot, alvo, largura, altura, ocupados)
        if cx is None:
            return None
        ocupados.append(cx)
        rx0, ry0, _, _ = c.caixa(rot)
        posicoes[c.ref] = Posicao(cx[0] - rx0, cx[1] - ry0, rot)
    return posicoes


# --- montagem ----------------------------------------------------------------------------

def _posicoes_dos_blocos(blocos, regioes):
    saida = {}
    for b in blocos:
        if b.id not in regioes:
            continue
        bx, by = regioes[b.id][:2]
        for p in b.pecas:
            lx, ly = b.locais[p.ref]
            x0, y0 = p.caixa()[:2]
            saida[p.ref] = Posicao(bx + lx - x0, by + ly - y0, 0)
    return saida


def _custo(de_borda, pecas, regioes, bordas, largura, altura):
    """Soma das distancias de cada bloco de referencia ate a borda da sua peca de borda."""
    return sum(_distancias(_regiao_de_referencia(c, pecas, regioes, largura, altura), largura, altura)[bordas[c.ref]]
               for c in de_borda)


def _ajustar_bordas(blocos, de_borda, pecas, regioes, largura, altura, furos, tentativas=4):
    """A faixa de borda muda o miolo e o reempacotamento muda onde cada bloco cai: reescolhe as
    bordas sobre o arranjo novo ate estabilizar (no maximo `tentativas`) e fica com o arranjo de menor
    soma de distancias bloco -> borda. Devolve (regioes, bordas) ou None se nada coube."""
    melhor = None
    bordas = _escolher_bordas(de_borda, pecas, regioes, largura, altura)
    for _ in range(tentativas):
        regioes = _arranjar_blocos(blocos, largura, altura, _margens(de_borda, bordas), furos)
        if regioes is None:
            break
        custo = _custo(de_borda, pecas, regioes, bordas, largura, altura)
        if melhor is None or custo < melhor[0] - 1e-9:
            melhor = (custo, regioes, bordas)
        novas = _escolher_bordas(de_borda, pecas, regioes, largura, altura)
        if novas == bordas:
            break
        bordas = novas
    return melhor[1:] if melhor else None


def _tentar(pecas, ordem_blocos, largura, altura, furos):
    blocos = [_montar_bloco(b, [p for p in pecas if p.bloco == b and not p.de_borda]) for b in ordem_blocos]
    de_borda = [p for p in pecas if p.de_borda]
    regioes = _arranjar_blocos(blocos, largura, altura, {b: MARGEM for b in BORDAS}, furos)
    if regioes is None:
        return None
    melhor = _ajustar_bordas(blocos, de_borda, pecas, regioes, largura, altura, furos)
    if melhor is None:
        return None
    regioes, bordas = melhor
    pos_con = _colocar_de_borda(de_borda, pecas, regioes, bordas, largura, altura, furos)
    if pos_con is None:
        return None
    posicoes = _posicoes_dos_blocos(blocos, regioes)
    posicoes.update(pos_con)
    return Resultado(largura, altura, posicoes, regioes, bordas, _furos(largura, altura, furos))


def _furos(largura, altura, furos):
    if not furos:
        return []
    d = CANTO_FURO / 2
    return [(d, d), (largura - d, d), (d, altura - d), (largura - d, altura - d)]


def _arredondar(v):
    return math.ceil(v / PASSO_PLACA - 1e-9) * PASSO_PLACA


def _tamanho_inicial(pecas):
    area = sum((l + 2 * FOLGA_PECA) * (a + 2 * FOLGA_PECA) for l, a in (p.tamanho() for p in pecas))
    largura = math.sqrt(area * 1.6 * 4 / 3) + 2 * MARGEM
    return _arredondar(largura), _arredondar(largura * 3 / 4)


def _automatico(pecas, ordem_blocos, furos, max_passos=60):
    largura, altura = _tamanho_inicial(pecas)
    for i in range(max_passos):
        r = _tentar(pecas, ordem_blocos, largura, altura, furos)
        if r:
            return r
        if i % 2 == 0:
            largura += PASSO_PLACA
        else:
            altura += PASSO_PLACA
    raise ErroPosicionamento(f"nao consegui posicionar nem numa placa de {largura} x {altura} mm")


def posicionar(pecas, ordem_blocos, largura=None, altura=None, furos=True):
    """Posicoes de todas as pecas. `ordem_blocos` = ids na ordem da spec (pecas de bloco fora da
    lista vao para um bloco 'outros' no fim). Com largura/altura, falha se nao couber e diz o minimo."""
    ordem = list(ordem_blocos) + sorted({p.bloco for p in pecas} - set(ordem_blocos))
    if largura and altura:
        r = _tentar(pecas, ordem, float(largura), float(altura), furos)
        if r is None:
            minimo = _automatico(pecas, ordem, furos)
            raise ErroPosicionamento(f"as pecas nao cabem em {largura} x {altura} mm com as folgas padrao; "
                                     f"menor placa achada: {minimo.largura:g} x {minimo.altura:g} mm")
        return r
    return _automatico(pecas, ordem, furos)


def eh_conector(ref):
    return ref.upper().startswith("J") and ref[1:2].isdigit()


def redes_de_sinal(pinos_por_ref, tamanho_rede):
    """ref -> frozenset das redes com ate REDE_GLOBAL pinos (para achar o bloco vizinho do conector)."""
    return {ref: frozenset(r for r in redes if tamanho_rede.get(r, 0) <= REDE_GLOBAL)
            for ref, redes in pinos_por_ref.items()}
