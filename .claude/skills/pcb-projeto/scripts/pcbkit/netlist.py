"""Netlist `kicadsexpr` exportada pelo kicad-cli e comparacao com a spec.

E a prova de conectividade: o ERC nao pega dois labels com o mesmo nome errado; a netlist pega.
Nomes na netlist: label local da folha raiz vem com prefixo `/` (`/MOTOR_IN1`); simbolo de power
vem sem prefixo (`GND`). Rede sem nome vira `Net-(R1-Pad1)`; pino solto, `unconnected-(...)`.
"""

from dataclasses import dataclass, field

from . import sexpr


@dataclass
class Netlist:
    redes: dict                 # nome como esta na netlist -> set((ref, pino))
    componentes: dict           # ref -> {'valor', 'footprint', 'uuid', 'folha', 'arquivo_folha', 'campos', 'propriedades'}
    pinos: dict = field(default_factory=dict)   # (ref, pino) -> {'rede', 'funcao', 'tipo'}
    classes: dict = field(default_factory=dict)  # rede -> ['HV', 'Power'] (o `(class "HV,Power")` do KiCad)


@dataclass
class Divergencias:
    redes_faltando: list = field(default_factory=list)
    pinos_faltando: dict = field(default_factory=dict)      # rede -> ['R1.2', ...]
    pinos_sobrando: dict = field(default_factory=dict)
    redes_inesperadas: dict = field(default_factory=dict)   # nome na netlist -> ['R1.2', ...]
    componentes_faltando: list = field(default_factory=list)
    componentes_sobrando: list = field(default_factory=list)
    footprints_diferentes: dict = field(default_factory=dict)   # ref -> (spec, netlist)

    @property
    def ok(self):
        return not any((self.redes_faltando, self.pinos_faltando, self.pinos_sobrando, self.redes_inesperadas,
                        self.componentes_faltando, self.componentes_sobrando, self.footprints_diferentes))


def _campos(comp):
    """(fields (field (name "MPN") "valor") ...) -> {'MPN': 'valor'}."""
    saida = {}
    for f in sexpr.filhos(sexpr.filho(comp, "fields") or [], "field"):
        texto = [x for x in f[1:] if isinstance(x, str) and not isinstance(x, sexpr.Simbolo)]
        saida[str(sexpr.valor(f, "name"))] = texto[0] if texto else ""
    return saida


def _propriedades(comp):
    return {str(sexpr.valor(p, "name")): str(sexpr.valor(p, "value", "")) for p in sexpr.filhos(comp, "property")}


def _componente(c):
    """`uuid` e o (tstamps ...) do simbolo: vira o (path "/<uuid>") do footprint na folha raiz."""
    folha = sexpr.filho(c, "sheetpath") or []
    props = _propriedades(c)
    return {"valor": str(sexpr.valor(c, "value", "")), "footprint": str(sexpr.valor(c, "footprint", "")),
            "uuid": str(sexpr.valor(c, "tstamps", "")), "folha": str(sexpr.valor(folha, "names", "/")),
            "caminho_folha": str(sexpr.valor(folha, "tstamps", "/")),
            "arquivo_folha": props.get("Sheetfile", ""), "campos": _campos(c), "propriedades": props}


def separar_classes(texto):
    """'HV,Power' -> ['HV', 'Power']: rede que casa com padroes de varias net classes tem classe composta."""
    return [c.strip() for c in str(texto or "").split(",") if c.strip()]


def ler(caminho):
    raiz = sexpr.carregar_arquivo(caminho)
    redes, pinos, classes = {}, {}, {}
    for net in sexpr.filhos(sexpr.filho(raiz, "nets") or [], "net"):
        nome = str(sexpr.valor(net, "name"))
        classes[nome] = separar_classes(sexpr.valor(net, "class", ""))
        for n in sexpr.filhos(net, "node"):
            chave = (str(sexpr.valor(n, "ref")), str(sexpr.valor(n, "pin")))
            redes.setdefault(nome, set()).add(chave)
            pinos[chave] = {"rede": nome, "funcao": str(sexpr.valor(n, "pinfunction", "")),
                            "tipo": str(sexpr.valor(n, "pintype", ""))}
    comps = {str(sexpr.valor(c, "ref")): _componente(c)
             for c in sexpr.filhos(sexpr.filho(raiz, "components") or [], "comp")}
    return Netlist(redes, comps, pinos, classes)


def nome_na_placa(netlist, nome_spec):
    """Nome com que a rede da spec aparece na netlist (e na placa): 'MOTOR_A' -> '/MOTOR_A', 'GND' -> 'GND'."""
    if nome_spec in netlist.redes:
        return nome_spec
    for nome in netlist.redes:
        if nome_sem_folha(nome) == nome_spec:
            return nome
    return None


def nome_sem_folha(nome):
    """'/MOTOR_IN1' -> 'MOTOR_IN1' (label local na folha raiz); 'GND' fica igual."""
    return nome[1:] if nome.startswith("/") and nome.count("/") == 1 else nome


def _fmt(pinos):
    return sorted(f"{r}.{p}" for r, p in pinos)


def _casar_redes(circuito, netlist, d):
    usadas = set()
    por_nome = {}
    for nome in netlist.redes:
        por_nome.setdefault(nome_sem_folha(nome), []).append(nome)
    for nome, rede in circuito.redes.items():
        candidatas = por_nome.get(nome, [])
        if not candidatas:
            d.redes_faltando.append(nome)
            continue
        real = candidatas[0]
        usadas.add(real)
        esperado, achado = set(rede.pinos), netlist.redes[real]
        if esperado - achado:
            d.pinos_faltando[nome] = _fmt(esperado - achado)
        if achado - esperado:
            d.pinos_sobrando[nome] = _fmt(achado - esperado)
    return usadas


def _redes_inesperadas(netlist, usadas, d):
    """Rede da netlist que nao casa com a spec e liga 2+ pinos (pino solto sozinho e esperado)."""
    for nome, pinos in netlist.redes.items():
        if nome not in usadas and len(pinos) > 1:
            d.redes_inesperadas[nome] = _fmt(pinos)


def _componentes(circuito, netlist, d):
    for ref, comp in circuito.componentes.items():
        achado = netlist.componentes.get(ref)
        if achado is None:
            d.componentes_faltando.append(ref)
        elif achado["footprint"] != comp.footprint:
            d.footprints_diferentes[ref] = (comp.footprint, achado["footprint"])
    d.componentes_sobrando = sorted(r for r in netlist.componentes if r not in circuito.componentes)


def comparar(circuito, netlist):
    """Cada rede da spec existe com exatamente os pinos declarados (resolvidos como no gerador)."""
    d = Divergencias()
    usadas = _casar_redes(circuito, netlist, d)
    _redes_inesperadas(netlist, usadas, d)
    _componentes(circuito, netlist, d)
    return d
