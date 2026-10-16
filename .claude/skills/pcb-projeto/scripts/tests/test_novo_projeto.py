"""Testes do novo_projeto.py: estrutura criada, notas com marcadores e aceite pelo kicad-cli."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import novo_projeto as npj  # noqa: E402
from pcbkit import ambiente, bibliotecas, kicad_cli, sexpr  # noqa: E402

AMB = ambiente.detectar()
HOJE = date(2026, 10, 12)


class BaseTmp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="pcbkit-novo-")
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name) / "repo & Inovação"     # caminho com espaco, & e acento


class TestCriarProjeto(BaseTmp):
    def test_estrutura(self):
        d = npj.criar_projeto(self.raiz / "hardware", "placa-x", camadas=2, hoje=HOJE)
        esperados = ["placa-x.kicad_pro", "placa-x.kicad_dru", "placa-x.kicad_sch", "placa-x.kicad_pcb",
                     "sym-lib-table", "fp-lib-table", "spec/placa-x.json", ".gitignore", "README.md",
                     "bibliotecas/placa-x.kicad_sym", "bibliotecas/placa-x.pretty", "bibliotecas/3d"]
        for rel in esperados:
            self.assertTrue((d / rel).exists(), rel)

    def test_pro_dru_e_spec(self):
        d = npj.criar_projeto(self.raiz / "hardware", "placa-x", camadas=4, rev="B", titulo="T", hoje=HOJE)
        pro = json.loads((d / "placa-x.kicad_pro").read_text(encoding="utf-8"))
        self.assertEqual(pro["meta"]["filename"], "placa-x.kicad_pro")
        classes = {c["name"]: (c["track_width"], c["clearance"]) for c in pro["net_settings"]["classes"]}
        self.assertEqual(classes, {"Default": (0.25, 0.2), "Power": (0.8, 0.3), "HV": (1.0, 2.5)})
        dru = (d / "placa-x.kicad_dru").read_text(encoding="utf-8")
        self.assertIn("4 camadas", dru)
        self.assertNotIn("hv_clearance", dru)
        spec = json.loads((d / "spec" / "placa-x.json").read_text(encoding="utf-8"))
        self.assertEqual((spec["projeto"], spec["revisao"], spec["titulo"]), ("placa-x", "B", "T"))
        self.assertIsNone(spec["tensao_max_v"])

    def test_alta_tensao_concatena_regras(self):
        d = npj.criar_projeto(self.raiz / "hardware", "placa-hv", alta_tensao=True, hoje=HOJE)
        dru = (d / "placa-hv.kicad_dru").read_text(encoding="utf-8")
        self.assertIn("jlc_trilha_minima", dru)
        self.assertIn("hv_creepage", dru)

    def test_camadas_na_placa(self):
        d = npj.criar_projeto(self.raiz / "hardware", "placa-4c", camadas=4, hoje=HOJE)
        pcb = sexpr.carregar_arquivo(d / "placa-4c.kicad_pcb")
        cobre = [(c[0], c[1]) for c in sexpr.filho(pcb, "layers")[1:] if str(c[2]) == "signal"]
        self.assertEqual(cobre, [(0, "F.Cu"), (4, "In1.Cu"), (6, "In2.Cu"), (2, "B.Cu")])

    def test_tabelas_apontam_para_bibliotecas_do_projeto(self):
        d = npj.criar_projeto(self.raiz / "hardware", "placa-x", hoje=HOJE)
        amb = ambiente.Ambiente(maior=10)
        entradas = bibliotecas.tabela(amb, "sym", projeto=d)
        self.assertEqual(entradas[0].nome, "placa-x")
        self.assertEqual(entradas[0].caminho.resolve(), (d / "bibliotecas" / "placa-x.kicad_sym").resolve())

    def test_nao_sobrescreve_projeto(self):
        npj.criar_projeto(self.raiz / "hardware", "placa-x", hoje=HOJE)
        with self.assertRaises(FileExistsError):
            npj.criar_projeto(self.raiz / "hardware", "placa-x", hoje=HOJE)

    def test_cli_rejeita_nome_invalido_e_repetido(self):
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(npj.main([str(self.raiz), "--nome", "Placa_X"]), 1)
            self.assertEqual(npj.main([str(self.raiz), "--nome", "placa-x"]), 0)
            self.assertEqual(npj.main([str(self.raiz), "--nome", "placa-x"]), 1)
        self.assertIn("invalido", erro.getvalue())


class TestValidacaoRevEProjeto(BaseTmp):
    """Achado 12 da revisao: --rev e --projeto viravam caminho (`--rev "../../x"`)."""

    def _rodar(self, *args):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = npj.main([str(self.raiz / "hardware"), "--nome", "placa-x", *args])
        return rc, err.getvalue()

    def _nada_criado(self):
        self.assertFalse((self.raiz / "hardware").exists())
        self.assertFalse((self.raiz / "03").exists())

    def test_rev_invalida_sai_com_2_e_nao_cria_nada(self):
        for rev in ("../../x", "a", "A/B", "A\\B", "1A", "", "A B", "A..", "A.B", "A-1"):
            with self.subTest(rev=rev):
                rc, erro = self._rodar("--rev", rev, "--docs", str(self.raiz / "03"))
                self.assertEqual(rc, 2)
                self.assertIn("revisao invalida", erro)
                self._nada_criado()

    def test_rev_valida_como_no_exportar_fab(self):
        for rev in ("A", "B", "AB", "A1"):
            self.assertIsNone(npj.erro_rev(rev), rev)

    def test_projeto_invalido_sai_com_2_e_nao_cria_nada(self):
        for nome in ("../fora", "a/b", "a\\b", "..", "a..b", "a:b", "a*b", 'a"b', "a|b", "a<b", "a?b", "a\nb",
                     "", "  ", "nome.", "nome ", "CON", "nul", "COM1.txt"):
            with self.subTest(projeto=nome):
                rc, erro = self._rodar("--projeto", nome, "--docs", str(self.raiz / "03"))
                self.assertEqual(rc, 2)
                self.assertIn("projeto", erro)
                self._nada_criado()

    def test_projeto_valido_passa_para_as_notas(self):
        for nome in ("Halcyon Tech", "ECO_Bombas", "proj-1", "Sensor (v2)"):
            self.assertIsNone(npj.erro_projeto(nome), nome)
        rc, _ = self._rodar("--projeto", "ECO Bombas", "--rev", "B", "--docs", str(self.raiz / "03"))
        self.assertEqual(rc, 0)
        nota = next((self.raiz / "03").rglob("placa-x_RevB_Revisao_Esquematico.md"))
        self.assertIn("project: ECO Bombas", nota.read_text(encoding="utf-8"))

    def test_criar_projeto_tambem_recusa_rev_invalida(self):
        with self.assertRaises(ValueError):
            npj.criar_projeto(self.raiz / "hardware", "placa-x", rev="../../x", hoje=HOJE)
        self._nada_criado()


class TestDocs(BaseTmp):
    def _modelos(self):
        m = self.raiz / "modelos"
        (m / "Prototipagem" / "Rev_{{rev}}").mkdir(parents=True)
        (m / "Prototipagem" / "Rev_{{rev}}" / "{{placa}}_Rev{{rev}}_Bring_Up.md").write_text(
            "placa: {{placa}}\nprojeto: {{projeto}}\ncreated: {{data}}\n{{outro}}\n", encoding="utf-8")
        (m / "Raiz.md").write_text("rev {{rev}}", encoding="utf-8")
        (m / "ignorar.txt").write_text("x", encoding="utf-8")
        hv = self.raiz / "opcionais"
        hv.mkdir()
        (hv / "{{placa}}_HV.md").write_text("hv {{placa}}", encoding="utf-8")
        return m, hv

    def test_marcadores_no_caminho_e_no_conteudo(self):
        m, hv = self._modelos()
        valores = {"placa": "placa-x", "projeto": "Projeto X", "rev": "A", "data": "2026-10-12"}
        criados, pulados = npj.criar_docs(self.raiz / "03_Hardware", valores, alta_tensao=True,
                                          modelos_docs=m, modelos_hv=hv)
        nota = self.raiz / "03_Hardware" / "Prototipagem" / "Rev_A" / "placa-x_RevA_Bring_Up.md"
        self.assertTrue(nota.exists())
        self.assertEqual(nota.read_text(encoding="utf-8"),
                         "placa: placa-x\nprojeto: Projeto X\ncreated: 2026-10-12\n{{outro}}\n")
        self.assertTrue((self.raiz / "03_Hardware" / "Eletronica" / "Gerber" / "placa-x_HV.md").exists())
        self.assertFalse((self.raiz / "03_Hardware" / "ignorar.txt").exists())
        self.assertEqual((len(criados), len(pulados)), (3, 0))

    def test_sem_alta_tensao_nao_copia_opcional(self):
        m, hv = self._modelos()
        valores = {"placa": "p", "projeto": "p", "rev": "A", "data": "2026-10-12"}
        criados, _ = npj.criar_docs(self.raiz / "03", valores, modelos_docs=m, modelos_hv=hv)
        self.assertEqual(len(criados), 2)

    def test_nunca_sobrescreve(self):
        m, hv = self._modelos()
        valores = {"placa": "p", "projeto": "p", "rev": "A", "data": "2026-10-12"}
        existente = self.raiz / "03" / "Raiz.md"
        existente.parent.mkdir(parents=True)
        existente.write_text("meu texto", encoding="utf-8")
        criados, pulados = npj.criar_docs(self.raiz / "03", valores, modelos_docs=m, modelos_hv=hv)
        self.assertEqual(pulados, [existente])
        self.assertEqual(existente.read_text(encoding="utf-8"), "meu texto")

    def test_modelos_ausentes(self):
        with self.assertRaises(FileNotFoundError):
            npj.criar_docs(self.raiz / "03", {}, modelos_docs=self.raiz / "nada")


@unittest.skipUnless(AMB.encontrado, "kicad-cli nao encontrado")
class TestProjetoNoKicad(BaseTmp):
    def test_erc_drc_e_regras_aceitos(self):
        for camadas, hv in ((2, False), (4, True)):
            with self.subTest(camadas=camadas, alta_tensao=hv):
                nome = f"placa-{camadas}c"
                d = npj.criar_projeto(self.raiz / "hardware", nome, camadas=camadas, alta_tensao=hv, hoje=HOJE)
                erc = kicad_cli.erc(AMB, d / f"{nome}.kicad_sch", saida=d / "erc.json")
                self.assertEqual(erc.total, 0)
                drc = kicad_cli.drc(AMB, d / f"{nome}.kicad_pcb", saida=d / "drc.json")
                # placa vazia: o unico problema esperado e a falta de contorno (Edge.Cuts)
                self.assertEqual({v["type"] for v in drc.violacoes}, {"invalid_outline"})
                ok, msg = kicad_cli.validar_dru(AMB, d / f"{nome}.kicad_dru", pro=d / f"{nome}.kicad_pro")
                self.assertTrue(ok, msg)

    def test_biblioteca_vazia_e_aceita(self):
        d = npj.criar_projeto(self.raiz / "hardware", "placa-x", hoje=HOJE)
        kicad_cli.upgrade(AMB, d / "bibliotecas" / "placa-x.kicad_sym")

    def test_netlist_exporta(self):
        d = npj.criar_projeto(self.raiz / "hardware", "placa-x", hoje=HOJE)
        net = kicad_cli.exportar_netlist(AMB, d / "placa-x.kicad_sch", d / "placa-x.net")
        self.assertEqual(sexpr.etiqueta(sexpr.carregar_arquivo(net)), "export")


if __name__ == "__main__":
    unittest.main()
