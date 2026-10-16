"""Testes de pcbkit.bibliotecas: biblioteca falsa (sem KiCad) e bibliotecas reais (pula sem KiCad)."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import ambiente, bibliotecas  # noqa: E402

PAI = '''(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")
  (symbol "AMP"
    (property "Reference" "U" (at 0 5 0))
    (property "Value" "AMP" (at 0 -5 0))
    (property "Description" "Amplificador duplo generico" (at 0 0 0))
    (property "ki_keywords" "opamp dual" (at 0 0 0))
    (symbol "AMP_1_1"
      (pin output line (at 7.62 0 180) (length 2.54) (name "~" (effects)) (number "1" (effects)))
      (pin input line (at -7.62 2.54 0) (length 2.54) (name "+" (effects)) (number "3" (effects))))
    (symbol "AMP_2_1"
      (pin output line (at 7.62 0 180) (length 2.54) (name "~" (effects)) (number "7" (effects))))
    (symbol "AMP_3_1"
      (pin power_in line (at 0 -7.62 90) (length 3.81) (hide yes) (name "V-" (effects)) (number "4" (effects))))))
'''
FILHO = '''(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")
  (symbol "AMP2"
    (extends "AMP")
    (property "Reference" "U" (at 0 5 0))
    (property "Value" "AMP2" (at 0 -5 0))
    (property "Description" "Variante de baixo ruido" (at 0 0 0))
    (property "MPN" "XYZ123" (at 0 0 0))))
'''
GND = '''(kicad_symbol_lib (version 20251024) (generator "kicad_symbol_editor") (generator_version "10.0")
  (symbol "GND" (power global)
    (property "Reference" "#PWR" (at 0 0 0))
    (property "Value" "GND" (at 0 0 0))
    (symbol "GND_0_1")
    (symbol "GND_1_1" (pin power_in line (at 0 0 270) (length 0) (name "~" (effects)) (number "1" (effects))))))
'''
TABELA_TEMPLATE = '''(sym_lib_table (version 7)
  (lib (name "Falsa") (type "KiCad") (uri "${KICAD10_SYMBOL_DIR}/Falsa.kicad_symdir") (options "") (descr "teste"))
  (lib (name "power") (type "KiCad") (uri "${KICAD10_SYMBOL_DIR}/power.kicad_sym") (options "") (descr ""))
  (lib (name "Desligada") (type "KiCad") (uri "/nao/existe") (options "") (descr "") (disabled)))
'''
TABELA_FP_TEMPLATE = '''(fp_lib_table (version 7)
  (lib (name "Res") (type "KiCad") (uri "${KICAD10_FOOTPRINT_DIR}/Res.pretty") (options "") (descr "")))
'''
TABELA_GLOBAL = '''(sym_lib_table (version 7)
  (lib (name "KiCad") (type "Table") (uri "${KICAD10_TEMPLATE_DIR}/sym-lib-table") (options "") (descr "")))
'''
FP_0603 = '''(footprint "R_0603_1608Metric" (version 20260206) (generator "x") (layer "F.Cu")
  (descr "Resistor SMD 0603") (tags "resistor")
  (pad "1" smd roundrect (at -0.8 0) (size 0.8 0.9) (layers "F.Cu"))
  (pad "2" smd roundrect (at 0.8 0) (size 0.8 0.9) (layers "F.Cu")))
'''


def _escrever(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def _sem_variaveis_kicad():
    return {k: v for k, v in os.environ.items() if not k.startswith("KICAD")}


class BaseFalsa(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="pcbkit-bib-")
        raiz = Path(self._tmp.name)
        share = raiz / "share" / "kicad"
        _escrever(share / "symbols" / "Falsa.kicad_symdir" / "AMP.kicad_sym", PAI)
        _escrever(share / "symbols" / "Falsa.kicad_symdir" / "AMP2.kicad_sym", FILHO)
        _escrever(share / "symbols" / "power.kicad_sym", GND)
        _escrever(share / "template" / "sym-lib-table", TABELA_TEMPLATE)
        _escrever(share / "template" / "fp-lib-table", TABELA_FP_TEMPLATE)
        _escrever(share / "footprints" / "Res.pretty" / "R_0603_1608Metric.kicad_mod", FP_0603)
        _escrever(raiz / "config" / "sym-lib-table", TABELA_GLOBAL)   # global aninhada (type Table)
        self.raiz = raiz
        self.amb = ambiente.Ambiente(share=share, maior=10, dir_config=raiz / "config")
        patch = mock.patch.dict(os.environ, _sem_variaveis_kicad(), clear=True)
        patch.start()
        self.addCleanup(patch.stop)
        self.addCleanup(self._tmp.cleanup)


class TestTabelas(BaseFalsa):
    def test_tabela_global_aninhada_e_variaveis(self):
        nomes = [e.nome for e in bibliotecas.tabela(self.amb, "sym")]
        self.assertEqual(nomes, ["Falsa", "power"])     # Desligada e ignorada
        e = bibliotecas.entrada(self.amb, "Falsa")
        self.assertTrue(e.caminho.is_dir())

    def test_sem_tabela_global_usa_template(self):
        self.amb.dir_config = self.raiz / "nao-existe"
        self.assertEqual([e.nome for e in bibliotecas.tabela(self.amb, "fp")], ["Res"])

    def test_tabela_do_projeto_vence_e_kiprjmod(self):
        proj = self.raiz / "proj com espaco & acento-ção"
        _escrever(proj / "bibliotecas" / "minha.kicad_sym", GND.replace('"GND"', '"TERRA"').replace("GND_", "TERRA_"))
        _escrever(proj / "sym-lib-table", '(sym_lib_table (version 7) (lib (name "power") (type "KiCad") '
                                          '(uri "${KIPRJMOD}/bibliotecas/minha.kicad_sym") (options "") (descr "")))')
        s = bibliotecas.carregar_simbolo(self.amb, "power:TERRA", proj)
        self.assertTrue(s.power)
        with self.assertRaises(bibliotecas.ErroBiblioteca):
            bibliotecas.carregar_simbolo(self.amb, "power:GND", proj)

    def test_lib_inexistente(self):
        with self.assertRaises(bibliotecas.ErroBiblioteca):
            bibliotecas.carregar_simbolo(self.amb, "Nada:R")
        with self.assertRaises(bibliotecas.ErroBiblioteca):
            bibliotecas.carregar_simbolo(self.amb, "sem-dois-pontos")


class TestSimbolos(BaseFalsa):
    def test_pinos_e_unidades(self):
        s = bibliotecas.carregar_simbolo(self.amb, "Falsa:AMP")
        self.assertEqual(s.unidades, 3)
        self.assertIsNone(s.extends)
        p = {x.numero: x for x in s.pinos}
        self.assertEqual(set(p), {"1", "3", "7", "4"})
        self.assertEqual((p["3"].nome, p["3"].tipo, p["3"].x, p["3"].y, p["3"].angulo, p["3"].comprimento, p["3"].unidade),
                         ("+", "input", -7.62, 2.54, 0.0, 2.54, 1))
        self.assertTrue(p["4"].oculto)
        self.assertEqual(p["4"].unidade, 3)

    def test_extends_achata(self):
        s = bibliotecas.carregar_simbolo(self.amb, "Falsa:AMP2")
        self.assertEqual(s.extends, "AMP")
        self.assertEqual(s.unidades, 3)
        self.assertEqual(len(s.pinos), 4)
        self.assertEqual(s.propriedades["Value"], "AMP2")
        self.assertEqual(s.propriedades["Description"], "Variante de baixo ruido")
        self.assertEqual(s.propriedades["MPN"], "XYZ123")
        self.assertEqual(s.propriedades["ki_keywords"], "opamp dual")   # herdada do pai
        unidades = [str(x[1]) for x in s.no if bibliotecas.etiqueta(x) == "symbol"]
        self.assertEqual(unidades, ["AMP2_1_1", "AMP2_2_1", "AMP2_3_1"])
        self.assertIsNone(bibliotecas.valor(s.no, "extends"))

    def test_no_embutido_usa_lib_id(self):
        s = bibliotecas.carregar_simbolo(self.amb, "Falsa:AMP2")
        self.assertEqual(bibliotecas.no_embutido(s)[1], "Falsa:AMP2")

    def test_power(self):
        s = bibliotecas.carregar_simbolo(self.amb, "power:GND")
        self.assertTrue(s.power)
        self.assertEqual([(p.numero, p.tipo) for p in s.pinos], [("1", "power_in")])


class TestBusca(BaseFalsa):
    def test_busca_por_nome_e_por_descricao(self):
        self.assertEqual([a.lib_id for a in bibliotecas.buscar_simbolos(self.amb, "amp2")], ["Falsa:AMP2"])
        self.assertEqual([a.lib_id for a in bibliotecas.buscar_simbolos(self.amb, "baixo ruido")], ["Falsa:AMP2"])
        self.assertEqual(bibliotecas.buscar_simbolos(self.amb, "inexistente"), [])

    def test_nome_exato_primeiro(self):
        achados = bibliotecas.buscar_simbolos(self.amb, "amp")
        self.assertEqual(achados[0].lib_id, "Falsa:AMP")

    def test_footprint(self):
        achados = bibliotecas.buscar_footprints(self.amb, "0603")
        self.assertEqual([a.lib_id for a in achados], ["Res:R_0603_1608Metric"])
        arq = bibliotecas.resolver_footprint(self.amb, "Res:R_0603_1608Metric")
        self.assertEqual(bibliotecas.pads_footprint(arq), ["1", "2"])
        self.assertEqual(bibliotecas.listar_footprints(self.amb, "Res"), ["R_0603_1608Metric"])


AMB = ambiente.detectar()


@unittest.skipUnless(AMB.share and AMB.dir_simbolos() and AMB.dir_simbolos().exists(), "KiCad nao instalado")
class TestBibliotecasReais(unittest.TestCase):
    def test_device_r_tem_dois_pinos_passivos(self):
        s = bibliotecas.carregar_simbolo(AMB, "Device:R")
        self.assertEqual(sorted((p.numero, p.tipo) for p in s.pinos), [("1", "passive"), ("2", "passive")])

    def test_simbolo_com_extends(self):
        s = bibliotecas.carregar_simbolo(AMB, "Amplifier_Operational:LM358")
        self.assertEqual(s.extends, "LM2904")
        self.assertEqual(s.unidades, 3)
        self.assertEqual(s.propriedades["Value"], "LM358")
        self.assertEqual(len({p.numero for p in s.pinos}), 8)

    def test_busca_esp32_s3(self):
        ids = [a.lib_id for a in bibliotecas.buscar_simbolos(AMB, "ESP32-S3")]
        self.assertIn("RF_Module:ESP32-S3-WROOM-1", ids)

    def test_busca_footprint_0603(self):
        ids = [a.lib_id for a in bibliotecas.buscar_footprints(AMB, "0603")]
        self.assertIn("Resistor_SMD:R_0603_1608Metric", ids)

    def test_pecas_da_placa_exemplo_existem(self):
        for lib_id in ("Driver_Motor:DRV8871DDA", "Regulator_Switching:AP63203WU", "Transistor_FET:AO3401A",
                       "Device:Polyfuse", "Device:D_Zener", "Connector:Screw_Terminal_01x02",
                       "power:+12V", "power:+3V3", "power:GND", "power:PWR_FLAG"):
            with self.subTest(lib_id=lib_id):
                bibliotecas.carregar_simbolo(AMB, lib_id)


if __name__ == "__main__":
    unittest.main()
