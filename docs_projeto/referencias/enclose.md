---
title: Enclose (enclosedev) — bancada desktop de CAD por codigo com Claude
source: https://github.com/enclosedev/enclose
type: referencia
status: rascunho
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, 3d, cad, build123d, mecanica, pcb, tscircuit, claude-code, tema/tooling]
---

# Enclose (enclosedev)

Nota de metodo: repo clonado raso (`--depth 1`, commit `3a43225` de 2026-10-15) e lido em
arquivo — `README`, `NOTICE.md`, `docs/`, `kit/` e um exemplo. Nada foi executado. Trechos
marcados como inferencia sao leitura nossa, nao do autor.

## O que e

App desktop (Electron + React + three.js) para projeto de CAD **escrito em codigo**. O
usuario ve o modelo em 3D, clica na peca, diz o que mudar, e o Claude Code (via Agent SDK,
na pasta do projeto) edita o `model.py` e reconstroi. Tambem fala com Codex e Grok.
Site: https://enclose.dev

- **So macOS 13+** (arm64 e x64). Exige Claude Code instalado e logado; Node.js para placas.
- Abre STEP, STL e OBJ; modela em **build123d**; placa em **tscircuit** (nao KiCad).
- AGPL-3.0 com permissao adicional (secao 7) para linkar o Claude Agent SDK. O nome e a
  marca "Enclose" nao vem com a licenca.
- 112 estrelas, 8 forks, criado 2026-10-10, push diario, um autor. Fonte:
  https://api.github.com/repos/enclosedev/enclose
- Telemetria para PostHog no app instalado (eventos de uso, sem conta; desliga nas
  configuracoes). Rodando do checkout nao envia nada. Fonte: `docs/usage-data.md`

## Estrutura do repo

| Pasta | O que tem |
|---|---|
| `apps/desktop/` | o app (Electron em `electron/`, UI em `src/`) |
| `kit/` | o que e copiado para cada projeto: `enclose.py`, `screws.py`, `board.mjs`, `board-check.mjs` e as instrucoes que o agente le (`assembly.md`, `pcb.md`, `tools.md`) |
| `examples/` | relogio de mesa, braco SO-101 (STEP do fabricante), luminaria, banqueta |
| `docs/` | manual de uso e de desenvolvimento |

**O valor para nos esta no `kit/`**, nao no app: e o contrato entre agente e modelo.

## Contrato de projeto (como um projeto e organizado)

Um projeto e uma pasta com git (o app commita depois de cada turno, mensagem gerada pelo
modelo mais barato; um ramo por conversa `version/...`):

```
model.py            build123d; monta as pecas e entrega ao exportador
enclose.py          exportador (copiado do kit, nao editar)
screws.py           biblioteca de fixadores (copiado do kit, nao editar)
enclose.json        { "model": "build/enclose.model.json", "build": "python3 model.py" }
build/              malha .glb + arestas + STEP por peca + manifesto (fora do git)
pcb/                placa tscircuit e o build dela
assembly/           guias de montagem em JSON (so ids de peca, sem geometria)
tools/              controles JS do modelo (slider, joystick) — animacao sem simulador
reference.py        cena de referencia de tamanho conhecido (mesa, sala, pessoa)
```

API do exportador (`kit/enclose.py`), em mm com Z para cima:

- `Model(title, reference="table"|"room")` — `group(label, shell=True)` marca o casco
  (o que se separa peca a peca na vista explodida); `part(id, shape, label, group, color,
  finish="metal"|"glass", explode=(x,y,z))`; `write()`.
- **Cada peca e construida na posicao montada.** Nao ha transformacao de montagem a parte.
- `keepout(id, label, low, high)` — caixa de espaco para o que nao e modelado (plugue,
  raio de curvatura de cabo). E desenhada e listada com as pecas, e o app registra colisao
  (`hits`).
- `read_step(...)` / `read_files(...)` — importa STEP (uma peca por componente da
  montagem) ou STL/OBJ (malha fechada vira solido; `mesh=True` fica fora do STEP).
- `read_board(name)` — placa e componentes 3D do fabricante, no referencial da placa
  (centro na origem, meio da espessura em Z=0, lado dos componentes para +Z). Um `Pos *
  Rot` posiciona tudo como uma peca so.
- Variavel de ambiente de rascunho: enquanto o agente salva o `model.py`, o app reconstroi
  numa pasta propria sem STEP para mostrar o progresso.

## Fixadores (`kit/screws.py`) — o que vale levar

Biblioteca metrica com rosca modelada e os furos que casam com cada parafuso. Origem do
parafuso = onde a cabeca assenta (embaixo da cabeca; topo da escareada). O mesmo
posicionamento serve para o parafuso e para todos os cortes dele.

| Cabeca | Norma | Faixa |
|---|---|---|
| Allen cilindrica (`socket`) | ISO 4762 | M1.6 a M12 |
| Abaulada (`button`) | ISO 7380 | M3 a M12 |
| Escareada (`countersunk`) | ISO 10642 | M3 a M12 |
| Panela Phillips (`pan`) | ISO 7045 | M1.6 a M8 |
| Sextavada (`hex`) | ISO 4017 | M1.6 a M12 |
| Porca sextavada | ISO 4032 | M1.6 a M12 |
| Arruela lisa | ISO 7089 | M1.6 a M12 |

Tabela do docstring (mm): rosca / cabeca allen / passagem / furo para rosca

```
M1.6  1.6  3.0  1.8  1.25      M4   4   7   4.5  3.3
M2    2    3.8  2.4  1.6       M5   5   8.5 5.5  4.2
M2.5  2.5  4.5  2.9  2.05      M6   6   10  6.6  5
M3    3    5.5  3.4  2.5       M8   8   13  9    6.8
                               M10  10  16  11   8.5
                               M12  12  18  13.5 10.2
```

Regras praticas do docstring:

- **Em plastico, o parafuso segura por cerca de 2x o diametro de rosca engajada**, e quer
  em volta do furo tanto plastico quanto o proprio diametro: pilar de **2,5 a 3x o
  diametro** do parafuso.
- M3 para o que fica na mao ou na mesa; M2/M2.5 para pequeno e fino (a maioria das
  placas); M4+ para grande ou com carga. **O furo de montagem da placa decide**: use o
  parafuso cuja passagem e a mais proxima do furo.
- So comprimentos comerciais; `lengths("M3")` lista. Comprimento conta de baixo da
  cabeca, ou do topo na escareada (que precisa de rosca sob a cabeca: minimo
  `0,62*d + 5*passo`).
- Cabeca embutida: desce o parafuso `head_height` e corta `hole(sunk=head_height)`.
- Porca: `nut.pocket()` e o alojamento que impede de girar.
- O nome da peca carrega a medida ("Parafusos da tampa, M3 x 8"); pedido de "maior" sem
  numero pergunta qual.
- Arestas de rosca a menos de 1 mm uma da outra saem do desenho (viram faixa preta).

## Guia de montagem (`kit/assembly.md`) — metodo

O guia e JSON com passos e ids de peca; o app desenha. O metodo vale fora do app, como
**prova de montabilidade** de qualquer gabinete:

1. Conhecer as pecas (caixa `min`/`max` de cada) e ler o script: ele diz o que a caixa nao
   diz — furo e parafuso, aba e fenda, interferencia, rosca.
2. Para cada peca: o que ela toca e como se une (prensa, parafuso, cola, gancho, apoio).
   **Grupo do modelo nao e unidade de montagem.**
3. Achar sub-montagens: peca que so entra enquanto o conjunto ainda esta fora.
4. Achar a base: a peca em que o resto se apoia (a que fica na mesa).
5. Ordenar pelo que bloqueia o que: o que fica preso dentro entra antes do que fecha; o
   que e parafusado entra antes do que cobre o parafuso; empate → grande para pequeno.
6. Testar cada passo como a mao faria: existe linha reta livre para a peca entrar
   (`from`)? O que a segura ate o proximo passo?
7. **Procurar o impossivel**: peca sem caminho de entrada, cabeca de parafuso coberta,
   peca que nada segura. Nao escrever passo impossivel como se fosse possivel; relatar.

Um passo = um tipo de peca, de um jeito. 25 pecas raramente dao menos de 15 passos.

## Placa (`kit/pcb.md`, `board.mjs`, `board-check.mjs`)

- Placa em tscircuit (React/TSX) em `pcb/<nome>.circuit.tsx`; `board.json` com
  `finished: false` enquanto e esboco (contorno, furos de fixacao, pecas que definem a
  forma) para o gabinete crescer em volta.
- Build gera `.step`, `.glb`, Gerbers com BOM e CPL no formato da JLCPCB, PNGs de PCB,
  esquematico e 3D para o agente conferir.
- `board-check.mjs` (Node 18+, internet): cada peca com codigo JLCPCB **em estoque**
  (consulta `jlcsearch.tscircuit.com`); rotacao do CPL casa o footprint da EasyEDA com os
  pads, pino a pino (tolerancia 0,2 mm); toda peca com modelo 3D; zip de Gerber igual ao
  arquivo atual; aviso de custo para THT e lado de baixo. Sai 0 so se os quatro passam.

### tscircuit x familia `pcb-*` (KiCad 10)

| | tscircuit (Enclose) | `pcb-*` (template) |
|---|---|---|
| Fonte da placa | TSX, roteamento automatico | `.kicad_sch`/`.kicad_pcb`, layout guiado |
| Verificacao | `board-check` contra estoque e footprint JLCPCB | ERC/DRC pelo `kicad-cli`, portoes e revisao humana |
| 3D para o gabinete | STEP + modelos do fabricante posicionados | `kicad-cli pcb export step` |
| Maturidade | jovem, depende de servico online | ferramenta de mercado, offline |

Leitura (inferencia): o tscircuit encurta o esboco de placa para dimensionar gabinete;
para placa que vai para producao, a familia `pcb-*` continua sendo o caminho. A checagem
de rotacao do CPL contra o footprint da JLCPCB e uma ideia que falta no `pcb-fabricacao`
(hoje e conferencia manual).

## O que o app da ao agente (ideias de fluxo)

Ferramentas proprias alem das do Claude Code: screenshot da vista como o usuario ve, lista
de pecas com grupo e caixa, selecao atual, estado dos `tools/` e um "dedo" para mexer nos
controles e testar antes de dizer que terminou, e a ferramenta que grava o guia de
montagem validado contra o modelo. O agente e instruido a nunca editar o proprio app nem o
`kit/` do projeto.

## Riscos

1. **AGPL-3.0**: copiar `enclose.py`/`screws.py` para um projeto que e distribuido ou
   servido leva a obrigacao de fonte. Nao vendorizar no template (decisao 2026-10-15).
2. Dependencia de servico online no check de placa (tscircuit e EasyEDA, este com
   user-agent de navegador para nao ser recusado).
3. Projeto de cinco dias, um mantenedor, API muda a cada commit.
4. Backup opcional cria repo privado `enclose-<projeto>` no GitHub do usuario sem
   perguntar a cada projeto.

## Veredito

- **App: estudo, nao adotado.** Nao roda no Windows deste PC.
- **Absorvido na skill `cad-parametrico`** (so fatos de norma e metodo, reescritos): regras
  de parafuso em plastico, tabela ISO estendida, keepout de conector e cabo, peca na
  posicao montada, prova de montabilidade. Ver `.claude/skills/cad-parametrico/`.
- **tscircuit: alternativa registrada, nao adotada.** A familia `pcb-*` segue como caminho.
