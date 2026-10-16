"""Partes do pcbkit que usam o SWIG `pcbnew` (Python embarcado do KiCad 10).

O kicad-cli 10 nao cria placa a partir do esquematico nem fala Specctra; so o `pcbnew` faz isso.
Este pacote isola essa dependencia (no KiCad 11 o SWIG sai e ela troca pela IPC API).

Este `__init__` NAO importa `pcbnew`: `posicionamento.py` e geometria pura e roda (e e testado) no
Python do sistema. `placa.py` e `specctra.py` chamam `exigir_pcbnew()` ao serem importados.
"""

import sys
from pathlib import Path


class ErroSwig(RuntimeError):
    pass


def comando_certo(script=None):
    """Linha de comando com o Python do KiCad, para a mensagem de erro."""
    from .. import ambiente
    amb = ambiente.detectar()
    script = Path(script or sys.argv[0]).resolve()
    py = amb.kicad_python or "<pasta do KiCad>/bin/python.exe"
    return f'"{py}" "{script}" ...'


def exigir_pcbnew():
    """Devolve o modulo `pcbnew` ou levanta ErroSwig dizendo como rodar no Python do KiCad."""
    try:
        import pcbnew
    except ImportError as e:
        raise ErroSwig("este script usa o pcbnew (SWIG) e so roda no Python que vem com o KiCad 10.\n"
                       f"  Rode assim: {comando_certo()}\n"
                       "  (python diagnostico.py mostra o caminho do Python do KiCad)") from e
    return pcbnew
