"""Pacote de fabricacao de uma placa KiCad 10 para a JLCPCB e, com --liberar, a release congelada.

Uso:
  python exportar_fab.py <dir-projeto> [--rev A] [--saida <dir>] [--json]
  python exportar_fab.py <dir-projeto> --rev A --liberar --checklist <nota> [--aprovacao-hv <nota>] [--json]

Sem --liberar: escreve em <dir-projeto>/fab/rev-<R>/ (ou --saida, nunca dentro de releases/) o zip
Gerber+furacao, BOM e CPL da JLC, BOM completa, PDF do esquematico, mapas de furo (PDF), STEP, render
top/bottom e manifesto.json.
Com --liberar: recusa se <dir-projeto>/releases/rev-<R>/ ja existe; roda o portao
(portao_liberacao.py) e, so se passar, gera o pacote e copia zip, BOM JLC, CPL JLC, BOM completa e
PDF para releases/rev-<R>/ com manifesto.json (SHA-256, versao do KiCad, data, comandos, portao com
revisores, avisos de DRC, severidades rebaixadas e exclusoes). A revisao precisa ser a da spec.

Saida: 0 ok; 1 portao bloqueou, release ja existe ou exportacao falhou; 2 uso errado ou KiCad ausente.
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

import portao_liberacao
from pcbkit import ambiente, console, kicad_cli, portao, projeto
from pcbkit.fab import manifesto, pacote

REV = re.compile(r"^[A-Z][A-Z0-9]*$")


def _args(argv):
    p = argparse.ArgumentParser(description="Pacote de fabricacao (JLCPCB) e liberacao da revisao.")
    p.add_argument("projeto", help="pasta da placa (hardware/<placa>)")
    p.add_argument("--rev", default="A", help="revisao (letra maiuscula; padrao A)")
    p.add_argument("--saida", help="pasta do pacote de trabalho (padrao: <projeto>/fab/rev-<R>)")
    p.add_argument("--liberar", action="store_true", help="roda o portao e grava releases/rev-<R>/")
    p.add_argument("--checklist", help="nota de liberacao (obrigatoria com --liberar)")
    p.add_argument("--aprovacao-hv", help="nota de aprovacao de alta tensao (padrao: ao lado da nota de liberacao)")
    p.add_argument("--json", action="store_true", help="saida em JSON")
    return p.parse_args(argv)


def _validar(args):
    if not REV.match(args.rev):
        return f"revisao invalida '{args.rev}': use letra maiuscula (A, B, ...)"
    if args.liberar and not args.checklist:
        return "--liberar exige --checklist <nota de liberacao>"
    return None


def _rel(caminho, base):
    try:
        return Path(os.path.relpath(Path(caminho).resolve(), base)).as_posix()
    except ValueError:                      # outro disco no Windows
        return str(Path(caminho).resolve())


def _dados_portao(res, proj, args):
    lib = next((v for v in res.verificacoes if v.nome == "nota de liberacao"), None)
    hv = next((v for v in res.verificacoes if v.nome == "nota de aprovacao de alta tensao"), None)
    return {"portao": {"checklist": _rel(args.checklist, proj.dir),
                       "revisores": lib.detalhes.get("revisores", []) if lib else [],
                       "aprovacao_hv": _rel(hv.detalhes["nota"], proj.dir) if hv else None,
                       "alta_tensao": res.alta_tensao,
                       "avisos_drc": [f"{a['tipo']}: {a['descricao']}" for a in res.avisos_drc],
                       "severidades_rebaixadas": res.severidades.get("rebaixadas", []),
                       "exclusoes_drc": res.severidades.get("exclusoes_drc", []),
                       "exclusoes_erc": res.severidades.get("exclusoes_erc", [])}}


def _manifesto(pasta, proj, rev, arquivos, versao, comandos, extra=None):
    dados = manifesto.montar(proj.placa, rev, arquivos, versao, comandos, extra)
    return manifesto.gravar(pasta, dados)


def liberar(r, proj, rev, versao, extra):
    """Copia o conjunto de fabricacao para releases/rev-<R>/ (pasta parcial renomeada no fim)."""
    destino = proj.dir / "releases" / f"rev-{rev}"
    parcial = destino.with_name(f".rev-{rev}-parcial")
    shutil.rmtree(parcial, ignore_errors=True)
    parcial.mkdir(parents=True)
    try:
        copiados = [Path(shutil.copy2(r.arquivos[t], parcial)) for t in pacote.TIPOS_RELEASE]
        _manifesto(parcial, proj, rev, copiados, versao, r.comandos, extra)
        parcial.rename(destino)
    except BaseException:
        shutil.rmtree(parcial, ignore_errors=True)
        raise
    return destino


def _arquivos(pasta):
    return [{"arquivo": a.name, "bytes": a.stat().st_size} for a in sorted(Path(pasta).iterdir()) if a.is_file()]


def _imprimir(saida):
    print(f"Pacote de fabricacao: {saida['placa']} rev {saida['revisao']} ({saida['camadas_cobre']} camadas)")
    print(f"  em {saida['fab']}")
    for a in saida["arquivos_fab"]:
        print(f"    {a['bytes']:>10}  {a['arquivo']}")
    print(f"  componentes montados: {saida['montados']}; montados pela JLC (BOM/CPL): {saida['montados_jlc']}")
    for aviso in saida["avisos"]:
        print(f"  AVISO: {aviso}")
    if saida.get("release"):
        print(f"  Release gravada em {saida['release']}")
        for a in saida["arquivos_release"]:
            print(f"    {a['bytes']:>10}  {a['arquivo']}")


def _resposta(r, proj, rev, release):
    return {"ok": True, "placa": proj.placa, "revisao": rev, "fab": str(r.saida),
            "camadas_cobre": sum(c.endswith(".Cu") for c in r.camadas), "arquivos_fab": _arquivos(r.saida),
            "montados": r.componentes_montados, "montados_jlc": r.componentes_jlc, "avisos": r.avisos,
            "release": str(release) if release else None,
            "arquivos_release": _arquivos(release) if release else []}


def _portao(amb, proj, args):
    res = portao.rodar(amb, proj, args.checklist, args.aprovacao_hv, args.rev)
    if not res.ok:
        console.imprimir_json(portao.resumo(res)) if args.json else portao_liberacao.imprimir(res)
    return res


def pasta_de_trabalho(proj, rev, saida=None):
    """Pasta do pacote de trabalho. Dentro de releases/ e recusada: la so entra o que passou no portao."""
    pasta = Path(saida) if saida else proj.dir / "fab" / f"rev-{rev}"
    releases = (proj.dir / "releases").resolve()
    alvo = pasta.resolve()
    if alvo == releases or releases in alvo.parents:
        raise projeto.ErroProjeto(f"--saida {pasta} fica dentro de releases/: o pacote de trabalho vai para fab/ "
                                  "(ou outra pasta fora de releases/); a release so e gravada por --liberar")
    return pasta


def executar(amb, args):
    proj = projeto.localizar(args.projeto)
    saida = pasta_de_trabalho(proj, args.rev, args.saida)
    release = proj.dir / "releases" / f"rev-{args.rev}"
    if args.liberar and release.exists():
        return console.erro(f"{release} ja existe: revisao liberada e congelada (abra a revisao seguinte)", 1)
    res = _portao(amb, proj, args) if args.liberar else None
    if res is not None and not res.ok:
        return 1
    r = pacote.gerar(amb, proj, args.rev, saida)
    versao = ambiente.versao_kicad(amb)
    _manifesto(r.saida, proj, args.rev, list(r.arquivos.values()), versao, r.comandos)
    destino = liberar(r, proj, args.rev, versao, _dados_portao(res, proj, args)) if res else None
    saida = _resposta(r, proj, args.rev, destino)
    console.imprimir_json(saida) if args.json else _imprimir(saida)
    return 0


def main(argv=None):
    console.configurar()
    args = _args(argv)
    problema = _validar(args)
    if problema:
        return console.erro(problema, 2)
    amb = ambiente.detectar()
    if not amb.encontrado:
        return console.erro("kicad-cli nao encontrado; rode diagnostico.py", 2)
    try:
        return executar(amb, args)
    except projeto.ErroProjeto as e:
        return console.erro(str(e), 2)
    except (pacote.ErroPacote, kicad_cli.ErroKicadCli) as e:
        return console.erro(str(e), 1)


if __name__ == "__main__":
    sys.exit(main())
