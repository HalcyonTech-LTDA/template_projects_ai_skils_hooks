"""Componentes da BOM lidos da netlist do esquematico e a BOM completa (CSV).

Fonte: `netlist.ler()` da netlist `kicadsexpr` exportada pelo kicad-cli. Os campos ficam em
`fields`; atributos do simbolo aparecem como `(property (name "dnp"))`, `exclude_from_bom` e
`exclude_from_pos_files` por PRESENCA (conferido no 10.0.0). Simbolos de power nao vem na netlist.

Campos lidos (contrato do handoff): `LCSC`, `MPN`, `Fabricante`, `Mouser`, `DigiKey`, `Datasheet`.
Fallbacks de simbolos importados (easyeda2kicad, Fabrication Toolkit): `LCSC` <- `LCSC Part`,
`LCSC Part #`, `JLCPCB Part #`; `Fabricante` <- `Manufacturer`. O campo da familia vence.

`Sem_LCSC` (decisao da fatia 4): texto com o motivo de um componente montado nao ter codigo LCSC
(ex.: "soldado a mao", "fornecido pelo cliente"). Ele fica na BOM completa, sai da BOM/CPL da JLC
e o portao aceita a falta do `LCSC`. Vence o `LCSC`: peca com os dois campos nao e montada pela JLC.

`exclude_from_pos_files` (atributo "excluir dos arquivos de posicao") tira a peca so do CPL da JLC.
"""

import csv
import re
from dataclasses import dataclass
from pathlib import Path

CAMPOS_LCSC = ("LCSC", "LCSC Part", "LCSC Part #", "JLCPCB Part #")
CAMPOS_FABRICANTE = ("Fabricante", "Manufacturer")
CAMPO_SEM_LCSC = "Sem_LCSC"
CABECALHO_COMPLETA = ["Item", "Valor", "Referencias", "Quantidade", "Footprint", "MPN", "Fabricante", "LCSC",
                      "Mouser", "DigiKey", "Datasheet"]
_VAZIOS = {"", "~"}


@dataclass
class Componente:
    ref: str
    valor: str
    footprint: str
    mpn: str = ""
    fabricante: str = ""
    lcsc: str = ""
    mouser: str = ""
    digikey: str = ""
    datasheet: str = ""
    sem_lcsc: str = ""
    dnp: bool = False
    fora_da_bom: bool = False
    fora_do_pos: bool = False

    @property
    def montado(self):
        return not self.dnp and not self.fora_da_bom

    @property
    def montado_pela_jlc(self):
        """Entra na BOM da JLC: montada, com LCSC, sem `Sem_LCSC` (que vence o LCSC) e com posicao.

        Peca com `exclude_from_pos_files` nao tem linha no CPL; na BOM da JLC ela viraria peca
        a montar sem coordenada, que o upload acusa. Por isso sai das duas e fica so na BOM completa.
        """
        return self.montado and bool(self.lcsc) and not self.sem_lcsc and not self.fora_do_pos

    @property
    def no_cpl(self):
        """Entra no CPL da JLC: exatamente as pecas da BOM da JLC."""
        return self.montado_pela_jlc


def campo(campos, nomes):
    """Primeiro campo nao vazio na ordem de `nomes` ('~' do KiCad conta como vazio)."""
    for nome in nomes:
        valor = str(campos.get(nome, "")).strip()
        if valor not in _VAZIOS:
            return valor
    return ""


def componente(ref, dados):
    """`dados` = netlist.componentes[ref]."""
    campos, props = dados.get("campos", {}), dados.get("propriedades", {})
    return Componente(ref=ref, valor=dados.get("valor", ""), footprint=dados.get("footprint", ""),
                      mpn=campo(campos, ("MPN",)), fabricante=campo(campos, CAMPOS_FABRICANTE),
                      lcsc=campo(campos, CAMPOS_LCSC), mouser=campo(campos, ("Mouser",)),
                      digikey=campo(campos, ("DigiKey",)), datasheet=campo(campos, ("Datasheet",)),
                      sem_lcsc=campo(campos, (CAMPO_SEM_LCSC,)), dnp="dnp" in props,
                      fora_da_bom="exclude_from_bom" in props, fora_do_pos="exclude_from_pos_files" in props)


def ordem_ref(ref):
    """'C10' depois de 'C9': (prefixo, numero, resto)."""
    m = re.match(r"^([A-Za-z_#]*)(\d*)(.*)$", ref)
    return (m.group(1), int(m.group(2)) if m.group(2) else -1, m.group(3))


def componentes(netlist):
    return sorted((componente(ref, d) for ref, d in netlist.componentes.items()), key=lambda c: ordem_ref(c.ref))


def montados(comps):
    return [c for c in comps if c.montado]


def agrupar(comps, chave):
    """Grupos (listas de Componente) na ordem da primeira referencia de cada grupo."""
    grupos = {}
    for c in sorted(comps, key=lambda c: ordem_ref(c.ref)):
        grupos.setdefault(chave(c), []).append(c)
    return list(grupos.values())


def refs(grupo):
    return ",".join(c.ref for c in grupo)


def _chave_completa(c):
    return (c.valor, c.footprint, c.mpn, c.fabricante, c.lcsc, c.mouser, c.digikey)


def linhas_completa(comps):
    linhas = []
    for i, g in enumerate(agrupar(montados(comps), _chave_completa), start=1):
        c = g[0]
        linhas.append([i, c.valor, refs(g), len(g), c.footprint, c.mpn, c.fabricante, c.lcsc, c.mouser, c.digikey,
                       next((x.datasheet for x in g if x.datasheet), "")])
    return linhas


def escrever_csv(caminho, cabecalho, linhas):
    with Path(caminho).open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)
    return Path(caminho)


def escrever_completa(caminho, comps):
    return escrever_csv(caminho, CABECALHO_COMPLETA, linhas_completa(comps))


def pendencias(comps):
    """Componentes montados sem MPN, ou sem LCSC e sem motivo em `Sem_LCSC`. Lista de textos."""
    saida = []
    for c in montados(comps):
        falta = [nome for nome, ok in (("MPN", c.mpn), ("LCSC", c.lcsc or c.sem_lcsc)) if not ok]
        if falta:
            saida.append(f"{c.ref} ({c.valor}): sem {' e '.join(falta)}")
    return saida
