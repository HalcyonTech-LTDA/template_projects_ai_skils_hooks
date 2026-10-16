"""exportar_fab.py e portao_liberacao.py pelo kicad-cli (pulam sem KiCad).

Fixture: projeto de 4 camadas do novo_projeto.py com o esquematico da placa exemplo e a placa vazia
(sem contorno nem footprints). Serve para o pacote (Gerber de 4 camadas, BOM, CPL vazio com aviso) e
para o portao bloquear de verdade (DRC). A liberacao com portao aprovado usa `portao.rodar` simulado:
a placa que passa no DRC e a da prova ponta a ponta, nao cabe num teste rapido.
"""
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import exportar_fab  # noqa: E402
import gerar_esquematico  # noqa: E402
import novo_projeto  # noqa: E402
import portao_liberacao  # noqa: E402
from pcbkit import ambiente, portao, projeto  # noqa: E402
from pcbkit.fab import manifesto  # noqa: E402

AMB = ambiente.detectar()
EXEMPLO = Path(__file__).resolve().parents[2] / "assets" / "exemplo" / "placa-exemplo.json"
MODELO_NOTA = Path(__file__).resolve().parents[2] / "assets" / "docs" / "Eletronica" / "Gerber" / \
    "{{placa}}_Rev{{rev}}_Liberacao_Fabricacao.md"
GITIGNORE = Path(__file__).resolve().parents[2] / "assets" / "gitignore-hardware.txt"
SEM_KICAD = "kicad-cli nao encontrado"


def _rodar(main, argv):
    saida, erro = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
        codigo = main(argv)
    return codigo, saida.getvalue(), erro.getvalue()


def _resultado_ok(placa):
    lib = portao.Verificacao("nota de liberacao", True, [], {"revisores": ["Teste"], "nota": "n.md"})
    sev = {"criticas_rebaixadas": [], "rebaixadas": ["DRC silk_overlap: 'ignore' (padrao 'warning')"],
           "exclusoes_drc": [{"violacao": "silk_edge_clearance|1|2|a|b", "comentario": "antena"}], "exclusoes_erc": []}
    return portao.Resultado(placa, [lib], avisos_drc=[{"tipo": "silk_edge_clearance", "descricao": "d",
                                                       "itens": []}], severidades=sev)


@unittest.skipUnless(AMB.encontrado, SEM_KICAD)
class TestExportarFab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="pcbkit-fab-")
        raiz = Path(cls._tmp.name) / "repo & Inovação"
        cls.proj = novo_projeto.criar_projeto(raiz / "hardware", "placa-t", camadas=4, hoje=date(2026, 10, 12))
        shutil.copy(EXEMPLO, cls.proj / "spec" / "placa-t.json")
        with contextlib.redirect_stdout(io.StringIO()):
            assert gerar_esquematico.main([str(EXEMPLO), "-o", str(cls.proj / "placa-t.kicad_sch")]) == 0
        cls.nota = raiz / "docs" / "placa-t_RevA_Liberacao_Fabricacao.md"
        cls.nota.parent.mkdir(parents=True)
        cls.nota.write_text(novo_projeto.substituir(MODELO_NOTA.read_text(encoding="utf-8"), {
            "placa": "placa-t", "projeto": "T", "rev": "A", "data": "2026-10-12"}), encoding="utf-8")
        cls.codigo, saida, _ = _rodar(exportar_fab.main, [str(cls.proj), "--rev", "B", "--json"])
        cls.saida = json.loads(saida)
        cls.fab = cls.proj / "fab" / "rev-B"

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_pacote_completo(self):
        self.assertEqual(self.codigo, 0)
        nomes = {a["arquivo"] for a in self.saida["arquivos_fab"]}
        for nome in ("placa-t-rev-B-gerber.zip", "placa-t-rev-B-bom-jlc.csv", "placa-t-rev-B-cpl-jlc.csv",
                     "placa-t-rev-B-bom.csv", "placa-t-rev-B-esquematico.pdf", "manifesto.json"):
            self.assertIn(nome, nomes)
        self.assertEqual(self.saida["camadas_cobre"], 4)
        self.assertIsNone(self.saida["release"])

    def test_zip_com_4_camadas_e_furacao(self):
        with zipfile.ZipFile(self.fab / "placa-t-rev-B-gerber.zip") as z:
            nomes = z.namelist()
        for sufixo in (".gtl", ".g1", ".g2", ".gbl", ".gtp", ".gbp", ".gto", ".gbo", ".gts", ".gbs", ".gm1",
                       "-PTH.drl", "-NPTH.drl"):
            self.assertTrue(any(n.endswith(sufixo) for n in nomes), sufixo)

    def test_bom_e_cpl(self):
        bom_jlc = (self.fab / "placa-t-rev-B-bom-jlc.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(bom_jlc[0], "Comment,Designator,Footprint,JLCPCB Part #")
        self.assertIn('10k,"R1,R2,R3,R5,R6",R_0603_1608Metric,C25804', bom_jlc)
        cpl = (self.fab / "placa-t-rev-B-cpl-jlc.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(cpl, ["Designator,Mid X,Mid Y,Rotation,Layer"])     # placa vazia: nenhum footprint
        self.assertTrue(any("sem linha no arquivo de posicao" in a for a in self.saida["avisos"]))

    def test_manifesto_confere(self):
        dados = json.loads((self.fab / "manifesto.json").read_text(encoding="utf-8"))
        self.assertEqual(manifesto.conferir(self.fab, dados), [])
        self.assertEqual((dados["placa"], dados["revisao"], dados["kicad"]), ("placa-t", "B", ambiente.versao_kicad(AMB)))
        self.assertTrue(all(c.startswith("kicad-cli ") for c in dados["comandos"]))
        self.assertFalse(any("Inovação" in c for c in dados["comandos"]))   # caminhos relativos

    def test_saida_em_releases_recusada(self):                       # achado 11: forjava release sem portao
        for destino in (self.proj / "releases" / "rev-Z", self.proj / "releases"):
            codigo, _, erro = _rodar(exportar_fab.main, [str(self.proj), "--rev", "Z", "--saida", str(destino)])
            self.assertEqual(codigo, 2, destino)
            self.assertIn("fica dentro de releases/", erro)
        self.assertFalse((self.proj / "releases" / "rev-Z").exists())

    def test_liberar_exige_checklist(self):
        self.assertEqual(_rodar(exportar_fab.main, [str(self.proj), "--liberar"])[0], 2)

    def test_portao_real_bloqueia(self):
        codigo, saida, _ = _rodar(portao_liberacao.main, [str(self.proj), "--checklist", str(self.nota), "--json",
                                                          "--rev", "B"])
        self.assertEqual(codigo, 1)
        res = json.loads(saida)
        por_nome = {v["nome"]: v for v in res["verificacoes"]}
        self.assertEqual(res["revisao"], "A")                                       # a da spec
        self.assertIn("--rev B nao bate com a revisao da spec (A)", por_nome["revisao declarada na spec"]["motivos"][0])
        self.assertTrue(por_nome["severidades de ERC/DRC no .kicad_pro"]["ok"])
        self.assertTrue(por_nome["ERC (estrito)"]["ok"])
        self.assertTrue(por_nome["tensao_max_v declarado na spec"]["ok"])
        self.assertTrue(por_nome["BOM: MPN e LCSC em todo componente montado"]["ok"])
        self.assertFalse(por_nome["DRC com paridade (zonas reenchidas)"]["ok"])     # placa vazia
        self.assertFalse(por_nome["nota de liberacao"]["ok"])                       # rascunho

    def test_liberar_bloqueado_nao_cria_release(self):
        res = portao.Resultado("placa-t", [portao.Verificacao("x", False, ["motivo"])])
        with mock.patch.object(portao, "rodar", return_value=res):
            codigo, saida, _ = _rodar(exportar_fab.main, [str(self.proj), "--rev", "D", "--liberar",
                                                          "--checklist", str(self.nota)])
        self.assertEqual(codigo, 1)
        self.assertIn("BLOQUEADO", saida)
        self.assertFalse((self.proj / "releases" / "rev-D").exists())

    def test_liberar_e_recusar_sobrescrever(self):
        with mock.patch.object(portao, "rodar", return_value=_resultado_ok("placa-t")) as rodar:
            codigo, _, _ = _rodar(exportar_fab.main, [str(self.proj), "--rev", "C", "--liberar",
                                                      "--checklist", str(self.nota)])
            self.assertEqual(codigo, 0)
            release = self.proj / "releases" / "rev-C"
            self.assertEqual(sorted(p.name for p in release.iterdir()), sorted([
                "manifesto.json", "placa-t-rev-C-gerber.zip", "placa-t-rev-C-bom-jlc.csv",
                "placa-t-rev-C-cpl-jlc.csv", "placa-t-rev-C-bom.csv", "placa-t-rev-C-esquematico.pdf"]))
            dados = json.loads((release / "manifesto.json").read_text(encoding="utf-8"))
            self.assertEqual(manifesto.conferir(release, dados), [])
            self.assertEqual(dados["portao"]["revisores"], ["Teste"])
            self.assertEqual(dados["portao"]["avisos_drc"], ["silk_edge_clearance: d"])
            self.assertEqual(dados["portao"]["severidades_rebaixadas"], ["DRC silk_overlap: 'ignore' (padrao 'warning')"])
            self.assertEqual(dados["portao"]["exclusoes_drc"][0]["comentario"], "antena")
            self.assertEqual(dados["portao"]["exclusoes_erc"], [])
            antes = (release / "manifesto.json").read_bytes()
            codigo, _, erro = _rodar(exportar_fab.main, [str(self.proj), "--rev", "C", "--liberar",
                                                         "--checklist", str(self.nota)])
        self.assertEqual(codigo, 1)
        self.assertIn("ja existe", erro)
        self.assertEqual(rodar.call_count, 1)                  # recusa antes de rodar o portao
        self.assertEqual((release / "manifesto.json").read_bytes(), antes)
        self.assertFalse(any(p.name.endswith("parcial") for p in release.parent.iterdir()))


class TestPastaDeTrabalho(unittest.TestCase):
    def test_dentro_de_releases_e_recusado(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = projeto.Projeto(Path(tmp).resolve(), "p")
            self.assertEqual(exportar_fab.pasta_de_trabalho(proj, "A"), proj.dir / "fab" / "rev-A")
            self.assertEqual(exportar_fab.pasta_de_trabalho(proj, "A", proj.dir / "releases" / ".." / "x"),
                             proj.dir / "releases" / ".." / "x")
            self.assertEqual(exportar_fab.pasta_de_trabalho(proj, "A", proj.dir / "releases-velhas"),
                             proj.dir / "releases-velhas")
            for ruim in (proj.dir / "releases", proj.dir / "releases" / "rev-A", proj.dir / "fab" / ".." / "releases"):
                with self.assertRaisesRegex(projeto.ErroProjeto, "dentro de releases/"):
                    exportar_fab.pasta_de_trabalho(proj, "A", ruim)


@unittest.skipUnless(shutil.which("git"), "git ausente")
class TestGitignoreDoProjeto(unittest.TestCase):
    def test_release_parcial_e_ignorada(self):                      # achado 13
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            shutil.copy(GITIGNORE, Path(tmp) / ".gitignore")
            def ignorado(caminho):
                return subprocess.run(["git", "-C", tmp, "check-ignore", "-q", "--no-index", caminho]).returncode == 0
            self.assertTrue(ignorado("releases/.rev-A-parcial/manifesto.json"))
            self.assertTrue(ignorado("fab/rev-A/x.zip"))
            self.assertFalse(ignorado("releases/rev-A/manifesto.json"))


if __name__ == "__main__":
    unittest.main()
