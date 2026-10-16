"""Pacote de fabricacao pelo kicad-cli: Gerber + furacao (zip), BOM/CPL da JLC, BOM completa, PDF do
esquematico, STEP e render.

Configuracao de Gerber (guia da JLC para KiCad, `pcb-fabricacao/references/pedido-jlcpcb.md`, mais
a pagina https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-8):
formato 4.6 em mm (`--precision 6`), extensoes Protel, X2 com atributos de netlist (padrao do
kicad-cli), `--check-zones` (reenche zonas so na memoria: a placa em disco nao muda) e
`--subtract-soldermask` (serigrafia fora dos pads, pedido pela JLC). Camadas: cobre (2 ou 4), pasta,
serigrafia e mascara dos dois lados, Edge.Cuts. Furacao Excellon em mm, origem absoluta, zeros
decimais, furo oval no modo alternativo, PTH e NPTH separados. Tudo em coordenadas absolutas
(Gerber, furacao e posicoes sem `--use-drill-file-origin`).

O zip leva so o que a fabrica le (Gerbers, `.gbrjob` e os dois `.drl`); o mapa de furos sai em PDF
ao lado, para leitura humana. STEP e render sao opcionais: se falharem, viram aviso.
"""

import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from .. import kicad_cli, netlist
from . import bom, jlc

EXT_PROTEL = {"F.Cu": "gtl", "B.Cu": "gbl", "F.Paste": "gtp", "B.Paste": "gbp", "F.SilkS": "gto",
              "B.SilkS": "gbo", "F.Mask": "gts", "B.Mask": "gbs", "Edge.Cuts": "gm1"}
CAMADAS_TECNICAS = ["F.Paste", "B.Paste", "F.SilkS", "B.SilkS", "F.Mask", "B.Mask", "Edge.Cuts"]
_COBRE = re.compile(r'\(\s*\d+\s+"((?:F|B|In\d+)\.Cu)"\s+(?:signal|power|mixed|jumper)')
TIPOS_RELEASE = ("gerber", "bom-jlc", "cpl-jlc", "bom", "esquematico")


class ErroPacote(RuntimeError):
    pass


# --- nomes ------------------------------------------------------------------------

def nomes(placa, rev):
    """Nome de cada arquivo do pacote (pcb-fabricacao/SKILL.md)."""
    base = f"{placa}-rev-{rev}"
    return {"gerber": f"{base}-gerber.zip", "bom-jlc": f"{base}-bom-jlc.csv", "cpl-jlc": f"{base}-cpl-jlc.csv",
            "bom": f"{base}-bom.csv", "esquematico": f"{base}-esquematico.pdf", "step": f"{base}.step",
            "render-top": "render-top.png", "render-bottom": "render-bottom.png",
            "mapa-pth": f"{base}-mapa-furos-PTH.pdf", "mapa-npth": f"{base}-mapa-furos-NPTH.pdf"}


# --- camadas -----------------------------------------------------------------------

def _ordem_cobre(nome):
    return 0 if nome == "F.Cu" else 10_000 if nome == "B.Cu" else int(nome[2:-3])


def camadas_cobre(pcb):
    """Camadas de cobre declaradas na placa, de F.Cu a B.Cu."""
    texto = Path(pcb).read_text(encoding="utf-8")
    inicio = texto.find("(layers")
    fim = texto.find("(setup", inicio)
    return sorted(set(_COBRE.findall(texto[inicio:fim if fim > 0 else None])), key=_ordem_cobre)


def camadas_gerber(pcb):
    return camadas_cobre(pcb) + CAMADAS_TECNICAS


def extensao_protel(camada):
    """Extensao Protel do KiCad: In1.Cu -> g1 (conferido no teste de 4 camadas)."""
    if camada in EXT_PROTEL:
        return EXT_PROTEL[camada]
    return "g" + camada[2:-3]


def faltando_no_zip(caminho, camadas):
    """Camadas e furacoes que nao estao no zip (lista vazia = completo)."""
    with zipfile.ZipFile(caminho) as z:
        presentes = z.namelist()
    faltas = [c for c in camadas if not any(n.lower().endswith("." + extensao_protel(c)) for n in presentes)]
    faltas += [f for f in ("-PTH.drl", "-NPTH.drl") if not any(n.endswith(f) for n in presentes)]
    return faltas


# --- execucao do kicad-cli -----------------------------------------------------------

@dataclass
class Execucao:
    """Roda o kicad-cli e guarda cada comando com caminhos relativos (para o manifesto)."""
    amb: object
    raizes: list                        # [(Path, rotulo)]: rotulo '' = relativo ao projeto
    comandos: list = field(default_factory=list)

    def _rel(self, arg):
        texto = str(arg)
        for raiz, rotulo in self.raizes:
            try:
                rel = Path(texto).resolve().relative_to(raiz).as_posix()
            except (ValueError, OSError):
                continue
            return f"{rotulo}/{rel}" if rotulo else rel
        return texto

    def rodar(self, args, esperado, timeout=600):
        self.comandos.append("kicad-cli " + " ".join(self._rel(a) for a in args))
        rc, texto = kicad_cli.rodar(self.amb, args, timeout=timeout)
        faltam = [p for p in ([esperado] if isinstance(esperado, Path) else esperado) if not Path(p).exists()]
        if rc != 0 or faltam:
            raise ErroPacote(f"kicad-cli {' '.join(map(str, args[:3]))} falhou (codigo {rc}): {texto.strip()[-400:]}")
        return texto


def _pasta(p):
    return str(p) + ("" if str(p).endswith(("/", "\\")) else "/")


def gerbers(ex, pcb, destino):
    camadas = camadas_gerber(pcb)
    ex.rodar(["pcb", "export", "gerbers", "--layers", ",".join(camadas), "--precision", "6", "--check-zones",
              "--subtract-soldermask", "-o", _pasta(destino), pcb], [destino])
    return camadas


def furacao(ex, pcb, destino, mapas):
    ex.rodar(["pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "--drill-origin",
              "absolute", "--excellon-zeros-format", "decimal", "--excellon-oval-format", "alternate",
              "--excellon-separate-th", "--generate-map", "--map-format", "pdf", "-o", _pasta(destino), pcb],
             [destino / f"{Path(pcb).stem}-PTH.drl", destino / f"{Path(pcb).stem}-NPTH.drl"])
    for lado, alvo in mapas.items():
        mapa = destino / f"{Path(pcb).stem}-{lado}-drl_map.pdf"
        if mapa.exists():
            shutil.move(str(mapa), str(alvo))


def zipar(origem, destino):
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for arq in sorted(Path(origem).iterdir()):
            if arq.is_file():
                z.write(arq, arq.name)
    return destino


def posicoes(ex, pcb, destino):
    ex.rodar(["pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp",
              "-o", destino, pcb], destino)
    return jlc.ler_pos(destino)


def componentes(ex, sch, tmp):
    arq = Path(tmp) / "placa.net"
    ex.rodar(["sch", "export", "netlist", "--format", "kicadsexpr", "-o", arq, sch], arq)
    return bom.componentes(netlist.ler(arq))


def pdf(ex, sch, destino):
    ex.rodar(["sch", "export", "pdf", "-o", destino, sch], destino)


def step(ex, pcb, destino):
    ex.rodar(["pcb", "export", "step", "--force", "--subst-models", "-o", destino, pcb], destino)


def render(ex, pcb, destino, lado):
    ex.rodar(["pcb", "render", "--side", lado, "-o", destino, pcb], destino)


# --- orquestracao --------------------------------------------------------------------

@dataclass
class Resultado:
    saida: Path
    arquivos: dict                      # tipo -> Path
    camadas: list
    comandos: list
    avisos: list = field(default_factory=list)
    componentes_jlc: int = 0
    componentes_montados: int = 0


def _gerber_zip(ex, pcb, tmp, saida, n):
    pasta = Path(tmp) / "gerber"
    pasta.mkdir()
    camadas = gerbers(ex, pcb, pasta)
    furacao(ex, pcb, pasta, {"PTH": saida / n["mapa-pth"], "NPTH": saida / n["mapa-npth"]})
    zipar(pasta, saida / n["gerber"])
    faltas = faltando_no_zip(saida / n["gerber"], camadas)
    if faltas:
        raise ErroPacote("zip de Gerber incompleto, falta: " + ", ".join(faltas))
    return camadas


def _boms(ex, proj, tmp, saida, n, avisos):
    comps = componentes(ex, proj.sch, tmp)
    bom.escrever_completa(saida / n["bom"], comps)
    jlc.escrever_bom(saida / n["bom-jlc"], comps)
    sem_posicao = jlc.escrever_cpl(saida / n["cpl-jlc"], posicoes(ex, proj.pcb, Path(tmp) / "pos.csv"), comps)
    if sem_posicao:
        avisos.append("montados pela JLC sem linha no arquivo de posicao (DNP ou 'excluir dos arquivos de "
                      "posicao' na placa?): " + ", ".join(sem_posicao))
    for p in bom.pendencias(comps):
        avisos.append("BOM: " + p)
    return comps


def _opcionais(ex, proj, saida, n, avisos):
    for tipo, func in (("step", lambda d: step(ex, proj.pcb, d)),
                       ("render-top", lambda d: render(ex, proj.pcb, d, "top")),
                       ("render-bottom", lambda d: render(ex, proj.pcb, d, "bottom"))):
        try:
            func(saida / n[tipo])
        except (ErroPacote, kicad_cli.ErroKicadCli) as e:
            avisos.append(f"{tipo} nao gerado (opcional): {e}")


def _limpar(saida, n):
    """Apaga so os arquivos do pacote de uma execucao anterior (nomes proprios), para nada velho ficar."""
    for nome in list(n.values()) + ["manifesto.json"]:
        (saida / nome).unlink(missing_ok=True)


def gerar(amb, proj, rev, saida):
    """Gera o pacote em `saida` (troca os arquivos do pacote anterior; o resto da pasta fica). Levanta
    ErroPacote se faltar algo obrigatorio (Gerber, furacao, BOM, CPL, PDF)."""
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    n = nomes(proj.placa, rev)
    _limpar(saida, n)
    avisos = []
    with tempfile.TemporaryDirectory(prefix="pcbkit-fab-") as tmp:
        ex = Execucao(amb, [(proj.dir, ""), (saida.resolve(), "<saida>"), (Path(tmp).resolve(), "<tmp>")])
        camadas = _gerber_zip(ex, proj.pcb, tmp, saida, n)
        comps = _boms(ex, proj, tmp, saida, n, avisos)
        pdf(ex, proj.sch, saida / n["esquematico"])
        _opcionais(ex, proj, saida, n, avisos)
    arquivos = {t: saida / nome for t, nome in n.items() if (saida / nome).exists()}
    return Resultado(saida, arquivos, camadas, ex.comandos, avisos,
                     len(jlc.para_jlc(comps)), len(bom.montados(comps)))
