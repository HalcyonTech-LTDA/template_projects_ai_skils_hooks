"""Ida e volta pelo kicad-cli: gerar -> ERC -> netlist -> comparar com a spec (pula sem KiCad)."""
import contextlib
import copy
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import ambiente, bibliotecas, kicad_cli, modelos, netlist, sexpr  # noqa: E402
from pcbkit.esquematico import ErroSobrescrita, escritor, gerar, geometria as g, spec  # noqa: E402
from pcbkit.esquematico import conferir_sobrescrita, gerador_do_arquivo  # noqa: E402
from pcbkit.sexpr import Simbolo as S  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_esquematico_spec import BASE  # noqa: E402

AMB = ambiente.detectar()
EXEMPLO = Path(__file__).resolve().parents[2] / "assets" / "exemplo" / "placa-exemplo.json"
SEM_KICAD = "kicad-cli nao encontrado"

AMPOP = {
    "projeto": "ampop", "titulo": "Ampop multiunidade", "revisao": "A", "folha": "A4", "tensao_max_v": 5,
    "blocos": [{"id": "a", "titulo": "Ampop", "componentes": ["J1", "U1", "R1", "R2"]}],
    "componentes": [
        {"ref": "J1", "simbolo": "Connector_Generic:Conn_01x04",
         "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"},
        {"ref": "U1", "simbolo": "Amplifier_Operational:LM358", "footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"},
        {"ref": "R1", "simbolo": "Device:R", "valor": "10k", "footprint": "Resistor_SMD:R_0603_1608Metric"},
        {"ref": "R2", "simbolo": "Device:R", "valor": "10k", "footprint": "Resistor_SMD:R_0603_1608Metric"},
    ],
    "redes": {"+5V": ["J1.1", "U1.8"], "GND": ["J1.2", "U1.4", "R2.2"], "ENT_A": ["J1.3", "U1.3"],
              "SAI_A": ["U1.1", "U1.2", "R1.1"], "ENT_B": ["R1.2", "U1.5", "R2.1"], "SAI_B": ["U1.7", "U1.6", "J1.4"]},
    "pwr_flag": ["+5V", "GND"],
}


def _gerar(dados, pasta, nome="placa"):
    circ = spec.validar(dados, AMB)
    saida = Path(pasta) / f"{nome}.kicad_sch"
    desenho, avisos = gerar(circ, AMB, saida, data="2026-10-12")
    return circ, saida, desenho, avisos


def _netlist(sch, pasta):
    return netlist.ler(kicad_cli.exportar_netlist(AMB, sch, Path(pasta) / "n.net"))


@unittest.skipUnless(AMB.encontrado, SEM_KICAD)
class TestIdaEVolta(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pcbkit-sch-")
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_netlist_bate_com_a_spec(self):
        circ, sch, _, _ = _gerar(BASE, self.tmp)
        d = netlist.comparar(circ, _netlist(sch, self.tmp))
        self.assertTrue(d.ok, d)

    def test_controle_negativo_pino_trocado(self):
        _, sch, _, _ = _gerar(BASE, self.tmp)
        trocada = copy.deepcopy(BASE)
        trocada["redes"]["SAIDA"] = ["Q1.D", "U1.IN2"]
        trocada["nao_conectar"] = [p for p in trocada["nao_conectar"] if p != "U1.IN2"] + ["U1.IN1"]
        d = netlist.comparar(spec.validar(trocada, AMB), _netlist(sch, self.tmp))
        self.assertFalse(d.ok)
        self.assertEqual(d.pinos_faltando, {"SAIDA": ["U1.2"]})
        self.assertEqual(d.pinos_sobrando, {"SAIDA": ["U1.3"]})

    def test_multiunidade_erc_e_netlist(self):
        circ, sch, desenho, _ = _gerar(AMPOP, self.tmp)
        self.assertEqual(sorted(i.item.unidade for i in desenho.instancias if i.item.chave == "U1"), [1, 2, 3])
        rel = kicad_cli.erc(AMB, sch, saida=Path(self.tmp) / "erc.json")
        self.assertEqual(rel.erros, 0, [v["type"] for v in rel.violacoes])
        self.assertTrue(netlist.comparar(circ, _netlist(sch, self.tmp)).ok)

    def test_uuids_unicos_e_deterministicos(self):
        _, sch, _, _ = _gerar(BASE, self.tmp)
        texto = sch.read_text(encoding="utf-8")
        uuids = re.findall(r'\(uuid "([0-9a-f-]+)"\)', texto)
        self.assertEqual(len(uuids), len(set(uuids)))
        self.assertIn(escritor.uuid_do_simbolo("teste", "R1"), uuids)
        _, sch2, _, _ = _gerar(BASE, self.tmp, "copia")
        self.assertEqual(texto.replace('"placa"', '"copia"'), sch2.read_text(encoding="utf-8"))


def _instancia(lib_id, ref, x, y, rot, espelho, raiz):
    no = [S("symbol"), [S("lib_id"), lib_id], [S("at"), x, y, rot]]
    if espelho:
        no.append([S("mirror"), S(espelho)])
    return no + [[S("unit"), 1], [S("exclude_from_sim"), S("no")], [S("in_bom"), S("yes")], [S("on_board"), S("yes")],
                 [S("dnp"), S("no")], [S("uuid"), str(uuid.uuid4())],
                 [S("property"), "Reference", ref, [S("at"), x, y, 0], [S("effects"), [S("font"), [S("size"), 1.27, 1.27]]]],
                 [S("property"), "Value", "Q", [S("at"), x, y, 0], [S("effects"), [S("font"), [S("size"), 1.27, 1.27]]]],
                 [S("instances"), [S("project"), "rot", [S("path"), f"/{raiz}", [S("reference"), ref], [S("unit"), 1]]]]]


@unittest.skipUnless(AMB.encontrado, SEM_KICAD)
class TestSobrescritaDoEsquematico(unittest.TestCase):
    """Achado 8: o gerador nao regrava um .kicad_sch salvo pela GUI (`generator` "eeschema")."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pcbkit-sobrescrita-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.sch = self.tmp / "placa.kicad_sch"

    def _arquivo(self, gerador):
        linha = f'\t(generator "{gerador}")\n' if gerador else ""
        self.sch.write_text(f'(kicad_sch\n\t(version 20260306)\n{linha}\t(uuid "x"))\n', encoding="utf-8")

    def test_gerador_do_arquivo(self):
        self._arquivo("eeschema")
        self.assertEqual(gerador_do_arquivo(self.sch), "eeschema")
        self._arquivo(None)
        self.assertIsNone(gerador_do_arquivo(self.sch))

    def test_recusa_arquivo_salvo_pela_gui_e_explica_o_modo_manual(self):
        self._arquivo("eeschema")
        with self.assertRaises(ErroSobrescrita) as c:
            conferir_sobrescrita(self.sch)
        msg = str(c.exception)
        for trecho in ("eeschema", "modo manual", "Modo spec e modo manual", "--sobrescrever"):
            self.assertIn(trecho, msg)

    def test_recusa_arquivo_sem_generator(self):
        self._arquivo(None)
        with self.assertRaises(ErroSobrescrita):
            conferir_sobrescrita(self.sch)

    def test_aceita_ausente_vazio_e_arquivo_do_proprio_gerador(self):
        conferir_sobrescrita(self.sch)                          # ausente
        self.sch.write_text("", encoding="utf-8")
        conferir_sobrescrita(self.sch)                          # vazio
        self._arquivo("pcbkit")
        conferir_sobrescrita(self.sch)                          # escrito pelo gerador (ou pelo novo_projeto)

    @unittest.skipUnless(AMB.encontrado, SEM_KICAD)
    def test_gerar_nao_toca_no_arquivo_da_gui_e_sobrescrever_forca(self):
        circ = spec.validar(BASE, AMB)
        self._arquivo("eeschema")
        antes = self.sch.read_text(encoding="utf-8")
        with self.assertRaises(ErroSobrescrita):
            gerar(circ, AMB, self.sch, data="2026-10-12")
        self.assertEqual(self.sch.read_text(encoding="utf-8"), antes)
        gerar(circ, AMB, self.sch, data="2026-10-12", sobrescrever=True)
        self.assertEqual(gerador_do_arquivo(self.sch), "pcbkit")
        gerar(circ, AMB, self.sch, data="2026-10-12")           # regerar o proprio arquivo segue livre

    @unittest.skipUnless(AMB.encontrado, SEM_KICAD)
    def test_cli_sai_com_1_e_so_grava_com_a_flag(self):
        import gerar_esquematico
        dados = self.tmp / "spec.json"
        dados.write_text(json.dumps(BASE), encoding="utf-8")
        self._arquivo("eeschema")
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gerar_esquematico.main([str(dados), "-o", str(self.sch)]), 1)
        self.assertIn("--sobrescrever", saida.getvalue())
        self.assertEqual(gerador_do_arquivo(self.sch), "eeschema")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gerar_esquematico.main([str(dados), "-o", str(self.sch), "--sobrescrever"]), 0)
        self.assertEqual(gerador_do_arquivo(self.sch), "pcbkit")


class TestRotacaoEspelhoNoKicad(unittest.TestCase):
    """Label na posicao calculada de cada pino de um simbolo assimetrico (AO3401A) em toda orientacao:
    a netlist do kicad-cli tem de ligar cada label ao pino certo."""

    def test_todas_as_orientacoes(self):
        sim = bibliotecas.carregar_simbolo(AMB, "Transistor_FET:AO3401A")
        raiz = str(uuid.uuid4())
        sch = modelos.esquematico_vazio("Rot", "2026-10-12", "A", uuid_raiz=raiz)
        sexpr.filho(sch, "lib_symbols").append(bibliotecas.no_embutido(sim))
        corpo, esperado = [], {}
        combos = [(r, e) for e in (None, "x", "y") for r in (0, 90, 180, 270)]
        for i, (rot, esp) in enumerate(combos):
            ref, x, y = f"Q{i + 1}", 25.4 + (i % 4) * 25.4, 25.4 + (i // 4) * 25.4
            corpo.append(_instancia(sim.lib_id, ref, x, y, rot, esp, raiz))
            for p in sim.pinos:
                px, py = g.posicao_pino(p, (x, y), g.Orientacao(rot, esp))
                nome = f"{ref}_{p.numero}"
                corpo.append([S("label"), nome, [S("at"), px, py, 0], [S("uuid"), str(uuid.uuid4())]])
                esperado[f"/{nome}"] = {(ref, p.numero)}
        pos = sch.index(sexpr.filho(sch, "sheet_instances"))
        sch[pos:pos] = corpo
        with tempfile.TemporaryDirectory() as tmp:
            arq = Path(tmp) / "rot.kicad_sch"
            sexpr.salvar_arquivo(arq, sch)
            redes = _netlist(arq, tmp).redes
        for nome, pinos in esperado.items():
            self.assertEqual(redes.get(nome), pinos, nome)


@unittest.skipUnless(AMB.encontrado, SEM_KICAD)
class TestExemplo(unittest.TestCase):
    """A placa exemplo inteira: ERC sem erro, netlist batendo, cabe na folha, sem itens sobrepostos."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="pcbkit-exemplo-")
        dados = json.loads(EXEMPLO.read_text(encoding="utf-8"))
        cls.circ, cls.sch, cls.desenho, cls.avisos = _gerar(dados, cls.tmp, "placa-exemplo")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, True)

    def test_erc_sem_violacao(self):
        rel = kicad_cli.erc(AMB, self.sch, saida=Path(self.tmp) / "erc.json")
        self.assertEqual((rel.erros, rel.avisos), (0, 0), [v["type"] for v in rel.violacoes])

    def test_netlist_bate(self):
        d = netlist.comparar(self.circ, _netlist(self.sch, self.tmp))
        self.assertTrue(d.ok, d)

    def test_cabe_na_folha_sem_aviso_de_layout(self):
        self.assertEqual([a for a in self.avisos if "folha" in a], [])

    def test_molduras_dos_blocos_nao_se_cruzam(self):
        m = self.desenho.molduras
        self.assertEqual(len(m), len(self.circ.blocos))
        for i in range(len(m)):
            for j in range(i + 1, len(m)):
                self.assertFalse(m[i].cruza(m[j]), (i, j))

    def test_todo_componente_montado_tem_mpn_e_lcsc(self):
        for ref, c in self.circ.componentes.items():
            self.assertTrue(c.campos.get("MPN") and re.fullmatch(r"C\d+", c.campos.get("LCSC", "")), ref)

    def test_pontos_de_conexao_na_grade(self):
        pontos = [(x2, y2) for _, _, x2, y2 in self.desenho.fios] + list(self.desenho.ncs)
        for x, y in pontos:
            self.assertAlmostEqual(x / g.GRADE, round(x / g.GRADE), places=3)
            self.assertAlmostEqual(y / g.GRADE, round(y / g.GRADE), places=3)


if __name__ == "__main__":
    unittest.main()
