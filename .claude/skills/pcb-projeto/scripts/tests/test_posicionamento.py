"""Testes do posicionamento por bloco (geometria pura: roda no Python do sistema, sem pcbnew)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit.swig import posicionamento as pos  # noqa: E402


def _girar(caixa, rot):
    """Caixa girada como o KiCad gira (angulo positivo anti-horario na tela, y para baixo)."""
    x0, y0, x1, y1 = caixa
    for _ in range(rot // 90):
        x0, y0, x1, y1 = y0, -x1, y1, -x0
    return (x0, y0, x1, y1)


def _ponto(p, rot):
    x, y = p
    for _ in range(rot // 90):
        x, y = y, -x
    return (x, y)


def peca(ref, bloco, l, a, conector=False, redes=(), pads=(0.0, 0.0), exclusao=None):
    caixa = (-l / 2, -a / 2, l / 2, a / 2)
    rots = (0, 90, 180, 270)
    excl = {r: _girar(exclusao, r) for r in rots} if exclusao else None
    return pos.Peca(ref, bloco, {r: _girar(caixa, r) for r in rots}, {r: _ponto(pads, r) for r in rots},
                    conector, frozenset(redes), excl)


def caixa_absoluta(p, posicao):
    x0, y0, x1, y1 = p.caixa(posicao.rotacao)
    return (posicao.x + x0, posicao.y + y0, posicao.x + x1, posicao.y + y1)


def circuito():
    """Bloco de entrada com borne, bloco de MCU com modulo de antena, bloco so com header."""
    return [
        peca("J1", "entrada", 10, 9, conector=True, redes={"+12V"}, pads=(2.5, 1.0)),
        peca("F1", "entrada", 6, 4, redes={"+12V", "VIN"}),
        peca("C1", "entrada", 9.5, 7.2, redes={"VIN"}),
        peca("R1", "entrada", 3, 1.5),
        peca("U1", "mcu", 19.5, 20.2, redes={"TX", "RX"}, exclusao=(-24, -31.0, 24, -10.1)),
        peca("R2", "mcu", 3, 1.5, redes={"EN"}),
        peca("C7", "mcu", 3, 1.5, redes={"EN"}),
        peca("J3", "gravacao", 3.6, 16.3, conector=True, redes={"TX", "RX", "EN"}),
    ]


class TestEmpacotar(unittest.TestCase):
    def test_respeita_limite_inferior_e_obstaculo(self):
        cantos = pos.empacotar([(4, 4), (4, 4)], (2, 2, 20, 20), obstaculos=[(0, 0, 8, 8)], folga=1)
        for (x, y) in cantos:
            self.assertGreaterEqual(x, 2)
            self.assertGreaterEqual(y, 2)
            self.assertFalse(pos._colide((x, y, x + 4, y + 4), (0, 0, 8, 8), 1))
        a, b = [(x, y, x + 4, y + 4) for x, y in cantos]
        self.assertFalse(pos._colide(a, b, 1))

    def test_nao_cabe(self):
        self.assertIsNone(pos.empacotar([(30, 5)], (0, 0, 20, 20)))


class TestPosicionar(unittest.TestCase):
    def setUp(self):
        self.pecas = circuito()
        self.res = pos.posicionar(self.pecas, ["entrada", "mcu", "gravacao"])
        self.caixas = {p.ref: caixa_absoluta(p, self.res.posicoes[p.ref]) for p in self.pecas}

    def test_tudo_dentro_e_sem_sobreposicao(self):
        r = self.res
        self.assertEqual(set(r.posicoes), {p.ref for p in self.pecas})
        refs = sorted(self.caixas)
        for i, a in enumerate(refs):
            ca = self.caixas[a]
            self.assertTrue(ca[0] >= -1e-6 and ca[1] >= -1e-6 and ca[2] <= r.largura + 1e-6
                            and ca[3] <= r.altura + 1e-6, f"{a} fora da placa: {ca}")
            for b in refs[i + 1:]:
                self.assertFalse(pos._colide(ca, self.caixas[b], 0), f"{a} sobrepoe {b}")
            for furo in pos._cantos_furo(r.largura, r.altura, True):
                self.assertFalse(pos._colide(ca, furo, 0), f"{a} invade o canto do furo")

    def test_tamanho_automatico_em_passos_de_5_mm(self):
        self.assertEqual(self.res.largura % 5, 0)
        self.assertEqual(self.res.altura % 5, 0)
        self.assertEqual(len(self.res.furos), 4)

    def test_conector_encostado_na_borda_com_lado_comprido_paralelo(self):
        r = self.res
        for ref in ("J1", "J3"):
            borda, (x0, y0, x1, y1) = r.bordas[ref], self.caixas[ref]
            dist = {"esquerda": x0, "direita": r.largura - x1, "superior": y0, "inferior": r.altura - y1}[borda]
            self.assertAlmostEqual(dist, pos.MARGEM_CONECTOR, places=6)
            vertical = borda in ("esquerda", "direita")
            self.assertEqual((y1 - y0) >= (x1 - x0), vertical, ref)

    def test_antena_com_exclusao_inteira_fora_da_placa(self):
        r, u1 = self.res, next(p for p in self.pecas if p.ref == "U1")
        p = r.posicoes["U1"]
        ex0, ey0, ex1, ey1 = u1.exclusao[p.rotacao]
        ex = (p.x + ex0, p.y + ey0, p.x + ex1, p.y + ey1)
        dentro = ex[0] < r.largura and ex[2] > 0 and ex[1] < r.altura and ex[3] > 0
        self.assertFalse(dentro, f"area de exclusao dentro da placa: {ex}")

    def test_conector_nao_divide_borda_com_antena(self):
        self.assertNotEqual(self.res.bordas["J1"], self.res.bordas["U1"])
        self.assertNotEqual(self.res.bordas["J3"], self.res.bordas["U1"])

    def test_header_sozinho_segue_o_bloco_que_divide_sinais(self):
        """J3 (bloco so de conector) usa como referencia o bloco mcu (divide TX/RX/EN com ele)."""
        j3 = next(p for p in self.pecas if p.ref == "J3")
        self.assertEqual(pos._bloco_vizinho(j3, self.pecas, self.res.blocos), "mcu")
        self.assertNotIn("gravacao", self.res.blocos)

    def test_deterministico(self):
        outro = pos.posicionar(circuito(), ["entrada", "mcu", "gravacao"])
        self.assertEqual(outro.posicoes, self.res.posicoes)

    def test_tamanho_dado_que_nao_cabe_diz_o_minimo(self):
        with self.assertRaises(pos.ErroPosicionamento) as ctx:
            pos.posicionar(circuito(), ["entrada", "mcu", "gravacao"], largura=20, altura=20)
        self.assertIn("menor placa achada", str(ctx.exception))

    def test_tamanho_dado_que_cabe(self):
        r = pos.posicionar(circuito(), ["entrada", "mcu", "gravacao"], largura=100, altura=80)
        self.assertEqual((r.largura, r.altura), (100.0, 80.0))

    def test_sem_furos(self):
        r = pos.posicionar(circuito(), ["entrada", "mcu", "gravacao"], furos=False)
        self.assertEqual(r.furos, [])

    def test_bloco_fora_da_ordem_entra_no_fim(self):
        pecas = circuito() + [peca("X1", "outros", 3, 3)]
        r = pos.posicionar(pecas, ["entrada", "mcu", "gravacao"])
        self.assertIn("X1", r.posicoes)
        self.assertIn("outros", r.blocos)


class TestOrientacaoNaBorda(unittest.TestCase):
    def test_corpo_decide_e_nao_o_texto_de_referencia(self):
        """Borne com o corpo abaixo dos pads e o texto de referencia bem acima: na borda superior o
        corpo (lado do fio) vai para fora, mesmo que a caixa com o texto aponte o contrario."""
        rots = (0, 90, 180, 270)
        corpo = (-3.0, -2.0, 8.0, 6.0)
        caixa = (-3.0, -10.0, 8.0, 6.0)
        j = pos.Peca("J1", "b", {r: _girar(caixa, r) for r in rots}, {r: _ponto((2.5, 0.0), r) for r in rots},
                     True, frozenset(), None, {r: _girar(corpo, r) for r in rots})
        rot = pos._rotacao_na_borda(j, "superior")
        x0, y0, x1, y1 = j.corpo(rot)
        px, py = j.pads[rot]
        self.assertEqual(rot, 180)
        self.assertGreater(py - y0, y1 - py)


class TestAuxiliares(unittest.TestCase):
    def test_eh_conector(self):
        self.assertTrue(pos.eh_conector("J1"))
        self.assertTrue(pos.eh_conector("J12"))
        self.assertFalse(pos.eh_conector("JP1"))
        self.assertFalse(pos.eh_conector("U1"))

    def test_redes_de_sinal_ignora_rede_global(self):
        tamanho = {"GND": 20, "TX": 2}
        self.assertEqual(pos.redes_de_sinal({"J3": {"GND", "TX"}}, tamanho), {"J3": frozenset({"TX"})})


if __name__ == "__main__":
    unittest.main()
