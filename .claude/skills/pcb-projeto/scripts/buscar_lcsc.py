#!/usr/bin/env python3
"""Busca componentes no indice publico do jlcsearch (pecas LCSC/JLCPCB).

Uso:
    buscar_lcsc.py <termo ou Cxxxx> [--basic] [--json] [--limite N]

AVISOS (leia antes de confiar no resultado):

* O jlcsearch (https://jlcsearch.tscircuit.com) NAO e oficial. E mantido pela
  tscircuit (repo tscircuit/jlcsearch), sem chave, sem SLA e sem garantia de
  atualizacao. A LCSC/JLCPCB nao tem API publica oficial de busca.
* O endpoint usado e /api/search (parametros q, package, limit, is_basic).
  O servidor so devolve pecas com estoque > 0 no ultimo import. Peca fora do
  indice NAO significa peca inexistente ou sem estoque na JLC.
* Busca por codigo (C1525 ou 1525) e exata. Busca por texto e fraca: no teste
  de 2026-10-12 devolveu itens sem relacao com o termo. Por isso o script
  sempre imprime um aviso na busca por texto (em stderr, o --json fica limpo)
  e avisa de novo quando nenhum resultado contem o termo.
* A API do jlcsearch nao informa o fabricante (so o MPN). A coluna fica vazia
  de proposito: nao se infere fabricante pela descricao.
* Estoque e preco sao de um espelho e podem estar defasados. CONFIRA SEMPRE
  estoque, preco e classe (Basic/Preferred/Extended) na pagina da JLC
  (https://jlcpcb.com/partdetail/<Cxxxx>) antes de fechar o pedido.

FALLBACK POR CODIGO: se o termo e um codigo (Cxxxx) e o jlcsearch volta vazio,
o script consulta https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=<C>,
a API web da LCSC. Ela NAO e documentada, exige User-Agent de navegador e pode
mudar ou bloquear sem aviso. Resolve qualquer codigo, com ou sem estoque, e traz
MPN, fabricante, encapsulamento, descricao, escada de precos e datasheet.
Limites: o ESTOQUE e o da LCSC, nao o da montagem JLC, e ela nao diz se a peca
e Basic/Extended (classe "desconhecido"). O resultado vem com fonte "lcsc-detail".
Caminho recomendado para peca nova: MPN (Mouser/DigiKey ou datasheet) -> codigo
LCSC (site da JLC/LCSC ou busca web "<MPN> LCSC") -> confirmar com este script.

Codigos de saida: 0 achou; 1 sem resultado; 3 erro de rede/HTTP/resposta; 2 uso.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

URL_BUSCA = "https://jlcsearch.tscircuit.com/api/search"
URL_DETALHE_LCSC = "https://wmsc.lcsc.com/ftps/wm/product/detail"
LINK_JLC = "https://jlcpcb.com/partdetail/{codigo}"
LINK_LCSC = "https://www.lcsc.com/product-detail/{codigo}.html"
UA_PADRAO = "pcb-projeto/buscar_lcsc"
UA_NAVEGADOR = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TIMEOUT_S = 20
LIMITE_PADRAO = 10
LARGURA_DESCRICAO = 110

NOME_JLCSEARCH = "jlcsearch"
NOME_LCSC = "LCSC (wmsc.lcsc.com)"
FONTE_JLCSEARCH = "jlcsearch"
FONTE_DETALHE = "lcsc-detail"
CLASSE_DESCONHECIDA = "desconhecido"

SAIDA_OK = 0
SAIDA_SEM_RESULTADO = 1
SAIDA_ERRO_REDE = 3

AVISO_BUSCA_TEXTO = (
    "AVISO: a busca por texto do jlcsearch e pouco confiavel (devolve itens sem relacao com o termo). "
    "Caminho recomendado: achar o MPN (Mouser/DigiKey ou datasheet) -> achar o codigo LCSC "
    "(site da JLC/LCSC ou busca web '<MPN> LCSC') -> confirmar com buscar_lcsc.py <Cxxxx>."
)


class ErroBusca(Exception):
    """Falha de rede, HTTP ou formato de resposta."""


def montar_url(termo, basic=False, limite=LIMITE_PADRAO):
    params = {"q": termo, "limit": str(limite)}
    if basic:
        params["is_basic"] = "true"
    return f"{URL_BUSCA}?{urllib.parse.urlencode(params)}"


def montar_url_detalhe(codigo):
    return f"{URL_DETALHE_LCSC}?{urllib.parse.urlencode({'productCode': codigo})}"


def requisitar(url, timeout=TIMEOUT_S, nome=NOME_JLCSEARCH, user_agent=UA_PADRAO):
    """GET e devolve o JSON decodificado; qualquer falha vira ErroBusca (`nome` entra na mensagem)."""
    pedido = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as resposta:
            status = getattr(resposta, "status", 200)
            if status != 200:
                raise ErroBusca(f"{nome} respondeu HTTP {status}.")
            corpo = resposta.read().decode("utf-8")
    except urllib.error.HTTPError as erro:
        raise ErroBusca(f"{nome} respondeu HTTP {erro.code}.") from erro
    except TimeoutError as erro:
        raise ErroBusca(f"Tempo esgotado ({timeout}s) ao consultar {nome}.") from erro
    except urllib.error.URLError as erro:
        if isinstance(erro.reason, TimeoutError):
            raise ErroBusca(f"Tempo esgotado ({timeout}s) ao consultar {nome}.") from erro
        raise ErroBusca(f"Sem conexao com {nome}: {erro.reason}.") from erro
    try:
        return json.loads(corpo)
    except json.JSONDecodeError as erro:
        raise ErroBusca(f"Resposta de {nome} nao e JSON valido.") from erro


def classe_da_peca(item):
    if item.get("is_basic"):
        return "Basic"
    if item.get("is_preferred"):
        return "Preferred"
    return "Extended"


def normalizar(item):
    codigo = f"C{int(item.get('lcsc') or 0)}"
    return {
        "lcsc": codigo,
        "mpn": item.get("mfr") or "",
        "fabricante": "",
        "encapsulamento": item.get("package") or "",
        "descricao": item.get("description") or "",
        "estoque": item.get("stock"),
        "preco_unitario_usd": item.get("price"),
        "classe": classe_da_peca(item),
        "fonte": FONTE_JLCSEARCH,
        "estoque_origem": "jlc",
        "datasheet": "",
        "preco_quebra_qtd": None,
        "link_jlc": LINK_JLC.format(codigo=codigo),
        "link_lcsc": LINK_LCSC.format(codigo=codigo),
    }


def extrair_componentes(resposta):
    if not isinstance(resposta, dict) or not isinstance(resposta.get("components"), list):
        raise ErroBusca("Resposta do jlcsearch sem a lista 'components'.")
    return [normalizar(item) for item in resposta["components"]]


def primeira_quebra_de_preco(escada):
    """(preco_usd, quantidade) da menor quebra da escada de precos, ou (None, None)."""
    if not isinstance(escada, list) or not escada or not isinstance(escada[0], dict):
        return None, None
    quebra = escada[0]
    bruto = quebra.get("usdPrice") if quebra.get("usdPrice") is not None else quebra.get("productPrice")
    try:
        return float(bruto), quebra.get("ladder")
    except (TypeError, ValueError):
        return None, None


def normalizar_detalhe(produto):
    """Converte o `result` do detalhe da LCSC na mesma forma de normalizar()."""
    codigo = produto.get("productCode") or ""
    preco, quebra = primeira_quebra_de_preco(produto.get("productPriceList"))
    return {
        "lcsc": codigo,
        "mpn": produto.get("productModel") or "",
        "fabricante": produto.get("brandNameEn") or "",
        "encapsulamento": produto.get("encapStandard") or "",
        "descricao": produto.get("productIntroEn") or produto.get("productNameEn") or "",
        "estoque": produto.get("stockNumber"),
        "preco_unitario_usd": preco,
        "classe": CLASSE_DESCONHECIDA,
        "fonte": FONTE_DETALHE,
        "estoque_origem": "lcsc",
        "datasheet": produto.get("pdfUrl") or produto.get("pdfLinkUrl") or "",
        "preco_quebra_qtd": quebra,
        "link_jlc": LINK_JLC.format(codigo=codigo),
        "link_lcsc": LINK_LCSC.format(codigo=codigo),
    }


def extrair_detalhe(resposta):
    """[] se a LCSC nao conhece o codigo (`result` nulo); ErroBusca se o formato mudou."""
    if not isinstance(resposta, dict) or "result" not in resposta:
        raise ErroBusca("resposta sem o campo 'result' (a API nao documentada pode ter mudado).")
    produto = resposta["result"]
    if produto is None:
        return []
    if not isinstance(produto, dict) or not produto.get("productCode"):
        raise ErroBusca("resposta sem 'productCode' (a API nao documentada pode ter mudado).")
    return [normalizar_detalhe(produto)]


def eh_codigo_lcsc(termo):
    return re.fullmatch(r"[Cc]?\d+", termo.strip()) is not None


def codigo_canonico(termo):
    return "C" + termo.strip().lstrip("Cc")


def alguem_contem_termo(resultados, termo):
    """True se ao menos um resultado cita algum token do termo (mpn, descricao, codigo)."""
    tokens = [t for t in re.findall(r"[a-z0-9]+", termo.lower()) if len(t) > 1]
    for r in resultados:
        texto = f"{r['mpn']} {r['descricao']} {r['lcsc']}".lower()
        if any(t in texto for t in tokens):
            return True
    return False


def aviso_relevancia(resultados, termo):
    if eh_codigo_lcsc(termo) or not resultados:
        return None
    if alguem_contem_termo(resultados, termo):
        return None
    return ("Nenhum resultado cita o termo buscado. A busca por texto do jlcsearch "
            "esta imprecisa; trate a lista como ruido e confira no site da JLC.")


def mensagem_sem_resultado(termo):
    linhas = [f"Nenhum resultado para '{termo}'."]
    if eh_codigo_lcsc(termo):
        linhas.append("O jlcsearch so cobre pecas com estoque > 0 e o detalhe da LCSC "
                      "nao conhece esse codigo.")
        linhas.append(f"Confira direto: {LINK_JLC.format(codigo=codigo_canonico(termo))}")
    else:
        linhas.append("O indice do jlcsearch so cobre pecas com estoque > 0; "
                      "a peca pode existir na JLC/LCSC mesmo assim.")
        linhas.append("Pesquise em https://jlcpcb.com/parts ou tente o MPN exato.")
    return "\n".join(linhas)


def formatar_preco(preco):
    return "n/d" if preco is None else f"US$ {preco:g}"


def formatar_estoque(estoque):
    return "n/d" if estoque is None else f"{estoque:,}".replace(",", ".")


def cortar(texto, limite):
    return texto if len(texto) <= limite else texto[: limite - 3] + "..."


def linha_estoque(r):
    estoque = formatar_estoque(r["estoque"])
    if r["estoque_origem"] == "lcsc":
        return f"estoque LCSC: {estoque} (NAO e o estoque da montagem JLC)"
    return f"estoque: {estoque}"


def linha_preco(r):
    qtd = r["preco_quebra_qtd"]
    quebra = f" a partir de {qtd} un." if qtd else ""
    return f"preco unit. (menor quebra{quebra}): {formatar_preco(r['preco_unitario_usd'])}"


def formatar_item(r):
    linhas = [
        f"{r['lcsc']}  {r['mpn']}  [{r['classe']}]",
        f"    encapsulamento: {r['encapsulamento'] or 'n/d'}   {linha_estoque(r)}   {linha_preco(r)}",
    ]
    if r["fabricante"]:
        linhas.append(f"    fabricante: {r['fabricante']}")
    linhas.append(f"    {cortar(r['descricao'], LARGURA_DESCRICAO)}")
    if r["datasheet"]:
        linhas.append(f"    Datasheet: {r['datasheet']}")
    linhas += [f"    JLC:  {r['link_jlc']}", f"    LCSC: {r['link_lcsc']}"]
    return "\n".join(linhas)


def cabecalho_detalhe(termo, codigo):
    return [
        f"1 resultado para '{termo}' via detalhe do produto na LCSC (fonte lcsc-detail; "
        "API web nao documentada). O jlcsearch nao tem a peca.",
        "ATENCAO: o estoque mostrado e o da LCSC, nao o da montagem JLC. "
        "Classe Basic/Extended: desconhecido (essa API nao informa).",
        f"Confira estoque, preco e classe em {LINK_JLC.format(codigo=codigo)} antes do pedido.",
    ]


def cabecalho_jlcsearch(resultados, termo):
    cabecalho = [
        f"{len(resultados)} resultado(s) no jlcsearch para '{termo}' (fonte nao oficial).",
        "Fabricante: a API nao informa. Estoque e preco podem estar defasados: "
        "confira no site da JLC antes do pedido.",
    ]
    aviso = aviso_relevancia(resultados, termo)
    if aviso:
        cabecalho.append("AVISO: " + aviso)
    return cabecalho


def formatar_texto(resultados, termo):
    if resultados[0]["fonte"] == FONTE_DETALHE:
        cabecalho = cabecalho_detalhe(termo, resultados[0]["lcsc"])
    else:
        cabecalho = cabecalho_jlcsearch(resultados, termo)
    return "\n".join(cabecalho) + "\n\n" + "\n\n".join(formatar_item(r) for r in resultados)


def buscar_jlcsearch(termo, basic=False, limite=LIMITE_PADRAO):
    return extrair_componentes(requisitar(montar_url(termo, basic, limite)))


def buscar_detalhe_lcsc(codigo):
    resposta = requisitar(montar_url_detalhe(codigo), nome=NOME_LCSC, user_agent=UA_NAVEGADOR)
    return extrair_detalhe(resposta)


def buscar_fallback_lcsc(termo):
    """Consulta o detalhe na LCSC; falha vira ErroBusca que explica o contexto."""
    codigo = codigo_canonico(termo)
    try:
        return buscar_detalhe_lcsc(codigo)
    except ErroBusca as erro:
        raise ErroBusca(f"o jlcsearch nao tem {codigo} e o fallback na LCSC falhou: {erro}") from erro


def buscar(termo, basic=False, limite=LIMITE_PADRAO):
    """jlcsearch primeiro; so se vier vazio e o termo for um codigo, cai para o detalhe da LCSC."""
    resultados = buscar_jlcsearch(termo, basic, limite)
    if not resultados and eh_codigo_lcsc(termo):
        return buscar_fallback_lcsc(termo)
    return resultados


def criar_parser():
    p = argparse.ArgumentParser(
        prog="buscar_lcsc.py",
        description="Busca pecas LCSC/JLCPCB no jlcsearch (nao oficial, sem chave); "
                    "codigo fora do indice cai no detalhe da LCSC.",
    )
    p.add_argument("termo", help="MPN, texto ou codigo LCSC (Cxxxx)")
    p.add_argument("--basic", action="store_true", help="somente pecas Basic (sem taxa de feeder)")
    p.add_argument("--json", action="store_true", help="saida em JSON")
    p.add_argument("--limite", type=int, default=LIMITE_PADRAO, help=f"maximo de resultados (padrao {LIMITE_PADRAO})")
    return p


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = criar_parser().parse_args(argv)
    if args.limite < 1:
        print("--limite precisa ser >= 1.", file=sys.stderr)
        return 2
    if not eh_codigo_lcsc(args.termo):
        print(AVISO_BUSCA_TEXTO, file=sys.stderr)
    try:
        resultados = buscar(args.termo, args.basic, args.limite)
    except ErroBusca as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return SAIDA_ERRO_REDE
    if not resultados:
        print(mensagem_sem_resultado(args.termo), file=sys.stderr)
        return SAIDA_SEM_RESULTADO
    if args.basic and resultados[0]["fonte"] == FONTE_DETALHE:
        print("Nota: --basic nao se aplica ao fallback da LCSC (a classe e desconhecida).", file=sys.stderr)
    if args.json:
        print(json.dumps({"termo": args.termo, "resultados": resultados}, ensure_ascii=False, indent=2))
    else:
        print(formatar_texto(resultados, args.termo))
    return SAIDA_OK


if __name__ == "__main__":
    sys.exit(main())
