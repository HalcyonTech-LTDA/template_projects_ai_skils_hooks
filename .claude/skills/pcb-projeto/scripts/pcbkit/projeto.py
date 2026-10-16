"""Arquivos de um projeto de placa em `hardware/<placa>/` (layout de `novo_projeto.py`).

A placa e o stem do unico `.kicad_pro` da pasta; os demais arquivos tem o mesmo nome.
"""

import json
from dataclasses import dataclass
from pathlib import Path


class ErroProjeto(ValueError):
    pass


@dataclass
class Projeto:
    dir: Path
    placa: str

    def _arq(self, ext):
        return self.dir / f"{self.placa}{ext}"

    @property
    def pro(self):
        return self._arq(".kicad_pro")

    @property
    def sch(self):
        return self._arq(".kicad_sch")

    @property
    def pcb(self):
        return self._arq(".kicad_pcb")

    @property
    def dru(self):
        return self._arq(".kicad_dru")

    @property
    def spec(self):
        return self.dir / "spec" / f"{self.placa}.json"

    def faltando(self):
        """Arquivos obrigatorios que nao existem (a spec e tratada a parte, pelo portao)."""
        return [p.name for p in (self.pro, self.sch, self.pcb, self.dru) if not p.is_file()]


def localizar(pasta):
    pasta = Path(pasta)
    if not pasta.is_dir():
        raise ErroProjeto(f"pasta do projeto nao encontrada: {pasta}")
    pros = sorted(pasta.glob("*.kicad_pro"))
    if len(pros) != 1:
        raise ErroProjeto(f"esperado exatamente um .kicad_pro em {pasta}; achados {len(pros)}")
    return Projeto(pasta.resolve(), pros[0].stem)


def ler_spec(proj):
    """Dict da spec do projeto, ou None se o arquivo nao existe. JSON invalido levanta ErroProjeto."""
    if not proj.spec.is_file():
        return None
    try:
        return json.loads(proj.spec.read_text(encoding="utf-8"))
    except ValueError as e:
        raise ErroProjeto(f"spec invalida ({proj.spec.name}): {e}") from e
