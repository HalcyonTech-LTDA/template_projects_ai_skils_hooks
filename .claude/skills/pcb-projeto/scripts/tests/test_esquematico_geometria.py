"""Geometria do esquematico: transformacao biblioteca -> folha (sem KiCad) e o oraculo dos demos (com KiCad)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import ambiente, bibliotecas, sexpr  # noqa: E402
from pcbkit.esquematico import geometria as g  # noqa: E402
from pcbkit.esquematico.caixas import Caixa, caixa_texto  # noqa: E402

AMB = ambiente.detectar()


def pino(x, y, angulo):
    return bibliotecas.Pino("1", "A", "passive", "line", x, y, angulo, 2.54, 1, 1)


class TestTransformacao(unittest.TestCase):
    # Pino a direita (x = 5.08) e acima (y = 2.54) da origem, apontando para a esquerda (para o corpo).
    P = pino(5.08, 2.54, 180)

    def _pos(self, rot, espelho=None):
        return g.posicao_pino(self.P, (100, 100), g.Orientacao(rot, espelho))

    def test_rotacao_0_inverte_y(self):
        self.assertEqual(self._pos(0), (105.08, 97.46))

    def test_rotacao_90_anti_horaria_na_tela(self):
        # (5.08, 2.54) girado 90 graus anti-horario (Y para cima) = (-2.54, 5.08) -> folha (-2.54, -5.08)
        self.assertEqual(self._pos(90), (97.46, 94.92))

    def test_rotacao_180(self):
        self.assertEqual(self._pos(180), (94.92, 102.54))

    def test_rotacao_270(self):
        self.assertEqual(self._pos(270), (102.54, 105.08))

    def test_espelho_x_inverte_y_na_folha(self):
        self.assertEqual(self._pos(0, "x"), (105.08, 102.54))

    def test_espelho_y_inverte_x_na_folha(self):
        self.assertEqual(self._pos(0, "y"), (94.92, 97.46))

    def test_espelho_vem_depois_da_rotacao(self):
        # rot 90 leva a (-2.54, -5.08); espelho y inverte X -> (+2.54, -5.08)
        self.assertEqual(self._pos(90, "y"), (102.54, 94.92))

    def test_direcao_para_fora_e_oposta_ao_corpo(self):
        self.assertEqual(g.direcao_para_fora(self.P), (1, 0))
        self.assertEqual(g.direcao_para_fora(self.P, g.Orientacao(90)), (0, -1))
        self.assertEqual(g.direcao_para_fora(self.P, g.Orientacao(180)), (-1, 0))
        self.assertEqual(g.direcao_para_fora(self.P, g.Orientacao(270)), (0, 1))
        self.assertEqual(g.direcao_para_fora(self.P, g.Orientacao(0, "y")), (-1, 0))

    def test_angulo_da_direcao(self):
        self.assertEqual([g.angulo_da_direcao(v) for v in ((1, 0), (0, -1), (-1, 0), (0, 1))], [0, 90, 180, 270])

    def test_grade(self):
        self.assertEqual(g.na_grade(101.60000001), 101.6)
        self.assertEqual(g.na_grade(2.0), 2.54)
        self.assertEqual(g.na_grade(1.9), 1.27)


class TestCaixas(unittest.TestCase):
    def test_texto_vertical_cresce_para_cima(self):
        c = caixa_texto("ABCD", 10, 10, 1.27, 90, "left", "bottom")
        self.assertLess(c.y1, 10 - 4)
        self.assertAlmostEqual(c.y2, 10)

    def test_cruza(self):
        self.assertTrue(Caixa(0, 0, 2, 2).cruza(Caixa(1, 1, 3, 3)))
        self.assertFalse(Caixa(0, 0, 2, 2).cruza(Caixa(2, 0, 3, 2)))


def _pontos_conectaveis(sch):
    pts = set()
    for w in sexpr.filhos(sch, "wire"):
        pts |= {(round(xy[1], 2), round(xy[2], 2)) for xy in sexpr.filhos(sexpr.filho(w, "pts"), "xy")}
    for tag in ("label", "no_connect", "junction"):
        pts |= {(round(sexpr.filho(n, "at")[1], 2), round(sexpr.filho(n, "at")[2], 2)) for n in sexpr.filhos(sch, tag)}
    return pts


@unittest.skipUnless(AMB.share and (AMB.share / "demos" / "pic_programmer").is_dir(), "demos do KiCad ausentes")
class TestOraculoDemos(unittest.TestCase):
    """Todo pino de todo simbolo do demo cai numa ponta de fio, label, NC ou outro pino."""

    def test_pic_programmer(self):
        sch = sexpr.carregar_arquivo(AMB.share / "demos" / "pic_programmer" / "pic_programmer.kicad_sch")
        libs = {str(s[1]): s for s in sexpr.filhos(sexpr.filho(sch, "lib_symbols"), "symbol")}
        conect = _pontos_conectaveis(sch)
        todos, soltos, orientacoes = [], [], set()
        for inst in sexpr.filhos(sch, "symbol"):
            at, esp = sexpr.filho(inst, "at"), sexpr.valor(inst, "mirror")
            o = g.Orientacao(int(at[3]), str(esp) if esp else None)
            orientacoes.add(o)
            unidade = sexpr.valor(inst, "unit", 1)
            for p in bibliotecas.pinos_do_no(libs[str(sexpr.valor(inst, "lib_id"))]):
                if p.unidade in (0, unidade) and p.corpo in (0, 1):
                    todos.append(tuple(round(v, 2) for v in g.posicao_pino(p, (at[1], at[2]), o)))
        for pos in todos:
            if pos not in conect and todos.count(pos) < 2:
                soltos.append(pos)
        self.assertGreater(len(todos), 150)
        self.assertGreaterEqual(len(orientacoes), 5)     # 0/90/180/270 e espelhos x e y
        self.assertEqual(soltos, [])


if __name__ == "__main__":
    unittest.main()
