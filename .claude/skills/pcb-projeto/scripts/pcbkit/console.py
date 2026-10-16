"""Saida dos scripts: UTF-8 no console do Windows e JSON para maquina."""

import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path


def configurar():
    """O console do Windows usa cp1252 e quebra com 'Ω' ou 'µ' das bibliotecas."""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _padrao(obj):
    if isinstance(obj, Path):
        return str(obj)
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError(f"nao serializavel: {type(obj).__name__}")


def imprimir_json(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=_padrao))


def erro(mensagem, codigo=1):
    print(f"ERRO: {mensagem}", file=sys.stderr)
    return codigo
