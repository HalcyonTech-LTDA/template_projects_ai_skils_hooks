"""Placa a partir do esquematico, DRC e roteamento com o KiCad de verdade.

- `verificar.py dru/drc`: pulam sem kicad-cli.
- `pcb_do_esquematico.py`/`rotear.py`: rodam no Python do KiCad por subprocesso; pulam sem pcbnew.
- Freerouting: pula sem `FREEROUTING_JAR` (e Java). Cada roteamento leva ~10-20 s.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import ambiente, modelos, sexpr  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
ASSETS = SCRIPTS.parent / "assets"
EXEMPLO = ASSETS / "exemplo" / "placa-exemplo.json"
AMB = ambiente.detectar()
SEM_KICAD = "kicad-cli nao encontrado"
PCBNEW_OK = AMB.encontrado and ambiente.verificar_pcbnew(AMB)[0]
SEM_PCBNEW = "Python do KiCad com pcbnew nao encontrado"
FR_OK = bool(AMB.freerouting_jar and AMB.java)
SEM_FR = "Freerouting ausente (defina FREEROUTING_JAR; precisa de Java 21+)"


def rodar(script, *args, kicad=False, timeout=900):
    py = str(AMB.kicad_python) if kicad else sys.executable
    r = subprocess.run([py, str(SCRIPTS / script)] + [str(a) for a in args], capture_output=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def rodar_json(script, *args, kicad=False):
    rc, saida, erro = rodar(script, *args, "--json", kicad=kicad)
    try:
        return rc, json.loads(saida)
    except ValueError as e:
        raise AssertionError(f"{script} nao devolveu JSON (rc {rc}): {saida[-800:]} {erro[-800:]}") from e


def kicad_py(codigo, *args):
    """Roda um trecho no Python do KiCad (para montar cenarios de teste)."""
    r = subprocess.run([str(AMB.kicad_python), "-I", "-c", codigo] + [str(a) for a in args], capture_output=True,
                       encoding="utf-8", errors="replace", timeout=300)
    if r.returncode != 0:
        raise AssertionError(f"trecho pcbnew falhou: {r.stderr[-800:]}")
    return r.stdout


@unittest.skipUnless(AMB.encontrado, SEM_KICAD)
class TestVerificarDru(unittest.TestCase):
    def test_aceita_os_assets(self):
        for nome in ("jlc-2camadas", "jlc-4camadas", "alta-tensao"):
            rc, r = rodar_json("verificar.py", "dru", ASSETS / "kicad" / f"{nome}.kicad_dru")
            self.assertEqual((rc, r["ok"]), (0, True), nome)

    def test_rejeita_arquivo_quebrado(self):
        with tempfile.TemporaryDirectory() as tmp:
            dru = Path(tmp) / "quebrado.kicad_dru"
            dru.write_text('(version 1)\n(rule "x"\n\t(constraint clearance (min 1mm))\n', encoding="utf-8")
            rc, r = rodar_json("verificar.py", "dru", dru)
            self.assertEqual((rc, r["ok"]), (1, False))
            dru.write_text('(version 1)\n(rule "x" (condition "A.Naoexiste == 1") (constraint clearance (min 1mm)))\n',
                           encoding="utf-8")
            self.assertEqual(rodar("verificar.py", "dru", dru)[0], 1)


@unittest.skipUnless(AMB.encontrado, SEM_KICAD)
class TestVerificarDrc(unittest.TestCase):
    def test_placa_sem_contorno_falha_com_resumo_por_tipo(self):
        with tempfile.TemporaryDirectory() as tmp:
            pcb = Path(tmp) / "vazia.kicad_pcb"
            sexpr.salvar_arquivo(pcb, modelos.placa_vazia(2, "t", "2026-10-12", "A"))
            rc, r = rodar_json("verificar.py", "drc", pcb)
            self.assertEqual(rc, 1)
            self.assertIn("invalid_outline", [t["tipo"] for t in r["por_tipo"]])
            self.assertFalse(r["paridade_conferida"])
            self.assertEqual(list(Path(tmp).iterdir()), [pcb], "o drc nao deve gravar nada ao lado da placa")


class TestSwigForaDoKicad(unittest.TestCase):
    def test_diz_o_comando_certo(self):
        try:
            import pcbnew  # noqa: F401
            self.skipTest("este Python tem pcbnew")
        except ImportError:
            pass
        for script in ("pcb_do_esquematico.py", "rotear.py"):
            args = ("a.kicad_sch", "--spec", "b.json", "-o", "c.kicad_pcb") if script.startswith("pcb") else ("c.kicad_pcb",)
            rc, _, erro = rodar(script, *args)
            self.assertEqual(rc, 2, script)
            self.assertIn("Python que vem com o KiCad", erro)
            self.assertIn(script, erro)


@unittest.skipUnless(PCBNEW_OK, SEM_PCBNEW)
class TestPlacaDoExemplo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="pcbkit-teste-pcb-")
        hw = Path(cls.tmp) / "hardware & placas"
        cls.dir = hw / "placa-exemplo"
        assert rodar("novo_projeto.py", hw, "--nome", "placa-exemplo")[0] == 0
        cls.sch = cls.dir / "placa-exemplo.kicad_sch"
        cls.pcb = cls.dir / "placa-exemplo.kicad_pcb"
        assert rodar("gerar_esquematico.py", EXEMPLO, "-o", cls.sch)[0] == 0
        cls.rc, cls.r = rodar_json("pcb_do_esquematico.py", cls.sch, "--spec", EXEMPLO, "-o", cls.pcb, kicad=True)
        cls.posicionada = Path(cls.tmp) / "posicionada"
        shutil.copytree(cls.dir, cls.posicionada)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _copia(self, nome):
        destino = Path(self.tmp) / nome / "placa-exemplo"
        shutil.copytree(self.posicionada, destino)
        return destino / "placa-exemplo.kicad_pcb"

    def test_placa_com_31_footprints_furos_e_classes(self):
        self.assertEqual(self.rc, 0, self.r)
        self.assertEqual((self.r["footprints"], self.r["furos"]), (31, 4))
        self.assertEqual(self.r["classes"]["/MOTOR_A"], "Power")
        self.assertEqual(self.r["classes"]["+12V"], "Power")
        self.assertFalse([a for a in self.r["avisos"] if "net class" in a], self.r["avisos"])

    def test_kicad_pro_recebe_os_padroes_com_o_nome_da_placa(self):
        dados = json.loads(self.dir.joinpath("placa-exemplo.kicad_pro").read_text(encoding="utf-8"))
        padroes = {p["pattern"]: p["netclass"] for p in dados["net_settings"]["netclass_patterns"]}
        self.assertEqual(padroes, {"+12V": "Power", "/VIN_FUSE": "Power", "/+12V_SYS": "Power",
                                   "/MOTOR_A": "Power", "/MOTOR_B": "Power"})

    def test_drc_com_paridade_so_falta_rotear(self):
        rc, r = rodar_json("verificar.py", "drc", self.posicionada / "placa-exemplo.kicad_pcb", "--paridade")
        self.assertEqual(rc, 1)
        self.assertEqual(r["paridade"], [], "footprint faltando/sobrando ou rede divergente")
        erros = {t["tipo"] for t in r["por_tipo"] if t["severidade"] == "error"}
        self.assertEqual(erros, {"unconnected_items"})

    def test_nao_sobrescreve_sem_pedir(self):
        rc, _, erro = rodar("pcb_do_esquematico.py", self.posicionada / "placa-exemplo.kicad_sch", "--spec", EXEMPLO,
                            "-o", self.posicionada / "placa-exemplo.kicad_pcb", kicad=True)
        self.assertEqual(rc, 1)
        self.assertIn("--sobrescrever", erro)

    @unittest.skipUnless(FR_OK, SEM_FR)
    def test_rotear_padrao_deixa_so_power(self):
        rc, r = rodar_json("rotear.py", self._copia("padrao"), kicad=True)
        self.assertEqual(rc, 0, r)
        self.assertEqual(r["classes_ignoradas"], ["Power"])
        self.assertEqual(set(r["desconectados_por_classe"]), {"Power"})
        self.assertGreater(r["desconectados_por_classe"]["Power"], 0)

    @unittest.skipUnless(FR_OK, SEM_FR)
    def test_rotear_tudo_chega_a_drc_zero_com_paridade(self):
        pcb = self._copia("tudo")
        rc, r = rodar_json("rotear.py", pcb, "--ignorar-classes", "", kicad=True)
        self.assertEqual(rc, 0, r)
        rc, d = rodar_json("verificar.py", "drc", pcb, "--paridade")
        self.assertEqual((rc, d["erros"], d["paridade"]), (0, 0, []), d["por_tipo"])
        # Rodar de novo numa placa ja roteada nao pode duplicar cobre (o Freerouting rotearia tudo de novo).
        rc, r = rodar_json("rotear.py", pcb, kicad=True)
        self.assertEqual(rc, 0, r)
        self.assertIsNone(r["freerouting"])
        self.assertEqual(r["trilhas_vias_antes"], r["trilhas_vias_depois"])

    @unittest.skipUnless(FR_OK, SEM_FR)
    def test_trilha_existente_e_preservada(self):
        pcb = self._copia("preserva")
        uuid = kicad_py(ADICIONAR_TRILHA, pcb).strip()
        rc, r = rodar_json("rotear.py", pcb, kicad=True)
        self.assertEqual(r["preservadas"], 1)
        self.assertEqual(kicad_py(CONTAR_TRILHA, pcb, uuid).strip(), "1 destravada")


# Trilha de 0,8 mm entre F1.2 e Q1.3 (rede /VIN_FUSE, classe Power) como se a pessoa a tivesse roteado.
ADICIONAR_TRILHA = """
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
pads = {(fp.GetReference(), p.GetNumber()): p for fp in b.GetFootprints() for p in fp.Pads()}
a, c = pads[("F1", "2")], pads[("Q1", "3")]
t = pcbnew.PCB_TRACK(b)
t.SetStart(a.GetPosition()); t.SetEnd(c.GetPosition()); t.SetWidth(pcbnew.FromMM(0.8))
t.SetLayer(pcbnew.F_Cu); t.SetNet(a.GetNet()); b.Add(t)
pcbnew.SaveBoard(sys.argv[1], b, True)
print(t.m_Uuid.AsString())
"""

CONTAR_TRILHA = """
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
alvo = [t for t in b.GetTracks() if t.m_Uuid.AsString() == sys.argv[2]]
iguais = [t for t in b.GetTracks() if alvo and t.GetClass() == "PCB_TRACK" and t.GetStart() == alvo[0].GetStart()
          and t.GetEnd() == alvo[0].GetEnd()]
print(len(iguais), "travada" if alvo and alvo[0].IsLocked() else "destravada")
"""


if __name__ == "__main__":
    unittest.main()
