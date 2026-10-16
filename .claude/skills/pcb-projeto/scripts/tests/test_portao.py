"""Testes de pcbkit.portao: cada motivo de bloqueio pelas verificacoes puras (sem kicad-cli)."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import kicad_cli, nota, portao, regra_hv, regras, severidades, sexpr  # noqa: E402
from pcbkit.fab import bom  # noqa: E402

ASSETS = Path(__file__).resolve().parents[2] / "assets"
KICAD = ASSETS / "kicad"
MODELOS_NOTA = {
    "esquematico": ASSETS / "docs" / "Eletronica" / "Esquematicos" / "{{placa}}_Rev{{rev}}_Revisao_Esquematico.md",
    "liberacao": ASSETS / "docs" / "Eletronica" / "Gerber" / "{{placa}}_Rev{{rev}}_Liberacao_Fabricacao.md",
    "alta-tensao": ASSETS / "opcionais" / "{{placa}}_Rev{{rev}}_Aprovacao_Alta_Tensao.md",
}


def _rel(violacoes=(), nao_conectados=(), paridade=()):
    return kicad_cli.Relatorio("drc", 0, Path("x.json"), {}, list(violacoes), list(nao_conectados), list(paridade))


def _viol(tipo, sev, itens=()):
    return {"type": tipo, "severity": sev, "description": tipo, "items": [{"description": i} for i in itens]}


def _dru(texto):
    return sexpr.carregar_todos(texto, comentarios=True)


def _asset_hv():
    return (KICAD / "jlc-2camadas.kicad_dru").read_text(encoding="utf-8") + \
        (KICAD / "alta-tensao.kicad_dru").read_text(encoding="utf-8")


APROVADA = "---\ntype: gate\ngate: liberacao\nstatus: aprovado\nrevisores: [Ana]\nplaca: placa-x\nrevisao: A\n---\n" \
           "- [x] ok\n"


def _modelo_aprovado(papel, placa="placa-x", rev="A"):
    """Nota modelo de assets/ com placa/rev trocados, aprovada (so no teste)."""
    texto = MODELOS_NOTA[papel].read_text(encoding="utf-8")
    for chave, valor in {"placa": placa, "rev": rev, "projeto": "P", "data": "2026-10-12"}.items():
        texto = texto.replace("{{" + chave + "}}", valor)
    texto = texto.replace("status: rascunho", "status: aprovado").replace("revisores: []", "revisores: [Ana]")
    return nota.carregar_texto(texto.replace("- [ ] ", "- [x] "))


class TestErcDrcDru(unittest.TestCase):
    def test_erc_limpo(self):
        self.assertTrue(portao.verificar_erc(_rel()).ok)

    def test_erc_aviso_bloqueia(self):
        v = portao.verificar_erc(_rel([_viol("pin_not_driven", "warning")]))
        self.assertFalse(v.ok)
        self.assertIn("1 aviso", v.motivos[0])

    def test_drc_erro_bloqueia(self):
        v = portao.verificar_drc(_rel([_viol("clearance", "error")], [_viol("unconnected_items", "error")]))
        self.assertFalse(v.ok)
        self.assertIn("2 violacao(oes) que bloqueiam", v.motivos[0])

    def test_drc_paridade_bloqueia_mesmo_como_aviso(self):
        # No 10.0.0 o footprint faltando sai como warning (medido): antes passava no portao.
        self.assertFalse(portao.verificar_drc(_rel(paridade=[_viol("missing_footprint", "error")])).ok)
        v = portao.verificar_drc(_rel(paridade=[_viol("missing_footprint", "warning")]))
        self.assertFalse(v.ok)
        self.assertIn("missing_footprint (warning)", v.motivos[0])

    def test_conexao_faltando_rebaixada_continua_bloqueando(self):
        self.assertFalse(portao.verificar_drc(_rel(nao_conectados=[_viol("unconnected_items", "warning")])).ok)

    def test_drc_avisos_nao_bloqueiam_e_sao_listados(self):
        rel = _rel([_viol("silk_edge_clearance", "warning", ["Retangulo no Edge.Cuts", "Segmento de U1"])] * 2)
        v = portao.verificar_drc(rel)
        self.assertTrue(v.ok)
        self.assertEqual(v.detalhes["avisos"], 2)
        avisos = portao.avisos_drc(rel)
        self.assertEqual(avisos[0]["tipo"], "silk_edge_clearance")
        self.assertEqual(avisos[0]["itens"], ["Retangulo no Edge.Cuts", "Segmento de U1"])

    def test_dru_rejeitado(self):
        v = portao.verificar_dru(False, "descartado")
        self.assertEqual((v.ok, v.motivos), (False, ["descartado"]))


class TestSeveridades(unittest.TestCase):
    """Achado 3: `rule_severities` e exclusoes do .kicad_pro somem com violacoes do relatorio."""

    def _pro(self, drc=None, erc=None, exc_drc=None, exc_erc=None):
        dados = copy.deepcopy(regras.ler_pro(regras.MODELO_PRO))
        ds = dados["board"]["design_settings"]
        if drc is not None:
            ds["rule_severities"] = drc
        if exc_drc is not None:
            ds["drc_exclusions"] = exc_drc
        if erc is not None or exc_erc is not None:
            dados["erc"] = {"rule_severities": erc or {}, "erc_exclusions": exc_erc or []}
        return portao.verificar_severidades(severidades.auditar(dados))

    def test_modelo_do_template_passa_sem_nada_listado(self):
        v = self._pro()
        self.assertTrue(v.ok)
        self.assertEqual((v.detalhes["rebaixadas"], v.detalhes["exclusoes_drc"], v.detalhes["exclusoes_erc"]),
                         ([], [], []))

    def test_invalid_outline_ignorado_bloqueia(self):          # cenario do t2.py do reviewer
        v = self._pro(drc={"invalid_outline": "ignore"})
        self.assertFalse(v.ok)
        self.assertIn("DRC invalid_outline: 'ignore' (precisa 'error')", v.motivos[0])

    def test_critica_drc_em_warning_bloqueia(self):
        for regra in ("clearance", "unconnected_items", "creepage", "track_width", "shorting_items"):
            self.assertFalse(self._pro(drc={regra: "warning"}).ok, regra)

    def test_paridade_so_nao_pode_ser_ignorada(self):
        self.assertTrue(self._pro(drc={"missing_footprint": "warning", "net_conflict": "error"}).ok)
        self.assertFalse(self._pro(drc={"missing_footprint": "ignore"}).ok)

    def test_critica_erc_ignorada_bloqueia_warning_nao(self):
        self.assertFalse(self._pro(erc={"pin_not_connected": "ignore"}).ok)
        self.assertFalse(self._pro(erc={"label_dangling": "ignore"}).ok)
        self.assertTrue(self._pro(erc={"pin_to_pin": "warning", "multiple_net_names": "warning"}).ok)

    def test_nao_critica_rebaixada_vai_para_detalhes(self):
        v = self._pro(drc={"silk_overlap": "ignore", "footprint_filters_mismatch": "ignore"},
                      erc={"similar_labels": "ignore", "footprint_filter": "ignore"})
        self.assertTrue(v.ok)
        self.assertEqual(v.detalhes["rebaixadas"], ["DRC silk_overlap: 'ignore' (padrao 'warning')",
                                                    "ERC similar_labels: 'ignore'"])

    def test_exclusoes_listadas(self):
        v = self._pro(exc_drc=[["clearance|1|2|u1|u2", "afastamento conferido"]], exc_erc=["pin_to_pin|0|0|a|b"])
        self.assertTrue(v.ok)
        self.assertEqual(v.detalhes["exclusoes_drc"], [{"violacao": "clearance|1|2|u1|u2",
                                                        "comentario": "afastamento conferido"}])
        self.assertEqual(v.detalhes["exclusoes_erc"], [{"violacao": "pin_to_pin|0|0|a|b", "comentario": ""}])

    def test_padrao_do_kicad_nao_rebaixa_critica(self):
        for regra, minimo in severidades.CRITICAS_DRC.items():
            if regra in severidades.PADRAO_DRC:
                self.assertEqual(severidades.PADRAO_DRC[regra], minimo, regra)


class TestRevisao(unittest.TestCase):
    def test_revisao_da_spec(self):
        v = portao.verificar_revisao({"revisao": "B"}, None)
        self.assertEqual((v.ok, v.detalhes["revisao"]), (True, "B"))
        self.assertTrue(portao.verificar_revisao({"revisao": "B"}, "B").ok)

    def test_rev_diferente_da_spec_bloqueia(self):
        v = portao.verificar_revisao({"revisao": "B"}, "A")
        self.assertFalse(v.ok)
        self.assertIn("--rev A nao bate com a revisao da spec (B)", v.motivos[0])

    def test_spec_sem_revisao_bloqueia(self):
        for spec in (None, {}, {"revisao": ""}, {"revisao": None}):
            v = portao.verificar_revisao(spec, "A")
            self.assertFalse(v.ok, spec)
            self.assertIn("'revisao' ausente na spec", v.motivos[0])


class TestTensaoEBom(unittest.TestCase):
    def test_tensao(self):
        self.assertTrue(portao.verificar_tensao({"tensao_max_v": 12}).ok)
        for spec in (None, {}, {"tensao_max_v": None}, {"tensao_max_v": "12"}, {"tensao_max_v": True}):
            self.assertFalse(portao.verificar_tensao(spec).ok, spec)

    def test_mensagem_pede_o_valor(self):
        self.assertIn("declare", portao.verificar_tensao({"tensao_max_v": None}).motivos[0])

    def test_nao_finito_bloqueia_e_vira_hv(self):           # achado 7
        for valor in (float("nan"), float("inf"), float("-inf")):
            spec = {"tensao_max_v": valor}
            v = portao.verificar_tensao(spec)
            self.assertFalse(v.ok, valor)
            self.assertIn("nao finito", v.motivos[0])
            self.assertIn("nao declarado", portao.motivos_alta_tensao(spec, {}, [])[0])

    def test_negativo_vale_o_modulo(self):                  # achado 7: -311 V e rede, nao baixa tensao
        self.assertEqual(portao.tensao_max({"tensao_max_v": -311})[0], 311)
        self.assertIn("311 V", portao.motivos_alta_tensao({"tensao_max_v": -311}, {}, [])[0])

    def test_limite_ac_e_42v4_de_pico(self):                # achado 15
        self.assertEqual(portao.motivos_alta_tensao({"tensao_max_v": 48}, {}, []), [])
        m = portao.motivos_alta_tensao({"tensao_max_v": 48, "tensao_ac": True}, {}, [])
        self.assertIn("48 V de pico > 42.4 V (AC", m[0])
        self.assertEqual(portao.motivos_alta_tensao({"tensao_max_v": 42.4, "tensao_ac": True}, {}, []), [])
        self.assertEqual(portao.motivos_alta_tensao({"tensao_max_v": 48, "tensao_ac": False}, {}, []), [])
        v = portao.verificar_tensao({"tensao_max_v": 24, "tensao_ac": True})
        self.assertEqual((v.ok, v.detalhes["limite_hv_v"]), (True, 42.4))

    def test_tensao_ac_nao_booleano_bloqueia_e_conta_como_ac(self):
        spec = {"tensao_max_v": 48, "tensao_ac": "sim"}
        self.assertIn("'tensao_ac' deve ser true ou false", portao.verificar_tensao(spec).motivos[0])
        self.assertTrue(portao.motivos_alta_tensao(spec, {}, []))

    def test_bom(self):
        ok = bom.Componente("R1", "10k", "R", mpn="M", lcsc="C1")
        self.assertTrue(portao.verificar_bom([ok]).ok)
        sem_mpn = bom.Componente("R2", "10k", "R", lcsc="C1")
        sem_lcsc = bom.Componente("J1", "B", "TB", mpn="M")
        justificado = bom.Componente("J2", "B", "TB", mpn="M", sem_lcsc="soldado a mao")
        dnp = bom.Componente("R3", "10k", "R", dnp=True)
        v = portao.verificar_bom([ok, sem_mpn, sem_lcsc, justificado, dnp])
        self.assertFalse(v.ok)
        self.assertIn("2 componente(s)", v.motivos[0])
        self.assertIn("R2 (10k): sem MPN", v.motivos[0])
        self.assertIn("J1 (B): sem LCSC", v.motivos[0])
        self.assertEqual(v.detalhes["sem_lcsc_justificado"], ["J2"])


class TestNotaDoPortao(unittest.TestCase):
    def _v(self, texto, placa="placa-x", rev="A", papel="liberacao", caminho="n.md"):
        return portao.verificar_nota(nota.carregar_texto(texto), caminho, placa, rev, "x", papel)

    def test_aprovada(self):
        v = self._v(APROVADA)
        self.assertTrue(v.ok, v.motivos)
        self.assertEqual(v.detalhes["revisores"], ["Ana"])

    def test_ausente(self):
        v = portao.verificar_nota(None, "nao-existe.md", "placa-x", "A", "nota de liberacao", "liberacao")
        self.assertIn("nao encontrada", v.motivos[0])

    def test_rascunho_bloqueia(self):
        self.assertFalse(self._v(APROVADA.replace("aprovado", "rascunho")).ok)

    def test_outra_placa_ou_revisao(self):
        self.assertIn("placa 'placa-x', nao de 'placa-y'", self._v(APROVADA, placa="placa-y").motivos[0])
        self.assertIn("revisao A, nao da B", self._v(APROVADA, rev="B").motivos[0])

    def test_placa_e_revisao_ausentes_bloqueiam(self):      # achado 1: antes so comparava se existissem
        sem = APROVADA.replace("placa: placa-x\n", "").replace("revisao: A\n", "")
        motivos = " | ".join(self._v(sem).motivos)
        self.assertIn("'placa' ausente no frontmatter da nota (precisa ser 'placa-x')", motivos)
        self.assertIn("'revisao' ausente no frontmatter da nota (precisa ser 'A')", motivos)

    def test_nome_do_arquivo_de_outra_revisao_bloqueia(self):
        v = self._v(APROVADA, caminho="docs/placa-x_RevC_Liberacao_Fabricacao.md")
        self.assertIn("o nome do arquivo diz RevC, nao RevA", v.motivos[0])
        self.assertEqual(portao.revisao_no_nome("docs/placa-x_RevC_Liberacao_Fabricacao.md"), "C")

    def test_precisa_ser_gate_do_papel_certo(self):         # achado 1: qualquer nota aprovada servia
        self.assertIn("'type: gate'", self._v(APROVADA.replace("type: gate\n", "")).motivos[0])
        self.assertIn("portao 'alta-tensao', nao 'liberacao'",
                      self._v(APROVADA.replace("gate: liberacao", "gate: alta-tensao")).motivos[0])
        self.assertIn("portao 'vazio', nao 'alta-tensao'",
                      self._v(APROVADA.replace("gate: liberacao\n", ""), papel="alta-tensao").motivos[0])

    def test_notas_modelo_so_servem_ao_proprio_portao(self):
        for papel_modelo in MODELOS_NOTA:
            n = _modelo_aprovado(papel_modelo)
            for papel in ("liberacao", "alta-tensao"):
                v = portao.verificar_nota(n, "n.md", "placa-x", "A", "x", papel)
                self.assertEqual(v.ok, papel == papel_modelo, (papel_modelo, papel, v.motivos))

    def test_caminho_da_nota_hv(self):
        self.assertEqual(portao.caminho_nota_hv(Path("d/n.md"), "placa-x", "C"),
                         Path("d") / "placa-x_RevC_Aprovacao_Alta_Tensao.md")
        self.assertTrue(portao.mesmo_arquivo("d/../d/n.md", Path("d") / "n.md"))
        self.assertFalse(portao.mesmo_arquivo("d/n.md", "d/m.md"))


class TestAltaTensao(unittest.TestCase):
    PRO_HV = {"net_settings": {"netclass_patterns": [{"netclass": "HV", "pattern": "/AC_*"}]}}

    def test_baixa_tensao(self):
        self.assertEqual(portao.motivos_alta_tensao({"tensao_max_v": 12}, self.PRO_HV, ["GND", "/SINAL"]), [])

    def test_acima_de_60(self):
        self.assertIn("220 V", portao.motivos_alta_tensao({"tensao_max_v": 220}, {}, [])[0])
        self.assertEqual(portao.motivos_alta_tensao({"tensao_max_v": 60}, {}, []), [])

    def test_tensao_nula_trata_como_hv(self):
        self.assertIn("nao declarado", portao.motivos_alta_tensao({"tensao_max_v": None}, {}, [])[0])
        self.assertTrue(portao.motivos_alta_tensao(None, {}, []))

    def test_net_class_hv_com_redes(self):
        m = portao.motivos_alta_tensao({"tensao_max_v": 12}, self.PRO_HV, ["/AC_L", "GND"])
        self.assertIn("/AC_L", m[0])

    def test_classe_composta_da_netlist(self):              # achado 2: (class "HV,Power") na netlist
        classes = {"/MOTOR_A": ["HV", "Power"], "GND": []}
        m = portao.motivos_alta_tensao({"tensao_max_v": 12}, {}, ["/MOTOR_A", "GND"], classes)
        self.assertEqual(m, ["net class HV com redes na placa: /MOTOR_A"])

    def test_padrao_regex_no_kicad_pro(self):               # achado 2: /MOTOR_(A|B) e regex no KiCad
        pro = {"net_settings": {"netclass_patterns": [{"netclass": "HV", "pattern": "/MOTOR_(A|B)"},
                                                      {"netclass": "Power", "pattern": "/MOTOR_A"}]}}
        m = portao.motivos_alta_tensao({"tensao_max_v": 12}, pro, ["/MOTOR_A", "/MOTOR_B", "/MOTOR_C"])
        self.assertEqual(m, ["net class HV com redes na placa: /MOTOR_A, /MOTOR_B"])

    def test_spec_atribui_redes_a_hv(self):
        spec = {"tensao_max_v": 12, "classes_de_rede": {"HV": {"redes": ["AC_N"]}}}
        self.assertIn("AC_N", portao.motivos_alta_tensao(spec, {}, [])[0])


class TestRegraHv(unittest.TestCase):
    """Achado 6: a regra HV era conferida so pelo texto da condicao."""

    def _regra(self, condicao="A.hasNetclass('HV')", extra="", minimo="3mm"):
        return _dru(f"(version 1)\n(rule hv (condition \"{condicao}\") {extra}"
                    f" (constraint clearance (min {minimo})) (constraint creepage (min {minimo})))")

    def test_asset_de_alta_tensao_em_regras_separadas(self):
        arvore = _dru(_asset_hv())
        self.assertEqual(regra_hv.minimos(arvore), {"clearance": 2.5, "creepage": 2.5})
        self.assertTrue(portao.verificar_regra_hv(arvore, True).ok)

    def test_condicoes_aceitas(self):
        for cond in ("A.hasNetclass('HV')", "A.hasNetclass('HV') || B.hasNetclass('HV')",
                     "A.hasNetclass( 'HV' )||B.hasNetclass('HV')"):
            self.assertTrue(portao.verificar_regra_hv(self._regra(cond), True).ok, cond)

    def test_casos_do_reviewer_bloqueiam(self):
        casos = {"negada": self._regra("!A.hasNetclass('HV')"),
                 "condicao a mais": self._regra("A.hasNetclass('HV') && A.Type == 'Nada'"),
                 "severity ignore": self._regra(extra="(severity ignore)"),
                 "severity warning": self._regra(extra="(severity warning)"),
                 "layer": self._regra(extra='(layer "F.SilkS")'),
                 "minimo 0,01 mm": self._regra(minimo="0.01mm"),
                 "NetClass ==": self._regra("A.NetClass == 'HV'")}
        for nome, arvore in casos.items():
            v = portao.verificar_regra_hv(arvore, True)
            self.assertFalse(v.ok, nome)
            self.assertIn("nao tem regra valida de clearance e creepage", v.motivos[0], nome)

    def test_motivo_explica_regra_que_nao_conta(self):
        v = portao.verificar_regra_hv(self._regra(extra="(severity ignore)"), True)
        self.assertIn("regra 'hv' nao conta: severity ignore", " | ".join(v.motivos))

    def test_severity_error_explicita_vale(self):
        self.assertTrue(portao.verificar_regra_hv(self._regra(extra="(severity error)"), True).ok)

    def test_medida_mm(self):
        self.assertEqual([regra_hv.medida_mm(x) for x in ("2.5mm", "2.5", ".5 mm", "100mil", "0.1in", "x", "-1mm")],
                         [2.5, 2.5, 0.5, 2.54, 2.54, None, None])

    def test_minimo_em_mil(self):
        self.assertTrue(portao.verificar_regra_hv(self._regra(minimo="100mil"), True).ok)     # 2,54 mm
        self.assertFalse(portao.verificar_regra_hv(self._regra(minimo="90mil"), True).ok)     # 2,286 mm

    def test_sem_regra_hv(self):
        arvore = _dru((KICAD / "jlc-2camadas.kicad_dru").read_text(encoding="utf-8"))
        v = portao.verificar_regra_hv(arvore, True)
        self.assertFalse(v.ok)
        self.assertIn("clearance e creepage", v.motivos[0])

    def test_so_clearance_bloqueia(self):
        arvore = _dru("(version 1)\n(rule hv (condition \"A.hasNetclass('HV')\") (constraint clearance (min 3mm)))")
        v = portao.verificar_regra_hv(arvore, True)
        self.assertFalse(v.ok)
        self.assertIn("de creepage", v.motivos[0])

    def test_regra_posterior_mais_fraca_vence_e_bloqueia(self):
        # O KiCad usa a ultima regra que casa, mesmo de condicao mais ampla (medido no 10.0.0).
        depois = "\n(rule geral (condition \"A.Type == 'Track'\") (constraint clearance (min 0.1mm)))\n"
        v = portao.verificar_regra_hv(_dru(_asset_hv() + depois), True)
        self.assertFalse(v.ok)
        self.assertIn("geral depois da regra HV redefinem clearance", v.motivos[0])
        forte = "\n(rule geral (condition \"A.Type == 'Track'\") (constraint clearance (min 3mm)))\n"
        self.assertTrue(portao.verificar_regra_hv(_dru(_asset_hv() + forte), True).ok)

    def test_minimo_registrado_na_nota_hv(self):
        n = nota.carregar_texto("---\nclearance_mm: 4\ncreepage_mm: 6.4mm\n---\n")
        minimos = portao.minimo_da_nota(n)
        self.assertEqual(minimos, {"clearance": 4.0, "creepage": 6.4})
        v = portao.verificar_regra_hv(_dru(_asset_hv()), True, minimos)
        self.assertFalse(v.ok)
        self.assertIn("clearance >= 4 mm (achado: 2.5 mm); creepage >= 6.4 mm (achado: 2.5 mm)", v.motivos[0])
        self.assertEqual(portao.minimo_da_nota(None), {"clearance": 2.5, "creepage": 2.5})

    def test_minimo_da_nota_hv_com_virgula_vazio_e_texto(self):
        # o modelo da nota traz os campos vazios; a pessoa digita com virgula decimal
        vazio = nota.carregar_texto("---\nclearance_mm:\ncreepage_mm:\n---\n")
        self.assertEqual(portao.minimo_da_nota(vazio), {"clearance": 2.5, "creepage": 2.5})
        self.assertEqual(portao.medidas_ilegiveis(vazio), [])
        virgula = nota.carregar_texto("---\nclearance_mm: 3,2\ncreepage_mm: 6,4 mm\n---\n")
        self.assertEqual(portao.minimo_da_nota(virgula), {"clearance": 3.2, "creepage": 6.4})
        self.assertEqual(portao.medidas_ilegiveis(virgula), [])
        texto = nota.carregar_texto("---\nclearance_mm: tres\ncreepage_mm: 4\n---\n")
        self.assertEqual(portao.minimo_da_nota(texto), {"clearance": 2.5, "creepage": 4.0})
        motivos = portao.medidas_ilegiveis(texto)
        self.assertEqual(len(motivos), 1)
        self.assertIn("clearance_mm = 'tres'", motivos[0])

    def test_regra_hv_em_dru_rejeitado_bloqueia(self):
        arvore = _dru((KICAD / "alta-tensao.kicad_dru").read_text(encoding="utf-8"))
        v = portao.verificar_regra_hv(arvore, False)
        self.assertFalse(v.ok)
        self.assertIn("rejeitado", v.motivos[0])

    def test_regra_de_outra_classe_nao_conta(self):
        arvore = _dru("(version 1)\n(rule p (condition \"A.hasNetclass('Power')\") (constraint creepage (min 3mm))"
                      " (constraint clearance (min 3mm)))")
        self.assertEqual(regra_hv.minimos(arvore), {})


class TestResultado(unittest.TestCase):
    def test_ok_so_com_tudo_ok(self):
        res = portao.Resultado("p", [portao.Verificacao("a", True), portao.Verificacao("b", True)])
        self.assertTrue(res.ok)
        res.verificacoes.append(portao.Verificacao("c", False, ["x"]))
        self.assertFalse(res.ok)
        self.assertEqual(portao.resumo(res)["verificacoes"][2]["motivos"], ["x"])


class TestNotaHvMesmoArquivo(unittest.TestCase):
    """Achado 1: a nota de liberacao passada tambem como --aprovacao-hv nao serve de aprovacao HV."""

    def test_mesmo_caminho_bloqueia(self):
        with tempfile.TemporaryDirectory() as tmp:
            arq = Path(tmp) / "placa-x_RevA_Liberacao_Fabricacao.md"
            arq.write_text(APROVADA.replace("gate: liberacao", "gate: alta-tensao"), encoding="utf-8")
            res = portao.Resultado("placa-x", [], revisao="A")
            proj = type("P", (), {"placa": "placa-x", "dru": Path(tmp) / "nao.kicad_dru"})()
            net = type("N", (), {"redes": {}, "classes": {}})()
            portao._verificacoes_hv(res, {"tensao_max_v": 220}, {}, net, True, proj, arq, str(arq))
        nota_hv = next(v for v in res.verificacoes if v.nome == "nota de aprovacao de alta tensao")
        self.assertFalse(nota_hv.ok)
        self.assertIn("mesmo arquivo da nota de liberacao", nota_hv.motivos[-1])


if __name__ == "__main__":
    unittest.main()
