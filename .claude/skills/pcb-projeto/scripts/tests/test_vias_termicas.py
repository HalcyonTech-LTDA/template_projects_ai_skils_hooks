"""Vias termicas de pad exposto ligam cheio na zona (pcbkit.swig.placa.vias_termicas_cheias).

Roda no Python do KiCad por subprocesso; pula sem pcbnew.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import ambiente  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
AMB = ambiente.detectar()
PCBNEW_OK = AMB.encontrado and ambiente.verificar_pcbnew(AMB)[0]

# Carrega o footprint pela biblioteca, aplica a regra e devolve, por pad, (numero, tipo, ligacao local).
TRECHO = """
import json, sys
sys.path.insert(0, sys.argv[1])
from pcbkit import ambiente
from pcbkit.swig import placa
amb = ambiente.detectar()
fp = placa.carregar_footprint(amb, sys.argv[2])
mudou = placa.vias_termicas_cheias(fp)
pads = [[p.GetNumber(), int(p.GetAttribute()), int(p.GetLocalZoneConnection())] for p in fp.Pads()]
print(json.dumps({"mudou": mudou, "pads": pads}))
"""


def aplicar(fp_id):
    r = subprocess.run([str(AMB.kicad_python), "-I", "-c", TRECHO, str(SCRIPTS), fp_id], capture_output=True,
                       encoding="utf-8", errors="replace", timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-800:])
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(PCBNEW_OK, "Python do KiCad com pcbnew nao encontrado")
class TestViasTermicas(unittest.TestCase):
    PTH, SMD, HERDA, CHEIA = 0, 1, -1, 2

    def test_vias_do_pad_exposto_do_drv8871_ficam_cheias(self):
        r = aplicar("Package_SO:Texas_HTSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.95x4.9mm_Mask2.4x3.1mm_ThermalVias")
        vias = [p for p in r["pads"] if p[0] == "9" and p[1] == self.PTH]
        self.assertTrue(vias)
        self.assertEqual(r["mudou"], len(vias))
        self.assertTrue(all(p[2] == self.CHEIA for p in vias))
        outros = [p for p in r["pads"] if not (p[0] == "9" and p[1] == self.PTH)]
        self.assertTrue(all(p[2] == self.HERDA for p in outros), "so as vias do pad exposto mudam")

    def test_pad_com_ligacao_propria_fica_como_esta(self):
        """No ESP32-S3-WROOM-1 as vias do pad 41 ja vem com ligacao cheia no proprio footprint."""
        r = aplicar("RF_Module:ESP32-S3-WROOM-1")
        self.assertEqual(r["mudou"], 0)
        vias = [p for p in r["pads"] if p[0] == "41" and p[1] == self.PTH]
        self.assertTrue(vias and all(p[2] == self.CHEIA for p in vias))

    def test_pad_passante_sem_par_smd_continua_herdando(self):
        r = aplicar("Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical")
        self.assertEqual(r["mudou"], 0)
        self.assertTrue(all(p[2] == self.HERDA for p in r["pads"]))


if __name__ == "__main__":
    unittest.main()
