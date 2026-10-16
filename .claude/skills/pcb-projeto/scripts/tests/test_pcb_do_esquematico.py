"""pcb_do_esquematico.py: o que conta como "placa que ja tem trabalho" e atributos do simbolo no footprint.

- `itens_da_placa`: logica pura (sem KiCad).
- `--sobrescrever` e `aplicar_atributos`: rodam no Python do KiCad por subprocesso; pulam sem pcbnew.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pcb_do_esquematico as pde  # noqa: E402
from pcbkit import ambiente, modelos, sexpr  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
EXEMPLO = SCRIPTS.parent / "assets" / "exemplo" / "placa-exemplo.json"
AMB = ambiente.detectar()
PCBNEW_OK = AMB.encontrado and ambiente.verificar_pcbnew(AMB)[0]
SEM_PCBNEW = "Python do KiCad com pcbnew nao encontrado"

S = sexpr.Simbolo
CONTORNO = [S("gr_rect"), [S("start"), 100, 100], [S("end"), 140, 130],
            [S("stroke"), [S("width"), 0.1], [S("type"), S("default")]], [S("fill"), S("no")],
            [S("layer"), "Edge.Cuts"], [S("uuid"), "4f2c8e1a-0000-4000-8000-000000000001"]]
TRILHA = [S("segment"), [S("start"), 101, 101], [S("end"), 110, 101], [S("width"), 0.25], [S("layer"), "F.Cu"],
          [S("net"), "GND"], [S("uuid"), "4f2c8e1a-0000-4000-8000-000000000002"]]
VIA = [S("via"), [S("at"), 105, 105], [S("size"), 0.6], [S("drill"), 0.3], [S("layers"), "F.Cu", "B.Cu"],
       [S("net"), "GND"], [S("uuid"), "4f2c8e1a-0000-4000-8000-000000000003"]]
TEXTO = [S("gr_text"), "nota", [S("at"), 101, 101, 0], [S("layer"), "F.SilkS"],
         [S("uuid"), "4f2c8e1a-0000-4000-8000-000000000004"]]


def _placa(extras=()):
    return modelos.placa_vazia(2, "t", "2026-10-12", "A") + list(extras)


class TestItensDaPlaca(unittest.TestCase):
    """Achado 17: placa com contorno/trilha/via/zona desenhados a mao nao e 'vazia'."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.pcb = Path(self._tmp.name) / "p.kicad_pcb"

    def _itens(self, extras=()):
        sexpr.salvar_arquivo(self.pcb, _placa(extras))
        return pde.itens_da_placa(self.pcb)

    def test_ausente_e_so_cabecalho_nao_tem_itens(self):
        self.assertEqual(pde.itens_da_placa(self.pcb), {})
        self.assertEqual(self._itens(), {})

    def test_cada_tipo_de_item_conta(self):
        for nome, item, etiqueta in (("contorno", CONTORNO, "gr_rect"), ("trilha", TRILHA, "segment"),
                                     ("via", VIA, "via"), ("texto", TEXTO, "gr_text"),
                                     ("footprint", [S("footprint"), "R_0603"], "footprint"),
                                     ("zona", [S("zone"), [S("net"), 1]], "zone")):
            with self.subTest(nome):
                self.assertEqual(self._itens([item]), {etiqueta: 1})

    def test_conta_e_descreve(self):
        itens = self._itens([CONTORNO, TRILHA, TRILHA, VIA])
        self.assertEqual(itens, {"gr_rect": 1, "segment": 2, "via": 1})
        texto = pde._descrever_itens(itens)
        for trecho in ("2 trilha(s)", "1 via(s)", "1 retangulo(s) de desenho"):
            self.assertIn(trecho, texto)

    def test_redes_e_net_class_do_cabecalho_nao_contam(self):
        self.assertEqual(self._itens([[S("net"), 0, ""], [S("net"), 1, "GND"]]), {})


@unittest.skipUnless(PCBNEW_OK, SEM_PCBNEW)
class TestSobrescreverComItensQuaisquer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="pcbkit-teste-5b-"))
        cls.hw = cls.tmp / "hardware"
        cls.dir = cls.hw / "placa-exemplo"
        assert _rodar("novo_projeto.py", cls.hw, "--nome", "placa-exemplo")[0] == 0
        cls.sch = cls.dir / "placa-exemplo.kicad_sch"
        cls.pcb = cls.dir / "placa-exemplo.kicad_pcb"
        assert _rodar("gerar_esquematico.py", EXEMPLO, "-o", cls.sch)[0] == 0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _pcb_com(self, nome, extras):
        destino = self.tmp / nome
        shutil.copytree(self.dir, destino)
        pcb = destino / "placa-exemplo.kicad_pcb"
        sexpr.salvar_arquivo(pcb, sexpr.carregar_arquivo(pcb) + list(extras))
        return destino, pcb

    def _gerar(self, destino, *extra):
        return _rodar("pcb_do_esquematico.py", destino / "placa-exemplo.kicad_sch", "--spec", EXEMPLO,
                      "-o", destino / "placa-exemplo.kicad_pcb", *extra, kicad=True)

    def test_contorno_a_mao_sem_footprints_exige_sobrescrever(self):
        destino, pcb = self._pcb_com("contorno", [CONTORNO])
        antes = pcb.read_bytes()
        rc, _, erro = self._gerar(destino)
        self.assertEqual(rc, 1)
        self.assertIn("--sobrescrever", erro)
        self.assertIn("retangulo(s) de desenho", erro)
        self.assertEqual(pcb.read_bytes(), antes, "a recusa nao pode tocar na placa")

    def test_trilha_e_via_sem_footprints_tambem(self):
        destino, pcb = self._pcb_com("trilha", [TRILHA, VIA])
        rc, _, erro = self._gerar(destino)
        self.assertEqual(rc, 1)
        self.assertIn("trilha(s)", erro)

    def test_com_a_flag_refaz_a_placa(self):
        destino, pcb = self._pcb_com("flag", [CONTORNO])
        rc, _, erro = self._gerar(destino, "--sobrescrever")
        self.assertEqual(rc, 0, erro)
        self.assertTrue(pde.itens_da_placa(pcb)["footprint"])

    def test_placa_do_novo_projeto_nao_pede_flag(self):
        destino = self.tmp / "limpa"
        shutil.copytree(self.dir, destino)
        rc, _, erro = self._gerar(destino)
        self.assertEqual(rc, 0, erro)


def _rodar(script, *args, kicad=False):
    py = str(AMB.kicad_python) if kicad else sys.executable
    r = subprocess.run([py, str(SCRIPTS / script)] + [str(a) for a in args], capture_output=True,
                       encoding="utf-8", errors="replace", timeout=900)
    return r.returncode, r.stdout, r.stderr


# Atributos do simbolo -> footprint, sem montar a placa: devolve (dnp, fora da BOM, fora da posicao).
TRECHO_ATRIBUTOS = """
import json, sys
sys.path.insert(0, sys.argv[1])
from pcbkit import ambiente
from pcbkit.swig import placa
fp = placa.carregar_footprint(ambiente.detectar(), "Resistor_SMD:R_0603_1608Metric")
placa.aplicar_atributos(fp, json.loads(sys.argv[2]))
print(json.dumps([fp.IsDNP(), fp.IsExcludedFromBOM(), fp.IsExcludedFromPosFiles()]))
"""


def _atributos(props):
    r = subprocess.run([str(AMB.kicad_python), "-I", "-c", TRECHO_ATRIBUTOS, str(SCRIPTS), json.dumps(props)],
                       capture_output=True, encoding="utf-8", errors="replace", timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stderr[-800:])
    return json.loads(r.stdout.strip().splitlines()[-1])


@unittest.skipUnless(PCBNEW_OK, SEM_PCBNEW)
class TestAtributosDoSimbolo(unittest.TestCase):
    """Achado 9: `exclude_from_pos_files` do simbolo chega ao footprint (e dai ao `pcb export pos`)."""

    def test_propaga_cada_atributo(self):
        self.assertEqual(_atributos({}), [False, False, False])
        self.assertEqual(_atributos({"exclude_from_pos_files": ""}), [False, False, True])
        self.assertEqual(_atributos({"exclude_from_bom": ""}), [False, True, False])
        self.assertEqual(_atributos({"dnp": "", "exclude_from_bom": "", "exclude_from_pos_files": ""}),
                         [True, True, True])

    def test_valor_desligado_nao_liga(self):
        self.assertEqual(_atributos({"exclude_from_pos_files": "no"}), [False, False, False])


if __name__ == "__main__":
    unittest.main()
