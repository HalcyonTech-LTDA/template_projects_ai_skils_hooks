"""Diagnostico do ambiente da familia pcb-*: KiCad, kicad-cli, Python do KiCad, Java, Freerouting.

Uso: python diagnostico.py [--json]
Saida 0 se o nucleo (kicad-cli + Python do KiCad com pcbnew) esta pronto; 1 se falta algo do nucleo.
Itens opcionais (Java, Freerouting, uvx, chaves de distribuidor) so geram aviso.
"""

import argparse
import sys
from pathlib import Path

from pcbkit import ambiente, console

AQUI = Path(__file__).resolve().parent
SCRIPTS_SWIG = ("pcb_do_esquematico.py", "rotear.py")


def coletar(amb):
    ok_pcbnew, msg_pcbnew = ambiente.verificar_pcbnew(amb)
    return {
        "kicad_versao": ambiente.versao_kicad(amb),
        "kicad_dir": amb.kicad_dir,
        "kicad_cli": amb.kicad_cli,
        "kicad_python": amb.kicad_python,
        "pcbnew": {"ok": ok_pcbnew, "detalhe": msg_pcbnew},
        "dir_config": amb.dir_config,
        "bibliotecas": {
            "simbolos": amb.dir_simbolos(),
            "footprints": amb.dir_footprints(),
            "modelos_3d": amb.dir_modelos_3d(),
            "template": amb.dir_template(),
        },
        "java": amb.java,
        "java_versao": ambiente.versao_java(amb),
        "freerouting_jar": amb.freerouting_jar,
        "uvx": amb.uvx,
        "easyeda2kicad": amb.easyeda2kicad,
        "chaves_distribuidor": amb.chaves,
        "comando_swig": f'"{amb.kicad_python}" "{AQUI / "<script>.py"}"' if amb.kicad_python else None,
    }


def problemas(info):
    """(faltas do nucleo, avisos)."""
    faltas, avisos = [], []
    if not info["kicad_cli"]:
        faltas.append("kicad-cli nao encontrado. Instale o KiCad 10 (https://www.kicad.org/download/) "
                      "ou defina KICAD_CLI/KICAD_DIR.")
    if not info["pcbnew"]["ok"]:
        faltas.append(f"pcbnew nao importa no Python do KiCad ({info['pcbnew']['detalhe']}). "
                      f"Os scripts {', '.join(SCRIPTS_SWIG)} nao vao rodar.")
    if not info["java"]:
        avisos.append("Java nao encontrado: o Freerouting (rotear.py) precisa de Java 21+.")
    if not info["freerouting_jar"]:
        avisos.append("FREEROUTING_JAR nao definido: baixe o jar em https://github.com/freerouting/freerouting/releases "
                      "e aponte a variavel para ele (bloco env do .claude/settings.local.json).")
    if not (info["uvx"] or info["easyeda2kicad"]):
        avisos.append("uvx nao encontrado: importar peca LCSC usa 'uvx easyeda2kicad' (instale o uv).")
    for nome, presente in info["chaves_distribuidor"].items():
        if not presente:
            avisos.append(f"{nome} ausente: buscar_distribuidor.py sai com instrucao (opcional).")
    return faltas, avisos


def _linha(rotulo, valor):
    print(f"  {rotulo:<22} {valor if valor not in (None, '') else '-- nao encontrado'}")


def imprimir(info, faltas, avisos):
    print("Ambiente pcb-* (KiCad)")
    _linha("KiCad", info["kicad_versao"])
    _linha("kicad-cli", info["kicad_cli"])
    _linha("Python do KiCad", info["kicad_python"])
    _linha("pcbnew", "ok " + info["pcbnew"]["detalhe"] if info["pcbnew"]["ok"] else None)
    _linha("Config do usuario", info["dir_config"])
    for nome, caminho in info["bibliotecas"].items():
        _linha(f"Bibl. {nome}", caminho)
    _linha("Java", f'{info["java"]} ({info["java_versao"]})' if info["java"] else None)
    _linha("Freerouting (jar)", info["freerouting_jar"])
    _linha("uvx", info["uvx"])
    _linha("easyeda2kicad", info["easyeda2kicad"] or ("via uvx" if info["uvx"] else None))
    for nome, presente in info["chaves_distribuidor"].items():
        _linha(nome, "definida" if presente else "ausente")
    if info["comando_swig"]:
        print(f"\nScripts SWIG ({', '.join(SCRIPTS_SWIG)}) rodam assim:\n  {info['comando_swig']}")
    for f in faltas:
        print(f"\nFALTA: {f}")
    for a in avisos:
        print(f"AVISO: {a}")
    print("\nNucleo pronto." if not faltas else "\nNucleo incompleto.")


def main(argv=None):
    console.configurar()
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--json", action="store_true", help="saida em JSON")
    args = p.parse_args(argv)
    info = coletar(ambiente.detectar())
    faltas, avisos = problemas(info)
    if args.json:
        console.imprimir_json({**info, "faltas": faltas, "avisos": avisos, "ok": not faltas})
    else:
        imprimir(info, faltas, avisos)
    return 1 if faltas else 0


if __name__ == "__main__":
    sys.exit(main())
