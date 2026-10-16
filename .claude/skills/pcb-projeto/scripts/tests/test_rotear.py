"""rotear.py: classes ignoradas e pendencias com classe composta (sem KiCad; `import rotear` nao carrega o pcbnew)."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rotear  # noqa: E402
from pcbkit import kicad_cli, regras  # noqa: E402

# Classes como o KiCad 10 exporta no DSN quando /MOTOR_A casa padroes de HV e de Power (medido).
CLASSES_DSN = {"kicad_default": ["+3V3", "/LED_A"], "Power": ["+12V", "/VIN_FUSE"], "HV,Power": ["/MOTOR_A", "/MOTOR_B"]}


def _nc(rede):
    return {"type": "unconnected_items", "severity": "error", "description": "x",
            "items": [{"description": f"Pad 1 [{rede}] de X no F.Cu", "uuid": "u"}]}


class TestIgnoradas(unittest.TestCase):
    def test_classe_composta_ignorada_se_alguma_parte_for_pedida(self):
        for pedidas in (["Power", "HV"], ["HV"], ["Power"]):
            ativas, redes = rotear._ignoradas(pedidas, CLASSES_DSN)
            self.assertIn("HV,Power", ativas, pedidas)
            self.assertIn("/MOTOR_A", redes, pedidas)

    def test_so_hv_nao_ignora_power_simples(self):
        ativas, redes = rotear._ignoradas(["HV"], CLASSES_DSN)
        self.assertEqual(ativas, ["HV,Power"])
        self.assertNotIn("+12V", redes)

    def test_default_e_vazio(self):
        self.assertEqual(rotear._ignoradas(["Default"], CLASSES_DSN)[0], ["kicad_default"])
        self.assertEqual(rotear._ignoradas([], CLASSES_DSN), ([], []))

    def test_flag_do_freerouting_so_leva_nomes_simples(self):
        # A virgula separa a lista na flag ignore_net_classes: a composta e protegida pelo filtro do SES.
        self.assertEqual(rotear._para_freerouting(["HV,Power", "Power", "kicad_default"]), ["Power", "kicad_default"])


class TestPendencias(unittest.TestCase):
    def test_composta_nao_conta_fora_das_ignoradas(self):
        with tempfile.TemporaryDirectory() as tmp:
            pcb = Path(tmp) / "p.kicad_pcb"
            dados = copy.deepcopy(regras.ler_pro(regras.MODELO_PRO))
            dados["net_settings"]["netclass_patterns"] = [{"netclass": "Power", "pattern": "/MOTOR_A"},
                                                          {"netclass": "HV", "pattern": "/MOTOR_(A|B)"}]
            regras.gravar_pro(pcb.with_suffix(".kicad_pro"), dados)
            rel = kicad_cli.Relatorio("drc", 5, Path("x.json"), {}, [], [_nc("/MOTOR_A"), _nc("/SINAL")], [])
            so_hv = rotear._pendencias(rel, pcb, ["HV"])
            nada = rotear._pendencias(rel, pcb, [])
        self.assertEqual(so_hv["desconectados_por_classe"], {"Default": 1, "HV,Power": 1})
        self.assertEqual(so_hv["desconectados_fora_das_ignoradas"], {"Default": 1})
        self.assertEqual(nada["desconectados_fora_das_ignoradas"], {"Default": 1, "HV,Power": 1})


if __name__ == "__main__":
    unittest.main()
