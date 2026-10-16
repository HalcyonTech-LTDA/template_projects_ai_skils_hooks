"""Validacao da spec (usa as bibliotecas instaladas do KiCad; pula sem elas)."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import ambiente  # noqa: E402
from pcbkit.esquematico import spec  # noqa: E402

AMB = ambiente.detectar()

BASE = {
    "projeto": "teste", "titulo": "Teste", "revisao": "A", "folha": "A4", "tensao_max_v": 12,
    "blocos": [{"id": "a", "titulo": "A", "componentes": ["J1", "R1"]},
               {"id": "b", "titulo": "B", "componentes": ["Q1", "U1"]}],
    "componentes": [
        {"ref": "J1", "simbolo": "Connector:Screw_Terminal_01x02",
         "footprint": "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal"},
        {"ref": "R1", "simbolo": "Device:R", "valor": "10k", "footprint": "Resistor_SMD:R_0603_1608Metric"},
        {"ref": "Q1", "simbolo": "Transistor_FET:AO3401A"},
        {"ref": "U1", "simbolo": "Driver_Motor:DRV8871DDA"},
    ],
    "redes": {
        "+12V": ["J1.1", "R1.1", "U1.VM"],
        "GND": ["J1.2", "U1.1", "U1.7", "U1.9", "U1.ILIM"],
        "GATE": ["R1.2", "Q1.G"],
        "SAIDA": ["Q1.D", "U1.IN1"],
    },
    "nao_conectar": ["Q1.S", "U1.IN2", "U1.OUT1", "U1.OUT2"],
    "pwr_flag": ["+12V", "GND"],
}


@unittest.skipUnless(AMB.share, "bibliotecas do KiCad ausentes")
class TestSpec(unittest.TestCase):
    def _validar(self, mudar=None):
        d = copy.deepcopy(BASE)
        if mudar:
            mudar(d)
        return spec.validar(d, AMB)

    def _erros(self, mudar):
        with self.assertRaises(spec.ErroSpec) as ctx:
            self._validar(mudar)
        return " | ".join(ctx.exception.erros)

    def test_base_valida(self):
        c = self._validar()
        self.assertEqual(list(c.componentes), ["J1", "R1", "Q1", "U1"])
        self.assertEqual(c.componentes["R1"].bloco, "a")
        self.assertEqual(c.redes["SAIDA"].pinos, [("Q1", "3"), ("U1", "3")])
        self.assertIn(("U1", "4"), c.redes["GND"].pinos)      # ILIM resolvido por nome

    def test_power_por_nome_da_biblioteca(self):
        c = self._validar()
        self.assertEqual(c.redes["+12V"].power.lib_id, "power:+12V")
        self.assertEqual(c.redes["GND"].power.lib_id, "power:GND")
        self.assertIsNone(c.redes["GATE"].power)
        self.assertTrue(c.redes["GND"].pwr_flag)

    def test_footprint_vem_do_simbolo(self):
        self.assertEqual(self._validar().componentes["Q1"].footprint, "Package_TO_SOT_SMD:SOT-23")

    def test_nome_que_casa_varios_pinos_avisa(self):
        def mudar(d):
            d["redes"]["GND"] = ["J1.2", "U1.GND", "U1.ILIM"]
        c = self._validar(mudar)
        self.assertTrue(any("U1.GND" in a and "3 pinos" in a for a in c.avisos))
        self.assertTrue({("U1", "1"), ("U1", "7"), ("U1", "9")} <= set(c.redes["GND"].pinos))

    def test_ref_duplicada(self):
        self.assertIn("ref duplicada: R1", self._erros(lambda d: d["componentes"].append(dict(d["componentes"][1]))))

    def test_componente_fora_de_bloco(self):
        self.assertIn("R1 nao esta em nenhum bloco", self._erros(lambda d: d["blocos"][0]["componentes"].remove("R1")))

    def test_componente_em_dois_blocos(self):
        self.assertIn("R1 esta em dois blocos", self._erros(lambda d: d["blocos"][1]["componentes"].append("R1")))

    def test_bloco_cita_componente_inexistente(self):
        self.assertIn("cita 'X9'", self._erros(lambda d: d["blocos"][1]["componentes"].append("X9")))

    def test_simbolo_inexistente(self):
        e = self._erros(lambda d: d["componentes"][1].update(simbolo="Device:NaoExiste"))
        self.assertIn("simbolo 'Device:NaoExiste' nao encontrado", e)

    def test_footprint_inexistente(self):
        e = self._erros(lambda d: d["componentes"][1].update(footprint="Resistor_SMD:R_9999"))
        self.assertIn("footprint 'Resistor_SMD:R_9999' nao encontrado", e)

    def test_componente_sem_footprint(self):
        e = self._erros(lambda d: d["componentes"][1].pop("footprint"))
        self.assertIn("R1: sem footprint", e)

    def test_pino_inexistente(self):
        e = self._erros(lambda d: d["redes"]["SAIDA"].append("U1.XYZ"))
        self.assertIn("pino 'XYZ' nao existe em U1", e)

    def test_rede_com_um_pino(self):
        def mudar(d):
            d["redes"]["SOLTA"] = ["Q1.S"]
            d["nao_conectar"].remove("Q1.S")
        self.assertIn("rede 'SOLTA' tem um pino so", self._erros(mudar))

    def test_pino_em_duas_redes(self):
        e = self._erros(lambda d: d["redes"]["GATE"].append("Q1.D"))
        self.assertIn("pino Q1.3 esta em duas redes", e)

    def test_pino_sem_rede_fora_de_nao_conectar(self):
        e = self._erros(lambda d: d["nao_conectar"].remove("U1.OUT2"))
        self.assertIn("pinos sem rede e fora de 'nao_conectar': U1.8 (OUT2)", e)

    def test_pino_em_rede_e_em_nao_conectar(self):
        e = self._erros(lambda d: d["nao_conectar"].append("R1.1"))
        self.assertIn("R1.1 esta em 'nao_conectar' e na rede '+12V'", e)

    def test_pinos_empilhados_em_redes_diferentes(self):
        def mudar(d):
            d["redes"]["GND"].remove("U1.9")
            d["nao_conectar"].append("U1.9")
        self.assertIn("pinos empilhados", self._erros(mudar))

    def test_simbolo_de_power_como_componente(self):
        def mudar(d):
            d["componentes"].append({"ref": "P1", "simbolo": "power:GND", "footprint": "x"})
            d["blocos"][0]["componentes"].append("P1")
        self.assertIn("simbolo de power", self._erros(mudar))

    def test_pwr_flag_e_classe_com_rede_inexistente(self):
        def mudar(d):
            d["pwr_flag"].append("NADA")
            d["classes_de_rede"] = {"Power": {"redes": ["OUTRA"]}}
        e = self._erros(mudar)
        self.assertIn("pwr_flag cita a rede 'NADA'", e)
        self.assertIn("classe de rede 'Power' cita a rede 'OUTRA'", e)

    def test_campos_obrigatorios_e_folha(self):
        def mudar(d):
            d.pop("tensao_max_v")
            d["folha"] = "Carta"
        e = self._erros(mudar)
        self.assertIn("'tensao_max_v'", e)
        self.assertIn("folha 'Carta' invalida", e)

    def test_tensao_ac_e_booleano_opcional(self):
        self._validar(lambda d: d.update(tensao_ac=True))
        self._validar(lambda d: d.update(tensao_ac=False))
        self.assertIn("tensao_ac deve ser true", self._erros(lambda d: d.update(tensao_ac="sim")))
        self.assertIn("tensao_ac deve ser true", self._erros(lambda d: d.update(tensao_ac=1)))

    def test_junta_todos_os_erros(self):
        def mudar(d):
            d["componentes"][1]["simbolo"] = "Device:NaoExiste"
            d["redes"]["SAIDA"].append("U1.XYZ")
        with self.assertRaises(spec.ErroSpec) as ctx:
            self._validar(mudar)
        self.assertGreaterEqual(len(ctx.exception.erros), 2)


class TestLeitura(unittest.TestCase):
    def test_json_invalido(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("{nao e json")
        self.addCleanup(Path(f.name).unlink)
        with self.assertRaises(spec.ErroSpec) as ctx:
            spec.ler_json(f.name)
        self.assertIn("nao e JSON valido", ctx.exception.erros[0])

    def test_separar_pino(self):
        self.assertEqual(spec.separar_pino("U1.IO0"), ("U1", "IO0"))
        self.assertEqual(spec.separar_pino("U1"), (None, None))


if __name__ == "__main__":
    unittest.main()
