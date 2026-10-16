"""Verificacoes pelo kicad-cli: ERC, netlist contra a spec, DRC da placa e validade do .kicad_dru.

Uso:
  python verificar.py erc <placa.kicad_sch> [--relatorio erc.json] [--estrito] [--json]
  python verificar.py netlist <placa.kicad_sch> --spec <spec.json> [--projeto DIR] [--json]
  python verificar.py drc <placa.kicad_pcb> [--paridade] [--estrito] [--relatorio drc.json] [--json]
  python verificar.py dru <placa.kicad_dru> [--pro placa.kicad_pro] [--json]

erc      roda `kicad-cli sch erc --severity-all` e resume por tipo. Falha (1) com qualquer erro;
         aviso so falha com --estrito. Pronto para o portao = zero erros e avisos justificados.
netlist  exporta a netlist (kicadsexpr) e prova que cada rede da spec existe com EXATAMENTE os
         pinos declarados (REF.pino resolvido como no gerador); relata redes faltando, pinos
         sobrando/faltando, redes inesperadas e componentes/footprints divergentes.
drc      roda `kicad-cli pcb drc --severity-all --refill-zones` (a placa em disco nao muda) e
         resume por tipo, conexoes faltando por rede e por net class; `--paridade` acrescenta
         `--schematic-parity` (o .kicad_sch com o mesmo nome fica ao lado da placa). Falha (1) com
         qualquer erro, conexao faltando ou violacao de paridade de QUALQUER severidade (no KiCad
         10.0.0 footprint faltando e `warning`); os demais avisos so falham com --estrito.
dru      prova que o kicad-cli aceita o .kicad_dru (regra-canario: arquivo invalido e descartado em
         silencio pelo DRC). Usa o .kicad_pro de mesmo nome, se existir.

Saida: 0 ok; 1 violacao, divergencia ou .kicad_dru rejeitado; 2 uso errado, spec invalida ou KiCad ausente.
Os subcomandos ficam em SUBCOMANDOS: cada um e uma funcao `configurar_<nome>(subparsers)` que registra `func`.
"""

import argparse
import collections
import sys
import tempfile
from pathlib import Path

from pcbkit import ambiente, bibliotecas, console, drc, kicad_cli, netlist, regras
from pcbkit.esquematico import spec


# --- erc --------------------------------------------------------------------------

def _resumo_erc(rel):
    por_tipo = collections.Counter((v.get("type"), v.get("severity")) for v in rel.violacoes)
    return {"ok": rel.erros == 0, "erros": rel.erros, "avisos": rel.avisos,
            "por_tipo": [{"tipo": t, "severidade": s, "quantidade": n} for (t, s), n in sorted(por_tipo.items())],
            "violacoes": [{"tipo": v.get("type"), "severidade": v.get("severity"), "descricao": v.get("description"),
                           "itens": [i.get("description") for i in v.get("items", [])]} for v in rel.violacoes],
            "relatorio": str(rel.arquivo)}


def _imprimir_erc(r):
    print(f"ERC: {r['erros']} erro(s), {r['avisos']} aviso(s)")
    for t in r["por_tipo"]:
        print(f"  {t['quantidade']:>3} x {t['tipo']} ({t['severidade']})")
    for v in r["violacoes"]:
        print(f"  - [{v['severidade']}] {v['tipo']}: {v['descricao']}")
        for item in v["itens"]:
            print(f"      {item}")


def cmd_erc(amb, args):
    with tempfile.TemporaryDirectory(prefix="pcbkit-erc-") as tmp:
        saida = Path(args.relatorio) if args.relatorio else Path(tmp) / "erc.json"
        rel = kicad_cli.erc(amb, args.sch, saida=saida)
        r = _resumo_erc(rel)
        r["relatorio"] = args.relatorio
    falhou = r["erros"] > 0 or (args.estrito and r["avisos"] > 0)
    r["ok"] = not falhou
    console.imprimir_json(r) if args.json else _imprimir_erc(r)
    return 1 if falhou else 0


def configurar_erc(sub):
    p = sub.add_parser("erc", help="ERC do esquematico pelo kicad-cli")
    p.add_argument("sch", help="arquivo .kicad_sch")
    p.add_argument("--relatorio", help="grava o relatorio JSON do kicad-cli neste caminho")
    p.add_argument("--estrito", action="store_true", help="avisos tambem falham")
    p.set_defaults(func=cmd_erc)


# --- netlist ------------------------------------------------------------------------

def _resumo_netlist(d, circuito):
    return {"ok": d.ok, "redes_na_spec": len(circuito.redes), "redes_faltando": d.redes_faltando,
            "pinos_faltando": d.pinos_faltando, "pinos_sobrando": d.pinos_sobrando,
            "redes_inesperadas": d.redes_inesperadas, "componentes_faltando": d.componentes_faltando,
            "componentes_sobrando": d.componentes_sobrando,
            "footprints_diferentes": {k: {"spec": a, "netlist": b} for k, (a, b) in d.footprints_diferentes.items()}}


def _imprimir_netlist(r):
    if r["ok"]:
        print(f"Netlist bate com a spec: {r['redes_na_spec']} redes, cada uma com exatamente os pinos declarados.")
        return
    print("Netlist DIVERGE da spec:")
    for nome in r["redes_faltando"]:
        print(f"  - rede '{nome}' nao existe na netlist")
    for rotulo, chave in (("faltando", "pinos_faltando"), ("sobrando", "pinos_sobrando")):
        for nome, pinos in r[chave].items():
            print(f"  - rede '{nome}': pinos {rotulo}: {', '.join(pinos)}")
    for nome, pinos in r["redes_inesperadas"].items():
        print(f"  - rede inesperada '{nome}': {', '.join(pinos)}")
    for ref in r["componentes_faltando"]:
        print(f"  - componente {ref} da spec nao esta no esquematico")
    for ref in r["componentes_sobrando"]:
        print(f"  - componente {ref} esta no esquematico e nao na spec")
    for ref, fp in r["footprints_diferentes"].items():
        print(f"  - {ref}: footprint na spec '{fp['spec']}', no esquematico '{fp['netlist']}'")


def cmd_netlist(amb, args):
    projeto = spec.pasta_projeto(args.sch, args.projeto)
    try:
        circuito = spec.carregar(args.spec, amb, projeto)
    except spec.ErroSpec as e:
        return console.erro("spec invalida: " + "; ".join(e.erros), 2)
    with tempfile.TemporaryDirectory(prefix="pcbkit-net-") as tmp:
        arq = kicad_cli.exportar_netlist(amb, args.sch, Path(tmp) / "placa.net")
        d = netlist.comparar(circuito, netlist.ler(arq))
    r = _resumo_netlist(d, circuito)
    console.imprimir_json(r) if args.json else _imprimir_netlist(r)
    return 0 if d.ok else 1


def configurar_netlist(sub):
    p = sub.add_parser("netlist", help="netlist exportada contra a spec")
    p.add_argument("sch", help="arquivo .kicad_sch")
    p.add_argument("--spec", required=True, help="spec do circuito (JSON)")
    p.add_argument("--projeto", help="pasta com sym-lib-table/fp-lib-table do projeto")
    p.set_defaults(func=cmd_netlist)


# --- drc ------------------------------------------------------------------------------

def _dados_pro(pcb):
    pro = Path(pcb).with_suffix(".kicad_pro")
    try:
        return regras.ler_pro(pro) if pro.is_file() else None
    except ValueError:
        return None


def _imprimir_drc(r):
    print(f"DRC: {r['erros']} erro(s), {r['avisos']} aviso(s), {r['desconectados']} conexao(oes) faltando"
          + ("" if r["paridade_conferida"] else " (sem paridade com o esquematico)"))
    for t in r["por_tipo"]:
        print(f"  {t['quantidade']:>3} x {t['tipo']} ({t['severidade']})")
    if r["desconectados"]:
        print("  conexoes faltando por net class: "
              + ", ".join(f"{c} {n}" for c, n in r["desconectados_por_classe"].items()))
        print("  por rede: " + ", ".join(f"{rede} {n}" for rede, n in r["desconectados_por_rede"].items()))
    for v in r["paridade"] + r["violacoes"]:
        print(f"  - [{v['severidade']}] {v['tipo']}: {v['descricao']}")
        for item in v["itens"]:
            print(f"      {item}")


def cmd_drc(amb, args):
    with tempfile.TemporaryDirectory(prefix="pcbkit-drc-") as tmp:
        saida = Path(args.relatorio) if args.relatorio else Path(tmp) / "drc.json"
        rel = kicad_cli.drc(amb, args.pcb, saida=saida, paridade=args.paridade, reencher_zonas=True)
        r = drc.resumir(rel, _dados_pro(args.pcb))
    r.update({"relatorio": args.relatorio, "paridade_conferida": args.paridade})
    falhou = drc.reprova(r, estrito=args.estrito)
    r["ok"] = not falhou
    console.imprimir_json(r) if args.json else _imprimir_drc(r)
    return 1 if falhou else 0


def configurar_drc(sub):
    p = sub.add_parser("drc", help="DRC da placa pelo kicad-cli (zonas reenchidas)")
    p.add_argument("pcb", help="arquivo .kicad_pcb")
    p.add_argument("--paridade", action="store_true", help="confere a paridade com o esquematico (--schematic-parity)")
    p.add_argument("--relatorio", help="grava o relatorio JSON do kicad-cli neste caminho")
    p.add_argument("--estrito", action="store_true", help="avisos tambem falham")
    p.set_defaults(func=cmd_drc)


# --- dru ------------------------------------------------------------------------------

def cmd_dru(amb, args):
    pro = Path(args.pro) if args.pro else Path(args.dru).with_suffix(".kicad_pro")
    ok, mensagem = kicad_cli.validar_dru(amb, args.dru, pro if pro.is_file() else None)
    r = {"ok": ok, "arquivo": args.dru, "pro": str(pro) if pro.is_file() else None, "mensagem": mensagem}
    if args.json:
        console.imprimir_json(r)
    else:
        print(f"{'OK' if ok else 'REJEITADO'}: {args.dru}: {mensagem}")
    return 0 if ok else 1


def configurar_dru(sub):
    p = sub.add_parser("dru", help="o kicad-cli aceita este .kicad_dru? (regra-canario)")
    p.add_argument("dru", help="arquivo .kicad_dru")
    p.add_argument("--pro", help=".kicad_pro a usar junto (padrao: o de mesmo nome, se existir)")
    p.set_defaults(func=cmd_dru)


# --- principal ------------------------------------------------------------------------

SUBCOMANDOS = [configurar_erc, configurar_netlist, configurar_drc, configurar_dru]


def _args(argv):
    p = argparse.ArgumentParser(description="ERC, netlist, DRC e .kicad_dru pelo kicad-cli.")
    comum = argparse.ArgumentParser(add_help=False)
    comum.add_argument("--json", action="store_true", help="saida em JSON")
    sub = p.add_subparsers(dest="comando", required=True)
    sub_com_json = _ComJson(sub, comum)
    for configurar in SUBCOMANDOS:
        configurar(sub_com_json)
    return p.parse_args(argv)


class _ComJson:
    """Repassa add_parser acrescentando o --json comum a todo subcomando."""

    def __init__(self, sub, comum):
        self.sub, self.comum = sub, comum

    def add_parser(self, nome, **kw):
        return self.sub.add_parser(nome, parents=[self.comum], **kw)


def main(argv=None):
    console.configurar()
    args = _args(argv)
    amb = ambiente.detectar()
    if not amb.encontrado:
        return console.erro("kicad-cli nao encontrado; rode diagnostico.py", 2)
    alvo = getattr(args, "sch", None) or getattr(args, "pcb", None) or getattr(args, "dru", None)
    if alvo and not Path(alvo).is_file():
        return console.erro(f"arquivo nao encontrado: {alvo}", 2)
    try:
        return args.func(amb, args)
    except (kicad_cli.ErroKicadCli, bibliotecas.ErroBiblioteca) as e:
        return console.erro(str(e), 2)


if __name__ == "__main__":
    sys.exit(main())
