"""Testes de pcbkit.nota: frontmatter das notas de portao e criterio de aprovacao."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import nota  # noqa: E402

MODELO = Path(__file__).resolve().parents[2] / "assets" / "docs" / "Eletronica" / "Gerber" / \
    "{{placa}}_Rev{{rev}}_Liberacao_Fabricacao.md"


def _nota(status="aprovado", revisores="[Fulano]", corpo="- [x] item feito\n"):
    return nota.carregar_texto(f"---\ntitle: x\nstatus: {status}\nrevisores: {revisores}\nplaca: p\n---\n\n{corpo}")


class TestFrontmatter(unittest.TestCase):
    def test_escalares_e_lista_em_linha(self):
        n = _nota(revisores="[Ana, 'Bruno Silva']")
        self.assertEqual(n.frontmatter["status"], "aprovado")
        self.assertEqual(nota.revisores(n), ["Ana", "Bruno Silva"])

    def test_lista_vazia(self):
        self.assertEqual(nota.revisores(_nota(revisores="[]")), [])

    def test_lista_em_bloco(self):
        n = nota.carregar_texto("---\nstatus: aprovado\nrevisores:\n  - Ana\n  - Bruno\ndate:\n---\ncorpo\n")
        self.assertEqual(nota.revisores(n), ["Ana", "Bruno"])
        self.assertEqual(n.frontmatter["date"], "")

    def test_vazios_do_yaml_nao_contam_como_revisor(self):          # achado 4
        for valor in ("null", "~", "Null", '""', "''", "[]  # pendente", "[ ]", "['']", "[null, ~]",
                      "# so comentario"):
            self.assertEqual(nota.revisores(_nota(revisores=valor)), [], valor)
            self.assertTrue(any("revisores" in m for m in nota.pendencias(_nota(revisores=valor))), valor)

    def test_comentario_cortado_fora_de_aspas(self):
        self.assertEqual(nota.revisores(_nota(revisores="[Ana]  # revisou em 12/10")), ["Ana"])
        self.assertEqual(nota.revisores(_nota(revisores="'Ana # Silva'")), ["Ana # Silva"])
        self.assertEqual(_nota(status="aprovado # pela Ana").frontmatter["status"], "aprovado")

    def test_lista_em_bloco_na_coluna_zero_e_com_nulos(self):
        n = nota.carregar_texto("---\nstatus: aprovado\nrevisores:\n- Ana\n- null\n- ~\n---\nok\n")
        self.assertEqual(nota.revisores(n), ["Ana"])

    def test_campo_repetido_bloqueia(self):
        n = nota.carregar_texto("---\nstatus: rascunho\nrevisores: [Ana]\nstatus: aprovado\n---\nok\n")
        self.assertIn("campo(s) repetido(s) no frontmatter: status", nota.pendencias(n)[0])

    def test_bom_utf8_no_inicio(self):
        n = nota.carregar_texto("﻿---\nstatus: aprovado\nrevisores: [Ana]\n---\nok\n")
        self.assertEqual(nota.pendencias(n), [])

    def test_sem_frontmatter(self):
        n = nota.carregar_texto("# Titulo\n- [ ] coisa\n")
        self.assertEqual(n.frontmatter, {})
        self.assertTrue(any("status" in m for m in nota.pendencias(n)))

    def test_modelo_do_template_e_rascunho(self):
        n = nota.ler(MODELO)
        self.assertEqual(n.frontmatter["status"], "rascunho")
        self.assertEqual(nota.revisores(n), [])
        self.assertGreater(len(nota.itens_abertos(n.corpo)), 10)


class TestAprovacao(unittest.TestCase):
    def test_aprovada(self):
        self.assertEqual(nota.pendencias(_nota()), [])

    def test_rascunho(self):
        motivos = nota.pendencias(_nota(status="rascunho"))
        self.assertEqual(len(motivos), 1)
        self.assertIn("rascunho", motivos[0])

    def test_sem_revisores(self):
        motivos = nota.pendencias(_nota(revisores="[]"))
        self.assertEqual(len(motivos), 1)
        self.assertIn("revisores", motivos[0])

    def test_item_aberto(self):
        motivos = nota.pendencias(_nota(corpo="- [x] feito\n  - [ ] subitem aberto\n* [ ] outro\n"))
        self.assertEqual(len(motivos), 1)
        self.assertIn("2 item(ns)", motivos[0])

    def test_na_com_motivo_conta_como_marcado(self):
        corpo = "- [x] N/A — sem radio nesta placa\n- [X] N/A: sem USB\n- [x] NA - sem cristal\n"
        self.assertEqual(nota.pendencias(_nota(corpo=corpo)), [])

    def test_na_sem_motivo_bloqueia(self):
        motivos = nota.pendencias(_nota(corpo="- [x] N/A\n- [x] N/A —\n"))
        self.assertEqual(len(motivos), 1)
        self.assertIn("2 item(ns) 'N/A' sem motivo", motivos[0])

    def test_checkbox_em_bloco_de_codigo_e_inline_nao_conta(self):
        corpo = "Use `- [ ]` para itens.\n```\n- [ ] exemplo\n```\n- [x] feito\n"
        self.assertEqual(nota.pendencias(_nota(corpo=corpo)), [])

    def test_itens_numerados_e_em_callout_contam(self):             # achado 5
        corpo = "1. [ ] numerado\n2) [ ] outro\n> [!warning]\n> - [ ] no callout\n>> * [ ] aninhado\n- [/] meio\n"
        self.assertEqual(nota.itens_abertos(corpo), ["numerado", "outro", "no callout", "aninhado", "meio"])

    def test_na_minusculo_sem_motivo_bloqueia(self):
        motivos = nota.pendencias(_nota(corpo="- [x] n/a\n1. [x] na\n> - [X] N/a —\n- [x] n/a — sem USB\n"))
        self.assertEqual(len(motivos), 1)
        self.assertIn("3 item(ns) 'N/A' sem motivo", motivos[0])

    def test_cerca_so_fecha_com_mesmo_marcador_e_comprimento(self):
        # ```` com ``` dentro: a cerca fecha no ```` e o item depois dela esta aberto
        self.assertEqual(nota.itens_abertos("````\n```\n````\n- [ ] aberto\n"), ["aberto"])
        # ~~~ dentro de ``` nao fecha: o item continua dentro do codigo
        self.assertEqual(nota.itens_abertos("```\n~~~\n- [ ] exemplo\n~~~\n```\n"), [])
        # cerca de fechamento mais longa vale; com texto depois nao fecha
        self.assertEqual(nota.itens_abertos("```\n`````\n- [ ] fora\n"), ["fora"])
        self.assertEqual(nota.cerca_aberta("```\n``` texto\n- [ ] dentro\n"), "```")

    def test_cerca_sem_fechamento_bloqueia(self):
        motivos = nota.pendencias(_nota(corpo="- [x] feito\n```\n- [ ] escondido\n"))
        self.assertEqual(len(motivos), 1)
        self.assertIn("bloco de codigo aberto com ``` sem fechamento", motivos[0])

    def test_ler_arquivo_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            arq = Path(tmp) / "nota & ç.md"
            arq.write_text("---\nstatus: aprovado\nrevisores: [Joao Conceição]\n---\n- [x] ok\n", encoding="utf-8")
            n = nota.ler(arq)
        self.assertEqual(nota.revisores(n), ["Joao Conceição"])
        self.assertEqual(nota.pendencias(n), [])


if __name__ == "__main__":
    unittest.main()
