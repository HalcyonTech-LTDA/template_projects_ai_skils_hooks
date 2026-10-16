# Estrutura de pastas e revisoes

## Arvore de uma placa

```
hardware/
  <placa>/                          slug ASCII kebab-case: controlador-bomba, sensor-nivel
    <placa>.kicad_pro               projeto (JSON): net classes, regras de board, variaveis
    <placa>.kicad_sch               esquematico (gerado da spec ou editado na GUI — ver abaixo)
    <placa>.kicad_pcb               placa
    <placa>.kicad_dru               regras customizadas de DRC (copia de assets/kicad/jlc-*.kicad_dru)
    sym-lib-table                   bibliotecas de simbolo do projeto
    fp-lib-table                    bibliotecas de footprint do projeto
    spec/
      <placa>.json                  spec do circuito (fonte do esquematico no "modo spec")
    bibliotecas/
      <placa>.kicad_sym             simbolos desenhados pela equipe
      <placa>.pretty/               footprints desenhados pela equipe
      3d/                           modelos STEP proprios
    lcsc.kicad_sym                  importados pelo easyeda2kicad (prefixo na raiz do projeto,
    lcsc.pretty/                    para o caminho ${KIPRJMOD}/lcsc.3dshapes do modelo 3D resolver;
    lcsc.3dshapes/                  ver pcb-componentes/references/simbolos-e-footprints.md)
    fab/                            saidas de trabalho (IGNORADO pelo git)
    releases/
      rev-A/                        pacote liberado pelo portao (versionado)
        <placa>-rev-A-gerber.zip
        <placa>-rev-A-bom-jlc.csv
        <placa>-rev-A-cpl-jlc.csv
        <placa>-rev-A-bom.csv
        <placa>-rev-A-esquematico.pdf
        manifesto.json
    .gitignore                      de assets/gitignore-hardware.txt
    README.md                       o que e a placa, revisao atual, modo (spec ou manual)
```

Mais de uma placa no mesmo produto (placa principal + placa de sensor): uma pasta por placa em
`hardware/`. Cabo e chicote entre elas ficam documentados em `03_Hardware/Eletronica/` como nota.

## Por que `fab/` e ignorado e `releases/` nao

`fab/` e regeneravel a qualquer momento a partir do commit — versionar so cria diff ruidoso. O que
foi **mandado para a fabrica** e evidencia e precisa ser identico ao que chegou: por isso o
`exportar_fab.py --liberar` copia o pacote para `releases/rev-<R>/` com SHA-256 de cada arquivo no
`manifesto.json`. Se o zip na fabrica e o do repositorio divergirem, o hash mostra.

STEP e render ficam fora de `releases/` (sao grandes e regeneraveis). O STEP que a mecanica usa vai
para `03_Hardware/Mecanica/CAD_3D/` quando ela pedir.

## Modo spec e modo manual

O esquematico tem **uma** fonte de verdade por vez, declarada no `README.md` da placa:

- **Modo spec** (padrao no inicio): `spec/<placa>.json` e a fonte. O `.kicad_sch` e regenerado por
  `gerar_esquematico.py` a cada mudanca. Editar o `.kicad_sch` na GUI nesse modo e perder trabalho na
  proxima geracao.
- **Modo manual**: a partir do momento em que alguem edita o esquematico na GUI (arruma o desenho,
  agrupa melhor, cria folhas hierarquicas), o `.kicad_sch` vira a fonte. Mude o README, e a partir dai
  o agente edita pela GUI do usuario ou por patch cuidadoso no S-expression, sempre seguido de ERC e
  netlist. A spec continua util como documentacao das redes, mas nao e regenerada.

A troca e de mao unica: nao volte para o modo spec depois de editar na GUI.

## Revisoes

- Letra maiuscula: Rev A, Rev B... A revisao entra no title block do esquematico, no texto de
  serigrafia da placa (`<placa> Rev A`) e no nome do pacote.
- Revisao liberada e congelada. A seguinte comeca com o mesmo projeto e a nota de bring-up da anterior
  listando o que muda.
- Tag git sugerida ao liberar: `hw-<placa>-rev-a`. Criar tag e commitar sao decisoes do usuario.

## Notas em 03_Hardware (criadas pelo `novo_projeto.py --docs`)

| Nota | Pasta | Tipo | Papel |
|---|---|---|---|
| `<placa>_Diagrama_de_Blocos.md` | `Eletronica/Esquematicos/` | `diagrama` | Requisitos resumidos, blocos em Mermaid, orcamento de potencia |
| `<placa>_RevA_Revisao_Esquematico.md` | `Eletronica/Esquematicos/` | `gate` | Portao 1 |
| `<placa>_RevA_Liberacao_Fabricacao.md` | `Eletronica/Gerber/` | `gate` | Portao 2 (layout + fabricacao) |
| `<placa>_RevA_Bring_Up.md` | `Prototipagem/Rev_A/` | `relatorio-teste` | Bring-up e achados |

Opcional (copiar de `assets/opcionais/` so quando houver alta tensao):
`<placa>_RevA_Aprovacao_Alta_Tensao.md` ao lado da nota de liberacao.

Os tipos `gate`, `diagrama` e `relatorio-teste` e as properties `placa`, `revisao` e `revisores`
estao no schema de `docs_projeto/CONVENCOES.md`.

## `.gitignore` da placa

Vem de `assets/gitignore-hardware.txt`: `fab/`, `*-backups/`, `fp-info-cache`, `*.kicad_prl`
(preferencias locais de tela), `_autosave-*`, `~*.lck`, e os intermediarios do Freerouting
(`*.dsn`, `*.ses`, `freerouting*.log`). O `rotear.py` grava esses intermediarios numa pasta
temporaria (com `--manter-intermediarios` eles ficam); as linhas do `.gitignore` cobrem quem rodar
o Freerouting a mao.
