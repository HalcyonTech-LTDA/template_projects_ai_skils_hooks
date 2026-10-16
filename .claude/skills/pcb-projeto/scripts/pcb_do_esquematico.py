"""Placa (.kicad_pcb) a partir do esquematico e da spec. Roda SO no Python do KiCad (pcbnew).

Uso:
  "<KiCad>/bin/python.exe" pcb_do_esquematico.py <placa.kicad_sch> --spec <spec.json> -o <placa.kicad_pcb>
      [--largura MM --altura MM] [--furos M3|nenhum] [--projeto DIR] [--sobrescrever] [--json]

1. Exporta a netlist com o kicad-cli (a netlist manda: footprints, uuids, redes).
2. Escreve no `.kicad_pro` vizinho as net classes da spec (`classes_de_rede`: largura, clearance e
   um `netclass_patterns` por rede, com o nome como a placa o ve: `/REDE` para label local, `REDE`
   para simbolo de power). `.kicad_pro`/`.kicad_dru` ausentes: avisa e copia os modelos de assets/kicad/.
3. Footprints ligados aos simbolos (path = uuid do simbolo), redes nos pads, posicionamento por
   bloco da spec (ver pcbkit/swig/posicionamento.py), contorno retangular, furos M3 nos cantos,
   zonas de GND em F.Cu e B.Cu, zonas preenchidas.

O posicionamento e ponto de partida para revisao humana, nao layout final.
A placa de destino precisa estar vazia (so o cabecalho que o `novo_projeto.py` cria): qualquer item
nela (footprint, trilha, via, zona, desenho em Edge.Cuts, texto) exige --sobrescrever, que a refaz do
zero e perde tudo isso.
Saida: 0 placa gravada; 1 spec invalida, pecas nao cabem ou placa ja tem itens (use --sobrescrever);
2 uso errado, KiCad ausente ou fora do Python do KiCad.
"""

import argparse
import datetime
import sys
import tempfile
from pathlib import Path

from pcbkit import ambiente, bibliotecas, console, kicad_cli, modelos, netlist, regras, sexpr
from pcbkit.esquematico import spec
from pcbkit.swig import ErroSwig
from pcbkit.swig import posicionamento as pos

REDE_TERRA = "GND"
# Nos de nivel superior do .kicad_pcb que nao sao item de layout: o resto (footprint, segment, arc, via,
# zone, gr_*, text, dimension, group...) conta como trabalho que --sobrescrever apagaria.
CABECALHO_PLACA = {"version", "generator", "generator_version", "general", "paper", "page", "title_block",
                   "layers", "setup", "net", "net_class", "property", "embedded_fonts", "embedded_files", "uuid"}
ROTULO_ITEM = {"footprint": "footprint(s)", "segment": "trilha(s)", "arc": "trilha(s) em arco", "via": "via(s)",
               "zone": "zona(s)", "gr_line": "linha(s) de desenho", "gr_arc": "arco(s) de desenho",
               "gr_rect": "retangulo(s) de desenho", "gr_circle": "circulo(s) de desenho",
               "gr_poly": "poligono(s) de desenho"}


def _args(argv):
    p = argparse.ArgumentParser(description="Placa KiCad a partir do esquematico e da spec (Python do KiCad).")
    p.add_argument("sch", help="esquematico .kicad_sch")
    p.add_argument("--spec", required=True, help="spec do circuito (JSON): blocos e classes de rede")
    p.add_argument("-o", "--saida", required=True, help="placa .kicad_pcb a gravar")
    p.add_argument("--largura", type=float, help="largura da placa em mm (sem ela, o tamanho e automatico)")
    p.add_argument("--altura", type=float, help="altura da placa em mm")
    p.add_argument("--furos", choices=("M3", "nenhum"), default="M3", help="furos de fixacao nos cantos")
    p.add_argument("--projeto", help="pasta com sym-lib-table/fp-lib-table (padrao: a do esquematico)")
    p.add_argument("--sobrescrever", action="store_true", help="refaz a placa mesmo que ja tenha itens (footprints, trilhas, contorno...)")
    p.add_argument("--json", action="store_true", help="saida em JSON")
    args = p.parse_args(argv)
    if (args.largura is None) != (args.altura is None):
        p.error("--largura e --altura andam juntas")
    return args


# --- etapas puras -------------------------------------------------------------------------

def _camadas_do_arquivo(pcb):
    """Camadas de cobre de uma placa existente (a do novo_projeto); 2 se o arquivo nao existe."""
    if not Path(pcb).is_file():
        return 2
    camadas = sexpr.filho(sexpr.carregar_arquivo(pcb), "layers") or []
    return sum(1 for c in camadas[1:] if isinstance(c, list) and len(c) > 1 and str(c[1]).endswith(".Cu")) or 2


def itens_da_placa(pcb):
    """{etiqueta: quantidade} do que a placa existente tem alem do cabecalho: footprints, trilhas (segment,
    arc), vias, zonas, desenhos (gr_*), textos, dimensoes, grupos... Placa ausente ou so cabecalho: {}."""
    if not Path(pcb).is_file():
        return {}
    itens = {}
    for no in sexpr.carregar_arquivo(pcb):
        etiqueta = sexpr.etiqueta(no) if isinstance(no, list) else None
        if etiqueta and etiqueta not in CABECALHO_PLACA:
            itens[etiqueta] = itens.get(etiqueta, 0) + 1
    return itens


def _descrever_itens(itens):
    return ", ".join(f"{n} {ROTULO_ITEM.get(e, e)}" for e, n in sorted(itens.items()))


def _exportar_netlist(amb, sch):
    with tempfile.TemporaryDirectory(prefix="pcbkit-pcb-") as tmp:
        return netlist.ler(kicad_cli.exportar_netlist(amb, sch, Path(tmp) / "placa.net"))


def _conferir_spec(circuito, nl):
    avisos = []
    for ref in sorted(set(nl.componentes) - set(circuito.componentes)):
        avisos.append(f"{ref} esta no esquematico e nao na spec: vai para o bloco 'outros'")
    for ref in sorted(set(circuito.componentes) - set(nl.componentes)):
        avisos.append(f"{ref} esta na spec e nao no esquematico: fica fora da placa (o esquematico manda)")
    for ref, comp in circuito.componentes.items():
        achado = nl.componentes.get(ref)
        if achado and achado["footprint"] != comp.footprint:
            avisos.append(f"{ref}: footprint da spec '{comp.footprint}' difere do esquematico "
                          f"'{achado['footprint']}'; vale o do esquematico")
    return avisos


def _escrever_classes(pcb, circuito, nl, camadas):
    avisos = regras.garantir_arquivos(pcb, camadas)
    pro, _ = regras.caminhos(pcb)
    dados = regras.ler_pro(pro)
    atribuicoes, mais = regras.aplicar_classes(dados, circuito.dados.get("classes_de_rede"),
                                                lambda r: netlist.nome_na_placa(nl, r))
    regras.gravar_pro(pro, dados)
    return atribuicoes, avisos + mais


def _rede_terra(nl):
    return netlist.nome_na_placa(nl, REDE_TERRA)


def _redes_por_ref(nl):
    por_ref, tamanho = {}, {}
    for (ref, _), info in nl.pinos.items():
        por_ref.setdefault(ref, set()).add(info["rede"])
    for nome, pinos in nl.redes.items():
        tamanho[nome] = len(pinos)
    return pos.redes_de_sinal(por_ref, tamanho)


# --- montagem (SWIG) -----------------------------------------------------------------------

def _placa_vazia(pcb, circuito, camadas):
    """Regrava a placa vazia (mesmo numero de camadas) antes de montar: tirar itens de uma placa
    aberta pelo SWIG deixa objetos orfaos e quebra o FootprintLoad seguinte (visto no 10.0.0)."""
    d = circuito.dados
    sexpr.salvar_arquivo(pcb, modelos.placa_vazia(camadas, d.get("titulo", ""), datetime.date.today().isoformat(),
                                                  d.get("revisao", ""), d.get("empresa", "")))


def _footprints(placa, board, amb, nl, projeto):
    redes = placa.criar_redes(board, nl.redes.keys())
    fps, avisos = {}, []
    for ref in sorted(nl.componentes):
        comp = nl.componentes[ref]
        if not comp["footprint"]:
            avisos.append(f"{ref} nao tem footprint no esquematico: fora da placa")
            continue
        fps[ref] = placa.montar_footprint(board, amb, ref, comp, nl.pinos, redes, projeto)
    placa.sincronizar_classes(board)
    return fps, redes, avisos


def _pecas(placa, fps, circuito, nl):
    redes = _redes_por_ref(nl)
    pecas = []
    for ref, fp in fps.items():
        caixas, corpos, pads, exclusao = placa.caixas_por_rotacao(fp)
        comp = circuito.componentes.get(ref)
        pecas.append(pos.Peca(ref, comp.bloco if comp else "outros", caixas, pads, pos.eh_conector(ref),
                              redes.get(ref, frozenset()), exclusao, corpos))
    return pecas


def _montar(placa, board, amb, circuito, nl, args, projeto):
    fps, redes, avisos = _footprints(placa, board, amb, nl, projeto)
    res = pos.posicionar(_pecas(placa, fps, circuito, nl), [b.id for b in circuito.blocos],
                         args.largura, args.altura, furos=args.furos != "nenhum")
    for ref, p in res.posicoes.items():
        placa.posicionar(fps[ref], p.x, p.y, p.rotacao)
    placa.contorno(board, res.largura, res.altura)
    placa.furos(board, amb, res.furos)
    terra = _rede_terra(nl)
    if terra:
        placa.zonas_gnd(board, redes[terra], res.largura, res.altura)
    else:
        avisos.append(f"rede '{REDE_TERRA}' nao existe: placa sem zonas de terra")
    placa.preencher_zonas(board)
    return res, avisos


def _conferir_classes(board, atribuicoes):
    """O KiCad carregou o .kicad_pro? Cada rede atribuida deve sair com a classe certa."""
    erradas = []
    for rede, classe in atribuicoes.items():
        net = board.FindNet(rede)
        if net is not None and net.GetNetClassName() != classe:
            erradas.append(f"{rede}: esperava '{classe}', a placa diz '{net.GetNetClassName()}'")
    return erradas


# --- saida ---------------------------------------------------------------------------------

def _resumo(pcb, res, nl, atribuicoes, avisos):
    return {"ok": True, "placa": str(pcb), "largura_mm": res.largura, "altura_mm": res.altura,
            "footprints": len(res.posicoes), "furos": len(res.furos), "redes": len(nl.redes),
            "blocos": {b: [round(v, 2) for v in r] for b, r in res.blocos.items()},
            "conectores": res.bordas, "classes": atribuicoes, "avisos": avisos}


def _imprimir(r):
    print(f"Placa gravada: {r['placa']}")
    print(f"  {r['largura_mm']:g} x {r['altura_mm']:g} mm, {r['footprints']} footprints, {r['furos']} furos, "
          f"{r['redes']} redes")
    for b, (x0, y0, x1, y1) in r["blocos"].items():
        print(f"  bloco {b:<12} x {x0:6.1f}..{x1:6.1f}  y {y0:6.1f}..{y1:6.1f} mm")
    for ref, borda in sorted(r["conectores"].items()):
        print(f"  {ref} na borda {borda}")
    for rede, classe in sorted(r["classes"].items()):
        print(f"  classe {classe}: {rede}")
    for a in r["avisos"]:
        print(f"AVISO: {a}")
    print("Posicionamento e ponto de partida: revise (render) antes de rotear.")
    print(f'  kicad-cli pcb render --side top -o top.png "{r["placa"]}"')
    print(f'  python verificar.py drc "{r["placa"]}" --paridade')


def executar(amb, args, placa):
    projeto = spec.pasta_projeto(args.sch, args.projeto)
    circuito = spec.carregar(args.spec, amb, projeto)
    pcb = Path(args.saida)
    itens = itens_da_placa(pcb)
    if itens and not args.sobrescrever:
        return console.erro(f"{pcb} ja tem itens ({_descrever_itens(itens)}); use --sobrescrever para refazer "
                            f"(trilhas, contorno e desenhos se perdem)", 1)
    nl = _exportar_netlist(amb, args.sch)
    camadas = _camadas_do_arquivo(pcb)
    atribuicoes, avisos = _escrever_classes(pcb, circuito, nl, camadas)
    avisos = _conferir_spec(circuito, nl) + avisos
    _placa_vazia(pcb, circuito, camadas)
    board = placa.carregar(pcb)
    res, mais = _montar(placa, board, amb, circuito, nl, args, projeto)
    avisos += mais + [f"net class nao aplicada pelo KiCad: {e}" for e in _conferir_classes(board, atribuicoes)]
    placa.salvar(board, pcb)
    r = _resumo(pcb, res, nl, atribuicoes, avisos)
    console.imprimir_json(r) if args.json else _imprimir(r)
    return 0


def main(argv=None):
    console.configurar()
    args = _args(argv)
    try:
        from pcbkit.swig import placa
    except ErroSwig as e:
        return console.erro(str(e), 2)
    amb = ambiente.detectar()
    if not amb.encontrado:
        return console.erro("kicad-cli nao encontrado; rode diagnostico.py", 2)
    for arq in (args.sch, args.spec):
        if not Path(arq).is_file():
            return console.erro(f"arquivo nao encontrado: {arq}", 2)
    try:
        return executar(amb, args, placa)
    except spec.ErroSpec as e:
        return console.erro("spec invalida: " + "; ".join(e.erros), 1)
    except pos.ErroPosicionamento as e:
        return console.erro(str(e), 1)
    except (kicad_cli.ErroKicadCli, bibliotecas.ErroBiblioteca) as e:
        return console.erro(str(e), 2)


if __name__ == "__main__":
    sys.exit(main())
