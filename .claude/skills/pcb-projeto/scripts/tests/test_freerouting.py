"""Testes de pcbkit.freerouting: comando, log e troca Specctra (sem rodar o Freerouting)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pcbkit import ambiente, freerouting as fr  # noqa: E402

# Trechos reais do DSN exportado pelo KiCad 10.0.0 (cabecalho com string_quote, plano, classes).
DSN = '''(pcb "C:/tmp/placa.dsn"
  (parser
    (string_quote ")
    (space_in_quoted_tokens on)
    (host_cad "KiCad's Pcbnew")
  )
  (structure
    (layer F.Cu (type signal))
    (plane GND (polygon F.Cu 0  100000 -100000  175000 -100000  175000 -155000  100000 -155000
            100000 -100000))
    (plane GND (polygon B.Cu 0  100000 -100000  175000 -100000  175000 -155000  100000 -155000
            100000 -100000))
    (via "Via[0-1]_600:300_um")
    (rule (width 250) (clearance 200))
  )
  (network
    (net GND (pins J1-2 C1-2))
    (class kicad_default +3V3 /BST_BUCK GND "unconnected-(U1-IO1-Pad39)"
      (circuit (use_via "Via[0-1]_600:300_um"))
      (rule (width 250) (clearance 200))
    )
    (class Power +12V /+12V_SYS /MOTOR_A
      (circuit (use_via "Via[0-1]_600:300_um"))
      (rule (width 800) (clearance 300))
    )
  )
  (wiring
  )
)
'''

SES = '''(session placa
  (base_design placa)
  (routes
    (resolution um 10)
    (parser
      (host_cad "KiCad's Pcbnew")
    )
    (network_out
      (net "/+12V_SYS"
        (wire
          (path F.Cu 6000
            1413778 -1303886
            1414146 -1304254
          )
        )
        (via "Via[0-1]_600:300_um" 1432934 -1249400
        )
      )
      (net +3V3
        (wire
          (path F.Cu 2500
            1 -2
            3 -4
          )
        )
      )
      (net +12V
        (wire
          (path B.Cu 8000
            5 -6
            7 -8
          )
        )
      )
    )
  )
)
'''

LOG = """2026-10-12 10:05:09.955 INFO   Freerouting v2.5.0 (build-date: 2026-10-05)
2026-10-12 10:05:15.324 INFO   [872AA0] Auto-routing pass #1 on board 'a' was completed in 1.22 seconds with score 838.83 (11 unrouted and 0 violations)
2026-10-12 10:05:15.791 INFO   [872AA0] Auto-routing pass #3 on board 'b' was completed in 0.19 seconds with score 853.48 (10 unrouted and 0 violations)
2026-10-12 10:05:16.011 INFO   [872AA0] Auto-routing stage completed: started with 44 unrouted nets, completed in 3.76 seconds, final score: 853.48 (10 unrouted and 0 violations), using 3.59 total CPU seconds
2026-10-12 10:05:16.055 INFO   [872AA0] Skipping optimization stage: the board has 10 unrouted connection(s)
2026-10-12 10:05:16.063 INFO   [872AA0] Job '872AA0' finished with state: COMPLETED (elapsed: 4.08 seconds)
"""


class TestComando(unittest.TestCase):
    def test_flags_reais_da_250(self):
        args = fr.comando(["java", "-jar", "fr.jar"], "a.dsn", "a.ses", "dados", passes=50, threads=4,
                          ignorar=["Power", "HV"], trilha_minima_um=150.0)
        self.assertEqual(args[:7], ["java", "-jar", "fr.jar", "-de", "a.dsn", "-do", "a.ses"])
        for flag in ("--router.autorouter.max_passes=50", "--router.fanout.enabled=false", "-da",
                     "--gui.enabled=false", "--user_data_path=dados",
                     "--router.autorouter.ignore_net_classes=Power,HV", "--router.neck_width_um=150"):
            self.assertIn(flag, args)
        self.assertEqual(args[args.index("-mt") + 1], "4")
        self.assertEqual(fr.dir_dados_de(args), "dados")

    def test_sem_classes_ignoradas_nao_passa_a_flag(self):
        args = fr.comando(["java"], "a.dsn", "a.ses", "d")
        self.assertFalse(any("ignore_net_classes" in a for a in args))
        self.assertNotIn("-mt", args)

    def test_sem_jar_ou_sem_java(self):
        sem_jar = ambiente.Ambiente(java="java")
        with self.assertRaisesRegex(fr.ErroFreerouting, "FREEROUTING_JAR"):
            fr.comando_base(sem_jar)
        sem_java = ambiente.Ambiente(freerouting_jar=Path("fr.jar"))
        with self.assertRaisesRegex(fr.ErroFreerouting, "Java"):
            fr.comando_base(sem_java)
        ok = ambiente.Ambiente(java="java", freerouting_jar=Path("fr.jar"))
        self.assertEqual(fr.comando_base(ok), ["java", "-jar", "fr.jar"])


class TestLog(unittest.TestCase):
    def test_resumo(self):
        r = fr.resumir_log(LOG)
        self.assertEqual((r.estado, r.pendentes_inicio, r.pendentes_fim, r.violacoes, r.passes, r.otimizou),
                         ("COMPLETED", 44, 10, 0, 3, False))
        self.assertIsNone(r.erro)

    def test_excecao(self):
        r = fr.resumir_log('Exception in thread "Thread-1" com.oracle.svm.core.jdk.UnsupportedFeatureError: x\n')
        self.assertIn("UnsupportedFeatureError", r.erro)
        self.assertIsNone(r.estado)


class TestSpecctra(unittest.TestCase):
    def test_classes_do_dsn_apesar_do_string_quote(self):
        classes = fr.classes_do_dsn(DSN)
        self.assertEqual(classes["Power"], ["+12V", "/+12V_SYS", "/MOTOR_A"])
        self.assertIn("unconnected-(U1-IO1-Pad39)", classes["kicad_default"])

    def test_sem_planos(self):
        texto, n = fr.sem_planos(DSN)
        self.assertEqual(n, 2)
        self.assertNotIn("(plane", texto)
        self.assertIn('(via "Via[0-1]_600:300_um")', texto)
        self.assertEqual(fr.classes_do_dsn(texto), fr.classes_do_dsn(DSN))
        self.assertEqual(texto.count("("), texto.count(")"))

    def test_filtrar_sessao_tira_so_as_redes_pedidas(self):
        texto, tirados = fr.filtrar_sessao(SES, ["/+12V_SYS", "+12V", "/NAO_ROTEADA"])
        self.assertEqual(tirados, {"/+12V_SYS": 1, "+12V": 1})
        self.assertNotIn("+12V_SYS", texto)
        self.assertNotIn("(net +12V", texto)
        self.assertIn("(net +3V3", texto)
        self.assertEqual(texto.count("("), texto.count(")"))

    def test_filtrar_sem_redes_devolve_igual(self):
        self.assertEqual(fr.filtrar_sessao(SES, []), (SES, {}))


if __name__ == "__main__":
    unittest.main()
