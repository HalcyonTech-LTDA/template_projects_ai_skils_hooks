"""Gerador de esquematico a partir da spec JSON (estilo label por pino).

- spec           carrega e valida a spec; resolve `REF.pino`
- geometria      biblioteca -> folha (rotacao, espelho, Y invertido), grade de 1,27 mm
- caixas         caixas delimitadoras e tamanho estimado de texto
- posicionamento blocos como regioes da folha, itens em prateleiras, fios/labels/power por pino
- escritor       serializa em .kicad_sch (uuids deterministicos)
"""

import datetime
import re
from pathlib import Path

from .. import GERADOR, bibliotecas
from . import escritor, posicionamento, spec

_GERADOR_NO_CABECALHO = re.compile(r'\(generator\s+"([^"]*)"')
_CABECALHO = 4096


class ErroSobrescrita(Exception):
    """O arquivo de saida existe e nao foi escrito por este gerador."""


def _cabecalho(caminho):
    with Path(caminho).open(encoding="utf-8", errors="replace") as f:
        return f.read(_CABECALHO)


def gerador_do_arquivo(caminho):
    """Valor de `(generator ...)` do cabecalho de um .kicad_sch, ou None se nao tem.
    O KiCad 10 regrava `"eeschema"` ao salvar na GUI (conferido com `kicad-cli sch upgrade --force`)."""
    achado = _GERADOR_NO_CABECALHO.search(_cabecalho(caminho))
    return achado.group(1) if achado else None


def conferir_sobrescrita(saida):
    """Recusa regravar um .kicad_sch que a GUI (ou outro programa) salvou: o gerador apagaria a edicao.
    Arquivo ausente ou vazio pode ser escrito."""
    saida = Path(saida)
    if not saida.is_file() or not _cabecalho(saida).strip():
        return
    gerador = gerador_do_arquivo(saida)
    if gerador == GERADOR:
        return
    quem = f'`generator` "{gerador}"' if gerador else "sem `generator` no cabecalho"
    raise ErroSobrescrita(
        f"{saida} nao foi escrito pelo gerador ({quem}; o KiCad grava \"eeschema\" ao salvar na GUI). "
        f"Regerar apaga a edicao. Se o esquematico virou a fonte de verdade (modo manual), nao regenere: "
        f"edite pela GUI ou por patch no S-expression e rode ERC e netlist (ver pcb-projeto/references/"
        f"estrutura-de-pastas.md, secao \"Modo spec e modo manual\"). Para descartar a edicao de proposito, "
        f"use --sobrescrever.")


def gerar(circuito, amb, saida, projeto=None, data=None, sobrescrever=False):
    """Escreve o .kicad_sch e devolve (Desenho, avisos). Levanta ErroSobrescrita se `saida` e de outra
    origem (arquivo salvo na GUI) e `sobrescrever` e falso; nada e escrito nesse caso."""
    saida = Path(saida)
    if not sobrescrever:
        conferir_sobrescrita(saida)
    flag = bibliotecas.carregar_simbolo(amb, "power:PWR_FLAG", projeto)
    desenho = posicionamento.montar(circuito.folha, posicionamento.blocos_com_itens(circuito, flag))
    data = data or datetime.date.today().isoformat()
    arvore = escritor.esquematico(circuito, desenho, saida.stem, data, origem=f"spec/{circuito.projeto}.json")
    saida.parent.mkdir(parents=True, exist_ok=True)
    escritor.escrever(saida, arvore)
    return desenho, circuito.avisos + desenho.avisos


__all__ = ["gerar", "ErroSobrescrita", "spec", "escritor", "posicionamento"]
