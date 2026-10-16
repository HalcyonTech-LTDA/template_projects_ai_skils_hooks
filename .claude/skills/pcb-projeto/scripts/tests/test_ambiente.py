"""Testes de pcbkit.ambiente e do diagnostico.py (sem depender do KiCad instalado)."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import diagnostico  # noqa: E402
from pcbkit import ambiente  # noqa: E402


def _instalacao_falsa(raiz, versao="10.0"):
    d = Path(raiz) / versao
    (d / "bin").mkdir(parents=True)
    (d / "bin" / "kicad-cli.exe").write_text("")
    (d / "share" / "kicad" / "symbols").mkdir(parents=True)
    return d


class TestLocalizar(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="pcbkit-amb-")
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)

    def test_variavel_kicad_cli(self):
        d = _instalacao_falsa(self.raiz)
        with mock.patch.dict(os.environ, {"KICAD_CLI": str(d / "bin" / "kicad-cli.exe")}):
            cli, kdir = ambiente.localizar_kicad_cli()
        self.assertEqual(Path(cli).name, "kicad-cli.exe")
        self.assertEqual(kdir.resolve(), d.resolve())

    def test_variavel_kicad_dir(self):
        d = _instalacao_falsa(self.raiz)
        with mock.patch.dict(os.environ, {"KICAD_DIR": str(d)}):
            os.environ.pop("KICAD_CLI", None)
            cli, kdir = ambiente.localizar_kicad_cli()
        self.assertEqual(kdir, d)

    def test_maior_versao_instalada(self):
        _instalacao_falsa(self.raiz, "9.0")
        d10 = _instalacao_falsa(self.raiz, "10.0")
        _instalacao_falsa(self.raiz, "8.0")
        limpo = {k: v for k, v in os.environ.items() if k not in ("KICAD_CLI", "KICAD_DIR")}
        with mock.patch.dict(os.environ, limpo, clear=True), \
                mock.patch.object(ambiente, "RAIZES_WINDOWS", [self.raiz]):
            cli, kdir = ambiente.localizar_kicad_cli()
        self.assertEqual(kdir, d10)

    def test_variaveis_de_caminho_padrao_e_sobrescrita(self):
        d = _instalacao_falsa(self.raiz)
        amb = ambiente.Ambiente(kicad_dir=d, share=d / "share" / "kicad", maior=10)
        limpo = {k: v for k, v in os.environ.items() if not k.startswith("KICAD")}
        with mock.patch.dict(os.environ, limpo, clear=True):
            self.assertEqual(amb.dir_simbolos(), d / "share" / "kicad" / "symbols")
            os.environ["KICAD10_SYMBOL_DIR"] = str(self.raiz / "outro")
            self.assertEqual(amb.dir_simbolos(), self.raiz / "outro")

    def test_chaves_so_presenca(self):
        with mock.patch.dict(os.environ, {"MOUSER_API_KEY": "segredo-123"}):
            os.environ.pop("DIGIKEY_CLIENT_ID", None)
            amb = ambiente.detectar()
        self.assertIs(amb.chaves["MOUSER_API_KEY"], True)
        self.assertIs(amb.chaves["DIGIKEY_CLIENT_ID"], False)


class TestDiagnostico(unittest.TestCase):
    def _rodar(self, *args):
        saida = io.StringIO()
        with mock.patch.object(ambiente, "verificar_pcbnew", return_value=(True, "10.0.0")), \
                mock.patch.object(ambiente, "versao_kicad", return_value="10.0.0"), \
                mock.patch.object(ambiente, "versao_java", return_value="21"), \
                mock.patch.dict(os.environ, {"MOUSER_API_KEY": "segredo-mouser-987"}), \
                contextlib.redirect_stdout(saida):
            rc = diagnostico.main(list(args))
        return rc, saida.getvalue()

    def test_nao_vaza_valor_de_chave(self):
        for args in ([], ["--json"]):
            rc, texto = self._rodar(*args)
            self.assertNotIn("segredo-mouser-987", texto)
        dados = json.loads(self._rodar("--json")[1])
        self.assertIs(dados["chaves_distribuidor"]["MOUSER_API_KEY"], True)
        self.assertIn("uvx", dados)

    def test_falta_do_nucleo_da_codigo_1(self):
        info = {"kicad_cli": None, "pcbnew": {"ok": False, "detalhe": "x"}, "java": None,
                "freerouting_jar": None, "uvx": None, "easyeda2kicad": None, "chaves_distribuidor": {}}
        faltas, avisos = diagnostico.problemas(info)
        self.assertEqual(len(faltas), 2)
        self.assertTrue(any("Java" in a for a in avisos))
        self.assertTrue(any("uvx" in a for a in avisos))


if __name__ == "__main__":
    unittest.main()
