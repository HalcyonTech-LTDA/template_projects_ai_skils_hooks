"""Net classes e regras do projeto KiCad (`.kicad_pro` JSON e `.kicad_dru`) a partir da spec.

O `.kicad_pro` guarda as net classes em `net_settings.classes` e a atribuicao em
`net_settings.netclass_patterns` (`{"netclass": "Power", "pattern": "/+12V_SYS"}`). O padrao
casa o nome da rede **como a placa o ve**: label local vem com `/` (`/MOTOR_A`), simbolo de power
sem (`+12V`). Por isso a atribuicao recebe o nome ja traduzido pela netlist.

O kicad-cli carrega o `.kicad_pro` e o `.kicad_dru` com o mesmo nome da placa (ver Oraculo).
"""

import copy
import json
import re
import shutil
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[2] / "assets" / "kicad"
MODELO_PRO = ASSETS / "projeto-modelo.kicad_pro"
MODELOS_DRU = {2: ASSETS / "jlc-2camadas.kicad_dru", 4: ASSETS / "jlc-4camadas.kicad_dru"}
CLASSE_PADRAO = "Default"


def caminhos(pcb):
    pcb = Path(pcb)
    return pcb.with_suffix(".kicad_pro"), pcb.with_suffix(".kicad_dru")


def garantir_arquivos(pcb, camadas=2):
    """Copia o modelo de `.kicad_pro`/`.kicad_dru` que faltar ao lado da placa. Devolve os avisos."""
    pro, dru = caminhos(pcb)
    avisos = []
    if not pro.is_file():
        dados = json.loads(MODELO_PRO.read_text(encoding="utf-8"))
        dados["meta"]["filename"] = pro.name
        gravar_pro(pro, dados)
        avisos.append(f"{pro.name} nao existia: criado a partir de assets/kicad/{MODELO_PRO.name} "
                      "(crie o projeto com novo_projeto.py para ter tabelas de biblioteca e docs)")
    if not dru.is_file():
        modelo = MODELOS_DRU.get(camadas, MODELOS_DRU[4 if camadas > 2 else 2])
        shutil.copy(modelo, dru)
        avisos.append(f"{dru.name} nao existia: copiado de assets/kicad/{modelo.name}")
    return avisos


def ler_pro(pro):
    return json.loads(Path(pro).read_text(encoding="utf-8"))


def gravar_pro(pro, dados):
    Path(pro).write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _classe(net_settings, nome):
    for c in net_settings.setdefault("classes", []):
        if c.get("name") == nome:
            return c
    base = next((c for c in net_settings["classes"] if c.get("name") == CLASSE_PADRAO), None)
    nova = copy.deepcopy(base) if base else {"track_width": 0.25, "clearance": 0.2, "via_diameter": 0.6,
                                             "via_drill": 0.3}
    nova.update({"name": nome, "priority": len(net_settings["classes"])})
    net_settings["classes"].append(nova)
    return nova


def aplicar_classes(dados, classes_spec, nome_na_placa):
    """Escreve no dict do `.kicad_pro` as classes da spec (largura/clearance) e um padrao por rede.

    `classes_spec` = `classes_de_rede` da spec; `nome_na_placa(rede_spec)` -> nome na placa ou None.
    Padroes antigos para as mesmas redes sao trocados; os demais ficam. Devolve (atribuicoes, avisos)."""
    ns = dados.setdefault("net_settings", {})
    atribuicoes, avisos = {}, []
    for nome, cfg in (classes_spec or {}).items():
        cfg = cfg or {}
        classe = _classe(ns, nome)
        if cfg.get("largura_mm") is not None:
            classe["track_width"] = float(cfg["largura_mm"])
        if cfg.get("clearance_mm") is not None:
            classe["clearance"] = float(cfg["clearance_mm"])
        for rede in cfg.get("redes", []):
            real = nome_na_placa(rede)
            if real is None:
                avisos.append(f"classe '{nome}': rede '{rede}' nao existe na netlist; ignorada")
            else:
                atribuicoes[real] = nome
    padroes = [p for p in (ns.get("netclass_patterns") or []) if p.get("pattern") not in atribuicoes]
    padroes += [{"netclass": c, "pattern": r} for r, c in atribuicoes.items()]
    ns["netclass_patterns"] = padroes
    return atribuicoes, avisos


def _regex_curinga(padrao):
    """Padrao do KiCad (`*` e `?`) para regex; o resto e literal."""
    return re.compile("^" + "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in padrao) + "$")


def casa_padrao(padrao, rede):
    """Como o KiCad 10.0.0 casa `netclass_patterns` (medido pela classe na netlist): curinga (`*`, `?`)
    ou expressao regular (`/MOTOR_(A|B)`), ancorados no nome inteiro e sensiveis a maiusculas."""
    if _regex_curinga(padrao).match(rede):
        return True
    try:
        return re.fullmatch(padrao, rede) is not None
    except re.error:
        return False


def classes_da_rede(dados, rede):
    """Todas as net classes cujos padroes casam com a rede, na ordem de prioridade do KiCad (a de menor
    `priority` primeiro). Lista vazia = Default. Duas ou mais = classe composta (`HV,Power`)."""
    ns = (dados or {}).get("net_settings", {})
    prioridade = {c.get("name"): c.get("priority", 0) for c in ns.get("classes") or []}
    achadas = {p.get("netclass") for p in ns.get("netclass_patterns") or []
               if p.get("netclass") and casa_padrao(p.get("pattern", ""), rede)}
    return sorted(achadas, key=lambda c: (prioridade.get(c, float("inf")), c))


def classe_da_rede(dados, rede):
    """Net class como o KiCad a mostra: `Default`, `Power` ou a composta `HV,Power`."""
    return ",".join(classes_da_rede(dados, rede)) or CLASSE_PADRAO


def tem_classe(classe, nomes):
    """A net class (simples ou composta `HV,Power`) contem alguma das classes em `nomes`?"""
    return any(c.strip() in nomes for c in str(classe).split(","))


def classes_declaradas(dados):
    return [c.get("name") for c in dados.get("net_settings", {}).get("classes", [])]
