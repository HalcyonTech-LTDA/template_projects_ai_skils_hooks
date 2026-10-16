"""Placa a partir da netlist, pelo SWIG `pcbnew` (so no Python do KiCad 10).

Faz o que o "Update PCB from Schematic" da GUI faz, na medida que o DRC com `--schematic-parity`
confere: footprint da biblioteca com o `Lib:Nome` da netlist, `path "/<uuid do simbolo>"`
(o `tstamps` do componente na netlist; sem o uuid da raiz), `sheetname`/`sheetfile`, campos do
simbolo (ocultos, na F.Fab) e a rede de cada pad pelo numero do pino, inclusive as
`unconnected-(...)` de pino solto. Pad sem pino no simbolo (furo mecanico) fica sem rede.

Depois: contorno retangular em Edge.Cuts, furos M3 nos cantos (board only: fora da BOM, do
arquivo de posicao e da paridade) e zonas de GND nas faces de cobre externas.
"""

from pathlib import PureWindowsPath

from .. import bibliotecas
from . import exigir_pcbnew

pcbnew = exigir_pcbnew()

ORIGEM = (100.0, 100.0)             # canto superior esquerdo da placa na folha, em mm
FURO_M3 = "MountingHole:MountingHole_3.2mm_M3"
LARGURA_CONTORNO = 0.1
CAMPOS_FIXOS = {"Reference", "Value", "Footprint"}
ZONA_ESPESSURA_MIN = 0.25
ZONA_ALIVIO_GAP = 0.5             # alivio termico dos pads passantes
ZONA_ALIVIO_RAIO = 0.5


def mm(v):
    return pcbnew.FromMM(float(v))


def ponto(x, y):
    """Ponto da placa (mm, relativo ao canto superior esquerdo) em unidades internas."""
    return pcbnew.VECTOR2I(mm(ORIGEM[0] + x), mm(ORIGEM[1] + y))


# --- arquivo ---------------------------------------------------------------------------

def carregar(caminho):
    """Abre a placa; o KiCad carrega junto o `.kicad_pro` vizinho (net classes e regras)."""
    return pcbnew.LoadBoard(str(caminho))


def salvar(board, caminho):
    """Grava so a placa: o `.kicad_pro` e escrito pelo pcbkit.regras (aSkipSettings=True)."""
    if not pcbnew.SaveBoard(str(caminho), board, True):
        raise RuntimeError(f"pcbnew nao conseguiu gravar {caminho}")


def camadas_de_cobre(board):
    return board.GetCopperLayerCount()


# --- footprints ------------------------------------------------------------------------

def carregar_footprint(amb, fp_id, projeto=None):
    """Footprint da biblioteca (tabela do projeto vence a global), com o FPID `Lib:Nome` certo:
    o FootprintLoad por pasta deixa o apelido da biblioteca vazio."""
    arq = bibliotecas.resolver_footprint(amb, fp_id, projeto)
    lib, nome = bibliotecas.separar_lib_id(fp_id)
    fp = pcbnew.FootprintLoad(str(arq.parent), nome)
    if fp is None:
        raise bibliotecas.ErroBiblioteca(f"pcbnew nao carregou {fp_id} ({arq})")
    fp.SetFPID(pcbnew.LIB_ID(lib, nome))
    return fp


def _campo_oculto(fp, nome, valor):
    fp.SetField(nome, valor)
    campo = fp.GetField(nome)
    campo.SetVisible(False)
    campo.SetLayer(pcbnew.F_Fab)


def _aplicar_campos(fp, comp):
    for nome, valor in comp["campos"].items():
        if nome in CAMPOS_FIXOS:
            continue
        if nome in ("Datasheet", "Description"):
            fp.GetField(nome).SetText(valor)
        else:
            _campo_oculto(fp, nome, valor)


def _ligar_pads(fp, ref, pinos, redes):
    for pad in fp.Pads():
        info = pinos.get((ref, pad.GetNumber()))
        if not info:
            continue
        pad.SetNet(redes[info["rede"]])
        pad.SetPinFunction(info["funcao"])
        pad.SetPinType(info["tipo"])


def _arquivo_folha(valor):
    """Sem .kicad_pro ao lado do esquematico a netlist traz o caminho absoluto: fica so o nome."""
    return PureWindowsPath(valor).name if PureWindowsPath(valor).is_absolute() or valor.startswith("/") else valor


def _propriedade_ligada(props, nome):
    """Propriedade presente na netlist liga a opcao (o DNP vem como `(property (name "dnp"))`)."""
    return nome in props and props[nome].strip().lower() not in ("0", "no", "false", "nao")


def aplicar_atributos(fp, props):
    """DNP, fora da BOM e fora do arquivo de posicao do simbolo passam para os atributos do footprint."""
    if _propriedade_ligada(props, "dnp"):
        fp.SetDNP(True)
    if _propriedade_ligada(props, "exclude_from_bom"):
        fp.SetExcludedFromBOM(True)
    if _propriedade_ligada(props, "exclude_from_pos_files"):
        fp.SetExcludedFromPosFiles(True)


def vias_termicas_cheias(fp):
    """Via termica de pad exposto (pad passante com o mesmo numero de um pad SMD do footprint, como
    nos `..._ThermalVias` oficiais) liga CHEIA na zona: a zona usa alivio em PTH e, sem isso, a via
    do pad exposto do driver perderia a dissipacao para o plano. Pad com ligacao propria (o ESP32 ja
    vem marcado) fica como esta. Devolve quantos pads mudaram."""
    smd = {p.GetNumber() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and p.GetNumber()}
    n = 0
    for p in fp.Pads():
        if (p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and p.GetNumber() in smd
                and p.GetLocalZoneConnection() == pcbnew.ZONE_CONNECTION_INHERITED):
            p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
            n += 1
    return n


def montar_footprint(board, amb, ref, comp, pinos, redes, projeto=None):
    """Footprint de um componente da netlist, ligado ao simbolo e as redes; ainda sem posicao."""
    fp = carregar_footprint(amb, comp["footprint"], projeto)
    vias_termicas_cheias(fp)
    fp.SetReference(ref)
    fp.SetValue(comp["valor"])
    _aplicar_campos(fp, comp)
    fp.SetPath(pcbnew.KIID_PATH(comp["caminho_folha"].rstrip("/") + "/" + comp["uuid"]))
    fp.SetSheetname(comp["folha"])
    fp.SetSheetfile(_arquivo_folha(comp["arquivo_folha"]))
    aplicar_atributos(fp, comp["propriedades"])
    _ligar_pads(fp, ref, pinos, redes)
    board.Add(fp)
    return fp


def criar_redes(board, nomes):
    """NETINFO_ITEM por nome (no 10 a rede e gravada pelo nome, sem tabela numerada)."""
    redes = {}
    for nome in sorted(nomes):
        net = board.FindNet(nome)
        if net is None:
            net = pcbnew.NETINFO_ITEM(board, nome)
            board.Add(net)
        redes[nome] = net
    return redes


def sincronizar_classes(board):
    """Aplica os netclass_patterns do .kicad_pro as redes criadas depois de abrir a placa."""
    board.SynchronizeNetsAndNetClasses(True)


# --- geometria para o posicionamento ----------------------------------------------------

def _caixa_mm(caixa):
    return tuple(pcbnew.ToMM(v) for v in (caixa.GetLeft(), caixa.GetTop(), caixa.GetRight(), caixa.GetBottom()))


def _exclusao(fp):
    """Contorno da area de regra que proibe footprints (antena de modulo de radio), ou None."""
    for z in fp.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowFootprints():
            return z.Outline()
    return None


def _courtyard(fp):
    fp.BuildCourtyardCaches()
    poli = fp.GetCourtyard(pcbnew.F_CrtYd)
    return poli if poli.OutlineCount() else fp.GetCourtyard(pcbnew.B_CrtYd)


def _centroide_pads(fp):
    lista = [p.GetPosition() for p in fp.Pads()] or [pcbnew.VECTOR2I(0, 0)]
    return (sum(pcbnew.ToMM(p.x) for p in lista) / len(lista), sum(pcbnew.ToMM(p.y) for p in lista) / len(lista))


def _com_referencia(caixa, fp):
    """Junta a caixa do texto de referencia visivel: assim a serigrafia de uma peca nao cai sobre a
    vizinha nem fora da placa."""
    ref = fp.Reference()
    if not ref.IsVisible():
        return caixa
    r = _caixa_mm(ref.GetBoundingBox())
    return (min(caixa[0], r[0]), min(caixa[1], r[1]), max(caixa[2], r[2]), max(caixa[3], r[3]))


def caixas_por_rotacao(fp):
    """Para cada rotacao (0, 90, 180, 270), relativos a origem do footprint, em mm: caixa de
    empacotamento (corpo + texto de referencia), corpo (courtyard sem a area de exclusao da antena, se
    houver; sem courtyard, o contorno sem texto), centroide dos pads e caixa da area de exclusao (ou
    None). Devolve (caixas, corpos, pads, exclusoes). Deixa o footprint na origem, rot 0."""
    caixas, corpos, pads, exclusoes = {}, {}, {}, {}
    for rot in (0, 90, 180, 270):
        fp.SetPosition(pcbnew.VECTOR2I(0, 0))
        fp.SetOrientationDegrees(rot)
        poli, excl = _courtyard(fp), _exclusao(fp)
        if poli.OutlineCount() and excl is not None:
            poli = pcbnew.SHAPE_POLY_SET(poli)
            poli.BooleanSubtract(excl)
            exclusoes[rot] = _caixa_mm(excl.BBox())
        corpos[rot] = _caixa_mm(poli.BBox() if poli.OutlineCount() else fp.GetBoundingBox(False))
        caixas[rot] = _com_referencia(corpos[rot], fp)
        pads[rot] = _centroide_pads(fp)
    fp.SetOrientationDegrees(0)
    return caixas, corpos, pads, (exclusoes or None)


def posicionar(fp, x, y, rot):
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(ponto(x, y))


# --- contorno, furos, zonas ------------------------------------------------------------

def contorno(board, largura, altura):
    r = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_RECTANGLE)
    r.SetStart(ponto(0, 0))
    r.SetEnd(ponto(largura, altura))
    r.SetLayer(pcbnew.Edge_Cuts)
    r.SetWidth(mm(LARGURA_CONTORNO))
    board.Add(r)
    return r


def furos(board, amb, posicoes, fp_id=FURO_M3):
    """Furos de fixacao H1..Hn: board only (fora da BOM, do arquivo de posicao e da paridade)."""
    saida = []
    for i, (x, y) in enumerate(posicoes, 1):
        fp = carregar_footprint(amb, fp_id)
        fp.SetReference(f"H{i}")
        fp.Reference().SetVisible(False)
        fp.SetBoardOnly(True)
        fp.SetExcludedFromBOM(True)
        posicionar(fp, x, y, 0)
        board.Add(fp)
        saida.append(fp)
    return saida


def _camadas_externas(board):
    return [pcbnew.F_Cu, pcbnew.B_Cu]


def zona(board, net, camada, largura, altura, prioridade=0):
    """Zona retangular do tamanho da placa. Modo "Reliefs for PTH" do KiCad (THT_THERMAL): alivio
    termico so em pad passante (borne e header soldaveis a mao e na onda num plano de 1 oz) e
    ligacao cheia em SMD (com alivio em SMD o roteamento automatico deixava raios bloqueados:
    `starved_thermal` em C9.2 e U3.7; o terra do driver e o pad exposto pedem ligacao cheia)."""
    z = pcbnew.ZONE(board)
    z.SetLayer(camada)
    z.SetNet(net)
    contorno_z = z.Outline()
    contorno_z.NewOutline()
    for x, y in ((0, 0), (largura, 0), (largura, altura), (0, altura)):
        contorno_z.Append(ponto(x, y))
    z.SetMinThickness(mm(ZONA_ESPESSURA_MIN))
    z.SetThermalReliefGap(mm(ZONA_ALIVIO_GAP))
    z.SetThermalReliefSpokeWidth(mm(ZONA_ALIVIO_RAIO))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
    z.SetAssignedPriority(prioridade)
    board.Add(z)
    return z


def zonas_gnd(board, net, largura, altura):
    """Uma zona da rede de terra em cada face externa, do tamanho da placa (a folga ate a borda
    vem da regra de borda); o preenchimento respeita as areas de regra dos footprints (antena)."""
    return [zona(board, net, c, largura, altura) for c in _camadas_externas(board)]


def preencher_zonas(board):
    zonas = board.Zones()
    if len(zonas):
        pcbnew.ZONE_FILLER(board).Fill(zonas)
