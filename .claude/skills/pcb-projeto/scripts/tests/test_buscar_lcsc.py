"""Testes de buscar_lcsc.py. Rede mockada; o teste real exige PCB_TESTES_REDE=1."""
import contextlib
import io
import json
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import buscar_lcsc as bl  # noqa: E402

ITEM_BASIC = {"lcsc": 1525, "mfr": "CL05B104KO5NNNC", "package": "0402", "is_basic": True,
              "is_preferred": False, "description": "100nF 16V X7R 0402 MLCC", "stock": 24396892,
              "price": 0.006}
ITEM_PREFERRED = {"lcsc": 99, "mfr": "XYZ", "package": "SOT-23", "is_basic": False,
                  "is_preferred": True, "description": "algo", "stock": 10, "price": 0.5}
ITEM_EXTENDED = {"lcsc": 7, "mfr": "ABC", "package": "", "is_basic": False, "is_preferred": False,
                 "description": "", "stock": None, "price": None}

# Trecho da resposta real de wmsc.lcsc.com/ftps/wm/product/detail?productCode=C25804 (2026-10-12),
# so com os campos que o script le e 3 das 5 quebras de preco.
DETALHE_C25804 = {
    "code": 200, "msg": None, "ok": True,
    "result": {
        "productCode": "C25804",
        "productModel": "0603WAF1002T5E",
        "productNameEn": "RES 10kΩ ±1% 100mW 0603",
        "brandNameEn": "UNI-ROYAL",
        "encapStandard": "0603",
        "stockNumber": 0,
        "productIntroEn": "10kΩ ±1% 100mW 0603 Thick Film Resistor",
        "pdfUrl": "https://datasheet.lcsc.com/datasheet/pdf/0a975aaa49b7c97f38a963127be4a823.pdf?productCode=C25804",
        "currencyType": "USD",
        "productPriceList": [
            {"ladder": 100, "productPrice": "0.0022", "usdPrice": 0.0022},
            {"ladder": 1000, "productPrice": "0.0018", "usdPrice": 0.0018},
            {"ladder": 5000, "productPrice": "0.0016", "usdPrice": 0.0016},
        ],
    },
}
DETALHE_INEXISTENTE = {"code": 200, "msg": None, "result": None, "ok": True}
VAZIO = {"components": []}


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


def por_url(jlcsearch, wmsc):
    """urlopen falso que escolhe a resposta (ou excecao) pelo host da URL pedida."""
    def falso(pedido, timeout=None):
        alvo = jlcsearch if "jlcsearch" in pedido.full_url else wmsc
        if isinstance(alvo, Exception):
            raise alvo
        return RespostaFalsa(alvo)
    return falso


def executar(argv):
    saida, erro = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
        codigo = bl.main(argv)
    return codigo, saida.getvalue(), erro.getvalue()


class TestMontarUrl(unittest.TestCase):
    def test_parametros_basicos(self):
        url = bl.montar_url("C1525", limite=3)
        self.assertIn("q=C1525", url)
        self.assertIn("limit=3", url)
        self.assertNotIn("is_basic", url)

    def test_basic_e_termo_com_espaco(self):
        url = bl.montar_url("10k 0603", basic=True)
        self.assertIn("q=10k+0603", url)
        self.assertIn("is_basic=true", url)


class TestNormalizar(unittest.TestCase):
    def test_classes(self):
        self.assertEqual(bl.normalizar(ITEM_BASIC)["classe"], "Basic")
        self.assertEqual(bl.normalizar(ITEM_PREFERRED)["classe"], "Preferred")
        self.assertEqual(bl.normalizar(ITEM_EXTENDED)["classe"], "Extended")

    def test_campos_e_links(self):
        r = bl.normalizar(ITEM_BASIC)
        self.assertEqual(r["lcsc"], "C1525")
        self.assertEqual(r["mpn"], "CL05B104KO5NNNC")
        self.assertEqual(r["fabricante"], "")
        self.assertEqual(r["link_jlc"], "https://jlcpcb.com/partdetail/C1525")
        self.assertEqual(r["link_lcsc"], "https://www.lcsc.com/product-detail/C1525.html")

    def test_campos_nulos_nao_quebram(self):
        r = bl.normalizar(ITEM_EXTENDED)
        self.assertIsNone(r["estoque"])
        self.assertEqual(r["encapsulamento"], "")

    def test_extrair_exige_lista_components(self):
        with self.assertRaises(bl.ErroBusca):
            bl.extrair_componentes({"outra": []})


class TestRelevancia(unittest.TestCase):
    def test_codigo_nao_avisa(self):
        self.assertIsNone(bl.aviso_relevancia([bl.normalizar(ITEM_BASIC)], "C1525"))

    def test_texto_sem_ocorrencia_avisa(self):
        self.assertIn("Nenhum resultado cita", bl.aviso_relevancia([bl.normalizar(ITEM_BASIC)], "LM358"))

    def test_texto_com_ocorrencia_nao_avisa(self):
        self.assertIsNone(bl.aviso_relevancia([bl.normalizar(ITEM_BASIC)], "100nF"))


class TestRequisitar(unittest.TestCase):
    def test_ok(self):
        with mock.patch("urllib.request.urlopen", return_value=RespostaFalsa({"components": []})):
            self.assertEqual(bl.requisitar("http://x"), {"components": []})

    def test_http_diferente_de_200(self):
        erro = urllib.error.HTTPError("http://x", 503, "indisponivel", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=erro):
            with self.assertRaisesRegex(bl.ErroBusca, "HTTP 503"):
                bl.requisitar("http://x")

    def test_timeout(self):
        with mock.patch("urllib.request.urlopen", side_effect=TimeoutError()):
            with self.assertRaisesRegex(bl.ErroBusca, "Tempo esgotado"):
                bl.requisitar("http://x")

    def test_timeout_dentro_de_urlerror(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError(TimeoutError())):
            with self.assertRaisesRegex(bl.ErroBusca, "Tempo esgotado"):
                bl.requisitar("http://x")

    def test_sem_rede(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("dns")):
            with self.assertRaisesRegex(bl.ErroBusca, "Sem conexao"):
                bl.requisitar("http://x")

    def test_json_invalido(self):
        with mock.patch("urllib.request.urlopen", return_value=RespostaFalsa(b"<html>")):
            with self.assertRaisesRegex(bl.ErroBusca, "JSON"):
                bl.requisitar("http://x")


class TestDetalheLcsc(unittest.TestCase):
    def test_normaliza_resposta_real(self):
        r = bl.extrair_detalhe(DETALHE_C25804)[0]
        self.assertEqual(r["lcsc"], "C25804")
        self.assertEqual(r["mpn"], "0603WAF1002T5E")
        self.assertEqual(r["fabricante"], "UNI-ROYAL")
        self.assertEqual(r["encapsulamento"], "0603")
        self.assertEqual(r["estoque"], 0)
        self.assertEqual(r["estoque_origem"], "lcsc")
        self.assertEqual(r["fonte"], "lcsc-detail")
        self.assertEqual(r["classe"], "desconhecido")
        self.assertEqual(r["preco_unitario_usd"], 0.0022)
        self.assertEqual(r["preco_quebra_qtd"], 100)
        self.assertIn("productCode=C25804", r["datasheet"])
        self.assertEqual(r["link_jlc"], "https://jlcpcb.com/partdetail/C25804")

    def test_mesmas_chaves_do_jlcsearch(self):
        self.assertEqual(set(bl.extrair_detalhe(DETALHE_C25804)[0]), set(bl.normalizar(ITEM_BASIC)))

    def test_codigo_desconhecido_da_lista_vazia(self):
        self.assertEqual(bl.extrair_detalhe(DETALHE_INEXISTENTE), [])

    def test_formato_inesperado_vira_erro(self):
        with self.assertRaisesRegex(bl.ErroBusca, "result"):
            bl.extrair_detalhe({"code": 200})
        with self.assertRaisesRegex(bl.ErroBusca, "productCode"):
            bl.extrair_detalhe({"result": {"productModel": "X"}})

    def test_preco_ausente_ou_invalido_nao_quebra(self):
        produto = {"productCode": "C1", "productPriceList": [{"ladder": 1, "productPrice": "abc"}]}
        self.assertIsNone(bl.normalizar_detalhe(produto)["preco_unitario_usd"])
        self.assertIsNone(bl.normalizar_detalhe({"productCode": "C1"})["preco_unitario_usd"])

    def test_preco_cai_para_productprice_sem_usdprice(self):
        produto = {"productCode": "C1", "productPriceList": [{"ladder": 10, "productPrice": "0.5"}]}
        self.assertEqual(bl.normalizar_detalhe(produto)["preco_unitario_usd"], 0.5)

    def test_url_e_user_agent_de_navegador(self):
        self.assertEqual(bl.montar_url_detalhe("C25804"),
                         "https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C25804")
        capturado = {}

        def falso(pedido, timeout=None):
            capturado["ua"] = pedido.get_header("User-agent")
            return RespostaFalsa(DETALHE_C25804)
        with mock.patch("urllib.request.urlopen", side_effect=falso):
            bl.buscar_detalhe_lcsc("C25804")
        self.assertTrue(capturado["ua"].startswith("Mozilla/5.0"))


class TestFallback(unittest.TestCase):
    def test_aciona_quando_jlcsearch_vem_vazio(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, DETALHE_C25804)):
            r = bl.buscar("C25804")
        self.assertEqual(r[0]["mpn"], "0603WAF1002T5E")
        self.assertEqual(r[0]["fonte"], "lcsc-detail")

    def test_aceita_codigo_sem_c(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, DETALHE_C25804)):
            self.assertEqual(bl.buscar("25804")[0]["lcsc"], "C25804")

    def test_nao_aciona_quando_jlcsearch_acha(self):
        with mock.patch("urllib.request.urlopen",
                        side_effect=por_url({"components": [ITEM_BASIC]}, OSError("nao devia chamar"))):
            r = bl.buscar("C1525")
        self.assertEqual(r[0]["fonte"], "jlcsearch")

    def test_nao_aciona_para_texto(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, OSError("nao devia chamar"))):
            self.assertEqual(bl.buscar("LM358"), [])

    def test_nao_aciona_quando_jlcsearch_falha(self):
        erro = urllib.error.URLError("dns")
        with mock.patch("urllib.request.urlopen", side_effect=por_url(erro, OSError("nao devia chamar"))):
            with self.assertRaisesRegex(bl.ErroBusca, "Sem conexao com jlcsearch"):
                bl.buscar("C25804")

    def test_wmsc_403_tem_mensagem_clara(self):
        erro = urllib.error.HTTPError("http://x", 403, "proibido", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, erro)):
            with self.assertRaises(bl.ErroBusca) as ctx:
                bl.buscar("C25804")
        mensagem = str(ctx.exception)
        self.assertIn("HTTP 403", mensagem)
        self.assertIn("LCSC", mensagem)
        self.assertIn("C25804", mensagem)

    def test_wmsc_timeout_tem_mensagem_clara(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, TimeoutError())):
            with self.assertRaisesRegex(bl.ErroBusca, "Tempo esgotado.*LCSC"):
                bl.buscar("C25804")

    def test_wmsc_nao_json_vira_erro(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, b"<html>")):
            with self.assertRaisesRegex(bl.ErroBusca, "JSON"):
                bl.buscar("C25804")


class TestMain(unittest.TestCase):
    def test_sucesso_texto(self):
        with mock.patch("urllib.request.urlopen", return_value=RespostaFalsa({"components": [ITEM_BASIC]})):
            codigo, saida, _ = executar(["C1525"])
        self.assertEqual(codigo, 0)
        self.assertIn("C1525", saida)
        self.assertIn("[Basic]", saida)
        self.assertIn("nao oficial", saida)

    def test_sucesso_json(self):
        with mock.patch("urllib.request.urlopen", return_value=RespostaFalsa({"components": [ITEM_BASIC]})):
            codigo, saida, _ = executar(["C1525", "--json"])
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(saida)["resultados"][0]["lcsc"], "C1525")

    def test_codigo_que_nenhuma_fonte_conhece(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, DETALHE_INEXISTENTE)):
            codigo, _, erro = executar(["C25804"])
        self.assertEqual(codigo, bl.SAIDA_SEM_RESULTADO)
        self.assertIn("https://jlcpcb.com/partdetail/C25804", erro)

    def test_texto_sem_resultado(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, OSError("nao devia chamar"))):
            codigo, _, erro = executar(["LM358"])
        self.assertEqual(codigo, bl.SAIDA_SEM_RESULTADO)
        self.assertIn("jlcpcb.com/parts", erro)

    def test_fallback_texto_destaca_estoque_da_lcsc(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, DETALHE_C25804)):
            codigo, saida, erro = executar(["C25804"])
        self.assertEqual(codigo, 0)
        self.assertIn("0603WAF1002T5E", saida)
        self.assertIn("UNI-ROYAL", saida)
        self.assertIn("estoque LCSC: 0 (NAO e o estoque da montagem JLC)", saida)
        self.assertIn("[desconhecido]", saida)
        self.assertIn("Datasheet: https://datasheet.lcsc.com/", saida)
        self.assertEqual(erro, "")

    def test_fallback_json_mantem_a_forma(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, DETALHE_C25804)):
            codigo, saida, _ = executar(["C25804", "--json"])
        dados = json.loads(saida)
        self.assertEqual(codigo, 0)
        self.assertEqual(set(dados), {"termo", "resultados"})
        self.assertEqual(dados["resultados"][0]["fonte"], "lcsc-detail")
        self.assertEqual(dados["resultados"][0]["mpn"], "0603WAF1002T5E")

    def test_fallback_com_basic_avisa_que_o_filtro_nao_vale(self):
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, DETALHE_C25804)):
            codigo, _, erro = executar(["C25804", "--basic"])
        self.assertEqual(codigo, 0)
        self.assertIn("--basic nao se aplica", erro)

    def test_fallback_com_erro_sai_com_3(self):
        erro_http = urllib.error.HTTPError("http://x", 403, "proibido", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=por_url(VAZIO, erro_http)):
            codigo, saida, erro = executar(["C25804"])
        self.assertEqual(codigo, bl.SAIDA_ERRO_REDE)
        self.assertEqual(saida, "")
        self.assertIn("HTTP 403", erro)

    def test_busca_por_texto_sempre_avisa_em_stderr(self):
        with mock.patch("urllib.request.urlopen", return_value=RespostaFalsa({"components": [ITEM_BASIC]})):
            codigo, saida, erro = executar(["100nF", "--json"])
        self.assertEqual(codigo, 0)
        self.assertIn("pouco confiavel", erro)
        self.assertIn("MPN", erro)
        json.loads(saida)  # o aviso nao suja o JSON

    def test_busca_por_codigo_nao_da_aviso_de_texto(self):
        with mock.patch("urllib.request.urlopen", return_value=RespostaFalsa({"components": [ITEM_BASIC]})):
            _, _, erro = executar(["C1525"])
        self.assertEqual(erro, "")

    def test_erro_de_rede_sai_com_3(self):
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("dns")):
            codigo, _, erro = executar(["C1525"])
        self.assertEqual(codigo, bl.SAIDA_ERRO_REDE)
        self.assertIn("Erro:", erro)

    def test_limite_invalido(self):
        self.assertEqual(executar(["x", "--limite", "0"])[0], 2)


@unittest.skipUnless(os.environ.get("PCB_TESTES_REDE"), "defina PCB_TESTES_REDE=1 para testar a rede real")
class TestRedeReal(unittest.TestCase):
    def test_busca_por_codigo_no_jlcsearch(self):
        # C1525 esta no indice (estoque > 0). C25804 e AP63203 estavam fora em 2026-10-12.
        resultados = bl.buscar("C1525", limite=1)
        self.assertEqual(resultados[0]["lcsc"], "C1525")
        self.assertIn(resultados[0]["classe"], {"Basic", "Preferred", "Extended"})

    def test_fallback_por_codigo_na_lcsc(self):
        # C25804 esta fora do jlcsearch (sem estoque na JLC), mas a LCSC conhece.
        resultados = bl.buscar("C25804")
        self.assertEqual(resultados[0]["lcsc"], "C25804")
        self.assertEqual(resultados[0]["mpn"], "0603WAF1002T5E")
        self.assertEqual(resultados[0]["fonte"], "lcsc-detail")


if __name__ == "__main__":
    unittest.main()
