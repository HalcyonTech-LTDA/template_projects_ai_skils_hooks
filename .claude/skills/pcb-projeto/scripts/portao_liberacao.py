"""Portao de liberacao para fabricacao (portao 2). Roda tudo de novo e diz o que bloqueia.

Uso:
  python portao_liberacao.py <dir-projeto> --checklist <nota de liberacao> [--aprovacao-hv <nota>]
                             [--rev A] [--json]

Verifica: ERC sem erros e sem avisos; DRC sem erros com paridade e zonas reenchidas (paridade e conexao
faltando bloqueiam em qualquer severidade; os outros avisos sao listados e nao bloqueiam); nenhuma regra
critica de ERC/DRC rebaixada no .kicad_pro (rebaixamentos nao criticos e exclusoes sao listados);
`.kicad_dru` aceito pelo kicad-cli; `revisao` e `tensao_max_v` declarados na spec; `MPN` e `LCSC` (ou
motivo em `Sem_LCSC`) em todo componente montado; nota de liberacao (`type: gate`, `gate: liberacao`,
`placa` e `revisao` do projeto) com `status: aprovado`, `revisores` preenchido e nenhum item em aberto
(N/A = `- [x] N/A — motivo`). Alta tensao (`tensao_max_v` de pico > 60 V, ou > 42,4 V com
`tensao_ac: true`; valor ausente; ou rede na net class HV): nota `gate: alta-tensao`
`<placa>_Rev<R>_Aprovacao_Alta_Tensao.md` ao lado da nota de liberacao (ou `--aprovacao-hv`, outro
arquivo) aprovada pelo mesmo criterio, e regras HV de `clearance` e `creepage` >= 2,5 mm no `.kicad_dru`.
A revisao liberada e a `revisao` da spec; `--rev`, se dado, precisa bater com ela.

Saida: 0 tudo passou; 1 bloqueado; 2 uso errado, projeto invalido ou KiCad ausente.
"""

import argparse
import sys

from pcbkit import ambiente, console, kicad_cli, portao, projeto


def imprimir(res):
    print(f"Portao de liberacao: {res.placa}")
    for v in res.verificacoes:
        print(f"  {'OK       ' if v.ok else 'BLOQUEADO'}  {v.nome}")
        for motivo in v.motivos:
            print(f"             - {motivo}")
    if res.alta_tensao:
        print("  Alta tensao: " + "; ".join(res.alta_tensao))
    if res.avisos_drc:
        print(f"\n  AVISOS DE DRC ({len(res.avisos_drc)}; nao bloqueiam — justifique cada um na nota de liberacao "
              "ou exclua no KiCad com comentario):")
        for a in res.avisos_drc:
            print(f"    - {a['tipo']}: {a['descricao']}")
            for item in a["itens"]:
                print(f"        {item}")
    _imprimir_severidades(res.severidades)
    bloqueios = sum(not v.ok for v in res.verificacoes)
    print("\nLIBERADO" if res.ok else f"\nBLOQUEADO: {bloqueios} verificacao(oes) falharam")


def _imprimir_severidades(sev):
    linhas = [f"    - {r}" for r in sev.get("rebaixadas", [])]
    linhas += [f"    - exclusao DRC {e['violacao']} ({e['comentario'] or 'sem comentario'})"
               for e in sev.get("exclusoes_drc", [])]
    linhas += [f"    - exclusao ERC {e['violacao']} ({e['comentario'] or 'sem comentario'})"
               for e in sev.get("exclusoes_erc", [])]
    if linhas:
        print(f"\n  REBAIXAMENTOS E EXCLUSOES NO .kicad_pro ({len(linhas)}; nao bloqueiam — justifique na nota "
              "de liberacao):")
        print("\n".join(linhas))


def _args(argv):
    p = argparse.ArgumentParser(description="Portao de liberacao para fabricacao (ERC, DRC, BOM, notas, HV).")
    p.add_argument("projeto", help="pasta da placa (hardware/<placa>)")
    p.add_argument("--checklist", required=True, help="nota de liberacao (<placa>_Rev<R>_Liberacao_Fabricacao.md)")
    p.add_argument("--aprovacao-hv", help="nota de aprovacao de alta tensao (padrao: ao lado da nota de liberacao)")
    p.add_argument("--rev", help="revisao a liberar; precisa ser a 'revisao' da spec (padrao: a da spec)")
    p.add_argument("--json", action="store_true", help="saida em JSON")
    return p.parse_args(argv)


def executar(amb, args):
    """Devolve (codigo, resultado). O exportar_fab.py usa `imprimir` daqui para o mesmo texto."""
    proj = projeto.localizar(args.projeto)
    res = portao.rodar(amb, proj, args.checklist, args.aprovacao_hv, args.rev)
    return (0 if res.ok else 1), res


def main(argv=None):
    console.configurar()
    args = _args(argv)
    amb = ambiente.detectar()
    if not amb.encontrado:
        return console.erro("kicad-cli nao encontrado; rode diagnostico.py", 2)
    try:
        codigo, res = executar(amb, args)
    except projeto.ErroProjeto as e:
        return console.erro(str(e), 2)
    except kicad_cli.ErroKicadCli as e:
        return console.erro(str(e), 2)
    console.imprimir_json(portao.resumo(res)) if args.json else imprimir(res)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
