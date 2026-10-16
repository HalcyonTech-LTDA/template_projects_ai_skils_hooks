#!/usr/bin/env python3
"""Busca componentes nas APIs oficiais da Mouser e da DigiKey.

Uso:
    buscar_distribuidor.py mouser|digikey <termo ou MPN> [--json] [--limite N]
                           [--moeda USD] [--site US] [--idioma en] [--modo auto|keyword|partnumber]

Credenciais (variaveis de ambiente; NUNCA no repositorio):
    Mouser : MOUSER_API_KEY
    DigiKey: DIGIKEY_CLIENT_ID e DIGIKEY_CLIENT_SECRET
Sem credencial o script sai com codigo 2 e explica como obte-la e onde grava-la
(bloco "env" do .claude/settings.local.json, ignorado pelo git; ver
docs_projeto/MCPS.md, secao 6).

APIs usadas (documentacao oficial consultada em 2026-10-12):
    Mouser  - swagger publico https://api.mouser.com/api/docs/v1
              POST https://api.mouser.com/api/v1/search/keyword?apiKey=...
              POST https://api.mouser.com/api/v1/search/partnumber?apiKey=...
              Atencao: chave invalida volta HTTP 200 com "Errors" preenchido.
    DigiKey - Product Information v4, swagger oficial baixado de
              https://developer.digikey.com/node/2357/oas-download
              (pagina https://developer.digikey.com/products/product-information-v4/productsearch/keywordsearch)
              POST https://api.digikey.com/products/v4/search/keyword
              OAuth2 client credentials em https://api.digikey.com/v1/oauth2/token
              (o swagger declara o fluxo "application" = 2-legged)

STATUS DE TESTE: sem chave nesta maquina, as chamadas reais NAO foram testadas.
O que foi testado: o caminho sem chave, o parsing contra respostas de exemplo
montadas a partir dos schemas oficiais, e a resposta real da Mouser para chave
invalida (HTTP 200 + Errors). Confira o primeiro uso real com uma peca conhecida.

Precos: sempre o preco unitario da menor quebra de quantidade, na moeda que a
API devolve. Importar da Mouser/DigiKey para CNPJ tem imposto; ver
docs_projeto/referencias/componentes-e-fabricacao-pcb.md, secao 3.

Codigos de saida: 0 achou; 1 sem resultado; 2 sem credencial ou uso errado;
3 erro de rede/HTTP/resposta.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

URL_MOUSER = "https://api.mouser.com/api/v1/search/{rota}?apiKey={chave}"
URL_DIGIKEY_TOKEN = "https://api.digikey.com/v1/oauth2/token"
URL_DIGIKEY_BUSCA = "https://api.digikey.com/products/v4/search/keyword"
TIMEOUT_S = 20
LIMITE_PADRAO = 10
LIMITE_MAXIMO = 50  # teto das duas APIs por chamada

SAIDA_OK = 0
SAIDA_SEM_RESULTADO = 1
SAIDA_SEM_CHAVE = 2
SAIDA_ERRO_REDE = 3

VARIAVEIS = {
    "mouser": ["MOUSER_API_KEY"],
    "digikey": ["DIGIKEY_CLIENT_ID", "DIGIKEY_CLIENT_SECRET"],
}

COMO_OBTER = {
    "mouser": (
        "Crie a conta em mouser.com, entre em My Account > APIs (https://www.mouser.com/api-hub/) "
        "e solicite a Search API. A chave chega por e-mail (gratuita)."
    ),
    "digikey": (
        "Crie conta em https://developer.digikey.com, faca uma Organization, crie um app em "
        "Production, assine o produto 'Product Information v4' e copie o Client ID e o Client Secret."
    ),
}


class ErroDistribuidor(Exception):
    """Falha de rede, HTTP, credencial recusada ou formato de resposta."""


class SemCredencial(Exception):
    def __init__(self, distribuidor, faltando):
        super().__init__(distribuidor)
        self.distribuidor = distribuidor
        self.faltando = faltando


# ---------- credenciais ----------

def ler_credenciais(distribuidor, env):
    faltando = [v for v in VARIAVEIS[distribuidor] if not env.get(v, "").strip()]
    if faltando:
        raise SemCredencial(distribuidor, faltando)
    return {v: env[v].strip() for v in VARIAVEIS[distribuidor]}


def mensagem_sem_credencial(distribuidor, faltando):
    exemplo = ",\n".join(f'    "{v}": "valor-real-que-nunca-vai-pro-git"' for v in VARIAVEIS[distribuidor])
    return (
        f"Faltam credenciais da {distribuidor}: {', '.join(faltando)}.\n"
        f"Como obter: {COMO_OBTER[distribuidor]}\n"
        "Onde gravar: bloco \"env\" do .claude/settings.local.json (ignorado pelo git), nunca no repo "
        "nem no .mcp.json:\n"
        '{\n  "env": {\n' + exemplo + "\n  }\n}\n"
        "Reabra a sessao do Claude Code depois de editar. Politica de segredos: docs_projeto/MCPS.md, secao 6."
    )


# ---------- HTTP ----------

def enviar(pedido, timeout=TIMEOUT_S):
    """Executa o pedido e devolve (status, corpo texto); falhas viram ErroDistribuidor."""
    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as resposta:
            return getattr(resposta, "status", 200), resposta.read().decode("utf-8")
    except urllib.error.HTTPError as erro:
        raise ErroDistribuidor(mensagem_http(erro.code)) from erro
    except TimeoutError as erro:
        raise ErroDistribuidor(f"Tempo esgotado ({timeout}s) ao consultar a API.") from erro
    except urllib.error.URLError as erro:
        if isinstance(erro.reason, TimeoutError):
            raise ErroDistribuidor(f"Tempo esgotado ({timeout}s) ao consultar a API.") from erro
        raise ErroDistribuidor(f"Sem conexao com a API: {erro.reason}.") from erro


def mensagem_http(codigo):
    if codigo in (401, 403):
        return (f"HTTP {codigo}: credencial recusada. Confira a chave/secret e, na DigiKey, "
                "se o app assinou o produto 'Product Information v4'.")
    if codigo == 429:
        return "HTTP 429: limite de chamadas excedido. Espere e reduza a frequencia."
    return f"A API respondeu HTTP {codigo}."


def decodificar_json(texto):
    try:
        return json.loads(texto)
    except json.JSONDecodeError as erro:
        raise ErroDistribuidor("Resposta da API nao e JSON valido.") from erro


def postar_json(url, corpo, cabecalhos):
    dados = json.dumps(corpo).encode("utf-8")
    base = {"Content-Type": "application/json", "Accept": "application/json",
            "User-Agent": "pcb-projeto/buscar_distribuidor"}
    pedido = urllib.request.Request(url, data=dados, headers={**base, **cabecalhos}, method="POST")
    return decodificar_json(enviar(pedido)[1])


def postar_form(url, campos):
    dados = urllib.parse.urlencode(campos).encode("utf-8")
    cab = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "pcb-projeto/buscar_distribuidor"}
    return decodificar_json(enviar(urllib.request.Request(url, data=dados, headers=cab, method="POST"))[1])


# ---------- normalizacao comum ----------

def parse_numero(texto):
    """'$0.10', '0,10 EUR', '1,234.56', '1.234,56' -> float; None se nao der."""
    limpo = re.sub(r"[^0-9.,]", "", str(texto or ""))
    if not limpo:
        return None
    ponto, virgula = limpo.rfind("."), limpo.rfind(",")
    if ponto >= 0 and virgula >= 0:
        decimal = "." if ponto > virgula else ","
        milhar = "," if decimal == "." else "."
        limpo = limpo.replace(milhar, "").replace(decimal, ".")
    else:
        limpo = limpo.replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


def classificar_ciclo(texto):
    """Reduz o texto da API a Active/NRND/Obsolete; o que nao reconhece volta como veio."""
    bruto = (texto or "").strip()
    if not bruto:
        return "n/d"
    t = bruto.lower()
    if "not for new" in t or "nrnd" in t:
        return "NRND"
    if "obsolete" in t or "discontinued" in t:
        return "Obsolete"
    if t == "active":
        return "Active"
    return bruto


def registro(**campos):
    base = {"mpn": "", "fabricante": "", "descricao": "", "estoque": None, "preco_unitario": None,
            "quebra_qtd": None, "moeda": "", "ciclo_de_vida": "n/d", "ciclo_texto_api": "",
            "codigo_distribuidor": "", "datasheet": "", "link_produto": ""}
    base.update(campos)
    return base


def inteiro_ou_none(valor):
    try:
        return int(re.sub(r"[^0-9]", "", str(valor))) if re.search(r"\d", str(valor)) else None
    except ValueError:
        return None


# ---------- Mouser ----------

def corpo_mouser(termo, limite, modo):
    if modo == "partnumber":
        return "partnumber", {"SearchByPartRequest": {"mouserPartNumber": termo, "partSearchOptions": "None"}}
    return "keyword", {"SearchByKeywordRequest": {"keyword": termo, "records": limite, "startingRecord": 0,
                                                  "searchOptions": "None", "searchWithYourSignUpLanguage": ""}}


def erros_mouser(resposta):
    if not isinstance(resposta, dict):
        raise ErroDistribuidor("Resposta da Mouser em formato inesperado.")
    erros = resposta.get("Errors") or []
    if erros:
        msg = "; ".join(f"{e.get('PropertyName') or e.get('Code')}: {e.get('Message')}" for e in erros)
        raise ErroDistribuidor(f"A Mouser recusou a chamada ({msg}).")


def menor_quebra_mouser(quebras):
    validas = [q for q in (quebras or []) if parse_numero(q.get("Price")) is not None]
    if not validas:
        return None, None, ""
    q = min(validas, key=lambda x: x.get("Quantity") or 0)
    return parse_numero(q["Price"]), q.get("Quantity"), q.get("Currency") or ""


def ciclo_mouser(peca):
    if str(peca.get("IsDiscontinued", "")).lower() == "true":
        return "Discontinued"
    return peca.get("LifecycleStatus") or ""


def normalizar_mouser(peca):
    preco, qtd, moeda = menor_quebra_mouser(peca.get("PriceBreaks"))
    estoque = inteiro_ou_none(peca.get("AvailabilityInStock"))
    if estoque is None:
        estoque = inteiro_ou_none(peca.get("Availability"))
    ciclo = ciclo_mouser(peca)
    return registro(
        mpn=peca.get("ManufacturerPartNumber") or "", fabricante=peca.get("Manufacturer") or "",
        descricao=peca.get("Description") or "", estoque=estoque, preco_unitario=preco, quebra_qtd=qtd,
        moeda=moeda, ciclo_de_vida=classificar_ciclo(ciclo), ciclo_texto_api=ciclo,
        codigo_distribuidor=peca.get("MouserPartNumber") or "", datasheet=peca.get("DataSheetUrl") or "",
        link_produto=peca.get("ProductDetailUrl") or "",
    )


def extrair_mouser(resposta, limite):
    erros_mouser(resposta)
    resultados = resposta.get("SearchResults") or {}
    return [normalizar_mouser(p) for p in (resultados.get("Parts") or [])][:limite]


def chamar_mouser(termo, chave, limite, modo):
    rota, corpo = corpo_mouser(termo, limite, modo)
    return extrair_mouser(postar_json(URL_MOUSER.format(rota=rota, chave=urllib.parse.quote(chave)), corpo, {}), limite)


def modos_mouser(termo, modo):
    if modo != "auto":
        return [modo]
    return ["partnumber", "keyword"] if re.fullmatch(r"\S{3,40}", termo) else ["keyword"]


def buscar_mouser(termo, cred, limite, modo="auto", **_):
    for m in modos_mouser(termo, modo):
        achados = chamar_mouser(termo, cred["MOUSER_API_KEY"], limite, m)
        if achados:
            return achados
    return []


# ---------- DigiKey ----------

def obter_token_digikey(cred):
    resposta = postar_form(URL_DIGIKEY_TOKEN, {
        "client_id": cred["DIGIKEY_CLIENT_ID"], "client_secret": cred["DIGIKEY_CLIENT_SECRET"],
        "grant_type": "client_credentials"})
    token = resposta.get("access_token") if isinstance(resposta, dict) else None
    if not token:
        raise ErroDistribuidor("A DigiKey nao devolveu access_token. Confira Client ID e Secret.")
    return token


def cabecalhos_digikey(cred, token, site, idioma, moeda):
    return {"Authorization": f"Bearer {token}", "X-DIGIKEY-Client-Id": cred["DIGIKEY_CLIENT_ID"],
            "X-DIGIKEY-Locale-Site": site, "X-DIGIKEY-Locale-Language": idioma,
            "X-DIGIKEY-Locale-Currency": moeda}


def menor_quebra_digikey(produto):
    """Primeira variacao com StandardPricing; dentro dela, a menor BreakQuantity."""
    for variacao in produto.get("ProductVariations") or []:
        precos = [p for p in (variacao.get("StandardPricing") or []) if p.get("UnitPrice") is not None]
        if precos:
            q = min(precos, key=lambda p: p.get("BreakQuantity") or 0)
            return q["UnitPrice"], q.get("BreakQuantity"), variacao.get("DigiKeyProductNumber") or ""
    return produto.get("UnitPrice"), None, ""


def normalizar_digikey(produto, moeda):
    preco, qtd, codigo = menor_quebra_digikey(produto)
    if not codigo:
        variacoes = produto.get("ProductVariations") or [{}]
        codigo = variacoes[0].get("DigiKeyProductNumber") or ""
    status = (produto.get("ProductStatus") or {}).get("Status") or ""
    return registro(
        mpn=produto.get("ManufacturerProductNumber") or "",
        fabricante=(produto.get("Manufacturer") or {}).get("Name") or "",
        descricao=(produto.get("Description") or {}).get("ProductDescription") or "",
        estoque=produto.get("QuantityAvailable"), preco_unitario=preco, quebra_qtd=qtd, moeda=moeda,
        ciclo_de_vida=classificar_ciclo(status), ciclo_texto_api=status, codigo_distribuidor=codigo,
        datasheet=produto.get("DatasheetUrl") or "", link_produto=produto.get("ProductUrl") or "",
    )


def extrair_digikey(resposta, moeda):
    if not isinstance(resposta, dict) or not isinstance(resposta.get("Products"), list):
        raise ErroDistribuidor("Resposta da DigiKey sem a lista 'Products'.")
    return [normalizar_digikey(p, moeda) for p in resposta["Products"]]


def buscar_digikey(termo, cred, limite, moeda="USD", site="US", idioma="en", **_):
    token = obter_token_digikey(cred)
    cab = cabecalhos_digikey(cred, token, site, idioma, moeda)
    resposta = postar_json(URL_DIGIKEY_BUSCA, {"Keywords": termo, "Limit": limite, "Offset": 0}, cab)
    return extrair_digikey(resposta, moeda)


BUSCADORES = {"mouser": buscar_mouser, "digikey": buscar_digikey}


# ---------- saida ----------

def formatar_preco(r):
    if r["preco_unitario"] is None:
        return "n/d"
    qtd = f" (a partir de {r['quebra_qtd']} un.)" if r["quebra_qtd"] else ""
    return f"{r['moeda']} {r['preco_unitario']:g}{qtd}".strip()


def formatar_estoque(estoque):
    return "n/d" if estoque is None else f"{estoque:,}".replace(",", ".")


def formatar_item(r):
    return "\n".join([
        f"{r['mpn']}  ({r['fabricante'] or 'fabricante n/d'})  [{r['codigo_distribuidor'] or 'sem codigo'}]",
        f"    estoque: {formatar_estoque(r['estoque'])}   preco unit.: {formatar_preco(r)}"
        f"   ciclo: {r['ciclo_de_vida']}",
        f"    {r['descricao']}",
        f"    datasheet: {r['datasheet'] or 'n/d'}",
        f"    produto:   {r['link_produto'] or 'n/d'}",
    ])


def formatar_texto(distribuidor, termo, resultados):
    cab = f"{len(resultados)} resultado(s) na {distribuidor} para '{termo}'. Confira estoque e preco no site antes de comprar."
    return cab + "\n\n" + "\n\n".join(formatar_item(r) for r in resultados)


# ---------- CLI ----------

def criar_parser():
    p = argparse.ArgumentParser(prog="buscar_distribuidor.py",
                                description="Busca pecas na API oficial da Mouser ou da DigiKey.")
    p.add_argument("distribuidor", choices=sorted(BUSCADORES))
    p.add_argument("termo", help="MPN, codigo do distribuidor ou palavras-chave")
    p.add_argument("--json", action="store_true", help="saida em JSON")
    p.add_argument("--limite", type=int, default=LIMITE_PADRAO, help=f"1 a {LIMITE_MAXIMO} (padrao {LIMITE_PADRAO})")
    p.add_argument("--moeda", default="USD", help="DigiKey: moeda dos precos (padrao USD)")
    p.add_argument("--site", default="US", help="DigiKey: site de busca, ex. US, BR (padrao US)")
    p.add_argument("--idioma", default="en", help="DigiKey: idioma (padrao en)")
    p.add_argument("--modo", choices=["auto", "keyword", "partnumber"], default="auto",
                   help="Mouser: tipo de busca (auto tenta partnumber e cai para keyword)")
    return p


def executar(args, env):
    cred = ler_credenciais(args.distribuidor, env)
    return BUSCADORES[args.distribuidor](args.termo, cred, args.limite, moeda=args.moeda.upper(),
                                         site=args.site.upper(), idioma=args.idioma.lower(), modo=args.modo)


def main(argv=None, env=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = criar_parser().parse_args(argv)
    if not 1 <= args.limite <= LIMITE_MAXIMO:
        print(f"--limite precisa estar entre 1 e {LIMITE_MAXIMO}.", file=sys.stderr)
        return SAIDA_SEM_CHAVE
    try:
        resultados = executar(args, os.environ if env is None else env)
    except SemCredencial as erro:
        print(mensagem_sem_credencial(erro.distribuidor, erro.faltando), file=sys.stderr)
        return SAIDA_SEM_CHAVE
    except ErroDistribuidor as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return SAIDA_ERRO_REDE
    if not resultados:
        print(f"Nenhum resultado na {args.distribuidor} para '{args.termo}'.", file=sys.stderr)
        return SAIDA_SEM_RESULTADO
    if args.json:
        print(json.dumps({"distribuidor": args.distribuidor, "termo": args.termo, "resultados": resultados},
                         ensure_ascii=False, indent=2))
    else:
        print(formatar_texto(args.distribuidor, args.termo, resultados))
    return SAIDA_OK


if __name__ == "__main__":
    sys.exit(main())
