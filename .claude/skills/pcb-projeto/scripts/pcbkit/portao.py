"""Portao de liberacao (portao 2): tudo de novo, nada confiado a execucao anterior.

Bloqueia se faltar qualquer um: ERC sem erros e sem avisos; DRC sem erros com paridade e zonas
reenchidas (qualquer violacao de paridade ou conexao faltando bloqueia, de qualquer severidade; os
demais avisos NAO bloqueiam, mas saem listados para a pessoa justificar na nota); nenhuma regra
critica de ERC/DRC rebaixada no `.kicad_pro` (`pcbkit.severidades`; rebaixamentos nao criticos e
exclusoes saem listados); `.kicad_dru` aceito pelo kicad-cli; `revisao` e `tensao_max_v` declarados
na spec, e `--rev` igual a `revisao` da spec; todo componente montado com `MPN` e `LCSC` (ou motivo
em `Sem_LCSC`); nota de liberacao aprovada (`pcbkit.nota`) com `type: gate`, `gate: liberacao`,
`placa` e `revisao` iguais as do projeto.

Alta tensao — `tensao_max_v` (pico) acima de 60 V (DC) ou de 42,4 V com `tensao_ac: true` (ES1 da
IEC 62368-1: 30 Vrms), ou sem o valor, ou rede na net class `HV` (inclusive composta, `HV,Power`),
ou redes atribuidas a `HV` na spec —: nota `gate: alta-tensao` aprovada (outro arquivo, nao a nota de
liberacao) e regras `clearance` e `creepage` para `HV` no `.kicad_dru` (`pcbkit.regra_hv`).

As verificacoes sao funcoes puras sobre dados ja carregados (testaveis sem KiCad); `rodar()` chama o
kicad-cli e as alimenta.
"""

import collections
import math
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from . import kicad_cli, netlist, nota, projeto, regra_hv, regras, severidades, sexpr
from .fab import bom

LIMITE_HV_DC_V = 60
LIMITE_HV_AC_PICO_V = 42.4
CLASSE_HV = "HV"
PAPEL_LIBERACAO = "liberacao"
PAPEL_HV = "alta-tensao"
RESTRICOES_HV = regra_hv.RESTRICOES
MINIMO_HV_MM = regra_hv.MINIMO_MM
_REV_NO_NOME = re.compile(r"_Rev([A-Za-z0-9]+)_")


@dataclass
class Verificacao:
    nome: str
    ok: bool
    motivos: list = field(default_factory=list)
    detalhes: dict = field(default_factory=dict)


@dataclass
class Resultado:
    placa: str
    verificacoes: list
    avisos_drc: list = field(default_factory=list)
    alta_tensao: list = field(default_factory=list)      # por que a placa e tratada como HV (vazio = nao e)
    revisao: str = None                                  # revisao liberada (a da spec)
    severidades: dict = field(default_factory=dict)      # rebaixamentos e exclusoes (severidades.Auditoria)

    @property
    def ok(self):
        return all(v.ok for v in self.verificacoes)


def _v(nome, motivos, **detalhes):
    return Verificacao(nome, not motivos, list(motivos), detalhes)


def _por_tipo(violacoes):
    contagem = collections.Counter(f"{v.get('type')} ({v.get('severity')})" for v in violacoes)
    return ", ".join(f"{n} x {t}" for t, n in sorted(contagem.items()))


# --- ERC, DRC e severidades ------------------------------------------------------------

def verificar_erc(rel):
    if rel.erros or rel.avisos:
        return _v("ERC (estrito)", [f"{rel.erros} erro(s) e {rel.avisos} aviso(s): {_por_tipo(rel.violacoes)}"])
    return _v("ERC (estrito)", [])


def avisos_drc(rel):
    return [{"tipo": v.get("type"), "descricao": v.get("description"),
             "itens": [i.get("description") for i in v.get("items", [])]}
            for v in rel.violacoes if v.get("severity") == "warning"]


def verificar_drc(rel):
    """Erro em qualquer secao bloqueia; paridade e conexao faltando bloqueiam em qualquer severidade
    (no 10.0.0 `missing_footprint` e cia. sao `warning` por padrao: footprint faltando passaria)."""
    erros = [v for v in rel.violacoes if v.get("severity") == "error"]
    erros += rel.nao_conectados + rel.paridade
    motivos = [f"{len(erros)} violacao(oes) que bloqueiam: {_por_tipo(erros)}"] if erros else []
    return _v("DRC com paridade (zonas reenchidas)", motivos, avisos=len(avisos_drc(rel)))


def verificar_severidades(aud):
    motivos = []
    if aud.criticas_rebaixadas:
        motivos.append("regra(s) critica(s) rebaixada(s) no .kicad_pro escondem violacoes do relatorio: "
                       + "; ".join(aud.criticas_rebaixadas)
                       + " (volte ao padrao em Regras de projeto > Severidade, ou apague a chave no .kicad_pro)")
    return _v("severidades de ERC/DRC no .kicad_pro", motivos, **aud.como_dict())


def verificar_dru(aceito, mensagem):
    return _v(".kicad_dru aceito pelo kicad-cli", [] if aceito else [mensagem])


# --- spec: revisao e tensao ------------------------------------------------------------

def revisao_da_spec(spec):
    return str((spec or {}).get("revisao") or "").strip() or None


def verificar_revisao(spec, rev_pedida):
    """A revisao liberada e a da spec; `--rev` (se dado) precisa bater com ela."""
    rev = revisao_da_spec(spec)
    if not rev:
        return _v("revisao declarada na spec", ["'revisao' ausente na spec: declare a revisao que esta sendo "
                                               "liberada (ex.: \"revisao\": \"A\") em spec/<placa>.json"])
    if rev_pedida and rev_pedida != rev:
        return _v("revisao declarada na spec", [f"--rev {rev_pedida} nao bate com a revisao da spec ({rev}): "
                                               f"use --rev {rev} ou atualize a spec"], revisao=rev)
    return _v("revisao declarada na spec", [], revisao=rev)


def tensao_ac(spec):
    """`tensao_ac` diferente de false conta como AC (o limite mais baixo)."""
    valor = (spec or {}).get("tensao_ac", False)
    return valor is not False and valor is not None


def limite_hv(spec):
    return LIMITE_HV_AC_PICO_V if tensao_ac(spec) else LIMITE_HV_DC_V


def tensao_max(spec):
    """(valor de pico em modulo ou None, motivo do bloqueio ou None)."""
    if spec is None:
        return None, "spec do projeto ausente: declare 'tensao_max_v' em spec/<placa>.json"
    valor = spec.get("tensao_max_v")
    if valor is None:
        return None, "'tensao_max_v' nulo ou ausente na spec: declare a maior tensao da placa em volts (pico)"
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return None, f"'tensao_max_v' nao numerico: {valor!r}"
    if not math.isfinite(valor):
        return None, f"'tensao_max_v' nao finito ({valor}): declare a maior tensao da placa em volts (pico)"
    return abs(float(valor)), None


def verificar_tensao(spec):
    valor, motivo = tensao_max(spec)
    motivos = [motivo] if motivo else []
    if spec is not None and not isinstance(spec.get("tensao_ac", False), bool):
        motivos.append(f"'tensao_ac' deve ser true ou false, nao {spec.get('tensao_ac')!r}")
    return _v("tensao_max_v declarado na spec", motivos, tensao_max_v=valor, tensao_ac=tensao_ac(spec),
              limite_hv_v=limite_hv(spec))


def verificar_bom(comps):
    pend = bom.pendencias(comps)
    motivos = [f"{len(pend)} componente(s) montado(s) sem codigo: " + "; ".join(pend)] if pend else []
    return _v("BOM: MPN e LCSC em todo componente montado", motivos,
              montados=len(bom.montados(comps)), sem_lcsc_justificado=[c.ref for c in comps if c.sem_lcsc])


# --- notas de portao -------------------------------------------------------------------

def revisao_no_nome(caminho):
    m = _REV_NO_NOME.search(Path(caminho).name)
    return m.group(1) if m else None


def _campo(n, nome):
    return str(n.frontmatter.get(nome, "") or "").strip()


def _papel(n, papel):
    if _campo(n, "type") != "gate":
        return ["a nota nao e de portao: o frontmatter precisa de 'type: gate' (use a nota modelo)"]
    gate = _campo(n, "gate")
    if gate != papel:
        return [f"a nota e do portao '{gate or 'vazio'}', nao '{papel}': use a nota modelo deste portao"]
    return []


def _identidade(n, caminho, placa, rev):
    motivos = []
    placa_nota, rev_nota, rev_nome = _campo(n, "placa"), _campo(n, "revisao"), revisao_no_nome(caminho)
    if placa_nota != placa:
        motivos.append(f"a nota e da placa '{placa_nota}', nao de '{placa}'" if placa_nota
                       else f"'placa' ausente no frontmatter da nota (precisa ser '{placa}')")
    if not rev_nota:
        motivos.append(f"'revisao' ausente no frontmatter da nota (precisa ser '{rev or '?'}')")
    elif rev and rev_nota != rev:
        motivos.append(f"a nota e da revisao {rev_nota}, nao da {rev}")
    if rev and rev_nome and rev_nome != rev:
        motivos.append(f"o nome do arquivo diz Rev{rev_nome}, nao Rev{rev}")
    return motivos


def verificar_nota(n, caminho, placa, rev, rotulo, papel):
    """Nota aprovada (`pcbkit.nota`), do portao `papel`, desta placa e desta revisao."""
    if n is None:
        return _v(rotulo, [f"nota nao encontrada: {caminho}"])
    motivos = nota.pendencias(n) + _papel(n, papel) + _identidade(n, caminho, placa, rev)
    return _v(rotulo, motivos, nota=str(caminho), revisores=nota.revisores(n))


def caminho_nota_hv(checklist, placa, rev):
    return Path(checklist).parent / f"{placa}_Rev{rev}_Aprovacao_Alta_Tensao.md"


def mesmo_arquivo(a, b):
    return Path(a).resolve() == Path(b).resolve()


# --- alta tensao -----------------------------------------------------------------------

def _redes_hv(redes, dados_pro, classes):
    """Redes na net class HV: pela classe da netlist (o KiCad resolve regex e classe composta) e,
    por garantia, pelos padroes do `.kicad_pro`."""
    return sorted(r for r in redes if CLASSE_HV in (classes or {}).get(r, [])
                  or (dados_pro and CLASSE_HV in regras.classes_da_rede(dados_pro, r)))


def motivos_alta_tensao(spec, dados_pro, redes, classes=None):
    """Por que a placa exige o portao HV (lista vazia = nao exige). `redes` = nomes da netlist;
    `classes` = rede -> [net classes] da netlist (`Netlist.classes`)."""
    motivos = []
    valor, problema = tensao_max(spec)
    limite = limite_hv(spec)
    if problema:
        motivos.append("tensao_max_v nao declarado (tratado como alta tensao ate ser declarado)")
    elif valor > limite:
        tipo = "AC: 30 Vrms, ES1 da IEC 62368-1" if tensao_ac(spec) else "DC"
        motivos.append(f"tensao_max_v = {valor:g} V de pico > {limite:g} V ({tipo})")
    em_hv = _redes_hv(redes, dados_pro, classes)
    if em_hv:
        motivos.append(f"net class {CLASSE_HV} com redes na placa: {', '.join(em_hv)}")
    declaradas = ((spec or {}).get("classes_de_rede") or {}).get(CLASSE_HV, {}) or {}
    if declaradas.get("redes"):
        motivos.append(f"spec atribui redes a {CLASSE_HV}: {', '.join(declaradas['redes'])}")
    return motivos


def _medida_da_nota(n, tipo):
    """(texto, valor em mm) de `<tipo>_mm` da nota HV. Vazio -> ("", None). Aceita virgula decimal
    ("3,2"), como se digita no Brasil; texto que nao e medida -> (texto, None)."""
    texto = str((n.frontmatter if n else {}).get(f"{tipo}_mm", "") or "").strip()
    return texto, (regra_hv.medida_mm(texto.replace(",", ".")) if texto else None)


def minimo_da_nota(n):
    """Maior entre 2,5 mm e `clearance_mm`/`creepage_mm` do frontmatter da nota HV, por restricao."""
    return {tipo: max(MINIMO_HV_MM, _medida_da_nota(n, tipo)[1] or 0) for tipo in RESTRICOES_HV}


def medidas_ilegiveis(n):
    """Motivos de bloqueio para `<tipo>_mm` preenchido com algo que nao e medida: ignorar em
    silencio deixaria o minimo cair para 2,5 mm sem ninguem saber."""
    motivos = []
    for tipo in RESTRICOES_HV:
        texto, valor = _medida_da_nota(n, tipo)
        if texto and valor is None:
            motivos.append(f"{tipo}_mm = {texto!r} na nota de alta tensao nao e uma medida "
                           "(use 3.2, 3,2 ou 3.2mm)")
    return motivos


def verificar_regra_hv(arvore_dru, dru_aceito, minimos=None):
    minimos = minimos or {t: MINIMO_HV_MM for t in RESTRICOES_HV}
    achadas = regra_hv.minimos(arvore_dru)
    motivos = []
    faltam = [t for t in RESTRICOES_HV if achadas.get(t, 0) < minimos[t]]
    if faltam:
        exigido = "; ".join(f"{t} >= {minimos[t]:g} mm (achado: "
                            + (f"{achadas[t]:g} mm)" if t in achadas else "nenhuma)") for t in faltam)
        motivos.append(f"o .kicad_dru nao tem regra valida de {' e '.join(faltam)} para a net class {CLASSE_HV}: "
                       f"{exigido}. Regra valida: condicao \"A.hasNetclass('HV')\" ou "
                       "\"A.hasNetclass('HV') || B.hasNetclass('HV')\", sem severity rebaixada, sem layer. "
                       "Concatene assets/kicad/alta-tensao.kicad_dru e ajuste pela norma")
        motivos += regra_hv.nao_contam(arvore_dru)
    for tipo in RESTRICOES_HV:
        depois = regra_hv.sobrepostas(arvore_dru, tipo, minimos[tipo])
        if depois:
            motivos.append(f"regra(s) {', '.join(depois)} depois da regra HV redefinem {tipo} abaixo de "
                           f"{minimos[tipo]:g} mm e vencem (o KiCad usa a ultima que casa): "
                           "mova as regras HV para o fim do .kicad_dru")
    if not dru_aceito:
        motivos.append("o .kicad_dru foi rejeitado pelo kicad-cli: as regras HV nao valem")
    return _v(f"regras {CLASSE_HV} (clearance e creepage) no .kicad_dru", motivos, minimos_mm=achadas,
              exigido_mm=minimos)


# --- orquestracao (kicad-cli) ------------------------------------------------------------

def _ler_nota(caminho):
    return nota.ler(caminho) if caminho and Path(caminho).is_file() else None


def _ler_dru(caminho):
    try:
        return sexpr.carregar_todos(Path(caminho).read_text(encoding="utf-8"), comentarios=True)
    except (OSError, sexpr.ErroSexpr):
        return None


def _kicad(amb, proj):
    """(relatorio ERC, relatorio DRC, (dru aceito, mensagem), netlist), tudo em pasta temporaria."""
    with tempfile.TemporaryDirectory(prefix="pcbkit-portao-") as tmp:
        tmp = Path(tmp)
        erc = kicad_cli.erc(amb, proj.sch, saida=tmp / "erc.json")
        drc = kicad_cli.drc(amb, proj.pcb, saida=tmp / "drc.json", paridade=True, reencher_zonas=True)
        dru = kicad_cli.validar_dru(amb, proj.dru, proj.pro)
        net = netlist.ler(kicad_cli.exportar_netlist(amb, proj.sch, tmp / "placa.net"))
    return erc, drc, dru, net


def _spec(proj):
    try:
        return projeto.ler_spec(proj), None
    except projeto.ErroProjeto as e:
        return None, str(e)


def _pro(proj):
    try:
        return regras.ler_pro(proj.pro), None
    except (OSError, ValueError) as e:
        return {}, _v(".kicad_pro legivel", [f"{proj.pro.name} nao e JSON valido: {e}"])


def _verificacoes_hv(res, spec, dados_pro, net, dru_aceito, proj, checklist, aprovacao_hv):
    res.alta_tensao = motivos_alta_tensao(spec, dados_pro, net.redes, net.classes)
    if not res.alta_tensao:
        return
    caminho = Path(aprovacao_hv) if aprovacao_hv else caminho_nota_hv(checklist, proj.placa, res.revisao or "?")
    n = _ler_nota(caminho)
    v = verificar_nota(n, caminho, proj.placa, res.revisao, "nota de aprovacao de alta tensao", PAPEL_HV)
    if n is not None and mesmo_arquivo(caminho, checklist):
        v.ok = False
        v.motivos.append("a nota de alta tensao e o mesmo arquivo da nota de liberacao: aprove a nota "
                         f"{proj.placa}_Rev{res.revisao}_Aprovacao_Alta_Tensao.md (assets/opcionais)")
    ilegiveis = medidas_ilegiveis(n)
    if ilegiveis:
        v.ok = False
        v.motivos += ilegiveis
    res.verificacoes.append(v)
    res.verificacoes.append(verificar_regra_hv(_ler_dru(proj.dru), dru_aceito, minimo_da_nota(n)))


def _verificacoes_spec(res, proj, rev):
    spec, erro_spec = _spec(proj)
    v_rev = verificar_revisao(spec, rev) if not erro_spec else _v("spec legivel", [erro_spec])
    res.revisao = revisao_da_spec(spec) or rev
    res.verificacoes.append(v_rev)
    return spec, erro_spec


def rodar(amb, proj, checklist, aprovacao_hv=None, rev=None):
    """Roda o portao inteiro. A revisao liberada e a da spec; `rev` (opcional) precisa bater com ela."""
    faltando = proj.faltando()
    res = Resultado(proj.placa, [_v("arquivos do projeto", [f"faltando: {', '.join(faltando)}"] if faltando else [])])
    spec, erro_spec = _verificacoes_spec(res, proj, rev)
    nota_lib = _ler_nota(checklist)
    v_nota = verificar_nota(nota_lib, checklist, proj.placa, res.revisao, "nota de liberacao", PAPEL_LIBERACAO)
    if faltando:
        res.verificacoes.append(v_nota)
        return res
    dados_pro, erro_pro = _pro(proj)
    aud = severidades.auditar(dados_pro)
    res.severidades = aud.como_dict()
    erc, drc, (dru_aceito, dru_msg), net = _kicad(amb, proj)
    res.avisos_drc = avisos_drc(drc)
    res.verificacoes += [verificar_erc(erc), verificar_drc(drc), verificar_severidades(aud),
                         verificar_dru(dru_aceito, dru_msg)] + ([erro_pro] if erro_pro else [])
    res.verificacoes += ([] if erro_spec else [verificar_tensao(spec)]) + [verificar_bom(bom.componentes(net)), v_nota]
    _verificacoes_hv(res, spec, dados_pro, net, dru_aceito, proj, checklist, aprovacao_hv)
    return res


def resumo(res):
    return {"ok": res.ok, "placa": res.placa, "revisao": res.revisao, "alta_tensao": res.alta_tensao,
            "avisos_drc": res.avisos_drc, "severidades": res.severidades,
            "verificacoes": [{"nome": v.nome, "ok": v.ok, "motivos": v.motivos, "detalhes": v.detalhes}
                             for v in res.verificacoes]}
