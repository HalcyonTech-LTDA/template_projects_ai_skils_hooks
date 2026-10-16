"""Parser e serializador de S-expression no dialeto do KiCad.

Representacao em Python:
- lista            -> list
- string com aspas -> str
- atomo sem aspas  -> Simbolo (subclasse de str), ex.: kicad_sch, yes, passive
- numero           -> int ou float

`carregar(texto)` e `despejar(no)` fazem round-trip semantico: o texto pode mudar de
formatacao, mas `carregar(despejar(carregar(t))) == carregar(t)`.
"""

import re

__all__ = [
    "Simbolo", "ErroSexpr", "carregar", "carregar_todos", "carregar_arquivo", "despejar", "salvar_arquivo",
    "etiqueta", "filho", "filhos", "valor", "valores",
]


class Simbolo(str):
    """Atomo sem aspas (palavra-chave do formato)."""

    def __repr__(self):
        return f"Simbolo({str.__repr__(self)})"


class ErroSexpr(ValueError):
    pass


_NUMERO = re.compile(r"-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?$")
_INTEIRO = re.compile(r"-?\d+$")
_DELIMITADORES = set("()\"") | set(" \t\r\n")
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"'}


# --- leitura ---------------------------------------------------------------

def _ler_string(texto, i):
    """Le uma string a partir da aspa em texto[i]. Devolve (valor, proximo indice)."""
    partes = []
    i += 1
    inicio = i
    n = len(texto)
    while i < n:
        c = texto[i]
        if c == '"':
            partes.append(texto[inicio:i])
            return "".join(partes), i + 1
        if c == "\\" and i + 1 < n:
            partes.append(texto[inicio:i])
            partes.append(_ESCAPES.get(texto[i + 1], texto[i + 1]))
            i += 2
            inicio = i
            continue
        i += 1
    raise ErroSexpr("string sem aspa de fechamento")


def _converter_atomo(bruto):
    if _NUMERO.match(bruto):
        return int(bruto) if _INTEIRO.match(bruto) else float(bruto)
    return Simbolo(bruto)


def _ler_atomo(texto, i):
    j = i
    n = len(texto)
    while j < n and texto[j] not in _DELIMITADORES:
        j += 1
    return _converter_atomo(texto[i:j]), j


def _pular_comentario(texto, i):
    fim = texto.find("\n", i)
    return len(texto) if fim < 0 else fim + 1


def carregar_todos(texto, comentarios=False):
    """Todas as expressoes do nivel de cima, ex. as regras de um .kicad_dru.
    `comentarios=True` ignora linhas iniciadas por '#' fora de string (formato .kicad_dru)."""
    pilha = [[]]
    i = 0
    n = len(texto)
    while i < n:
        c = texto[i]
        if c in " \t\r\n":
            i += 1
        elif c == "#" and comentarios:
            i = _pular_comentario(texto, i)
        elif c == "(":
            pilha.append([])
            i += 1
        elif c == ")":
            if len(pilha) == 1:
                raise ErroSexpr(f"')' sem '(' na posicao {i}")
            fechada = pilha.pop()
            pilha[-1].append(fechada)
            i += 1
        elif c == '"':
            s, i = _ler_string(texto, i)
            pilha[-1].append(s)
        else:
            atomo, i = _ler_atomo(texto, i)
            pilha[-1].append(atomo)
    if len(pilha) > 1:
        raise ErroSexpr("'(' sem ')' no fim do texto")
    return pilha[0]


def carregar(texto):
    """Converte o texto numa unica S-expression (a raiz de um arquivo do KiCad)."""
    nos = carregar_todos(texto)
    if len(nos) != 1 or not isinstance(nos[0], list):
        raise ErroSexpr("texto vazio" if not nos else f"esperava 1 expressao na raiz, achei {len(nos)}")
    return nos[0]


def carregar_arquivo(caminho):
    with open(caminho, encoding="utf-8") as f:
        return carregar(f.read())


# --- escrita ---------------------------------------------------------------

def _formatar_numero(v):
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return str(v)
    texto = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if texto in ("-0", "") else texto


def _formatar_string(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{s}"'


def _formatar_atomo(v):
    if isinstance(v, Simbolo):
        return str(v)
    if isinstance(v, str):
        return _formatar_string(v)
    if isinstance(v, (int, float)):
        return _formatar_numero(v)
    raise ErroSexpr(f"tipo nao serializavel: {type(v).__name__}")


# Listas cujos filhos ficam todos na mesma linha (como o KiCad grava).
_EM_LINHA = {"pts"}


def _eh_atomo(v):
    return not isinstance(v, list)


def _despejar_linha(no):
    return "(" + " ".join(
        _despejar_linha(x) if isinstance(x, list) else _formatar_atomo(x) for x in no
    ) + ")"


def _despejar(no, nivel, saida):
    recuo = "\t" * nivel
    if all(_eh_atomo(x) for x in no) or etiqueta(no) in _EM_LINHA:
        saida.append(recuo + _despejar_linha(no))
        return
    cabeca = []
    resto = list(no)
    while resto and _eh_atomo(resto[0]):
        cabeca.append(_formatar_atomo(resto.pop(0)))
    saida.append(recuo + "(" + " ".join(cabeca))
    for x in resto:
        if isinstance(x, list):
            _despejar(x, nivel + 1, saida)
        else:
            saida.append("\t" * (nivel + 1) + _formatar_atomo(x))
    saida.append(recuo + ")")


def despejar(no):
    """Serializa com recuo por tabulacao, no estilo dos arquivos do KiCad."""
    if not isinstance(no, list):
        return _formatar_atomo(no)
    saida = []
    _despejar(no, 0, saida)
    return "\n".join(saida) + "\n"


def salvar_arquivo(caminho, no):
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(despejar(no))


# --- consulta --------------------------------------------------------------

def etiqueta(no):
    """Primeiro elemento de uma lista, se for Simbolo; senao None."""
    if isinstance(no, list) and no and isinstance(no[0], Simbolo):
        return str(no[0])
    return None


def filhos(no, nome):
    """Todas as sublistas diretas cuja etiqueta e `nome`."""
    return [x for x in no if isinstance(x, list) and etiqueta(x) == nome]


def filho(no, nome):
    """Primeira sublista direta com a etiqueta `nome`, ou None."""
    for x in no:
        if isinstance(x, list) and etiqueta(x) == nome:
            return x
    return None


def valores(no, nome):
    """Argumentos (sem a etiqueta) do primeiro filho `nome`, ou lista vazia."""
    f = filho(no, nome)
    return f[1:] if f else []


def valor(no, nome, padrao=None):
    """Primeiro argumento do filho `nome`, ex.: valor(sym, 'lib_id') -> 'Device:R'."""
    v = valores(no, nome)
    return v[0] if v else padrao
