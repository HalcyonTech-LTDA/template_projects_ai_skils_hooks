"""Roteia os sinais simples com o Freerouting sem interface. Roda SO no Python do KiCad (pcbnew).

Uso:
  "<KiCad>/bin/python.exe" rotear.py <placa.kicad_pcb> [--ignorar-classes Power,HV] [--passes N]
      [--threads N] [--timeout S] [--manter-intermediarios] [--json]

Fluxo: DRC numa copia sem zonas para saber quais redes tem ligacao faltando -> trava as trilhas
que ja existem (o Freerouting nao mexe nelas) -> exporta Specctra DSN e tira dele as zonas (`plane`:
o GND passa a ser roteado por trilha) -> Freerouting (jar, sem fanout, `-da`, dados num diretorio
temporario) -> do SES so entram as redes que tinham ligacao faltando e nao sao de classe ignorada
(ele nao conta trilha existente como ligacao e roteia de novo o que ja esta ligado) -> importa ->
tira copias das trilhas preservadas -> destrava -> reenche as zonas -> alarga para a trilha minima o
que o neckdown afinou (desfaz se violar regra) -> grava a placa. Nada pendente: nao roda o Freerouting.
Detalhes e motivos em pcbkit/freerouting.py.

`--ignorar-classes` (padrao `Power,HV`) deixa essas net classes para a pessoa; `""` roteia tudo.
Trilhas que ja existem (ex.: `Power` roteado pela pessoa) sao preservadas intactas e o resto e
roteado em volta delas. O Freerouting so otimiza quando ele mesmo fecha 100% das ligacoes: com
classe ignorada ou com trilha fixa na placa a otimizacao fica de fora (ver references/freerouting.md).
Saida: 0 todos os sinais das classes nao ignoradas ligados e nenhum erro de regra no DRC; 1 sobrou
conexao fora das classes ignoradas, erro de regra no DRC ou o Freerouting falhou; 2 uso errado,
Freerouting/Java/KiCad ausente ou fora do Python do KiCad.
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from pcbkit import ambiente, console, drc, freerouting, kicad_cli, regras, sexpr
from pcbkit.swig import ErroSwig

CLASSES_PADRAO = "Power,HV"
CLASSE_DEFAULT_DSN = "kicad_default"


def _args(argv):
    p = argparse.ArgumentParser(description="Freerouting headless nos sinais simples (Python do KiCad).")
    p.add_argument("pcb", help="placa .kicad_pcb (o .kicad_pro com as net classes fica ao lado)")
    p.add_argument("--ignorar-classes", default=CLASSES_PADRAO,
                   help=f'net classes que o Freerouting nao roteia (padrao "{CLASSES_PADRAO}"; "" roteia tudo)')
    p.add_argument("--passes", type=int, default=freerouting.PASSES_PADRAO, help="maximo de passes do autorouter")
    p.add_argument("--threads", type=int, help="threads do otimizador (padrao do Freerouting: nucleos - 1)")
    p.add_argument("--timeout", type=int, default=freerouting.TIMEOUT_PADRAO, help="segundos ate abortar o Freerouting")
    p.add_argument("--manter-intermediarios", action="store_true",
                   help="mantem DSN, SES e log na pasta temporaria (o caminho sai no resumo)")
    p.add_argument("--json", action="store_true", help="saida em JSON")
    return p.parse_args(argv)


def _classes_pedidas(texto):
    return [c.strip() for c in (texto or "").split(",") if c.strip()]


def _ignoradas(pedidas, classes_dsn):
    """Classes do DSN que contem alguma pedida e as redes delas. 'Default' vira o nome do DSN.

    Rede em duas net classes sai no DSN com a classe composta (`HV,Power`): ela e ignorada se QUALQUER
    parte for pedida. O Freerouting separa `ignore_net_classes` por virgula e nao reconhece a composta;
    quem a protege e o filtro do SES (`_importar`), que tira as redes devolvidas aqui."""
    nomes = {CLASSE_DEFAULT_DSN if c == regras.CLASSE_PADRAO else c for c in pedidas}
    ativas = sorted(c for c in classes_dsn if regras.tem_classe(c, nomes))
    redes = sorted({r for c in ativas for r in classes_dsn[c]})
    return ativas, redes


def _para_freerouting(ativas):
    """Nomes que vao na flag `ignore_net_classes` (so os simples: a virgula e o separador da flag)."""
    return [c for c in ativas if "," not in c]


def _pendentes_sem_zonas(amb, pcb, tmp):
    """Redes com ligacao faltando sem contar as zonas (o GND entra, pois a zona e picotada pelas
    trilhas). E o que o Freerouting pode mexer: ele nao conta trilha existente como ligacao e
    rotearia de novo, em paralelo, o que ja esta ligado."""
    copia = tmp / "sem-zonas.kicad_pcb"
    raiz = sexpr.carregar_arquivo(pcb)
    sexpr.salvar_arquivo(copia, [n for n in raiz if sexpr.etiqueta(n) != "zone"])
    for ext in (".kicad_pro", ".kicad_dru"):
        if Path(pcb).with_suffix(ext).is_file():
            shutil.copy(Path(pcb).with_suffix(ext), copia.with_suffix(ext))
    rel = kicad_cli.drc(amb, copia, saida=tmp / "drc-sem-zonas.json")
    return set(drc.desconectados_por_rede(rel)) - {"?"}


def _exportar(specctra, board, args, tmp):
    """DSN sem planos; classes pedidas que existem nele e as redes delas."""
    dsn = tmp / "placa.dsn"
    specctra.exportar_dsn(board, dsn)
    texto, planos = freerouting.sem_planos(dsn.read_text(encoding="utf-8"))
    dsn.write_text(texto, encoding="utf-8")
    ativas, redes = _ignoradas(_classes_pedidas(args.ignorar_classes), freerouting.classes_do_dsn(texto))
    return dsn, planos, ativas, redes


def _rodar_freerouting(specctra, board, amb, args, tmp, dsn, ativas):
    ses, log = tmp / "placa.ses", tmp / "freerouting.log"
    cmd = freerouting.comando(freerouting.comando_base(amb), dsn, ses, tmp / "dados", args.passes, args.threads,
                              _para_freerouting(ativas), specctra.trilha_minima_um(board))
    rc = freerouting.rodar(cmd, tmp, log, args.timeout)
    resumo = freerouting.resumir_log(log.read_text(encoding="utf-8", errors="replace"))
    if rc != 0 or not ses.is_file():
        raise freerouting.ErroFreerouting(f"Freerouting saiu com codigo {rc} sem gerar o SES "
                                          f"({resumo.erro or 'ver o log'}); log em {log}")
    return ses, resumo, log


def _importar(specctra, board, ses, permitidas, travadas):
    """So entram do SES as redes permitidas (pendentes e fora das classes ignoradas)."""
    texto = ses.read_text(encoding="utf-8")
    texto, tirados = freerouting.filtrar_sessao(texto, set(freerouting.redes_da_sessao(texto)) - permitidas)
    filtrado = ses.with_name("placa-filtrada.ses")
    filtrado.write_text(texto, encoding="utf-8")
    specctra.importar_ses(board, filtrado)
    return tirados, specctra.remover_copias(board, travadas)


def _rotear(specctra, board, amb, args, tmp):
    """DSN -> Freerouting -> SES filtrado -> placa. Devolve o dicionario do resumo."""
    pendentes = _pendentes_sem_zonas(amb, args.pcb, tmp)
    travadas = specctra.travar_existentes(board)
    dsn, planos, ativas, redes_ignoradas = _exportar(specctra, board, args, tmp)
    permitidas = pendentes - set(redes_ignoradas)
    antes = specctra.contar(board)
    r = {"classes_pedidas": _classes_pedidas(args.ignorar_classes), "classes_ignoradas": ativas,
         "redes_ignoradas": redes_ignoradas, "redes_a_rotear": sorted(permitidas), "planos_tirados_do_dsn": planos,
         "preservadas": len(travadas), "trilhas_vias_antes": antes, "freerouting": None, "log": None,
         "redes_tiradas_do_ses": {}, "copias_removidas": 0}
    if permitidas:
        ses, resumo, log = _rodar_freerouting(specctra, board, amb, args, tmp, dsn, ativas)
        r["redes_tiradas_do_ses"], r["copias_removidas"] = _importar(specctra, board, ses, permitidas, travadas)
        r.update({"freerouting": vars(resumo), "log": str(log)})
    specctra.destravar(board, travadas)
    r["trilhas_vias_depois"] = specctra.contar(board)
    return r


def _drc(amb, pcb):
    """DRC sem paridade (zonas reenchidas), so para medir o roteamento."""
    with tempfile.TemporaryDirectory(prefix="pcbkit-drc-") as d:
        return kicad_cli.drc(amb, pcb, saida=Path(d) / "drc.json", reencher_zonas=True)


def _pendencias(rel, pcb, pedidas):
    """Conexoes que ficaram sem ligar, por net class, e as que estao fora das classes pedidas para ignorar
    (classe composta `HV,Power` conta como ignorada se alguma parte foi pedida)."""
    pro = Path(pcb).with_suffix(".kicad_pro")
    resumo = drc.resumir(rel, regras.ler_pro(pro) if pro.is_file() else None)
    por_classe = resumo["desconectados_por_classe"]
    fora = {c: n for c, n in por_classe.items() if not regras.tem_classe(c, set(pedidas))}
    return {"desconectados_por_classe": por_classe, "desconectados_por_rede": resumo["desconectados_por_rede"],
            "desconectados_fora_das_ignoradas": fora, "drc_erros_fora_desconexao": _erros_de_regra(rel)}


def _erros_de_regra(rel):
    return sorted({v.get("type") for v in rel.violacoes if v.get("severity") == "error"})


def _uuids_em_violacao(rel):
    return {i.get("uuid") for v in rel.violacoes for i in v.get("items", [])}


def _gravar_e_medir(placa, board, amb, pcb):
    placa.preencher_zonas(board)
    placa.salvar(board, pcb)
    return _drc(amb, pcb)


def _consertar_finas(specctra, placa, board, amb, pcb):
    """O neckdown do Freerouting deixa trilha de 0,125 mm na entrada de pino (abaixo da trilha minima).
    Alarga cada uma para a minima e mede; a que passar a violar alguma regra volta como estava.
    Devolve (relatorio de DRC final, alargadas, devolvidas)."""
    finas = specctra.alargar_finas(board)
    rel = _gravar_e_medir(placa, board, amb, pcb)
    voltar = {u: w for u, w in finas.items() if u in _uuids_em_violacao(rel)}
    if voltar:
        specctra.restaurar_larguras(board, voltar)
        rel = _gravar_e_medir(placa, board, amb, pcb)
    return rel, len(finas) - len(voltar), len(voltar)


def _imprimir(r):
    fr = r["freerouting"]
    print(f"Placa roteada: {r['placa']}")
    if fr:
        print(f"  Freerouting: {fr['estado']}, {fr['passes']} passe(s), pendentes {fr['pendentes_inicio']} -> "
              f"{fr['pendentes_fim']}, {fr['violacoes']} violacao(oes), "
              f"otimizacao {'feita' if fr['otimizou'] else 'pulada'}")
    else:
        print("  Freerouting nao rodou: nenhuma rede fora das classes ignoradas tem ligacao faltando")
    print(f"  classes ignoradas: {'; '.join(r['classes_ignoradas']) or 'nenhuma'}"
          + (f" ({len(r['redes_ignoradas'])} redes)" if r["redes_ignoradas"] else ""))
    if r["redes_tiradas_do_ses"]:
        print(f"  descartado do SES (rede ignorada ou ja ligada): {len(r['redes_tiradas_do_ses'])} rede(s)")
    t0, v0 = r["trilhas_vias_antes"]
    t1, v1 = r["trilhas_vias_depois"]
    print(f"  trilhas {t0} -> {t1}, vias {v0} -> {v1}; preservadas {r['preservadas']}, copias tiradas {r['copias_removidas']}")
    if r["finas_alargadas"] or r["finas_mantidas"]:
        print(f"  trilhas abaixo da minima (neckdown): {r['finas_alargadas']} alargadas, "
              f"{r['finas_mantidas']} mantidas (alargar violaria regra: revise na GUI)")
    if r["drc_erros_fora_desconexao"]:
        print("  DRC acusa ainda: " + ", ".join(r["drc_erros_fora_desconexao"]))
    pc = r["desconectados_por_classe"]
    print("  conexoes faltando por net class: " + (", ".join(f"{c} {n}" for c, n in pc.items()) or "nenhuma"))
    if r["desconectados_fora_das_ignoradas"]:
        print("  FALTA LIGAR fora das classes ignoradas: " + ", ".join(
            f"{rede} {n}" for rede, n in r["desconectados_por_rede"].items()))
    if r.get("intermediarios"):
        print(f"  intermediarios (DSN, SES, log): {r['intermediarios']}")
    print(f'Proximo: python verificar.py drc "{r["placa"]}" --paridade')


def executar(amb, args, specctra, placa):
    tmp = Path(tempfile.mkdtemp(prefix="pcbkit-rotear-"))
    try:
        board = placa.carregar(args.pcb)
        r = _rotear(specctra, board, amb, args, tmp)
        rel, r["finas_alargadas"], r["finas_mantidas"] = _consertar_finas(specctra, placa, board, amb, args.pcb)
        r.update(_pendencias(rel, args.pcb, r["classes_pedidas"]))
    finally:
        if not args.manter_intermediarios:
            shutil.rmtree(tmp, ignore_errors=True)
    r.update({"placa": str(args.pcb), "intermediarios": str(tmp) if args.manter_intermediarios else None,
              "ok": not (r["desconectados_fora_das_ignoradas"] or r["drc_erros_fora_desconexao"])})
    if not args.manter_intermediarios:
        r["log"] = None
    console.imprimir_json(r) if args.json else _imprimir(r)
    return 0 if r["ok"] else 1


def main(argv=None):
    console.configurar()
    args = _args(argv)
    try:
        from pcbkit.swig import placa, specctra
    except ErroSwig as e:
        return console.erro(str(e), 2)
    amb = ambiente.detectar()
    if not Path(args.pcb).is_file():
        return console.erro(f"arquivo nao encontrado: {args.pcb}", 2)
    try:
        freerouting.comando_base(amb)
    except freerouting.ErroFreerouting as e:
        return console.erro(str(e), 2)
    try:
        return executar(amb, args, specctra, placa)
    except freerouting.ErroFreerouting as e:
        return console.erro(str(e), 1)
    except kicad_cli.ErroKicadCli as e:
        return console.erro(str(e), 2)


if __name__ == "__main__":
    sys.exit(main())
