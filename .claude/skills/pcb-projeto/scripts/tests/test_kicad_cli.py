"""Testes de pcbkit.kicad_cli e dos assets .kicad_dru/.kicad_pro (os que rodam o kicad-cli pulam sem KiCad)."""
import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import ambiente, kicad_cli  # noqa: E402
from pcbkit.sexpr import Simbolo as S, salvar_arquivo  # noqa: E402

ASSETS = Path(__file__).resolve().parents[2] / "assets" / "kicad"
AMB = ambiente.detectar()
SEM_KICAD = "kicad-cli nao encontrado"

RELATORIO_ERC = {"$schema": "https://schemas.kicad.org/erc.v1.json", "sheets": [
    {"path": "/", "violations": [{"type": "pin_not_connected", "severity": "error", "description": "x"}]},
    {"path": "/sub/", "violations": [{"type": "lib_symbol_mismatch", "severity": "warning", "description": "y"}]}]}
RELATORIO_DRC = {"$schema": "https://schemas.kicad.org/drc.v1.json",
                 "violations": [{"type": "clearance", "severity": "error", "description": "a"}],
                 "unconnected_items": [{"type": "unconnected_items", "severity": "error", "description": "b"}],
                 "schematic_parity": [{"type": "missing_footprint", "severity": "warning", "description": "c"}]}


class TestRelatorios(unittest.TestCase):
    def _gravar(self, dados):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(dados, tmp)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink)
        return tmp.name

    def test_erc_junta_todas_as_folhas(self):
        rel = kicad_cli.ler_relatorio_erc(self._gravar(RELATORIO_ERC))
        self.assertEqual((rel.total, rel.erros, rel.avisos), (2, 1, 1))

    def test_drc_conta_desconectados_e_paridade(self):
        rel = kicad_cli.ler_relatorio_drc(self._gravar(RELATORIO_DRC))
        self.assertEqual((rel.total, rel.erros, rel.avisos), (3, 2, 1))

    def test_relatorio_ausente(self):
        with self.assertRaises(kicad_cli.ErroKicadCli):
            kicad_cli.ler_relatorio_drc("nao-existe.json")


def _placa_teste():
    """Trilha fina (0,1 mm), via pequena (0,5 mm) e via a 0,125 mm de uma trilha de outra rede."""
    def seg(x1, y1, x2, y2, w, rede):
        return [S("segment"), [S("start"), x1, y1], [S("end"), x2, y2], [S("width"), w],
                [S("layer"), "F.Cu"], [S("net"), rede], [S("uuid"), str(uuid.uuid4())]]

    def via(x, y, d, rede):
        return [S("via"), [S("at"), x, y], [S("size"), d], [S("drill"), 0.3], [S("layers"), "F.Cu", "B.Cu"],
                [S("net"), rede], [S("uuid"), str(uuid.uuid4())]]
    return [S("kicad_pcb"), [S("version"), 20260206], [S("generator"), "pcbkit"], [S("generator_version"), "10.0"],
            [S("general"), [S("thickness"), 1.6], [S("legacy_teardrops"), S("no")]], [S("paper"), "A4"],
            [S("layers"), [0, "F.Cu", S("signal")], [2, "B.Cu", S("signal")], [25, "Edge.Cuts", S("user")]],
            [S("setup"), [S("pad_to_mask_clearance"), 0]],
            [S("gr_rect"), [S("start"), 100, 100], [S("end"), 150, 130],
             [S("stroke"), [S("width"), 0.1], [S("type"), S("default")]], [S("fill"), S("no")],
             [S("layer"), "Edge.Cuts"], [S("uuid"), str(uuid.uuid4())]],
            seg(110, 110, 120, 110, 0.1, "A"), seg(111, 120, 121, 120, 0.25, "B"),
            via(115, 120.55, 0.6, "A"), via(135, 115, 0.5, "C"), [S("embedded_fonts"), S("no")]]


@unittest.skipUnless(AMB.encontrado, SEM_KICAD)
class TestAssetsNoKicad(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="pcbkit-cli-")
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _drc(self, nome, pro=None, dru=None):
        d = self.dir / nome
        d.mkdir()
        salvar_arquivo(d / "p.kicad_pcb", _placa_teste())
        if pro:
            (d / "p.kicad_pro").write_text(pro, encoding="utf-8")
        if dru:
            (d / "p.kicad_dru").write_text(dru, encoding="utf-8")
        rel = kicad_cli.drc(AMB, d / "p.kicad_pcb", saida=d / "drc.json")
        return rel, " | ".join(v["description"] for v in rel.violacoes), {v["type"] for v in rel.violacoes}

    def _ler(self, nome):
        return (ASSETS / nome).read_text(encoding="utf-8")

    def test_drus_sao_aceitos(self):
        for nome in ("jlc-2camadas.kicad_dru", "jlc-4camadas.kicad_dru", "alta-tensao.kicad_dru"):
            with self.subTest(nome=nome):
                ok, msg = kicad_cli.validar_dru(AMB, ASSETS / nome)
                self.assertTrue(ok, msg)

    def test_concatenacao_jlc_mais_alta_tensao_e_aceita(self):
        arq = self.dir / "concat.kicad_dru"
        arq.write_text(self._ler("jlc-2camadas.kicad_dru") + "\n" + self._ler("alta-tensao.kicad_dru"), encoding="utf-8")
        self.assertTrue(kicad_cli.validar_dru(AMB, arq)[0])

    def test_validar_dru_detecta_arquivo_descartado(self):
        casos = {"sintaxe": '(version 1)\n(rule "x" (constraint clearance (min 1mm))\n',
                 "condicao": '(version 1)\n(rule "x" (condition "A.Naoexiste == 1") (constraint clearance (min 1mm)))\n',
                 "sem_version": '(rule "x" (constraint clearance (min 1mm)))\n'}
        for nome, texto in casos.items():
            with self.subTest(nome=nome):
                arq = self.dir / f"{nome}.kicad_dru"
                arq.write_text(texto, encoding="utf-8")
                self.assertFalse(kicad_cli.validar_dru(AMB, arq)[0])

    def test_regras_do_dru_disparam(self):
        _, texto, tipos = self._drc("dru", dru=self._ler("jlc-2camadas.kicad_dru"))
        self.assertIn("jlc_via_trilha", texto)
        self.assertIn("via_diameter", tipos)

    def test_kicad_pro_modelo_e_carregado(self):
        _, _, sem_pro = self._drc("sem_pro")
        _, _, com_pro = self._drc("com_pro", pro=self._ler("projeto-modelo.kicad_pro"))
        self.assertNotIn("via_diameter", sem_pro)
        self.assertIn("via_diameter", com_pro)     # min_via_diameter 0,6 do modelo

    def test_regra_hv_dispara_com_net_class_por_padrao(self):
        pro = json.loads(self._ler("projeto-modelo.kicad_pro"))
        pro["net_settings"]["netclass_patterns"] = [{"netclass": "HV", "pattern": "B"}]
        dru = self._ler("jlc-2camadas.kicad_dru") + "\n" + self._ler("alta-tensao.kicad_dru")
        _, texto, _ = self._drc("hv", pro=json.dumps(pro), dru=dru)
        self.assertIn("hv_clearance", texto)

    def test_exit_code_violations(self):
        rel, _, _ = self._drc("rc")
        self.assertNotEqual(rel.rc, 0)
        self.assertGreater(rel.erros, 0)


if __name__ == "__main__":
    unittest.main()
