"""Spec do circuito (JSON): leitura, resolucao de pinos e validacao.

Contrato em `.claude/skills/pcb-esquematico/references/spec-json.md`. A validacao junta TODOS os
erros antes de falhar (`ErroSpec.erros`), para o agente corrigir a spec de uma vez.

Pino `REF.x`: casa primeiro por numero; se nenhum numero casar, por nome; nome que casa varios
pinos liga todos (gera aviso). A mesma resolucao serve ao gerador e a `pcbkit.netlist`.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from .. import bibliotecas

CAMPOS_TOPO = ("projeto", "titulo", "revisao", "tensao_max_v", "blocos", "componentes", "redes")
FOLHAS = ("A4", "A3", "A2", "A1")


class ErroSpec(ValueError):
    def __init__(self, erros):
        self.erros = list(erros)
        super().__init__("; ".join(self.erros))


@dataclass
class Componente:
    ref: str
    lib_id: str
    valor: str
    footprint: str
    campos: dict
    dnp: bool
    simbolo: object                 # bibliotecas.SimboloLib
    bloco: str = None

    def pinos(self):
        """Pinos eletricos do corpo normal, um por (numero, unidade)."""
        vistos, saida = set(), []
        for p in self.simbolo.pinos:
            if p.corpo in (0, 1) and (p.numero, p.unidade) not in vistos:
                vistos.add((p.numero, p.unidade))
                saida.append(p)
        return saida

    def numeros(self):
        return sorted({p.numero for p in self.pinos()}, key=_ordem_pino)


@dataclass
class Bloco:
    id: str
    titulo: str
    refs: list
    notas: str = ""


@dataclass
class Rede:
    nome: str
    pinos: list                     # [(ref, numero)] na ordem da spec
    power: object = None            # SimboloLib da biblioteca power, se o nome existir la
    pwr_flag: bool = False


@dataclass
class Circuito:
    dados: dict
    componentes: dict               # ref -> Componente, na ordem da spec
    blocos: list
    redes: dict                     # nome -> Rede, na ordem da spec
    nao_conectar: set
    rede_do_pino: dict              # (ref, numero) -> nome da rede
    avisos: list = field(default_factory=list)

    @property
    def projeto(self):
        return self.dados["projeto"]

    @property
    def folha(self):
        return self.dados.get("folha") or "A3"


def _ordem_pino(numero):
    return (0, int(numero), "") if numero.isdigit() else (1, 0, numero)


# --- leitura ----------------------------------------------------------------------

def ler_json(caminho):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except OSError as e:
        raise ErroSpec([f"nao consegui ler a spec {caminho}: {e}"]) from e
    except ValueError as e:
        raise ErroSpec([f"spec {caminho} nao e JSON valido: {e}"]) from e


def pasta_projeto(arquivo, explicita=None):
    """Pasta cujas sym-lib-table/fp-lib-table valem para `arquivo`: a explicita, ou a do proprio
    arquivo se ela tiver uma das tabelas; senao None (so as bibliotecas globais)."""
    if explicita:
        return Path(explicita)
    pasta = Path(arquivo).resolve().parent
    tem_tabela = (pasta / "sym-lib-table").is_file() or (pasta / "fp-lib-table").is_file()
    return pasta if tem_tabela else None


def carregar(caminho, amb, projeto=None):
    """Le e valida a spec. `projeto` = pasta com sym-lib-table/fp-lib-table do projeto (opcional)."""
    return validar(ler_json(caminho), amb, projeto)


# --- resolucao de pinos -------------------------------------------------------------

def separar_pino(texto):
    if not isinstance(texto, str) or "." not in texto:
        return None, None
    ref, pino = texto.split(".", 1)
    return ref, pino


def resolver_pino(comp, pino):
    """Numeros de pino que `pino` designa no componente: por numero, senao por nome."""
    numeros = comp.numeros()
    if pino in numeros:
        return [pino]
    return sorted({p.numero for p in comp.pinos() if p.nome == pino}, key=_ordem_pino)


def _resolver_lista(texto, comps, contexto, erros, avisos):
    ref, pino = separar_pino(texto)
    if ref is None:
        erros.append(f"{contexto}: '{texto}' nao esta no formato REF.pino")
        return []
    if ref not in comps:
        erros.append(f"{contexto}: '{texto}' cita o componente '{ref}', que nao existe")
        return []
    nums = resolver_pino(comps[ref], pino)
    if not nums:
        disp = ", ".join(f"{p.numero}={p.nome}" for p in comps[ref].pinos())
        erros.append(f"{contexto}: pino '{pino}' nao existe em {ref} ({comps[ref].lib_id}: {disp})")
    elif len(nums) > 1:
        avisos.append(f"{contexto}: '{texto}' casa {len(nums)} pinos pelo nome ({', '.join(nums)}); todos ligados")
    return [(ref, n) for n in nums]


# --- validacao ---------------------------------------------------------------------

def _checar_topo(d, erros):
    if not isinstance(d, dict):
        erros.append("a spec deve ser um objeto JSON")
        return False
    for c in CAMPOS_TOPO:
        if c not in d:
            erros.append(f"campo obrigatorio ausente: '{c}'")
    if d.get("folha", "A3") not in FOLHAS:
        erros.append(f"folha '{d.get('folha')}' invalida; use {', '.join(FOLHAS)}")
    tv = d.get("tensao_max_v")
    if tv is not None and (isinstance(tv, bool) or not isinstance(tv, (int, float))):
        erros.append("tensao_max_v deve ser numero (ou null enquanto nao declarado)")
    if "tensao_ac" in d and not isinstance(d["tensao_ac"], bool):
        erros.append("tensao_ac deve ser true (tensao_max_v e o pico de uma tensao alternada) ou false")
    tipos = {"blocos": list, "componentes": list, "redes": dict}
    for c, t in tipos.items():
        if c in d and not isinstance(d[c], t):
            erros.append(f"'{c}' deve ser {'lista' if t is list else 'objeto'}")
    return not erros


def _footprint(item, sim, amb, projeto, erros):
    fp = item.get("footprint") or sim.propriedades.get("Footprint", "")
    if not fp:
        erros.append(f"{item['ref']}: sem footprint (nem na spec nem no simbolo {sim.lib_id})")
        return ""
    try:
        bibliotecas.resolver_footprint(amb, fp, projeto)
    except bibliotecas.ErroBiblioteca as e:
        erros.append(f"{item['ref']}: footprint '{fp}' nao encontrado ({e})")
    return fp


def _carregar_simbolo(lib_id, amb, projeto, cache):
    if lib_id not in cache:
        cache[lib_id] = bibliotecas.carregar_simbolo(amb, lib_id, projeto)
    return cache[lib_id]


def _componente(item, amb, projeto, cache, erros):
    ref = item.get("ref") if isinstance(item, dict) else None
    if not ref or not isinstance(ref, str) or ref.startswith("#"):
        erros.append(f"componente sem 'ref' valida: {item!r}"[:160])
        return None
    if not item.get("simbolo"):
        erros.append(f"{ref}: falta 'simbolo' (Lib:Nome)")
        return None
    try:
        sim = _carregar_simbolo(item["simbolo"], amb, projeto, cache)
    except bibliotecas.ErroBiblioteca as e:
        erros.append(f"{ref}: simbolo '{item['simbolo']}' nao encontrado ({e})")
        return None
    if sim.power:
        erros.append(f"{ref}: '{sim.lib_id}' e simbolo de power; declare a rede em 'redes', nao como componente")
        return None
    campos = item.get("campos") or {}
    if not isinstance(campos, dict):
        erros.append(f"{ref}: 'campos' deve ser objeto")
        campos = {}
    return Componente(ref, sim.lib_id, str(item.get("valor") or sim.propriedades.get("Value", "")),
                      _footprint(item, sim, amb, projeto, erros), {k: str(v) for k, v in campos.items()},
                      bool(item.get("dnp", False)), sim)


def _componentes(d, amb, projeto, erros):
    comps, cache = {}, {}
    for item in d.get("componentes", []):
        c = _componente(item, amb, projeto, cache, erros)
        if c is None:
            continue
        if c.ref in comps:
            erros.append(f"ref duplicada: {c.ref}")
            continue
        comps[c.ref] = c
    return comps


def _blocos(d, comps, erros):
    blocos, dono = [], {}
    for i, b in enumerate(d.get("blocos", [])):
        if not isinstance(b, dict) or not b.get("id"):
            erros.append(f"bloco {i + 1} sem 'id'")
            continue
        refs = list(b.get("componentes") or [])
        for ref in refs:
            if ref not in comps:
                erros.append(f"bloco '{b['id']}' cita '{ref}', que nao esta em 'componentes'")
            elif ref in dono:
                erros.append(f"{ref} esta em dois blocos: '{dono[ref]}' e '{b['id']}'")
            else:
                dono[ref] = b["id"]
                comps[ref].bloco = b["id"]
        blocos.append(Bloco(b["id"], b.get("titulo") or b["id"], [r for r in refs if dono.get(r) == b["id"]],
                            str(b.get("notas") or "")))
    for ref in comps:
        if ref not in dono:
            erros.append(f"{ref} nao esta em nenhum bloco")
    return blocos


def _redes(d, comps, erros, avisos):
    redes, dono = {}, {}
    for nome, lista in d.get("redes", {}).items():
        if not isinstance(lista, list):
            erros.append(f"rede '{nome}': a lista de pinos deve ser uma lista")
            continue
        pinos, n_erros = [], len(erros)
        for texto in lista:
            for chave in _resolver_lista(texto, comps, f"rede '{nome}'", erros, avisos):
                if chave in dono and dono[chave] != nome:
                    erros.append(f"pino {chave[0]}.{chave[1]} esta em duas redes: '{dono[chave]}' e '{nome}'")
                elif chave not in pinos:
                    dono[chave] = nome
                    pinos.append(chave)
        if not lista:
            erros.append(f"rede '{nome}' esta vazia")
        elif len(pinos) < 2 and len(erros) == n_erros:
            erros.append(f"rede '{nome}' tem um pino so ({', '.join(map(str, lista))}); pino solto vai em 'nao_conectar'")
        redes[nome] = Rede(nome, pinos)
    return redes, dono


def _nao_conectar(d, comps, dono, erros, avisos):
    nc = set()
    for texto in d.get("nao_conectar") or []:
        for chave in _resolver_lista(texto, comps, "nao_conectar", erros, avisos):
            if chave in dono:
                erros.append(f"{chave[0]}.{chave[1]} esta em 'nao_conectar' e na rede '{dono[chave]}'")
            nc.add(chave)
    return nc


def _pinos_sem_rede(comps, dono, nc, erros):
    soltos = [f"{ref}.{n}" + (f" ({_nome(c, n)})" if _nome(c, n) else "")
              for ref, c in comps.items() for n in c.numeros() if (ref, n) not in dono and (ref, n) not in nc]
    if soltos:
        erros.append("pinos sem rede e fora de 'nao_conectar': " + ", ".join(soltos))


def _nome(comp, numero):
    for p in comp.pinos():
        if p.numero == numero and p.nome not in ("", "~"):
            return p.nome
    return ""


def _empilhados(comps, dono, erros):
    """Pinos na mesma posicao do simbolo (ex.: GND ocultos sob o GND visivel) sao um no so."""
    for ref, c in comps.items():
        por_pos = {}
        for p in c.pinos():
            por_pos.setdefault((p.unidade, p.x, p.y), []).append(p.numero)
        for nums in por_pos.values():
            redes = {dono.get((ref, n)) for n in nums}
            if len(redes) > 1:
                desc = ", ".join(f"{ref}.{n}={dono.get((ref, n)) or 'sem rede'}" for n in nums)
                erros.append(f"pinos empilhados no mesmo ponto do simbolo exigem a mesma rede: {desc}")


def _redes_power(redes, amb, projeto):
    """Rede cujo nome e um simbolo de power da biblioteca `power` usa esse simbolo."""
    try:
        e = bibliotecas.entrada(amb, "power", "sym", projeto)
    except bibliotecas.ErroBiblioteca:
        return
    nomes = {p.stem for p in e.caminho.glob("*.kicad_sym")} if e.caminho.is_dir() else None
    for rede in redes.values():
        if nomes is not None and rede.nome not in nomes:
            continue
        try:
            sim = bibliotecas.carregar_simbolo(amb, f"power:{rede.nome}", projeto)
        except bibliotecas.ErroBiblioteca:
            continue
        if sim.power and len(sim.pinos) == 1:
            rede.power = sim


def _listas_de_redes(d, redes, erros):
    for nome in d.get("pwr_flag") or []:
        if nome not in redes:
            erros.append(f"pwr_flag cita a rede '{nome}', que nao existe")
        else:
            redes[nome].pwr_flag = True
    for classe, cfg in (d.get("classes_de_rede") or {}).items():
        for nome in (cfg or {}).get("redes", []):
            if nome not in redes:
                erros.append(f"classe de rede '{classe}' cita a rede '{nome}', que nao existe")


def validar(d, amb, projeto=None):
    erros, avisos = [], []
    if not _checar_topo(d, erros):
        raise ErroSpec(erros)
    comps = _componentes(d, amb, projeto, erros)
    blocos = _blocos(d, comps, erros)
    redes, dono = _redes(d, comps, erros, avisos)
    nc = _nao_conectar(d, comps, dono, erros, avisos)
    _pinos_sem_rede(comps, dono, nc, erros)
    _empilhados(comps, dono, erros)
    _listas_de_redes(d, redes, erros)
    if erros:
        raise ErroSpec(erros)
    _redes_power(redes, amb, projeto)
    return Circuito(d, comps, blocos, redes, nc, dono, avisos)
