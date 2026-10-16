"""Testes de buscar_distribuidor.py.

As fixtures foram montadas a partir dos schemas oficiais (swagger da Mouser e da
DigiKey), nao de chamadas reais: nao ha chave nesta maquina. Rede toda mockada.
"""
import contextlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import buscar_distribuidor as bd  # noqa: E402

MOUSER_OK = {
    "Errors": [],
    "SearchResults": {"NumberOfResult": 2, "Parts": [
        {"Availability": "1,234 In Stock", "AvailabilityInStock": "1234",
         "DataSheetUrl": "https://www.mouser.com/datasheet/lm358.pdf", "Description": "Op Amps Dual",
         "LifecycleStatus": "", "IsDiscontinued": "false", "Manufacturer": "Texas Instruments",
         "ManufacturerPartNumber": "LM358DR", "MouserPartNumber": "595-LM358DR",
         "ProductDetailUrl": "https://www.mouser.com/ProductDetail/595-LM358DR",
         "PriceBreaks": [{"Quantity": 100, "Price": "$0.35", "Currency": "USD"},
                         {"Quantity": 1, "Price": "$0.61", "Currency": "USD"}]},
        {"Availability": "None", "DataSheetUrl": "", "Description": "Antigo",
         "LifecycleStatus": "End of Life", "IsDiscontinued": "true", "Manufacturer": "Foo",
         "ManufacturerPartNumber": "OLD1", "MouserPartNumber": "1-OLD1", "ProductDetailUrl": "",
         "PriceBreaks": []},
    ]},
}

MOUSER_CHAVE_INVALIDA = {"Errors": [{"Id": 0, "Code": "Invalid", "Message": "Invalid unique identifier.",
                                     "PropertyName": "API Key"}], "SearchResults": None}

DIGIKEY_OK = {
    "ProductsCount": 2,
    "Products": [
        {"Description": {"ProductDescription": "IC OPAMP GP 2 CIRCUIT 8SOIC", "DetailedDescription": "..."},
         "Manufacturer": {"Id": 296, "Name": "Texas Instruments"},
         "ManufacturerProductNumber": "LM358DR", "UnitPrice": 0.61,
         "ProductUrl": "https://www.digikey.com/en/products/detail/texas-instruments/LM358DR/404084",
         "DatasheetUrl": "https://www.ti.com/lit/ds/symlink/lm358.pdf", "QuantityAvailable": 50000,
         "ProductStatus": {"Id": 0, "Status": "Active"},
         "ProductVariations": [
             {"DigiKeyProductNumber": "296-1014-1-ND", "StandardPricing": [
                 {"BreakQuantity": 10, "UnitPrice": 0.5, "TotalPrice": 5.0},
                 {"BreakQuantity": 1, "UnitPrice": 0.61, "TotalPrice": 0.61}]}]},
        {"Description": {"ProductDescription": "Velho"}, "Manufacturer": {"Name": "Bar"},
         "ManufacturerProductNumber": "OLD2", "UnitPrice": 1.2, "QuantityAvailable": 0,
         "ProductStatus": {"Id": 2, "Status": "Not For New Designs"}, "ProductVariations": []},
    ],
}


class RespostaFalsa:
    def __init__(self, corpo, status=200):
        self._corpo = corpo if isinstance(corpo, bytes) else json.dumps(corpo).encode("utf-8")
        self.status = status

    def read(self):
        return self._corpo

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def executar(argv, env):
    saida, erro = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
        codigo = bd.main(argv, env)
    return codigo, saida.getvalue(), erro.getvalue()


class TestSemCredencial(unittest.TestCase):
    def test_mouser_sai_com_2_e_instrucao(self):
        codigo, _, erro = executar(["mouser", "LM358"], {})
        self.assertEqual(codigo, 2)
        self.assertIn("MOUSER_API_KEY", erro)
        self.assertIn("settings.local.json", erro)

    def test_digikey_lista_so_o_que_falta(self):
        codigo, _, erro = executar(["digikey", "LM358"], {"DIGIKEY_CLIENT_ID": "abc"})
        self.assertEqual(codigo, 2)
        self.assertIn("DIGIKEY_CLIENT_SECRET", erro.splitlines()[0])
        self.assertNotIn("DIGIKEY_CLIENT_ID,", erro.splitlines()[0])

    def test_valor_em_branco_conta_como_falta(self):
        self.assertEqual(executar(["mouser", "x"], {"MOUSER_API_KEY": "   "})[0], 2)

    def test_sem_chamada_de_rede(self):
        with mock.patch("urllib.request.urlopen") as m:
            executar(["mouser", "LM358"], {})
        m.assert_not_called()

    def test_limite_fora_da_faixa(self):
        self.assertEqual(executar(["mouser", "x", "--limite", "99"], {"MOUSER_API_KEY": "k"})[0], 2)


class TestNumeros(unittest.TestCase):
    def test_parse_numero(self):
        casos = {"$0.61": 0.61, "0,61 EUR": 0.61, "1,234.56": 1234.56, "1.234,56": 1234.56,
                 "R$ 3,50": 3.5, "": None, "n/a": None, None: None}
        for entrada, esperado in casos.items():
            self.assertEqual(bd.parse_numero(entrada), esperado, entrada)

    def test_classificar_ciclo(self):
        self.assertEqual(bd.classificar_ciclo("Active"), "Active")
        self.assertEqual(bd.classificar_ciclo("Not For New Designs"), "NRND")
        self.assertEqual(bd.classificar_ciclo("Obsolete"), "Obsolete")
        self.assertEqual(bd.classificar_ciclo("Discontinued at Digi-Key"), "Obsolete")
        self.assertEqual(bd.classificar_ciclo("Last Time Buy"), "Last Time Buy")
        self.assertEqual(bd.classificar_ciclo(""), "n/d")


class TestMouser(unittest.TestCase):
    def test_normaliza_menor_quebra_e_estoque(self):
        r = bd.extrair_mouser(MOUSER_OK, 10)[0]
        self.assertEqual((r["mpn"], r["fabricante"]), ("LM358DR", "Texas Instruments"))
        self.assertEqual((r["preco_unitario"], r["quebra_qtd"], r["moeda"]), (0.61, 1, "USD"))
        self.assertEqual(r["estoque"], 1234)
        self.assertEqual(r["codigo_distribuidor"], "595-LM358DR")

    def test_descontinuada_e_sem_preco(self):
        r = bd.extrair_mouser(MOUSER_OK, 10)[1]
        self.assertEqual(r["ciclo_de_vida"], "Obsolete")
        self.assertIsNone(r["preco_unitario"])
        self.assertIsNone(r["estoque"])

    def test_limite_corta(self):
        self.assertEqual(len(bd.extrair_mouser(MOUSER_OK, 1)), 1)

    def test_chave_invalida_vem_com_http_200(self):
        with self.assertRaisesRegex(bd.ErroDistribuidor, "Invalid unique identifier"):
            bd.extrair_mouser(MOUSER_CHAVE_INVALIDA, 10)

    def test_corpos_das_duas_rotas(self):
        rota, corpo = bd.corpo_mouser("LM358", 5, "keyword")
        self.assertEqual((rota, corpo["SearchByKeywordRequest"]["keyword"]), ("keyword", "LM358"))
        self.assertEqual(corpo["SearchByKeywordRequest"]["records"], 5)
        rota, corpo = bd.corpo_mouser("LM358DR", 5, "partnumber")
        self.assertEqual((rota, corpo["SearchByPartRequest"]["mouserPartNumber"]), ("partnumber", "LM358DR"))

    def test_modo_auto(self):
        self.assertEqual(bd.modos_mouser("LM358DR", "auto"), ["partnumber", "keyword"])
        self.assertEqual(bd.modos_mouser("op amp dual", "auto"), ["keyword"])
        self.assertEqual(bd.modos_mouser("LM358", "keyword"), ["keyword"])

    def test_auto_cai_para_keyword_quando_partnumber_vem_vazio(self):
        vazio = {"Errors": [], "SearchResults": {"NumberOfResult": 0, "Parts": []}}
        respostas = [RespostaFalsa(vazio), RespostaFalsa(MOUSER_OK)]
        with mock.patch("urllib.request.urlopen", side_effect=respostas) as m:
            codigo, saida, _ = executar(["mouser", "LM358DR"], {"MOUSER_API_KEY": "k"})
        self.assertEqual(codigo, 0)
        self.assertEqual(m.call_count, 2)
        urls = [c.args[0].full_url for c in m.call_args_list]
        self.assertIn("/search/partnumber?apiKey=k", urls[0])
        self.assertIn("/search/keyword?apiKey=k", urls[1])
        self.assertIn("LM358DR", saida)

    def test_chave_nao_vaza_na_mensagem_de_erro(self):
        erro = urllib.error.HTTPError("https://api.mouser.com/x?apiKey=SEGREDO", 403, "no", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=erro):
            codigo, _, msg = executar(["mouser", "LM358"], {"MOUSER_API_KEY": "SEGREDO"})
        self.assertEqual(codigo, 3)
        self.assertNotIn("SEGREDO", msg)


class TestDigiKey(unittest.TestCase):
    def test_normaliza(self):
        r = bd.extrair_digikey(DIGIKEY_OK, "USD")[0]
        self.assertEqual((r["mpn"], r["fabricante"]), ("LM358DR", "Texas Instruments"))
        self.assertEqual((r["preco_unitario"], r["quebra_qtd"]), (0.61, 1))
        self.assertEqual(r["codigo_distribuidor"], "296-1014-1-ND")
        self.assertEqual(r["ciclo_de_vida"], "Active")
        self.assertTrue(r["datasheet"].endswith("lm358.pdf"))

    def test_sem_variacao_usa_unitprice_e_nrnd(self):
        r = bd.extrair_digikey(DIGIKEY_OK, "USD")[1]
        self.assertEqual(r["preco_unitario"], 1.2)
        self.assertEqual(r["ciclo_de_vida"], "NRND")
        self.assertEqual(r["codigo_distribuidor"], "")

    def test_resposta_sem_products(self):
        with self.assertRaises(bd.ErroDistribuidor):
            bd.extrair_digikey({"x": 1}, "USD")

    def test_fluxo_completo_token_e_cabecalhos(self):
        respostas = [RespostaFalsa({"access_token": "TOK", "expires_in": 599}), RespostaFalsa(DIGIKEY_OK)]
        env = {"DIGIKEY_CLIENT_ID": "id1", "DIGIKEY_CLIENT_SECRET": "sec1"}
        with mock.patch("urllib.request.urlopen", side_effect=respostas) as m:
            codigo, saida, _ = executar(["digikey", "LM358", "--moeda", "brl", "--site", "br", "--limite", "3"], env)
        self.assertEqual(codigo, 0)
        token_req, busca_req = (c.args[0] for c in m.call_args_list)
        self.assertEqual(token_req.full_url, bd.URL_DIGIKEY_TOKEN)
        self.assertIn(b"grant_type=client_credentials", token_req.data)
        self.assertEqual(busca_req.full_url, bd.URL_DIGIKEY_BUSCA)
        cab = {k.lower(): v for k, v in busca_req.header_items()}
        self.assertEqual(cab["authorization"], "Bearer TOK")
        self.assertEqual(cab["x-digikey-client-id"], "id1")
        self.assertEqual(cab["x-digikey-locale-currency"], "BRL")
        self.assertEqual(cab["x-digikey-locale-site"], "BR")
        self.assertEqual(cab["x-digikey-locale-language"], "en")
        self.assertEqual(json.loads(busca_req.data), {"Keywords": "LM358", "Limit": 3, "Offset": 0})
        self.assertIn("BRL 0.61", saida)

    def test_token_ausente(self):
        env = {"DIGIKEY_CLIENT_ID": "a", "DIGIKEY_CLIENT_SECRET": "b"}
        with mock.patch("urllib.request.urlopen", return_value=RespostaFalsa({"error": "x"})):
            codigo, _, erro = executar(["digikey", "LM358"], env)
        self.assertEqual(codigo, 3)
        self.assertIn("access_token", erro)


class TestErrosHttp(unittest.TestCase):
    ENV = {"MOUSER_API_KEY": "k"}

    def test_429(self):
        erro = urllib.error.HTTPError("u", 429, "x", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=erro):
            codigo, _, msg = executar(["mouser", "LM358"], self.ENV)
        self.assertEqual(codigo, 3)
        self.assertIn("429", msg)

    def test_timeout(self):
        with mock.patch("urllib.request.urlopen", side_effect=TimeoutError()):
            codigo, _, msg = executar(["mouser", "LM358"], self.ENV)
        self.assertEqual(codigo, 3)
        self.assertIn("Tempo esgotado", msg)

    def test_sem_resultado_sai_com_1(self):
        vazio = {"Errors": [], "SearchResults": {"NumberOfResult": 0, "Parts": []}}
        with mock.patch("urllib.request.urlopen", return_value=RespostaFalsa(vazio)):
            codigo, _, _ = executar(["mouser", "xyz", "--modo", "keyword"], self.ENV)
        self.assertEqual(codigo, 1)

    def test_json_de_saida(self):
        with mock.patch("urllib.request.urlopen", return_value=RespostaFalsa(MOUSER_OK)):
            codigo, saida, _ = executar(["mouser", "LM358", "--json", "--modo", "keyword"], self.ENV)
        self.assertEqual(codigo, 0)
        dados = json.loads(saida)
        self.assertEqual(dados["distribuidor"], "mouser")
        self.assertEqual(dados["resultados"][0]["mpn"], "LM358DR")


if __name__ == "__main__":
    unittest.main()
