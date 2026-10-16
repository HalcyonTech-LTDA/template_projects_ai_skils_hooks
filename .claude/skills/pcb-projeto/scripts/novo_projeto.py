"""Cria o projeto KiCad 10 de uma placa em <dir-hardware>/<placa>/ e, opcionalmente, as notas de 03_Hardware.

Uso:
  python novo_projeto.py <dir-hardware> --nome <placa> [--camadas 2|4] [--rev A] [--projeto NOME]
                         [--titulo TEXTO] [--empresa TEXTO] [--alta-tensao] [--docs <dir 03_Hardware>]

Cria: <placa>.kicad_pro (do modelo, net classes Default/Power/HV), <placa>.kicad_dru (JLC 2 ou 4
camadas; com --alta-tensao, acrescenta as regras da net class HV), <placa>.kicad_sch e
<placa>.kicad_pcb vazios, sym-lib-table/fp-lib-table apontando para bibliotecas/, spec/<placa>.json
esqueleto, .gitignore e README.md. Com --docs, copia os modelos de assets/docs/ trocando
{{placa}}, {{projeto}}, {{rev}} e {{data}} no caminho e no conteudo (nunca sobrescreve).

`--rev` segue o `REV` do exportar_fab.py (letra maiuscula, depois letras maiusculas ou digitos) e
`--projeto` e um nome de arquivo valido no Windows (sem separador de caminho, `..` ou `<>:"|?*`): os
dois viram caminho e frontmatter nas notas.

Saida: 0 criado; 1 projeto ja existe ou nome invalido; 2 uso errado (inclui --rev/--projeto invalidos).
"""

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from pcbkit import console, modelos
from pcbkit.sexpr import salvar_arquivo

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"
MODELOS_DOCS = ASSETS / "docs"
MODELOS_OPCIONAIS_HV = ASSETS / "opcionais"
PASTA_NOTA_HV = Path("Eletronica") / "Gerber"     # ao lado da nota de liberacao
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REV = re.compile(r"^[A-Z][A-Z0-9]*$")                 # o mesmo regex do REV do exportar_fab.py
_INVALIDOS_WINDOWS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVADOS_WINDOWS = re.compile(r"^(?:CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(?:\..*)?$", re.IGNORECASE)
MARCADORES = ("placa", "projeto", "rev", "data")


# --- validacao ------------------------------------------------------------------

def erro_rev(rev):
    """Mensagem de erro de uma revisao fora do padrao do exportar_fab (ou None)."""
    if not REV.match(rev):
        return f"revisao invalida '{rev}': use letra maiuscula, depois letras maiusculas ou digitos (A, B, AB, A1)"
    return None


def erro_projeto(projeto):
    """Mensagem de erro de um nome de projeto que nao serve de nome de arquivo no Windows (ou None)."""
    if not projeto.strip():
        return "projeto vazio: informe o nome do projeto ou omita --projeto"
    if _INVALIDOS_WINDOWS.search(projeto) or ".." in projeto:
        return (f"projeto invalido '{projeto}': sem separador de caminho (/ ou \\), '..', nem os caracteres "
                f"< > : \" | ? * ou de controle")
    if projeto != projeto.rstrip(" .") or _RESERVADOS_WINDOWS.match(projeto):
        return (f"projeto invalido '{projeto}': o Windows nao aceita nome terminado em ponto ou espaco, "
                f"nem reservado (CON, NUL, ...)")
    return None


# --- conteudo -------------------------------------------------------------------

def _pro(placa):
    dados = json.loads((ASSETS / "kicad" / "projeto-modelo.kicad_pro").read_text(encoding="utf-8"))
    dados["meta"]["filename"] = f"{placa}.kicad_pro"
    return json.dumps(dados, indent=2, ensure_ascii=False) + "\n"


def _dru(camadas, alta_tensao):
    texto = (ASSETS / "kicad" / f"jlc-{camadas}camadas.kicad_dru").read_text(encoding="utf-8")
    if alta_tensao:
        texto += "\n" + (ASSETS / "kicad" / "alta-tensao.kicad_dru").read_text(encoding="utf-8")
    return texto


def _spec(placa, titulo, rev, empresa):
    return {
        "projeto": placa,
        "titulo": titulo,
        "revisao": rev,
        "empresa": empresa,
        "folha": "A3",
        "tensao_max_v": None,
        "blocos": [],
        "componentes": [],
        "redes": {},
        "pwr_flag": [],
        "nao_conectar": [],
        "classes_de_rede": {
            "Power": {"redes": [], "largura_mm": 0.8, "clearance_mm": 0.3},
            "HV": {"redes": [], "largura_mm": 1.0, "clearance_mm": 2.5},
        },
    }


def _readme(placa, titulo, rev, camadas, alta_tensao):
    hv = ("\nAlta tensao: SIM. Regras da net class `HV` estao no `.kicad_dru`; a liberacao exige a nota de "
          "aprovacao de alta tensao assinada.\n" if alta_tensao else "")
    return f"""# {placa}

{titulo or "(descreva a placa em uma linha)"}

- Revisao atual: **{rev}**
- Camadas de cobre: {camadas}
- Modo do esquematico: **spec** (`spec/{placa}.json` e a fonte; o `.kicad_sch` e regenerado).
  Ao editar o esquematico na GUI, troque para **manual** aqui e nao regenere mais.
- Fabricante alvo: JLCPCB (regras em `{placa}.kicad_dru`).
{hv}
## Pastas

- `spec/` spec do circuito (JSON)
- `bibliotecas/` simbolos (`{placa}.kicad_sym`), footprints (`{placa}.pretty/`) e modelos 3D (`3d/`) proprios
- `fab/` saidas de trabalho (ignorado pelo git)
- `releases/rev-<R>/` pacote liberado pelo portao (versionado)

## Comandos

Ver `.claude/skills/pcb-projeto/scripts/README.md`.
"""


# --- escrita --------------------------------------------------------------------

def _escrever(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def criar_projeto(dir_hardware, placa, camadas=2, rev="A", titulo="", empresa="", alta_tensao=False, hoje=None):
    """Cria a pasta da placa. Devolve o caminho. Levanta FileExistsError se o projeto ja existe e
    ValueError se a revisao nao segue o padrao."""
    if erro_rev(rev):
        raise ValueError(erro_rev(rev))
    destino = Path(dir_hardware) / placa
    if (destino / f"{placa}.kicad_pro").exists():
        raise FileExistsError(f"projeto ja existe: {destino / (placa + '.kicad_pro')}")
    data = (hoje or date.today()).isoformat()
    titulo_bloco = titulo or placa
    destino.mkdir(parents=True, exist_ok=True)
    _escrever(destino / f"{placa}.kicad_pro", _pro(placa))
    _escrever(destino / f"{placa}.kicad_dru", _dru(camadas, alta_tensao))
    salvar_arquivo(destino / f"{placa}.kicad_sch", modelos.esquematico_vazio(titulo_bloco, data, rev, empresa))
    salvar_arquivo(destino / f"{placa}.kicad_pcb", modelos.placa_vazia(camadas, titulo_bloco, data, rev, empresa))
    _criar_bibliotecas(destino, placa)
    _escrever(destino / "spec" / f"{placa}.json",
              json.dumps(_spec(placa, titulo, rev, empresa), indent=2, ensure_ascii=False) + "\n")
    shutil.copy(ASSETS / "gitignore-hardware.txt", destino / ".gitignore")
    _escrever(destino / "README.md", _readme(placa, titulo, rev, camadas, alta_tensao))
    return destino


def _criar_bibliotecas(destino, placa):
    libs = destino / "bibliotecas"
    (libs / f"{placa}.pretty").mkdir(parents=True, exist_ok=True)
    (libs / "3d").mkdir(exist_ok=True)
    for vazia in (libs / f"{placa}.pretty" / ".gitkeep", libs / "3d" / ".gitkeep"):
        vazia.touch()
    salvar_arquivo(libs / f"{placa}.kicad_sym", modelos.biblioteca_simbolos_vazia())
    salvar_arquivo(destino / "sym-lib-table", modelos.tabela_bibliotecas(
        "sym", [(placa, f"${{KIPRJMOD}}/bibliotecas/{placa}.kicad_sym", "Simbolos do projeto")]))
    salvar_arquivo(destino / "fp-lib-table", modelos.tabela_bibliotecas(
        "fp", [(placa, f"${{KIPRJMOD}}/bibliotecas/{placa}.pretty", "Footprints do projeto")]))


# --- notas de 03_Hardware -----------------------------------------------------------

def substituir(texto, valores):
    for chave in MARCADORES:
        texto = texto.replace("{{" + chave + "}}", valores[chave])
    return texto


def copiar_docs(origem, destino, valores, subpasta=None):
    """Copia todo *.md de `origem` para `destino` trocando marcadores no caminho e no conteudo.
    `subpasta` coloca tudo dentro de destino/subpasta. Devolve (criados, pulados)."""
    origem, destino = Path(origem), Path(destino)
    criados, pulados = [], []
    for modelo in sorted(origem.rglob("*.md")):
        relativo = Path(substituir(modelo.relative_to(origem).as_posix(), valores))
        alvo = destino / (subpasta or "") / relativo
        if alvo.exists():
            pulados.append(alvo)
            continue
        _escrever(alvo, substituir(modelo.read_text(encoding="utf-8"), valores))
        criados.append(alvo)
    return criados, pulados


def criar_docs(dir_docs, valores, alta_tensao=False, modelos_docs=MODELOS_DOCS, modelos_hv=MODELOS_OPCIONAIS_HV):
    if not Path(modelos_docs).is_dir():
        raise FileNotFoundError(f"modelos de notas nao encontrados em {modelos_docs}")
    criados, pulados = copiar_docs(modelos_docs, dir_docs, valores)
    if alta_tensao and Path(modelos_hv).is_dir():
        c, p = copiar_docs(modelos_hv, dir_docs, valores, subpasta=PASTA_NOTA_HV)
        criados, pulados = criados + c, pulados + p
    return criados, pulados


# --- CLI ------------------------------------------------------------------------------

def _args(argv):
    p = argparse.ArgumentParser(description="Cria o projeto KiCad 10 de uma placa.")
    p.add_argument("dir_hardware", help="pasta hardware/ do repositorio")
    p.add_argument("--nome", required=True, help="slug da placa (ASCII kebab-case), ex. controlador-bomba")
    p.add_argument("--camadas", type=int, choices=[2, 4], default=2)
    p.add_argument("--rev", default="A", help="revisao inicial: letra maiuscula (padrao A)")
    p.add_argument("--projeto", help="nome do projeto para as notas (padrao: o nome da placa)")
    p.add_argument("--titulo", default="", help="titulo da placa (title block e README)")
    p.add_argument("--empresa", default="", help="empresa no title block")
    p.add_argument("--alta-tensao", action="store_true",
                   help="acrescenta as regras HV ao .kicad_dru e a nota de aprovacao de alta tensao")
    p.add_argument("--docs", help="pasta 03_Hardware onde criar as notas modelo")
    return p.parse_args(argv)


def main(argv=None):
    console.configurar()
    args = _args(argv)
    if not SLUG.match(args.nome):
        return console.erro(f"nome '{args.nome}' invalido: use ASCII minusculo em kebab-case (ex. sensor-nivel)")
    erro = erro_rev(args.rev) or (erro_projeto(args.projeto) if args.projeto is not None else None)
    if erro:
        return console.erro(erro, 2)
    try:
        destino = criar_projeto(args.dir_hardware, args.nome, args.camadas, args.rev, args.titulo,
                                args.empresa, args.alta_tensao)
    except FileExistsError as e:
        return console.erro(str(e))
    print(f"Projeto criado em {destino}")
    if args.docs:
        valores = {"placa": args.nome, "projeto": args.projeto or args.nome, "rev": args.rev,
                   "data": date.today().isoformat()}
        criados, pulados = criar_docs(args.docs, valores, args.alta_tensao)
        for c in criados:
            print(f"  nota criada: {c}")
        for p in pulados:
            print(f"  AVISO: ja existe, nao sobrescrevi: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
