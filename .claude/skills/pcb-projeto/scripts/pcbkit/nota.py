"""Nota de portao (gate) em Markdown com frontmatter YAML: le e diz se esta aprovada.

Aprovada = `status: aprovado`, `revisores` nao vazio e nenhum item de tarefa em aberto no corpo. Item
que nao se aplica e marcado `- [x] N/A — motivo`; `N/A` sem motivo conta como pendente. Item em
aberto e qualquer caixa que nao seja `[x]`/`[X]`, em lista com `-`, `*`, `+` ou numerada (`1.`,
`1)`), inclusive dentro de citacao/callout (`> - [ ]`). Bloco de codigo cercado (``` ou ~~~) nao
conta; a cerca so fecha com o mesmo caractere e comprimento >= o da abertura (CommonMark), e cerca
sem fechamento bloqueia (esconderia o resto da nota).

O frontmatter e lido a mao (stdlib): um campo escalar por linha, listas em linha (`[A, B]`) ou em
bloco (`- A`), comentario `# ...` cortado, `null`/`~`/`""`/`[]` = vazio. Campo repetido bloqueia (o
YAML guardaria so o ultimo). E o formato das notas do vault; YAML mais rico nao e suportado.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

_PREFIXO = r"^\s*(?:>\s*)*(?:[-*+]|\d{1,9}[.)])\s+"
_ITEM_ABERTO = re.compile(_PREFIXO + r"\[[^xX\]]\]\s*(.*)$")
_ITEM_NA = re.compile(_PREFIXO + r"\[x\]\s+N/?A\b(.*)$", re.IGNORECASE)
_CERCA = re.compile(r"^\s*(?:>\s*)*(`{3,}|~{3,})(.*)$")
_SEPARADORES_NA = " \t-—–:;,."
_NULOS = {"", "null", "Null", "NULL", "~"}


@dataclass
class Nota:
    caminho: Path
    frontmatter: dict
    corpo: str
    repetidos: list = field(default_factory=list)      # campos que aparecem mais de uma vez


def _sem_comentario(bruto):
    """Corta o comentario YAML (`#` no inicio ou depois de espaco), fora de aspas."""
    aspas, anterior = None, ""
    for i, c in enumerate(bruto):
        if aspas:
            aspas = None if c == aspas else aspas
        elif c in "'\"" and anterior in ("", "[", ","):
            aspas = c
        elif c == "#" and (i == 0 or bruto[i - 1] in " \t"):
            return bruto[:i]
        if not c.isspace():
            anterior = c
    return bruto


def _escalar(bruto):
    bruto = bruto.strip()
    if len(bruto) >= 2 and bruto[0] == bruto[-1] and bruto[0] in "'\"":
        return bruto[1:-1]
    return "" if bruto in _NULOS else bruto


def _valor(bruto):
    bruto = _sem_comentario(bruto).strip()
    if bruto.startswith("[") and bruto.endswith("]"):
        return [_escalar(x) for x in bruto[1:-1].split(",") if _escalar(x)]
    return _escalar(bruto)


def _separar(texto):
    """(linhas do frontmatter, corpo). Sem frontmatter: ([], texto)."""
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return [], texto
    for i, linha in enumerate(linhas[1:], start=1):
        if linha.strip() == "---":
            return linhas[1:i], "\n".join(linhas[i + 1:])
    return [], texto


def _item_de_lista(linha, dados, chave):
    """Item `- x` da lista em bloco da ultima chave (indentado, ou na coluna 0 se a chave ficou vazia)."""
    item = re.match(r"^(\s*)-(?:\s+(.*))?$", linha)
    if not item or chave is None:
        return False
    atual = dados.get(chave)
    if not (item.group(1) or isinstance(atual, list) or atual == ""):
        return False
    valor = _escalar(_sem_comentario(item.group(2) or ""))
    dados[chave] = (atual if isinstance(atual, list) else []) + ([valor] if valor else [])
    return True


def ler_frontmatter(linhas, repetidos=None):
    dados, chave = {}, None
    for linha in linhas:
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        if _item_de_lista(linha, dados, chave):
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:(?:\s+(.*)|\s*)$", linha)
        if m:
            chave = m.group(1)
            if chave in dados and repetidos is not None:
                repetidos.append(chave)
            dados[chave] = _valor(m.group(2) or "")
    return dados


def carregar_texto(texto, caminho=None):
    linhas, corpo = _separar(texto.lstrip("﻿"))
    repetidos = []
    fm = ler_frontmatter(linhas, repetidos)
    return Nota(Path(caminho) if caminho else None, fm, corpo, sorted(set(repetidos)))


def ler(caminho):
    return carregar_texto(Path(caminho).read_text(encoding="utf-8-sig"), caminho)


def _fecha(linha, cerca):
    m = _CERCA.match(linha)
    return bool(m) and m.group(1)[0] == cerca[0] and len(m.group(1)) >= len(cerca) and not m.group(2).strip()


def _linhas_fora_de_codigo(corpo):
    """Linhas fora de bloco de codigo cercado. Devolve (linhas, cerca sem fechamento ou None)."""
    fora, cerca = [], None
    for linha in corpo.splitlines():
        if cerca:
            cerca = None if _fecha(linha, cerca) else cerca
            continue
        m = _CERCA.match(linha)
        if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
            cerca = m.group(1)
            continue
        fora.append(linha)
    return fora, cerca


def cerca_aberta(corpo):
    return _linhas_fora_de_codigo(corpo)[1]


def itens_abertos(corpo):
    return [m.group(1).strip() for m in map(_ITEM_ABERTO.match, _linhas_fora_de_codigo(corpo)[0]) if m]


def na_sem_motivo(corpo):
    return [linha.strip() for linha in _linhas_fora_de_codigo(corpo)[0]
            if (m := _ITEM_NA.match(linha)) and not m.group(1).strip(_SEPARADORES_NA)]


def revisores(nota):
    valor = nota.frontmatter.get("revisores")
    if isinstance(valor, list):
        return [r for r in valor if r]
    return [valor] if valor else []


def pendencias(nota):
    """Motivos pelos quais a nota NAO esta aprovada (lista vazia = aprovada)."""
    motivos = []
    if nota.repetidos:
        motivos.append(f"campo(s) repetido(s) no frontmatter: {', '.join(nota.repetidos)} (deixe um so)")
    status = str(nota.frontmatter.get("status", "")).strip()
    if status.lower() != "aprovado":
        motivos.append(f"status '{status or 'vazio'}' (precisa ser 'aprovado', marcado pela pessoa que revisou)")
    if not revisores(nota):
        motivos.append("'revisores' vazio (quem revisou precisa se registrar)")
    cerca = cerca_aberta(nota.corpo)
    if cerca:
        motivos.append(f"bloco de codigo aberto com {cerca} sem fechamento: feche o bloco "
                       "(ele esconde os itens que vem depois)")
    abertos = itens_abertos(nota.corpo)
    if abertos:
        motivos.append(f"{len(abertos)} item(ns) '- [ ]' em aberto: " + "; ".join(_curto(a) for a in abertos[:5])
                       + (" ..." if len(abertos) > 5 else ""))
    sem_motivo = na_sem_motivo(nota.corpo)
    if sem_motivo:
        motivos.append(f"{len(sem_motivo)} item(ns) 'N/A' sem motivo (use '- [x] N/A — motivo')")
    return motivos


def _curto(texto, n=60):
    return texto if len(texto) <= n else texto[:n - 3] + "..."
