"""Testes dos campos da netlist que a placa usa (uuid do simbolo, folha, campos, pino -> rede)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import netlist  # noqa: E402

# Formato do `kicad-cli sch export netlist --format kicadsexpr` do 10.0.0 (trecho do exemplo).
NETLIST = '''(export
	(version "E")
	(components
		(comp
			(ref "R1")
			(value "10k")
			(footprint "Resistor_SMD:R_0603_1608Metric")
			(datasheet "https://x")
			(fields
				(field (name "MPN") "0603WAF1002T5E")
				(field (name "Footprint") "Resistor_SMD:R_0603_1608Metric")
				(field (name "Description") "Resistor"))
			(property (name "Sheetname") (value ""))
			(property (name "Sheetfile") (value "placa.kicad_sch"))
			(property (name "dnp") (value ""))
			(sheetpath (names "/") (tstamps "/"))
			(tstamps "c35a303d-71d7-584f-9636-f66197e00026"))
		(comp
			(ref "J1")
			(value "Entrada")
			(footprint "TerminalBlock:X")
			(sheetpath (names "/") (tstamps "/"))
			(tstamps "dd684d4d-7200-5c6d-9ee6-f373c58e9e82")))
	(nets
		(net (code "1") (name "+12V") (class "Default")
			(node (ref "J1") (pin "1") (pinfunction "Pin_1_1") (pintype "passive"))
			(node (ref "R1") (pin "1") (pintype "passive")))
		(net (code "2") (name "/SINAL") (class "Default")
			(node (ref "R1") (pin "2") (pintype "passive"))
			(node (ref "J1") (pin "2") (pinfunction "Pin_2") (pintype "passive")))
		(net (code "3") (name "unconnected-(U1-IO7-Pad7)") (class "Default")
			(node (ref "U1") (pin "7") (pinfunction "IO7") (pintype "bidirectional")))))
'''


class TestNetlistParaPlaca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            arq = Path(tmp) / "x.net"
            arq.write_text(NETLIST, encoding="utf-8")
            cls.nl = netlist.ler(arq)

    def test_uuid_folha_e_campos(self):
        r1 = self.nl.componentes["R1"]
        self.assertEqual(r1["uuid"], "c35a303d-71d7-584f-9636-f66197e00026")
        self.assertEqual((r1["folha"], r1["caminho_folha"], r1["arquivo_folha"]), ("/", "/", "placa.kicad_sch"))
        self.assertEqual(r1["campos"]["MPN"], "0603WAF1002T5E")
        self.assertIn("dnp", r1["propriedades"])
        self.assertEqual(self.nl.componentes["J1"]["campos"], {})

    def test_pino_para_rede_com_funcao_e_tipo(self):
        self.assertEqual(self.nl.pinos[("J1", "1")], {"rede": "+12V", "funcao": "Pin_1_1", "tipo": "passive"})
        self.assertEqual(self.nl.pinos[("R1", "2")]["rede"], "/SINAL")
        self.assertEqual(self.nl.pinos[("U1", "7")]["rede"], "unconnected-(U1-IO7-Pad7)")

    def test_nome_na_placa(self):
        self.assertEqual(netlist.nome_na_placa(self.nl, "SINAL"), "/SINAL")
        self.assertEqual(netlist.nome_na_placa(self.nl, "+12V"), "+12V")
        self.assertIsNone(netlist.nome_na_placa(self.nl, "GND"))

    def test_continua_compativel_com_a_comparacao(self):
        self.assertEqual(self.nl.redes["/SINAL"], {("R1", "2"), ("J1", "2")})
        self.assertEqual(self.nl.componentes["R1"]["footprint"], "Resistor_SMD:R_0603_1608Metric")


if __name__ == "__main__":
    unittest.main()
