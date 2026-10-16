"""Bibliotecas de simbolo e footprint do KiCad 10.

- Tabelas: `sym-lib-table`/`fp-lib-table` do projeto vencem as globais pelo nome. A global fica em
  `<dir_config>/sym-lib-table`; no 10 ela costuma ter uma unica entrada `(type "Table")` que aponta
  para `<share>/template/sym-lib-table`. Sem tabela global, usa-se a do template.
- Biblioteca de simbolo e um arquivo `.kicad_sym` (varios simbolos) ou uma pasta `.kicad_symdir`
  (um arquivo por simbolo, formato das bibliotecas oficiais do 10).
- `extends` aponta para outro simbolo da mesma biblioteca; `carregar_simbolo` devolve o simbolo
  achatado (pinos e desenho do pai, propriedades do filho).
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import sexpr
from .sexpr import Simbolo, etiqueta, filho, filhos, valor

_VAR = re.compile(r"\$\{([^}]+)\}")
_UNIDADE = re.compile(r"_(\d+)_(\d+)$")
_STR = r'"([^"\\]*(?:\\.[^"\\]*)*)"'     # string com escapes, sem retrocesso exponencial
_PROP = re.compile(r'\(property "(Description|ki_keywords)" ' + _STR)
_FP_INFO = re.compile(r'\((descr|tags) ' + _STR)
_CABECA = 8192


class ErroBiblioteca(LookupError):
    pass


@dataclass
class EntradaLib:
    nome: str
    tipo: str
    uri: str            # como esta na tabela
    caminho: Path       # uri com variaveis expandidas
    descr: str = ""
    origem: str = ""    # arquivo de tabela de onde veio


@dataclass
class Pino:
    numero: str
    nome: str
    tipo: str           # tipo eletrico: passive, input, power_in...
    estilo: str         # line, inverted, clock...
    x: float
    y: float
    angulo: float
    comprimento: float
    unidade: int        # 0 = comum a todas as unidades
    corpo: int          # 1 = normal, 2 = De Morgan
    oculto: bool = False


@dataclass
class SimboloLib:
    lib: str
    nome: str
    no: list                        # S-expression achatada (sem extends)
    propriedades: dict = field(default_factory=dict)
    pinos: list = field(default_factory=list)
    unidades: int = 1
    power: bool = False
    extends: str = None             # nome do pai, se havia

    @property
    def lib_id(self):
        return f"{self.lib}:{self.nome}"


@dataclass
class Achado:
    lib_id: str
    descricao: str
    palavras: str
    caminho: Path
    nota: int           # 0 melhor


# --- tabelas ----------------------------------------------------------------

def expandir(uri, variaveis):
    """Troca ${VAR} pelo valor; variavel desconhecida fica como esta."""
    return _VAR.sub(lambda m: variaveis.get(m.group(1), m.group(0)), uri)


def _ler_entradas(caminho, variaveis, visitadas):
    caminho = Path(caminho)
    chave = str(caminho.resolve()).lower()
    if chave in visitadas or not caminho.is_file():
        return []
    visitadas.add(chave)
    raiz = sexpr.carregar_arquivo(caminho)
    saida = []
    for lib in filhos(raiz, "lib"):
        if filho(lib, "disabled") is not None:
            continue
        uri = valor(lib, "uri", "")
        tipo = valor(lib, "type", "KiCad")
        destino = Path(expandir(uri, variaveis))
        if tipo == "Table":
            saida += _ler_entradas(destino, variaveis, visitadas)
            continue
        saida.append(EntradaLib(valor(lib, "name"), tipo, uri, destino, valor(lib, "descr", ""), str(caminho)))
    return saida


def _tabela_global(amb, arquivo):
    if amb.dir_config and (amb.dir_config / arquivo).is_file():
        return amb.dir_config / arquivo
    tpl = amb.dir_template()
    return tpl / arquivo if tpl and (tpl / arquivo).is_file() else None


def tabela(amb, tipo="sym", projeto=None):
    """Entradas (projeto primeiro, depois globais), sem nomes repetidos. tipo: 'sym' ou 'fp'."""
    arquivo = f"{tipo}-lib-table"
    variaveis = dict(amb.variaveis())
    fontes = []
    if projeto:
        projeto = Path(projeto)
        variaveis["KIPRJMOD"] = str(projeto)
        fontes.append(projeto / arquivo)
    glob = _tabela_global(amb, arquivo)
    if glob:
        fontes.append(glob)
    vistas, saida = set(), []
    for f in fontes:
        for e in _ler_entradas(f, variaveis, set()):
            if e.nome not in vistas:
                vistas.add(e.nome)
                saida.append(e)
    return saida


def entrada(amb, nome_lib, tipo="sym", projeto=None):
    for e in tabela(amb, tipo, projeto):
        if e.nome == nome_lib:
            return e
    raise ErroBiblioteca(f"biblioteca '{nome_lib}' nao esta na {tipo}-lib-table")


def separar_lib_id(lib_id):
    if ":" not in lib_id:
        raise ErroBiblioteca(f"lib_id sem ':' -> '{lib_id}' (use Lib:Nome, ex. Device:R)")
    lib, nome = lib_id.split(":", 1)
    return lib, nome


# --- simbolos ---------------------------------------------------------------

def _simbolos_do_arquivo(caminho):
    raiz = sexpr.carregar_arquivo(caminho)
    return {str(s[1]): s for s in filhos(raiz, "symbol")}


def _no_bruto(entrada_lib, nome):
    """No `(symbol "nome" ...)` como esta no disco (pode ter extends)."""
    p = entrada_lib.caminho
    if p.is_dir():
        arq = p / f"{nome}.kicad_sym"
        if arq.is_file():
            nos = _simbolos_do_arquivo(arq)
            if nome in nos:
                return nos[nome]
        for arq in p.glob("*.kicad_sym"):      # nome de arquivo diferente do simbolo
            nos = _simbolos_do_arquivo(arq)
            if nome in nos:
                return nos[nome]
    elif p.is_file():
        nos = _simbolos_do_arquivo(p)
        if nome in nos:
            return nos[nome]
    else:
        raise ErroBiblioteca(f"biblioteca '{entrada_lib.nome}' aponta para caminho inexistente: {p}")
    raise ErroBiblioteca(f"simbolo '{nome}' nao existe em '{entrada_lib.nome}'")


def _renomear_unidades(no_pai, nome_pai, nome_novo):
    saida = []
    for x in no_pai:
        if etiqueta(x) == "symbol" and str(x[1]).startswith(nome_pai + "_"):
            x = [x[0], nome_novo + str(x[1])[len(nome_pai):]] + x[2:]
        saida.append(x)
    return saida


def achatar(no_filho, no_pai):
    """Simbolo derivado -> simbolo completo: desenho/pinos do pai, propriedades do filho."""
    nome_filho, nome_pai = str(no_filho[1]), str(no_pai[1])
    props_filho = {str(p[1]): p for p in filhos(no_filho, "property")}
    saida = [no_filho[0], nome_filho]
    for x in _renomear_unidades(no_pai, nome_pai, nome_filho)[2:]:
        if etiqueta(x) == "property" and str(x[1]) in props_filho:
            x = props_filho.pop(str(x[1]))
        saida.append(x)
    extras = list(props_filho.values())
    pos = max((i for i, x in enumerate(saida) if etiqueta(x) == "property"), default=1) + 1
    return saida[:pos] + extras + saida[pos:]


def _no_achatado(entrada_lib, nome, profundidade=0):
    no = _no_bruto(entrada_lib, nome)
    pai = valor(no, "extends")
    if pai is None:
        return no, None
    if profundidade > 8:
        raise ErroBiblioteca(f"cadeia de extends longa demais em '{nome}'")
    no_pai, _ = _no_achatado(entrada_lib, str(pai), profundidade + 1)
    return achatar(no, no_pai), str(pai)


def _oculto(no_pino):
    if Simbolo("hide") in no_pino:
        return True
    return valor(no_pino, "hide") == Simbolo("yes")


def _ler_pino(no_pino, unidade, corpo):
    at = filho(no_pino, "at") or ["at", 0, 0, 0]
    return Pino(
        numero=str(valor(no_pino, "number", "")),
        nome=str(valor(no_pino, "name", "")),
        tipo=str(no_pino[1]),
        estilo=str(no_pino[2]) if len(no_pino) > 2 and isinstance(no_pino[2], Simbolo) else "line",
        x=float(at[1]), y=float(at[2]), angulo=float(at[3]) if len(at) > 3 else 0.0,
        comprimento=float(valor(no_pino, "length", 0)),
        unidade=unidade, corpo=corpo, oculto=_oculto(no_pino),
    )


def pinos_do_no(no):
    saida = []
    for sub in filhos(no, "symbol"):
        m = _UNIDADE.search(str(sub[1]))
        unidade, corpo = (int(m.group(1)), int(m.group(2))) if m else (0, 1)
        saida += [_ler_pino(p, unidade, corpo) for p in filhos(sub, "pin")]
    return saida


def _contar_unidades(no):
    us = [int(m.group(1)) for s in filhos(no, "symbol") if (m := _UNIDADE.search(str(s[1])))]
    return max([u for u in us if u > 0], default=1)


def carregar_simbolo(amb, lib_id, projeto=None):
    """Resolve `Lib:Nome` e devolve um SimboloLib achatado."""
    lib, nome = separar_lib_id(lib_id)
    e = entrada(amb, lib, "sym", projeto)
    no, pai = _no_achatado(e, nome)
    props = {str(p[1]): str(p[2]) for p in filhos(no, "property")}
    return SimboloLib(lib=lib, nome=nome, no=no, propriedades=props, pinos=pinos_do_no(no),
                      unidades=_contar_unidades(no), power=filho(no, "power") is not None, extends=pai)


def no_embutido(simbolo):
    """Copia do no pronta para `lib_symbols` do esquematico: `(symbol "Lib:Nome" ...)`."""
    return [simbolo.no[0], simbolo.lib_id] + simbolo.no[2:]


# --- footprints ---------------------------------------------------------------

def resolver_footprint(amb, fp_id, projeto=None):
    lib, nome = separar_lib_id(fp_id)
    e = entrada(amb, lib, "fp", projeto)
    arq = e.caminho / f"{nome}.kicad_mod"
    if not arq.is_file():
        raise ErroBiblioteca(f"footprint '{nome}' nao existe em '{lib}' ({e.caminho})")
    return arq


def listar_footprints(amb, nome_lib, projeto=None):
    e = entrada(amb, nome_lib, "fp", projeto)
    if not e.caminho.is_dir():
        raise ErroBiblioteca(f"'{nome_lib}' nao aponta para uma pasta .pretty: {e.caminho}")
    return sorted(p.stem for p in e.caminho.glob("*.kicad_mod"))


def pads_footprint(caminho):
    """Numeros de pad (sem repeticao, na ordem do arquivo) de um .kicad_mod."""
    no = sexpr.carregar_arquivo(caminho)
    vistos = []
    for p in filhos(no, "pad"):
        n = str(p[1])
        if n and n not in vistos:
            vistos.append(n)
    return vistos


# --- busca --------------------------------------------------------------------

def _cabeca(caminho):
    with open(caminho, "rb") as f:
        return f.read(_CABECA).decode("utf-8", "replace")


def _inicia_segmento(token, nome):
    """'0603' casa como trecho inteiro em R_0603_1608Metric, mas nao em D_0201_0603Metric."""
    return re.search(r"(^|[_\-:. ])" + re.escape(token) + r"($|[_\-:. ])", nome) is not None


def _nota(termo, tokens, nome, texto):
    """0 nome exato, 1 nome comeca com o termo, 2 tokens no inicio de trechos do nome,
    3 tokens em qualquer lugar do nome, 4 so na descricao/palavras-chave; None nao casa."""
    n = nome.lower()
    if n == termo:
        return 0
    if n.startswith(termo):
        return 1
    if all(t in n for t in tokens):
        return 2 if all(_inicia_segmento(t, n) for t in tokens) else 3
    if all(t in texto for t in tokens):
        return 4
    return None


def _itens_simbolo(e):
    """(nome, caminho, cabeca) de cada simbolo da biblioteca."""
    if e.caminho.is_dir():
        for arq in sorted(e.caminho.glob("*.kicad_sym")):
            yield arq.stem, arq, None
    elif e.caminho.is_file():
        for nome, no in _simbolos_do_arquivo(e.caminho).items():
            props = {str(p[1]): str(p[2]) for p in filhos(no, "property")}
            yield nome, e.caminho, props


def _descricao_simbolo(arq, props):
    if props is None:
        achados = dict(_PROP.findall(_cabeca(arq)))
        return achados.get("Description", ""), achados.get("ki_keywords", "")
    return props.get("Description", ""), props.get("ki_keywords", "")


def buscar_simbolos(amb, termo, projeto=None, limite=20):
    termo = termo.lower().strip()
    tokens = termo.split()
    achados = []
    for e in tabela(amb, "sym", projeto):
        for nome, arq, props in _itens_simbolo(e):
            lib_id = f"{e.nome}:{nome}"
            desc, kw = _descricao_simbolo(arq, props)
            nota = _nota(termo, tokens, nome, f"{lib_id} {desc} {kw}".lower())
            if nota is not None and nota > 2 and all(_inicia_segmento(t, lib_id.lower()) for t in tokens):
                nota = 2        # ex. "rf_module esp32" casa a biblioteca e o nome
            if nota is not None:
                achados.append(Achado(lib_id, desc, kw, arq, nota))
    return _ordenar(achados, limite)


def buscar_footprints(amb, termo, projeto=None, limite=20):
    termo = termo.lower().strip()
    tokens = termo.split()
    achados = []
    for e in tabela(amb, "fp", projeto):
        if not e.caminho.is_dir():
            continue
        for arq in e.caminho.glob("*.kicad_mod"):
            info = dict(_FP_INFO.findall(_cabeca(arq)))
            lib_id = f"{e.nome}:{arq.stem}"
            texto = f"{lib_id} {info.get('descr', '')} {info.get('tags', '')}".lower()
            nota = _nota(termo, tokens, arq.stem, texto)
            if nota is not None:
                achados.append(Achado(lib_id, info.get("descr", ""), info.get("tags", ""), arq, nota))
    return _ordenar(achados, limite)


def _ordenar(achados, limite):
    achados.sort(key=lambda a: (a.nota, len(a.lib_id), a.lib_id))
    return achados[:limite] if limite else achados
