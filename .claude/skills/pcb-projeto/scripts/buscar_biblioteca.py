"""Busca simbolos e footprints nas bibliotecas do KiCad (instaladas + do projeto).

Uso:
  python buscar_biblioteca.py simbolo <termo>          [--projeto DIR] [--limite N] [--json]
  python buscar_biblioteca.py footprint <termo>        [--projeto DIR] [--limite N] [--json]
  python buscar_biblioteca.py pinos <Lib:Simbolo>      [--projeto DIR] [--json]
  python buscar_biblioteca.py pads <Lib:Footprint>     [--projeto DIR] [--json]

O termo casa com o nome (melhor nota), depois com descricao e palavras-chave. Varias palavras
precisam casar todas. Saida: 0 achou, 1 nada encontrado, 2 uso errado ou KiCad ausente.
"""

import argparse
import sys

from pcbkit import ambiente, bibliotecas, console


def _args(argv):
    p = argparse.ArgumentParser(description="Busca nas bibliotecas do KiCad.")
    p.add_argument("modo", choices=["simbolo", "footprint", "pinos", "pads"])
    p.add_argument("termo", help="texto de busca, ou Lib:Nome para pinos/pads")
    p.add_argument("--projeto", help="pasta do projeto (usa as sym-lib-table/fp-lib-table dele)")
    p.add_argument("--limite", type=int, default=20, help="maximo de resultados (0 = todos)")
    p.add_argument("--json", action="store_true", help="saida em JSON")
    return p.parse_args(argv)


def _achados(amb, args):
    busca = bibliotecas.buscar_simbolos if args.modo == "simbolo" else bibliotecas.buscar_footprints
    achados = busca(amb, args.termo, args.projeto, args.limite)
    if args.json:
        console.imprimir_json([{"lib_id": a.lib_id, "descricao": a.descricao, "palavras": a.palavras,
                                "arquivo": a.caminho, "nota": a.nota} for a in achados])
    else:
        for a in achados:
            print(f"{a.lib_id:<55} {a.descricao[:90]}")
        if not achados:
            print(f"Nada encontrado para '{args.termo}'.")
    return 0 if achados else 1


def _pinos(amb, args):
    s = bibliotecas.carregar_simbolo(amb, args.termo, args.projeto)
    if args.json:
        console.imprimir_json({"lib_id": s.lib_id, "extends": s.extends, "unidades": s.unidades,
                               "power": s.power, "propriedades": s.propriedades, "pinos": s.pinos})
        return 0
    print(f"{s.lib_id}  unidades={s.unidades}  power={'sim' if s.power else 'nao'}"
          + (f"  (deriva de {s.extends})" if s.extends else ""))
    print(f"  Footprint sugerido: {s.propriedades.get('Footprint') or '-'}")
    print(f"  Filtro de footprint: {s.propriedades.get('ki_fp_filters') or '-'}")
    print(f"  {'num':<6}{'nome':<20}{'tipo':<15}{'un':<4}{'x':>8}{'y':>8}{'ang':>6}{'comp':>7}")
    for p in sorted(s.pinos, key=lambda p: (p.unidade, p.corpo, _ordem(p.numero))):
        if p.corpo != 1:
            continue
        print(f"  {p.numero:<6}{p.nome[:19]:<20}{p.tipo:<15}{p.unidade:<4}{p.x:>8.2f}{p.y:>8.2f}"
              f"{p.angulo:>6.0f}{p.comprimento:>7.2f}" + ("  (oculto)" if p.oculto else ""))
    return 0


def _pads(amb, args):
    caminho = bibliotecas.resolver_footprint(amb, args.termo, args.projeto)
    pads = bibliotecas.pads_footprint(caminho)
    if args.json:
        console.imprimir_json({"fp_id": args.termo, "arquivo": caminho, "pads": pads})
    else:
        print(f"{args.termo}  ({len(pads)} pads)\n  {' '.join(pads)}")
    return 0


def _ordem(numero):
    return (0, int(numero), "") if numero.isdigit() else (1, 0, numero)


def main(argv=None):
    console.configurar()
    args = _args(argv)
    amb = ambiente.detectar()
    if not amb.share:
        return console.erro("bibliotecas do KiCad nao encontradas; rode diagnostico.py", 2)
    try:
        if args.modo in ("simbolo", "footprint"):
            return _achados(amb, args)
        return _pinos(amb, args) if args.modo == "pinos" else _pads(amb, args)
    except bibliotecas.ErroBiblioteca as e:
        return console.erro(str(e), 1)


if __name__ == "__main__":
    sys.exit(main())
