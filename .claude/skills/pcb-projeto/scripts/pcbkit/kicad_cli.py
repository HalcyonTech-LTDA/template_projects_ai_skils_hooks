"""Chamadas ao kicad-cli e leitura dos relatorios JSON.

A saida humana do kicad-cli sai no idioma da instalacao (aqui, portugues): nunca a interprete.
Leia so o relatorio `--format json`.

Armadilha medida no 10.0.0: um `.kicad_dru` com erro de sintaxe, sem `(version 1)` ou com
condicao invalida e DESCARTADO EM SILENCIO pelo `pcb drc` (saida 0, nada no stderr, nenhuma
violacao a mais). Use `validar_dru` para provar que o arquivo foi aceito.
"""

import json
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from . import VERSAO_PCB, GERADOR, GERADOR_VERSAO
from .sexpr import Simbolo as S, salvar_arquivo

CANARIO = "pcbkit_canario"


class ErroKicadCli(RuntimeError):
    pass


@dataclass
class Relatorio:
    tipo: str                       # 'erc' ou 'drc'
    rc: int
    arquivo: Path
    dados: dict
    violacoes: list = field(default_factory=list)   # dicts do JSON (ERC: todas as folhas)
    nao_conectados: list = field(default_factory=list)
    paridade: list = field(default_factory=list)

    def contar(self, severidade):
        todas = self.violacoes + self.nao_conectados + self.paridade
        return sum(1 for v in todas if v.get("severity") == severidade)

    @property
    def erros(self):
        return self.contar("error")

    @property
    def avisos(self):
        return self.contar("warning")

    @property
    def total(self):
        return len(self.violacoes) + len(self.nao_conectados) + len(self.paridade)


# --- execucao -----------------------------------------------------------------

def rodar(amb, args, cwd=None, timeout=600):
    """Roda `kicad-cli <args>`. Devolve (codigo, stdout+stderr)."""
    if not amb.kicad_cli:
        raise ErroKicadCli("kicad-cli nao encontrado; rode diagnostico.py")
    try:
        r = subprocess.run([str(amb.kicad_cli)] + [str(a) for a in args], cwd=cwd, capture_output=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise ErroKicadCli(f"kicad-cli passou de {timeout}s: {' '.join(map(str, args))}") from e
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _carregar_json(caminho):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ErroKicadCli(f"relatorio do kicad-cli ausente ou invalido: {caminho} ({e})") from e


def _saida_padrao(entrada, sufixo):
    entrada = Path(entrada)
    return entrada.with_name(f"{entrada.stem}-{sufixo}.json")


# --- ERC / DRC -------------------------------------------------------------------

def ler_relatorio_erc(caminho, rc=0):
    dados = _carregar_json(caminho)
    violacoes = [v for folha in dados.get("sheets", []) for v in folha.get("violations", [])]
    return Relatorio("erc", rc, Path(caminho), dados, violacoes)


def ler_relatorio_drc(caminho, rc=0):
    dados = _carregar_json(caminho)
    return Relatorio("drc", rc, Path(caminho), dados, list(dados.get("violations", [])),
                     list(dados.get("unconnected_items", [])), list(dados.get("schematic_parity", [])))


def erc(amb, sch, saida=None, todas_severidades=True):
    """ERC com relatorio JSON. O codigo de saida != 0 so por violacao vem em Relatorio.rc."""
    saida = Path(saida) if saida else _saida_padrao(sch, "erc")
    args = ["sch", "erc", "--format", "json", "--units", "mm", "--exit-code-violations", "-o", saida]
    if todas_severidades:
        args.insert(-2, "--severity-all")
    rc, texto = rodar(amb, args + [sch])
    if not saida.exists():
        raise ErroKicadCli(f"ERC nao gerou relatorio (codigo {rc}): {texto.strip()}")
    return ler_relatorio_erc(saida, rc)


def drc(amb, pcb, saida=None, paridade=False, reencher_zonas=False, todas_severidades=True):
    saida = Path(saida) if saida else _saida_padrao(pcb, "drc")
    args = ["pcb", "drc", "--format", "json", "--units", "mm", "--exit-code-violations"]
    if todas_severidades:
        args.append("--severity-all")
    if paridade:
        args.append("--schematic-parity")
    if reencher_zonas:
        args.append("--refill-zones")
    rc, texto = rodar(amb, args + ["-o", saida, pcb])
    if not saida.exists():
        raise ErroKicadCli(f"DRC nao gerou relatorio (codigo {rc}): {texto.strip()}")
    return ler_relatorio_drc(saida, rc)


# --- exportacao e upgrade -------------------------------------------------------

def exportar_netlist(amb, sch, destino, formato="kicadsexpr"):
    rc, texto = rodar(amb, ["sch", "export", "netlist", "--format", formato, "-o", destino, sch])
    if rc != 0 or not Path(destino).exists():
        raise ErroKicadCli(f"falha ao exportar netlist (codigo {rc}): {texto.strip()}")
    return Path(destino)


def upgrade(amb, arquivo, forcar=False):
    """Regrava no formato atual: .kicad_sch, .kicad_pcb, .kicad_sym ou pasta .pretty."""
    arquivo = Path(arquivo)
    tipo = {".kicad_sch": "sch", ".kicad_pcb": "pcb", ".kicad_sym": "sym", ".pretty": "fp"}.get(arquivo.suffix)
    if not tipo:
        raise ErroKicadCli(f"upgrade nao sabe tratar {arquivo.suffix}")
    args = [tipo, "upgrade"] + (["--force"] if forcar else []) + [arquivo]
    rc, texto = rodar(amb, args)
    if rc != 0:
        raise ErroKicadCli(f"upgrade falhou (codigo {rc}): {texto.strip()}")
    return texto


# --- validacao de .kicad_dru ------------------------------------------------------

def _trilha(x1, y1, x2, y2, rede):
    return [S("segment"), [S("start"), x1, y1], [S("end"), x2, y2], [S("width"), 0.25],
            [S("layer"), "F.Cu"], [S("net"), rede], [S("uuid"), str(uuid.uuid4())]]


def _placa_canario():
    """Placa minima com duas trilhas de redes diferentes a ~1 mm uma da outra."""
    return [S("kicad_pcb"), [S("version"), VERSAO_PCB], [S("generator"), GERADOR],
            [S("generator_version"), GERADOR_VERSAO],
            [S("general"), [S("thickness"), 1.6], [S("legacy_teardrops"), S("no")]], [S("paper"), "A4"],
            [S("layers"), [0, "F.Cu", S("signal")], [2, "B.Cu", S("signal")], [25, "Edge.Cuts", S("user")]],
            [S("setup"), [S("pad_to_mask_clearance"), 0]],
            [S("gr_rect"), [S("start"), 100, 100], [S("end"), 140, 130],
             [S("stroke"), [S("width"), 0.1], [S("type"), S("default")]], [S("fill"), S("no")],
             [S("layer"), "Edge.Cuts"], [S("uuid"), str(uuid.uuid4())]],
            _trilha(110, 110, 130, 110, "CANARIO_A"), _trilha(110, 111.25, 130, 111.25, "CANARIO_B"),
            [S("embedded_fonts"), S("no")]]


def _regra_canario():
    return (f'\n(version 1)\n(rule "{CANARIO}"\n\t(condition "A.NetName == \'CANARIO_A\'")\n'
            f'\t(constraint clearance (min 5mm)))\n')


def validar_dru(amb, dru, pro=None):
    """(ok, mensagem). Acrescenta uma regra-canario ao .kicad_dru e roda DRC numa placa de teste:
    se o canario nao dispara, o KiCad descartou o arquivo (erro de sintaxe ou de condicao)."""
    texto = Path(dru).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="pcbkit-dru-") as tmp:
        tmp = Path(tmp)
        salvar_arquivo(tmp / "canario.kicad_pcb", _placa_canario())
        (tmp / "canario.kicad_dru").write_text(texto + _regra_canario(), encoding="utf-8")
        if pro:
            shutil.copy(pro, tmp / "canario.kicad_pro")
        rel = drc(amb, tmp / "canario.kicad_pcb", saida=tmp / "drc.json", todas_severidades=False)
        aceito = any(CANARIO in v.get("description", "") for v in rel.violacoes)
    if aceito:
        return True, "regras aceitas pelo kicad-cli"
    return False, ("o kicad-cli descartou o .kicad_dru (erro de sintaxe, condicao invalida ou falta de "
                   "'(version 1)'); abra no editor de regras do KiCad para ver a linha")
