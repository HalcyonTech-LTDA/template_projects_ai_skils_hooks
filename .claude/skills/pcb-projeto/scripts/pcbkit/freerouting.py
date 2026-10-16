"""Freerouting 2.5.0 sem interface: linha de comando, execucao, log e troca Specctra (DSN/SES).

Verificado em 2026-10-12 com o `freerouting-2.5.0.jar` e Java 26 (ver
`pcb-layout/references/freerouting.md`):
- flags: `-de <dsn> -do <ses>`, `--router.autorouter.max_passes=N` (o `-mp` e obsoleto),
  `-mt N` (threads do otimizador), `--router.autorouter.ignore_net_classes=A,B` (o `-inc` e obsoleto),
  `-da` (desliga a telemetria, ligada por padrao), `--gui.enabled=false`,
  `--user_data_path=<dir>` (sem ela o Freerouting grava freerouting.json e log no perfil do usuario).
- o `freerouting-cli` nativo da mesma versao trava no roteamento (erro de serializacao do GraalVM):
  so o jar e usado.
- a etapa de fanout (ligada por padrao) cria "micro neckdowns" de 0,125 mm (abaixo da trilha minima
  de 0,15 mm: erro de DRC) e ignora `ignore_net_classes` (tocos e vias em rede ignorada). Ela fica
  desligada (`--router.fanout.enabled=false`); `filtrar_sessao` continua tirando do SES qualquer coisa
  feita em rede ignorada, por garantia. O neckdown na entrada de pino fino (0,1874 mm = 0,75 x 0,25)
  continua: sem ele o ESP32 nao fecha.
- quando uma rede nao passa, o Freerouting tenta de novo com trilha fina ("Necked retry", 0,125 mm
  por padrao); `--router.neck_width_um` passa a ser a trilha minima da placa.
- zona exportada como `(plane ...)`: o Freerouting liga o GND por via ate o plano, mas as trilhas
  picotam a zona em ilhas sem ligacao entre si (5 "conexoes faltando" de GND no exemplo). `sem_planos`
  tira os planos do DSN: o GND e roteado por trilha e a zona entra por cima, depois.
- com redes ignoradas a placa nunca fica 100% roteada e o Freerouting pula a otimizacao.
- ele NAO conta trilha que ja esta na placa como ligacao (nem `(type fix)` nem `(type protect)`): numa
  placa ja roteada, roteia tudo de novo em paralelo (70 trilhas a mais no exemplo). O `rotear.py` so
  aceita do SES as redes que o DRC (sem as zonas) mostra com ligacao faltando.

Os textos DSN/SES comecam com `(string_quote ")`: as funcoes daqui so leem a partir de
`(network` / `(network_out`, com um leitor que respeita aspas.
"""

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

PASSES_PADRAO = 100
TIMEOUT_PADRAO = 900


class ErroFreerouting(RuntimeError):
    pass


# --- linha de comando ----------------------------------------------------------------------

def comando_base(amb):
    """['java', '-jar', <jar>] ou levanta ErroFreerouting dizendo o que falta."""
    if not amb.freerouting_jar:
        raise ErroFreerouting("Freerouting nao encontrado: baixe freerouting-<versao>.jar em "
                              "https://github.com/freerouting/freerouting/releases e aponte FREEROUTING_JAR "
                              "para ele (bloco env do .claude/settings.local.json)")
    if not amb.java:
        raise ErroFreerouting("Java nao encontrado: o jar do Freerouting precisa de Java 21+ no PATH")
    return [str(amb.java), "-jar", str(amb.freerouting_jar)]


def comando(base, dsn, ses, dir_dados, passes=PASSES_PADRAO, threads=None, ignorar=(), trilha_minima_um=None):
    args = list(base) + ["-de", str(dsn), "-do", str(ses), f"--router.autorouter.max_passes={int(passes)}",
                         "--router.fanout.enabled=false", "-da", "--gui.enabled=false",
                         f"--user_data_path={dir_dados}"]
    if threads:
        args += ["-mt", str(int(threads))]
    if trilha_minima_um:
        args.append(f"--router.neck_width_um={int(round(trilha_minima_um))}")
    if ignorar:
        args.append("--router.autorouter.ignore_net_classes=" + ",".join(ignorar))
    return args


def rodar(args, cwd, log, timeout=TIMEOUT_PADRAO):
    """Roda o Freerouting com a saida no arquivo `log`. Devolve o codigo de saida."""
    Path(dir_dados_de(args)).mkdir(parents=True, exist_ok=True)
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        try:
            r = subprocess.run(args, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, timeout=timeout,
                               env=_ambiente_sem_telemetria())
        except subprocess.TimeoutExpired as e:
            raise ErroFreerouting(f"Freerouting passou de {timeout} s (aumente --timeout ou reduza --passes); "
                                  f"log em {log}") from e
        except OSError as e:
            raise ErroFreerouting(f"nao consegui rodar o Freerouting: {e}") from e
    return r.returncode


def dir_dados_de(args):
    for a in args:
        if str(a).startswith("--user_data_path="):
            return str(a).split("=", 1)[1]
    raise ValueError("comando sem --user_data_path")


def _ambiente_sem_telemetria():
    env = dict(os.environ)
    env["FREEROUTING__USAGE_AND_DIAGNOSTIC_DATA__DISABLE_ANALYTICS"] = "true"
    return env


# --- log -----------------------------------------------------------------------------------

_ROTEAMENTO = re.compile(r"Auto-routing stage completed: started with (\d+) unrouted nets.*?"
                         r"\((\d+) unrouted and (\d+) violations\)")
_ESTADO = re.compile(r"finished with state: (\w+)")
_PASSE = re.compile(r"Auto-routing pass #(\d+)")


@dataclass
class ResumoLog:
    estado: str = None          # COMPLETED, CANCELLED...
    pendentes_inicio: int = None
    pendentes_fim: int = None
    violacoes: int = None
    passes: int = 0
    otimizou: bool = False
    erro: str = None            # primeira linha de excecao, se houver


def resumir_log(texto):
    r = ResumoLog()
    m = _ROTEAMENTO.search(texto)
    if m:
        r.pendentes_inicio, r.pendentes_fim, r.violacoes = (int(g) for g in m.groups())
    m = _ESTADO.search(texto)
    r.estado = m.group(1) if m else None
    r.passes = max((int(n) for n in _PASSE.findall(texto)), default=0)
    r.otimizou = "Optimization stage completed" in texto
    excecao = next((ln for ln in texto.splitlines() if "Exception" in ln or ln.startswith("Error")), None)
    r.erro = excecao.strip() if excecao else None
    return r


# --- Specctra: leitor que respeita aspas ---------------------------------------------------

def _fim_da_lista(texto, i):
    """Indice logo depois do ')' que fecha o '(' em texto[i]."""
    nivel, n = 0, len(texto)
    while i < n:
        c = texto[i]
        if c == '"':
            fim = texto.find('"', i + 1)
            i = n if fim < 0 else fim + 1
            continue
        if c == "(":
            nivel += 1
        elif c == ")":
            nivel -= 1
            if nivel == 0:
                return i + 1
        i += 1
    raise ValueError("lista sem ')' de fechamento")


_TOKEN = re.compile(r'"([^"]*)"|([()])|([^\s()"]+)')


def _ler(texto):
    """Lista aninhada a partir de um trecho que comeca em '(' (sem o string_quote do cabecalho)."""
    pilha = [[]]
    for m in _TOKEN.finditer(texto):
        aspas, paren, atomo = m.groups()
        if paren == "(":
            pilha.append([])
        elif paren == ")":
            feito = pilha.pop()
            pilha[-1].append(feito)
            if len(pilha) == 1:
                break
        else:
            pilha[-1].append(aspas if aspas is not None else atomo)
    return pilha[0][0] if pilha[0] else []


def _secao(texto, nome):
    i = texto.find("(" + nome)
    if i < 0:
        return None, None
    return i, _fim_da_lista(texto, i)


def classes_do_dsn(texto):
    """{classe: [redes]} da secao (network ...) do DSN exportado pelo KiCad (Default = kicad_default)."""
    i, fim = _secao(texto, "network")
    if i is None:
        return {}
    classes = {}
    for no in _ler(texto[i:fim])[1:]:
        if isinstance(no, list) and no and no[0] == "class":
            classes[no[1]] = [x for x in no[2:] if isinstance(x, str)]
    return classes


def sem_planos(texto):
    """Tira as listas (plane ...) da secao structure do DSN. Devolve (texto, quantos tirou)."""
    i, fim = _secao(texto, "structure")
    if i is None:
        return texto, 0
    partes, j, n = [texto[:i]], i, 0
    while True:
        k = texto.find("(plane ", j, fim)
        if k < 0:
            break
        partes.append(texto[j:k].rstrip(" \t"))
        j = _fim_da_lista(texto, k)
        n += 1
    partes.append(texto[j:])
    return "".join(partes), n


def _nome_da_rede(bloco):
    m = re.match(r'\(net\s+(?:"([^"]*)"|([^\s()]+))', bloco)
    return (m.group(1) if m.group(1) is not None else m.group(2)) if m else None


def _blocos_de_rede(texto):
    """(inicio, fim, nome) de cada (net ...) da secao network_out do SES."""
    i, fim = _secao(texto, "network_out")
    if i is None:
        return
    j = i
    while True:
        k = texto.find("(net ", j, fim)
        if k < 0:
            return
        j = _fim_da_lista(texto, k)
        yield k, j, _nome_da_rede(texto[k:j])


def redes_da_sessao(texto):
    return [nome for _, _, nome in _blocos_de_rede(texto)]


def filtrar_sessao(texto, redes):
    """Tira do SES (secao network_out) o roteamento das `redes`. Devolve (texto, {rede: blocos tirados})."""
    redes, partes, tirados, j = set(redes or ()), [], {}, 0
    for inicio, fim, nome in _blocos_de_rede(texto):
        if nome in redes:
            partes.append(texto[j:inicio])
            tirados[nome] = tirados.get(nome, 0) + 1
            j = fim
    partes.append(texto[j:])
    return "".join(partes), tirados
