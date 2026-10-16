"""Testes de pcbkit.regras (.kicad_pro/.kicad_dru a partir da spec) e do resumo de DRC (pcbkit.drc)."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import drc, kicad_cli, regras  # noqa: E402

MODELO = json.loads(regras.MODELO_PRO.read_text(encoding="utf-8"))
NA_PLACA = {"+12V": "+12V", "MOTOR_A": "/MOTOR_A", "VIN_FUSE": "/VIN_FUSE", "SINAL": "/SINAL"}


class TestAplicarClasses(unittest.TestCase):
    def setUp(self):
        self.dados = copy.deepcopy(MODELO)

    def _aplicar(self, classes):
        return regras.aplicar_classes(self.dados, classes, NA_PLACA.get)

    def test_padrao_usa_o_nome_como_a_placa_ve(self):
        atrib, avisos = self._aplicar({"Power": {"redes": ["+12V", "MOTOR_A"], "largura_mm": 1.2, "clearance_mm": 0.4}})
        self.assertEqual(avisos, [])
        self.assertEqual(atrib, {"+12V": "Power", "/MOTOR_A": "Power"})
        padroes = self.dados["net_settings"]["netclass_patterns"]
        self.assertIn({"netclass": "Power", "pattern": "/MOTOR_A"}, padroes)
        power = next(c for c in self.dados["net_settings"]["classes"] if c["name"] == "Power")
        self.assertEqual((power["track_width"], power["clearance"]), (1.2, 0.4))

    def test_reaplicar_troca_o_padrao_da_mesma_rede_e_mantem_os_outros(self):
        self.dados["net_settings"]["netclass_patterns"] = [{"netclass": "HV", "pattern": "/MOTOR_A"},
                                                           {"netclass": "HV", "pattern": "REDE_MANUAL"}]
        self._aplicar({"Power": {"redes": ["MOTOR_A"]}})
        self._aplicar({"Power": {"redes": ["MOTOR_A"]}})
        padroes = self.dados["net_settings"]["netclass_patterns"]
        self.assertEqual(padroes, [{"netclass": "HV", "pattern": "REDE_MANUAL"},
                                   {"netclass": "Power", "pattern": "/MOTOR_A"}])

    def test_classe_nova_copia_a_default(self):
        self._aplicar({"Sinal_Fino": {"redes": ["SINAL"], "largura_mm": 0.2}})
        nova = next(c for c in self.dados["net_settings"]["classes"] if c["name"] == "Sinal_Fino")
        self.assertEqual(nova["track_width"], 0.2)
        self.assertEqual(nova["via_diameter"], 0.6)

    def test_rede_que_nao_existe_vira_aviso(self):
        atrib, avisos = self._aplicar({"Power": {"redes": ["NAO_EXISTE"]}})
        self.assertEqual(atrib, {})
        self.assertTrue(avisos and "NAO_EXISTE" in avisos[0])

    def test_classe_da_rede_com_curinga(self):
        self.dados["net_settings"]["netclass_patterns"] = [{"netclass": "Power", "pattern": "/MOTOR_*"},
                                                           {"netclass": "HV", "pattern": "+12V"}]
        self.assertEqual(regras.classe_da_rede(self.dados, "/MOTOR_B"), "Power")
        self.assertEqual(regras.classe_da_rede(self.dados, "+12V"), "HV")
        self.assertEqual(regras.classe_da_rede(self.dados, "+12"), "Default")
        self.assertEqual(regras.classe_da_rede(self.dados, "/SINAL"), "Default")

    def test_padrao_regex_e_classe_composta_como_o_kicad(self):
        # Medido no 10.0.0 pela classe na netlist: regex vale, tudo ancorado e sensivel a maiusculas, e a rede
        # que casa duas classes fica na composta, a de menor `priority` primeiro (HV 0, Power 1 no modelo).
        self.dados["net_settings"]["netclass_patterns"] = [
            {"netclass": "Power", "pattern": "/MOTOR_A"}, {"netclass": "HV", "pattern": "/MOTOR_(A|B)"},
            {"netclass": "HV", "pattern": "/VIN_F.SE"}, {"netclass": "HV", "pattern": "/motor_*"},
            {"netclass": "Power", "pattern": "LED"}]
        self.assertEqual(regras.classe_da_rede(self.dados, "/MOTOR_A"), "HV,Power")
        self.assertEqual(regras.classes_da_rede(self.dados, "/MOTOR_A"), ["HV", "Power"])
        self.assertEqual(regras.classe_da_rede(self.dados, "/MOTOR_B"), "HV")
        self.assertEqual(regras.classe_da_rede(self.dados, "/VIN_FUSE"), "HV")
        self.assertEqual(regras.classe_da_rede(self.dados, "/LED_A"), "Default")      # ancorado
        self.assertEqual(regras.classe_da_rede(self.dados, "/MOTOR_C"), "Default")    # /motor_* nao casa

    def test_tem_classe(self):
        self.assertTrue(regras.tem_classe("HV,Power", {"Power"}))
        self.assertTrue(regras.tem_classe("HV", {"Power", "HV"}))
        self.assertFalse(regras.tem_classe("Default", {"Power", "HV"}))


class TestGarantirArquivos(unittest.TestCase):
    def test_copia_modelos_que_faltam_e_nao_sobrescreve(self):
        with tempfile.TemporaryDirectory() as tmp:
            pcb = Path(tmp) / "placa.kicad_pcb"
            avisos = regras.garantir_arquivos(pcb, camadas=4)
            pro, dru = regras.caminhos(pcb)
            self.assertEqual(len(avisos), 2)
            self.assertEqual(regras.ler_pro(pro)["meta"]["filename"], "placa.kicad_pro")
            self.assertEqual(dru.read_text(encoding="utf-8"), regras.MODELOS_DRU[4].read_text(encoding="utf-8"))
            dru.write_text("(version 1)\n", encoding="utf-8")
            self.assertEqual(regras.garantir_arquivos(pcb), [])
            self.assertEqual(dru.read_text(encoding="utf-8"), "(version 1)\n")


class TestResumoDrc(unittest.TestCase):
    def _rel(self):
        def item(desc):
            return {"description": desc, "uuid": "u"}
        nc = [{"type": "unconnected_items", "severity": "error", "description": "x",
               "items": [item("Ilha 1 [/MOTOR_A] de U3 no F.Cu"), item("Ilha 1 [/MOTOR_A] de J2 no F.Cu")]},
              {"type": "unconnected_items", "severity": "error", "description": "x",
               "items": [item("Pad 2 [/SINAL] of R1 on F.Cu")]}]
        viol = [{"type": "silk_overlap", "severity": "warning", "description": "s", "items": []}]
        return kicad_cli.Relatorio("drc", 5, Path("x.json"), {}, viol, nc, [])

    def test_rede_entre_colchetes_em_qualquer_idioma(self):
        self.assertEqual(drc.rede_do_item("Ilha 2 [/+12V_SYS] de Q1 no F.Cu"), "/+12V_SYS")
        self.assertEqual(drc.rede_do_item("Zone [GND] on F.Cu"), "GND")
        self.assertIsNone(drc.rede_do_item("Retangulo no Edge.Cuts"))

    def test_desconectados_por_rede_e_por_classe(self):
        dados = copy.deepcopy(MODELO)
        dados["net_settings"]["netclass_patterns"] = [{"netclass": "Power", "pattern": "/MOTOR_A"}]
        r = drc.resumir(self._rel(), dados)
        self.assertEqual(r["desconectados_por_rede"], {"/MOTOR_A": 1, "/SINAL": 1})
        self.assertEqual(r["desconectados_por_classe"], {"Default": 1, "Power": 1})
        self.assertEqual((r["erros"], r["avisos"], r["desconectados"]), (2, 1, 2))
        self.assertEqual(drc.resumir(self._rel())["desconectados_por_classe"], {"Default": 2})

    def test_reprova_paridade_em_qualquer_severidade(self):
        # no KiCad 10.0.0 um footprint faltando sai como `missing_footprint` de severidade warning
        silk = [{"type": "silk_edge_clearance", "severity": "warning", "description": "s", "items": []}]
        falta = [{"type": "missing_footprint", "severity": "warning", "description": "R1", "items": []}]
        so_aviso = drc.resumir(kicad_cli.Relatorio("drc", 5, Path("x.json"), {}, silk, [], []))
        com_paridade = drc.resumir(kicad_cli.Relatorio("drc", 5, Path("x.json"), {}, silk, [], falta))
        self.assertEqual((so_aviso["erros"], com_paridade["erros"]), (0, 0))
        self.assertFalse(drc.reprova(so_aviso))
        self.assertTrue(drc.reprova(so_aviso, estrito=True))
        self.assertTrue(drc.reprova(com_paridade))
        self.assertTrue(drc.reprova(drc.resumir(self._rel())))   # conexao faltando

    def test_desconectados_em_classe_composta(self):
        dados = copy.deepcopy(MODELO)
        dados["net_settings"]["netclass_patterns"] = [{"netclass": "Power", "pattern": "/MOTOR_A"},
                                                      {"netclass": "HV", "pattern": "/MOTOR_(A|B)"}]
        self.assertEqual(drc.desconectados_por_classe(self._rel(), dados), {"Default": 1, "HV,Power": 1})


if __name__ == "__main__":
    unittest.main()
