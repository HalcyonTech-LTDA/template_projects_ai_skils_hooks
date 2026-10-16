"""Testes de pcbkit.fab (BOM, BOM/CPL da JLC, manifesto, camadas e zip) sem o kicad-cli."""
import csv
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import modelos, netlist  # noqa: E402
from pcbkit.fab import bom, jlc, manifesto, pacote  # noqa: E402
from pcbkit.sexpr import salvar_arquivo  # noqa: E402


def _dados(valor, fp, campos, props=()):
    return {"valor": valor, "footprint": fp, "campos": campos, "propriedades": {p: "" for p in props}}


R0603 = "Resistor_SMD:R_0603_1608Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
R10K = {"MPN": "0603WAF1002T5E", "Fabricante": "UNI-ROYAL", "LCSC": "C25804", "Datasheet": "https://x/r.pdf"}
C100N = {"MPN": "CC0603KRX7R9BB104", "Manufacturer": "YAGEO", "LCSC Part #": "C14663", "Datasheet": "~"}


def _netlist():
    comps = {
        "R10": _dados("10k", R0603, R10K),
        "R2": _dados("10k", R0603, R10K),
        "R1": _dados("10k", R0603, R10K),
        "R3": _dados("10k", R0603, {**R10K, "LCSC": "C99999"}),        # mesmo valor, outra peca
        "C1": _dados("100nF", C0603, C100N),
        "C2": _dados("100nF", C0603, C100N, props=("dnp",)),
        "TP1": _dados("TP", "TestPoint:TestPoint_Pad_D1.0mm", {}, props=("exclude_from_bom",)),
        "J1": _dados("Borne", "TerminalBlock:TB_1x02", {"MPN": "WJ126", "Sem_LCSC": "soldado a mao"}),
        "J2": _dados("Borne", "TerminalBlock:TB_1x02", {"MPN": "WJ126", "LCSC": "C8545", "Sem_LCSC": "consignado"}),
        "TP2": _dados("TP", "TestPoint:TestPoint_Pad_D1.0mm", {"MPN": "TP", "LCSC": "C1111"},
                      props=("exclude_from_pos_files",)),
        "U1": _dados("CI", "Package_SO:SOIC-8", {"JLCPCB Part #": "C1", "LCSC Part": "C2"}),
    }
    return netlist.Netlist({}, comps)


POS = [
    {"Ref": "R10", "Val": "10k", "Package": "R", "PosX": "10.5", "PosY": "-20.25", "Rot": "-90.000000", "Side": "top"},
    {"Ref": "R1", "Val": "10k", "Package": "R", "PosX": "1", "PosY": "-2", "Rot": "0.000000", "Side": "top"},
    {"Ref": "R2", "Val": "10k", "Package": "R", "PosX": "1", "PosY": "-2", "Rot": "450", "Side": "bottom"},
    {"Ref": "C1", "Val": "100nF", "Package": "C", "PosX": "3.123456", "PosY": "4", "Rot": "180", "Side": "top"},
    {"Ref": "J1", "Val": "Borne", "Package": "TB", "PosX": "0", "PosY": "0", "Rot": "0", "Side": "top"},
    {"Ref": "J2", "Val": "Borne", "Package": "TB", "PosX": "5", "PosY": "5", "Rot": "0", "Side": "top"},
    {"Ref": "H1", "Val": "M3", "Package": "Hole", "PosX": "0", "PosY": "0", "Rot": "0", "Side": "top"},
]


class TestComponentes(unittest.TestCase):
    def setUp(self):
        self.comps = {c.ref: c for c in bom.componentes(_netlist())}

    def test_ordem_natural(self):
        self.assertEqual([c.ref for c in bom.componentes(_netlist())][:6], ["C1", "C2", "J1", "J2", "R1", "R2"])
        self.assertLess(bom.ordem_ref("R2"), bom.ordem_ref("R10"))

    def test_fallbacks_de_campo(self):
        c1 = self.comps["C1"]
        self.assertEqual((c1.lcsc, c1.fabricante, c1.datasheet), ("C14663", "YAGEO", ""))   # '~' = vazio

    def test_campo_da_familia_vence_e_ordem_dos_fallbacks(self):
        self.assertEqual(self.comps["U1"].lcsc, "C2")        # 'LCSC Part' antes de 'JLCPCB Part #'
        d = _dados("x", "f", {"LCSC": "C10", "LCSC Part #": "C20", "Fabricante": "A", "Manufacturer": "B"})
        c = bom.componente("X1", d)
        self.assertEqual((c.lcsc, c.fabricante), ("C10", "A"))

    def test_dnp_e_fora_da_bom(self):
        self.assertTrue(self.comps["C2"].dnp)
        self.assertTrue(self.comps["TP1"].fora_da_bom)
        self.assertNotIn("C2", [c.ref for c in bom.montados(self.comps.values())])
        self.assertNotIn("TP1", [c.ref for c in bom.montados(self.comps.values())])

    def test_pendencias(self):
        pend = bom.pendencias(self.comps.values())
        self.assertEqual(len(pend), 1)
        self.assertIn("U1", pend[0])
        self.assertIn("sem MPN", pend[0])            # J1 tem Sem_LCSC: nao e pendencia


class TestBomJlc(unittest.TestCase):
    def setUp(self):
        self.comps = bom.componentes(_netlist())
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def _ler(self, caminho):
        with open(caminho, encoding="utf-8", newline="") as f:
            return list(csv.reader(f))

    def test_cabecalho_e_agrupamento(self):
        linhas = self._ler(jlc.escrever_bom(self.tmp / "bom-jlc.csv", self.comps))
        self.assertEqual(linhas[0], ["Comment", "Designator", "Footprint", "JLCPCB Part #"])
        self.assertIn(["10k", "R1,R2,R10", "R_0603_1608Metric", "C25804"], linhas)
        self.assertIn(["10k", "R3", "R_0603_1608Metric", "C99999"], linhas)     # LCSC diferente separa
        self.assertIn(["100nF", "C1", "C_0603_1608Metric", "C14663"], linhas)    # C2 DNP fora
        refs = ",".join(l[1] for l in linhas[1:])
        for fora in ("C2", "TP1", "J1"):
            self.assertNotIn(fora, refs.split(","))
        # achado 9: Sem_LCSC vence o LCSC (J2 tem os dois); fora_do_pos tira da BOM e do CPL da JLC
        # (peca na BOM da JLC sem linha no CPL e acusada no upload)
        self.assertNotIn("J2", refs.split(","))
        self.assertNotIn("C8545", [l[3] for l in linhas])
        self.assertNotIn("TP2", refs.split(","))

    def test_cpl(self):
        sem_posicao = jlc.escrever_cpl(self.tmp / "cpl.csv", POS, self.comps)
        linhas = self._ler(self.tmp / "cpl.csv")
        self.assertEqual(linhas[0], ["Designator", "Mid X", "Mid Y", "Rotation", "Layer"])
        self.assertEqual(linhas[1:], [["C1", "3.1235", "4.0000", "180", "Top"],
                                      ["R1", "1.0000", "-2.0000", "0", "Top"],
                                      ["R2", "1.0000", "-2.0000", "90", "Bottom"],
                                      ["R10", "10.5000", "-20.2500", "270", "Top"]])
        self.assertEqual(sem_posicao, ["R3", "U1"])      # J1/J2 (Sem_LCSC) e H1 (so na placa) nao entram
        refs = [l[0] for l in linhas[1:]]
        self.assertNotIn("J2", refs)         # tem LCSC e Sem_LCSC: o Sem_LCSC vence
        self.assertNotIn("TP2", refs)        # exclude_from_pos_files tira do CPL
        self.assertNotIn("TP2", sem_posicao)  # e nao e cobrado como posicao faltando

    def test_sem_lcsc_vence_o_lcsc_e_fora_do_pos_sai_da_bom_e_do_cpl_da_jlc(self):
        por_ref = {c.ref: c for c in self.comps}
        self.assertTrue(por_ref["J2"].montado)
        self.assertFalse(por_ref["J2"].montado_pela_jlc)
        self.assertTrue(por_ref["TP2"].fora_do_pos)
        self.assertTrue(por_ref["TP2"].montado)              # continua na BOM completa
        self.assertFalse(por_ref["TP2"].montado_pela_jlc)
        self.assertFalse(por_ref["TP2"].no_cpl)
        self.assertTrue(por_ref["R1"].no_cpl)

    def test_lado_desconhecido(self):
        with self.assertRaises(ValueError):
            jlc.linhas_cpl([{**POS[0], "Side": "meio"}], self.comps)

    def test_ler_pos_do_kicad(self):
        arq = self.tmp / "pos.csv"
        arq.write_text('Ref,Val,Package,PosX,PosY,Rot,Side\n"C1","100nF","C_0603",118.568300,-128.393200,'
                       '0.000000,top\n', encoding="utf-8")
        self.assertEqual(jlc.ler_pos(arq)[0]["PosX"], "118.568300")


class TestBomCompleta(unittest.TestCase):
    def test_colunas_e_dnp(self):
        linhas = bom.linhas_completa(bom.componentes(_netlist()))
        self.assertEqual(bom.CABECALHO_COMPLETA, ["Item", "Valor", "Referencias", "Quantidade", "Footprint", "MPN",
                                                  "Fabricante", "LCSC", "Mouser", "DigiKey", "Datasheet"])
        por_refs = {l[2]: l for l in linhas}
        self.assertEqual(por_refs["R1,R2,R10"][3], 3)
        self.assertEqual(por_refs["R1,R2,R10"][10], "https://x/r.pdf")
        self.assertIn("J1", por_refs)                  # sem LCSC justificado continua na BOM completa
        self.assertNotIn("C1,C2", por_refs)
        self.assertEqual([l[0] for l in linhas], list(range(1, len(linhas) + 1)))


class TestManifesto(unittest.TestCase):
    def test_sha_e_conferencia(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "a.txt").write_bytes(b"abc")
            dados = manifesto.montar("p", "A", [tmp / "a.txt"], "10.0.0", ["kicad-cli x"], {"portao": {"ok": 1}})
            self.assertEqual(dados["arquivos"], [{"arquivo": "a.txt", "bytes": 3, "sha256":
                             "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}])
            self.assertEqual((dados["kicad"], dados["revisao"], dados["portao"]), ("10.0.0", "A", {"ok": 1}))
            self.assertIn("T", dados["gerado_em"])
            gravado = json.loads(manifesto.gravar(tmp, dados).read_text(encoding="utf-8"))
            self.assertEqual(manifesto.conferir(tmp, gravado), [])
            (tmp / "a.txt").write_bytes(b"abd")
            self.assertEqual(manifesto.conferir(tmp, gravado), ["a.txt: SHA-256 diferente"])


class TestCamadasEZip(unittest.TestCase):
    def test_camadas_cobre_2_e_4(self):
        with tempfile.TemporaryDirectory() as tmp:
            for n, esperado in ((2, ["F.Cu", "B.Cu"]), (4, ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"])):
                pcb = Path(tmp) / f"p{n}.kicad_pcb"
                salvar_arquivo(pcb, modelos.placa_vazia(n, "t", "2026-10-12", "A"))
                self.assertEqual(pacote.camadas_cobre(pcb), esperado)
                self.assertEqual(pacote.camadas_gerber(pcb)[-1], "Edge.Cuts")

    def test_extensoes(self):
        self.assertEqual([pacote.extensao_protel(c) for c in ("F.Cu", "In2.Cu", "Edge.Cuts", "B.SilkS")],
                         ["gtl", "g2", "gm1", "gbo"])

    def test_zip_incompleto(self):
        with tempfile.TemporaryDirectory() as tmp:
            arq = Path(tmp) / "g.zip"
            with zipfile.ZipFile(arq, "w") as z:
                for nome in ("p-F_Cu.gtl", "p-B_Cu.gbl", "p-PTH.drl"):
                    z.writestr(nome, "x")
            self.assertEqual(pacote.faltando_no_zip(arq, ["F.Cu", "B.Cu", "Edge.Cuts"]), ["Edge.Cuts", "-NPTH.drl"])

    def test_nomes(self):
        n = pacote.nomes("placa-x", "B")
        self.assertEqual((n["gerber"], n["bom-jlc"], n["cpl-jlc"], n["bom"], n["esquematico"], n["step"]),
                         ("placa-x-rev-B-gerber.zip", "placa-x-rev-B-bom-jlc.csv", "placa-x-rev-B-cpl-jlc.csv",
                          "placa-x-rev-B-bom.csv", "placa-x-rev-B-esquematico.pdf", "placa-x-rev-B.step"))
        self.assertTrue(set(pacote.TIPOS_RELEASE) <= set(n))


if __name__ == "__main__":
    unittest.main()
