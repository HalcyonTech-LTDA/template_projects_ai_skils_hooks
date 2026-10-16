"""pcbkit.netlist: leitura da netlist kicadsexpr e comparacao com a spec (sem KiCad)."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import netlist  # noqa: E402

NETLIST = '''(export (version "E")
  (components
    (comp (ref "R1") (value "10k") (footprint "Resistor_SMD:R_0603_1608Metric"))
    (comp (ref "D1") (value "LED") (footprint "LED_SMD:LED_0603_1608Metric"))
    (comp (ref "X9") (value "?") (footprint "")))
  (nets
    (net (code "1") (name "GND") (class "Default") (node (ref "D1") (pin "1") (pinfunction "K") (pintype "passive")))
    (net (code "2") (name "/LED_A") (class "Default")
      (node (ref "R1") (pin "2") (pintype "passive")) (node (ref "D1") (pin "2") (pintype "passive")))
    (net (code "3") (name "Net-(R1-Pad1)") (class "Default")
      (node (ref "R1") (pin "1") (pintype "passive")) (node (ref "X9") (pin "1") (pintype "passive")))
    (net (code "4") (name "unconnected-(X9-Pad2)") (node (ref "X9") (pin "2") (pintype "passive")))))
'''


def _circuito(redes, comps):
    return SimpleNamespace(
        redes={n: SimpleNamespace(pinos=p) for n, p in redes.items()},
        componentes={r: SimpleNamespace(footprint=fp) for r, fp in comps.items()})


class TestNetlist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.NamedTemporaryFile("w", suffix=".net", delete=False, encoding="utf-8") as f:
            f.write(NETLIST)
        cls.net = netlist.ler(f.name)
        Path(f.name).unlink()

    def test_classes_da_netlist_inclusive_composta(self):
        # O KiCad 10 escreve (class "HV,Power") quando a rede casa padroes de duas net classes.
        self.assertEqual(self.net.classes["GND"], ["Default"])
        self.assertEqual(self.net.classes["unconnected-(X9-Pad2)"], [])
        texto = NETLIST.replace('(name "/LED_A") (class "Default")', '(name "/LED_A") (class "HV,Power")')
        with tempfile.NamedTemporaryFile("w", suffix=".net", delete=False, encoding="utf-8") as f:
            f.write(texto)
        self.addCleanup(Path(f.name).unlink)
        self.assertEqual(netlist.ler(f.name).classes["/LED_A"], ["HV", "Power"])
        self.assertEqual(netlist.separar_classes(" HV , Power "), ["HV", "Power"])

    def test_leitura(self):
        self.assertEqual(self.net.redes["/LED_A"], {("R1", "2"), ("D1", "2")})
        self.assertEqual(self.net.componentes["R1"]["footprint"], "Resistor_SMD:R_0603_1608Metric")

    def test_nome_sem_folha(self):
        self.assertEqual(netlist.nome_sem_folha("/LED_A"), "LED_A")
        self.assertEqual(netlist.nome_sem_folha("GND"), "GND")
        self.assertEqual(netlist.nome_sem_folha("/sub/X"), "/sub/X")

    def test_divergencias(self):
        circ = _circuito({"LED_A": [("R1", "2"), ("D1", "2")],
                          "GND": [("D1", "1"), ("R1", "1")],
                          "VCC": [("R1", "1"), ("D1", "9")]},
                         {"R1": "Resistor_SMD:R_0603_1608Metric", "D1": "LED_SMD:LED_0805_2012Metric", "Q1": "x"})
        d = netlist.comparar(circ, self.net)
        self.assertFalse(d.ok)
        self.assertEqual(d.redes_faltando, ["VCC"])
        self.assertEqual(d.pinos_faltando, {"GND": ["R1.1"]})
        self.assertEqual(d.pinos_sobrando, {})
        self.assertEqual(d.redes_inesperadas, {"Net-(R1-Pad1)": ["R1.1", "X9.1"]})
        self.assertEqual(d.componentes_faltando, ["Q1"])
        self.assertEqual(d.componentes_sobrando, ["X9"])
        self.assertEqual(d.footprints_diferentes, {"D1": ("LED_SMD:LED_0805_2012Metric", "LED_SMD:LED_0603_1608Metric")})

    def test_tudo_certo(self):
        circ = _circuito({"LED_A": [("D1", "2"), ("R1", "2")], "GND": [("D1", "1")], "N": [("R1", "1"), ("X9", "1")]},
                         {"R1": "Resistor_SMD:R_0603_1608Metric", "D1": "LED_SMD:LED_0603_1608Metric", "X9": ""})
        circ.redes["N"] = SimpleNamespace(pinos=[("R1", "1"), ("X9", "1")])
        net = netlist.Netlist({k.replace("Net-(R1-Pad1)", "/N"): v for k, v in self.net.redes.items()},
                              self.net.componentes)
        self.assertTrue(netlist.comparar(circ, net).ok)


if __name__ == "__main__":
    unittest.main()
