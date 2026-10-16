"""Gera o esquematico (.kicad_sch) a partir da spec JSON do circuito.

Uso:
  python gerar_esquematico.py <spec.json> -o <placa>.kicad_sch [--projeto DIR] [--sobrescrever] [--json]

Estilo label por pino: cada pino ganha um fio curto terminado num label local ou num simbolo de
power; pinos em `nao_conectar` ganham o X de nao conectado. Componentes agrupados por bloco.

A spec e validada inteira antes de escrever: ref duplicada, componente fora de bloco ou em dois,
simbolo/footprint inexistente, pino inexistente, rede com um pino so, pino em duas redes e pino sem
rede fora de `nao_conectar` fazem o gerador FALHAR listando todos os problemas.

`--projeto` aponta a pasta com sym-lib-table/fp-lib-table do projeto (padrao: a pasta da saida,
se tiver uma das tabelas). O nome do projeto nas instancias e o nome do arquivo de saida.

Recusa sobrescrever um `.kicad_sch` cujo `generator` nao seja "pcbkit" (o KiCad grava "eeschema" ao
salvar na GUI): o esquematico passou ao modo manual e regerar apaga a edicao. `--sobrescrever` forca.
Saida: 0 gerado; 1 spec invalida ou saida salva pela GUI; 2 uso errado ou KiCad ausente.
"""

import argparse
import sys

from pcbkit import ambiente, bibliotecas, console
from pcbkit.esquematico import ErroSobrescrita, gerar, spec


def _args(argv):
    p = argparse.ArgumentParser(description="Gera o .kicad_sch a partir da spec JSON.")
    p.add_argument("spec", help="spec do circuito (JSON)")
    p.add_argument("-o", "--saida", required=True, help="arquivo .kicad_sch de saida")
    p.add_argument("--projeto", help="pasta com sym-lib-table/fp-lib-table do projeto")
    p.add_argument("--sobrescrever", action="store_true",
                   help="regrava mesmo que o .kicad_sch tenha sido salvo pela GUI (descarta a edicao)")
    p.add_argument("--json", action="store_true", help="resumo em JSON")
    return p.parse_args(argv)


def _resumo(circuito, desenho, saida, avisos):
    return {"arquivo": str(saida), "componentes": len(circuito.componentes), "redes": len(circuito.redes),
            "blocos": len(circuito.blocos), "power": sorted(n for n, r in circuito.redes.items() if r.power),
            "labels": sorted(n for n, r in circuito.redes.items() if not r.power),
            "nao_conectar": len(circuito.nao_conectar), "avisos": avisos}


def _imprimir(r):
    print(f"Esquematico gerado: {r['arquivo']}")
    print(f"  {r['componentes']} componentes em {r['blocos']} blocos, {r['redes']} redes "
          f"({len(r['power'])} com simbolo de power), {r['nao_conectar']} pinos nao conectados")
    for a in r["avisos"]:
        print(f"  AVISO: {a}")
    print("Proximo passo: verificar.py erc <sch> e verificar.py netlist <sch> --spec <spec>")


def _falha_spec(e, como_json):
    if como_json:
        console.imprimir_json({"ok": False, "erros": e.erros})
    else:
        print(f"ERRO: a spec tem {len(e.erros)} problema(s); nada foi gerado:", file=sys.stderr)
        for m in e.erros:
            print(f"  - {m}", file=sys.stderr)
    return 1


def main(argv=None):
    console.configurar()
    args = _args(argv)
    if not args.saida.endswith(".kicad_sch"):
        return console.erro("a saida deve terminar em .kicad_sch", 2)
    amb = ambiente.detectar()
    if not amb.share:
        return console.erro("bibliotecas do KiCad nao encontradas; rode diagnostico.py", 2)
    projeto = spec.pasta_projeto(args.saida, args.projeto)
    try:
        circuito = spec.carregar(args.spec, amb, projeto)
        desenho, avisos = gerar(circuito, amb, args.saida, projeto, sobrescrever=args.sobrescrever)
    except spec.ErroSpec as e:
        return _falha_spec(e, args.json)
    except ErroSobrescrita as e:
        return console.erro(str(e), 1)
    except bibliotecas.ErroBiblioteca as e:
        return console.erro(str(e), 2)
    r = _resumo(circuito, desenho, args.saida, avisos)
    console.imprimir_json(dict(r, ok=True)) if args.json else _imprimir(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
