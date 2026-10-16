"""Testes do parser/serializador S-expression."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import ambiente, sexpr  # noqa: E402
from pcbkit.sexpr import Simbolo  # noqa: E402

AMOSTRA = r'''(kicad_sch
	(version 20260306)
	(generator "eeschema")
	(uuid "28f865a0-4433-4a53-bbd7-b62f276848e4")
	(property "Value" "10k \"1%\" \\ fim")
	(texto "linha1\nlinha2")
	(at 157.48 -85.09 180)
	(layerselection 0x00000000_00000000_55555555_5755f5ff)
	(hide yes)
	(nome "yes")
	(pts
		(xy 1 2) (xy 3.5 4)
	)
	(vazio)
	(string_vazia "")
)
'''


def _ida_e_volta(texto):
    return sexpr.despejar(sexpr.carregar(texto))


class TestCarregar(unittest.TestCase):
    def setUp(self):
        self.no = sexpr.carregar(AMOSTRA)

    def test_tipos(self):
        self.assertIsInstance(self.no[0], Simbolo)
        self.assertEqual(sexpr.valor(self.no, "version"), 20260306)
        self.assertIsInstance(sexpr.valor(self.no, "version"), int)
        self.assertEqual(sexpr.valores(self.no, "at"), [157.48, -85.09, 180])
        self.assertIsInstance(sexpr.valor(self.no, "generator"), str)
        self.assertNotIsInstance(sexpr.valor(self.no, "generator"), Simbolo)

    def test_aspas_preservam_distincao(self):
        # "yes" entre aspas e string; yes sem aspas e Simbolo. Ambos == "yes", por isso o isinstance.
        self.assertIsInstance(sexpr.valor(self.no, "hide"), Simbolo)
        self.assertNotIsInstance(sexpr.valor(self.no, "nome"), Simbolo)

    def test_escapes(self):
        self.assertEqual(sexpr.filho(self.no, "property")[2], '10k "1%" \\ fim')
        self.assertEqual(sexpr.valor(self.no, "texto"), "linha1\nlinha2")

    def test_hex_vira_simbolo(self):
        self.assertIsInstance(sexpr.valor(self.no, "layerselection"), Simbolo)

    def test_vazios(self):
        self.assertEqual(sexpr.filho(self.no, "vazio"), [Simbolo("vazio")])
        self.assertEqual(sexpr.valor(self.no, "string_vazia"), "")

    def test_carregar_todos_le_kicad_dru_com_comentarios(self):
        dru = Path(__file__).resolve().parents[2] / "assets" / "kicad" / "alta-tensao.kicad_dru"
        nos = sexpr.carregar_todos(dru.read_text(encoding="utf-8"), comentarios=True)
        self.assertEqual(nos[0], [Simbolo("version"), 1])
        regras = {str(n[1]) for n in nos if sexpr.etiqueta(n) == "rule"}
        self.assertEqual(regras, {"hv_clearance", "hv_creepage", "hv_cobre_borda"})

    def test_erros(self):
        for ruim in ("(a (b)", "(a))", "", '(a "sem fim)'):
            with self.assertRaises(sexpr.ErroSexpr, msg=ruim):
                sexpr.carregar(ruim)


class TestDespejar(unittest.TestCase):
    def test_round_trip_semantico_e_idempotente(self):
        uma = _ida_e_volta(AMOSTRA)
        self.assertEqual(sexpr.carregar(uma), sexpr.carregar(AMOSTRA))
        self.assertEqual(_ida_e_volta(uma), uma)

    def test_tipos_sobrevivem_ao_round_trip(self):
        no = sexpr.carregar(_ida_e_volta(AMOSTRA))
        self.assertIsInstance(sexpr.valor(no, "hide"), Simbolo)
        self.assertNotIsInstance(sexpr.valor(no, "nome"), Simbolo)

    def test_numeros(self):
        S = Simbolo
        self.assertEqual(sexpr.despejar([S("at"), 1.0, -0.0, 0.1 + 0.2, 2.54, 7]), "(at 1 0 0.3 2.54 7)\n")

    def test_pts_em_linha_e_recuo_por_tab(self):
        texto = _ida_e_volta(AMOSTRA)
        self.assertIn("\t(pts (xy 1 2) (xy 3.5 4))\n", texto)
        self.assertTrue(texto.startswith("(kicad_sch\n\t(version 20260306)\n"))

    def test_tipo_invalido(self):
        with self.assertRaises(sexpr.ErroSexpr):
            sexpr.despejar([Simbolo("a"), object()])


AMB = ambiente.detectar()


@unittest.skipUnless(AMB.share, "KiCad nao instalado")
class TestArquivosReais(unittest.TestCase):
    def _demo(self, *partes):
        caminho = AMB.share.joinpath("demos", *partes)
        if not caminho.exists():
            self.skipTest(f"demo ausente: {caminho}")
        return caminho.read_text(encoding="utf-8")

    def test_round_trip_esquematico_e_placa_do_demo(self):
        for arq in ("ecc83-pp.kicad_sch", "ecc83-pp.kicad_pcb"):
            texto = self._demo("ecc83", arq)
            uma = _ida_e_volta(texto)
            self.assertEqual(sexpr.carregar(uma), sexpr.carregar(texto), arq)
            self.assertEqual(_ida_e_volta(uma), uma, arq)


if __name__ == "__main__":
    unittest.main()
