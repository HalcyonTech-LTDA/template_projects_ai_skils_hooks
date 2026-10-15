---
name: trilha
description: Planeja e controla uma frente de trabalho no GitHub — marcos de entrega com prazo e progresso, issues em sequencia, dependencias nativas (blocked by), campos e views do Project, relatorio de progresso e checagem de deriva. Use quando o usuario pedir /trilha, "quebra isso em issues", "organiza no board", "cria os marcos", "monta a sequencia", "como esta o marco", "o que esta bloqueado" ou "planeja essa frente". A execucao de cada issue e da skill /issue.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, Agent, AskUserQuestion
version: 2.0
---

# /trilha — marcos, sequencia, bloqueios e progresso no GitHub

Esta skill **planeja, organiza e mede**; ela nao implementa. Cada issue criada aqui e depois conduzida pela
`/issue`. Se o projeto tiver `docs_projeto/BOARD.md`, os IDs e convencoes de la vencem este roteiro.

O objetivo e responder a qualquer momento, sem abrir issue por issue:
1. **Em que marco estamos e quanto falta?** (progresso ponderado e prazo)
2. **Qual a proxima issue?** (sequencia derivada das dependencias)
3. **O que esta parado e por que?** (bloqueio interno x externo)
4. **O board diz a verdade?** (checagem de deriva)

## 1. Modelo

Todo trabalho e **issue** do repo. Nada de draft item, nota de tarefa ou item solto no Project: draft nao
tem tipo, milestone nem dependencia, e o que nao e issue nao entra no fluxo da `/issue`.

| Camada | O que e | Mecanismo do GitHub | Mede |
|---|---|---|---|
| **Plano** | A fonte da verdade da frente | `docs_projeto/.../Roadmap/<Nome>.md` + manifesto `<Nome>.yml` | — |
| **Trilha** | A frente de trabalho, prefixo de 2-3 letras (`SU`, `EM`) | **issue-epico** (pai) + opcao no campo `Trilha` | % de sub-issues fechadas |
| **Marco** | Um estado entregavel, com criterio de saida e prazo opcional | **Milestone** do repo | % de issues fechadas, prazo |
| **Issue** | Uma entrega com prova propria | **sub-issue** do epico, no milestone do seu marco | criterio de pronto |
| **Dependencia** | "esta so comeca quando aquela fechar" | relacao nativa **blocked by** | `is:blocked` |
| **Board** | Vista. Nunca e a fonte de nada | GitHub Project (ProjectV2) | views e Insights |

Regras de forma:
- **Um repositorio de planejamento por projeto.** Milestone nao atravessa repositorio; se o trabalho toca
  varios repos (app, firmware, bootloader), as issues moram todas no repo de planejamento e o corpo diz onde o
  codigo muda.
- **Epico e marco sao eixos diferentes.** O epico agrupa o *assunto* (uma trilha); o milestone agrupa o
  *momento de entrega*. Um marco pode juntar issues de duas trilhas; uma trilha atravessa varios marcos.
- **Um nivel de sub-issue.** Epico -> issues. So uma issue XL que se divide em pecas com prova propria ganha
  sub-issues (segundo nivel); nunca use sub-issue para imitar marco.
- Tipo da issue: em repo de **organizacao**, use Issue Types (`Epico`, `Tarefa`, `Bug`, `Decisao`). Em repo de
  conta pessoal Issue Types nao existem (`repository.issueTypes` volta `null`): use labels `tipo:epico`,
  `tipo:tarefa`, `tipo:bug`, `tipo:decisao`.

## 2. Nomes e IDs

- Issue: `<PREFIXO>-<NN> · <entrega em uma frase>` — ex.: `SU-18 · Um CRC e uma identificacao por parte`.
- Epico: `<PREFIXO> · <nome da frente>` — ex.: `SU · Separacao legal do UMA 1.4`.
- Milestone: `<PREFIXO> M<n> · <estado alcancado>` — ex.: `SU M3 · Memoria e integridade separadas`.
  Se o marco juntar trilhas, use o nome da entrega: `Entrega campo 2026-11 · App de campo no ar`.
- Numeracao continua e nunca reaproveitada; issue cancelada fecha como `not planned` e continua no manifesto
  com `cancelada: true`.
- IDs reservados no inicio podem colidir com outra sessao em paralelo: confira antes de criar e renumere pelo
  alvo nominal, nunca por regex.

## 3. Marcos de entrega

Descricao do milestone, sempre neste formato:

```
Entrega: <o que o dono/cliente recebe quando este marco fecha, em uma frase>
Sai quando:
- <criterio verificavel> (<PREFIXO>-xx)
- <criterio verificavel> (<PREFIXO>-yy)
Fora do marco: <o que alguem poderia esperar aqui e nao esta>
```

- Toda issue do marco aparece no "Sai quando"; criterio sem issue nao existe.
- **Prazo (`due_on`)**: so quando ha compromisso real. Prazo inventado vira ruido; marco sem prazo e ordenado
  pela sequencia.
- 3 a 5 marcos por trilha; 4 a 8 issues por marco. Mais que isso, quebre.
- **Uma issue nunca depende de outra num marco posterior ao seu.** Se depender, ou a dependencia sobe de marco
  ou a issue desce.
- Quem fecha o milestone e o dono, depois de conferir o "Sai quando" item a item.

## 4. Corpo da issue

Issue criada pela tela usa os formularios de `.github/ISSUE_TEMPLATE/` (`tarefa.yml`, `epico.yml`, `bug.yml`),
que geram as mesmas secoes. Issue criada pelo agente usa `--body-file` com este molde:

```markdown
## Contexto
<por que existe; estado atual citado como `arquivo:linha` contra um commit fixo>

## O que fazer
- <entregavel>

## Criterio de pronto
- [ ] <prova observavel: comparacao, medicao, teste, leitura em ambiente real — nunca "implementado">

## Fora do escopo
- <o que fica para outra issue>

## Fontes
- `arquivo:linha` (`<branch>@<commit>`) · <norma, documento, referencia>

---
Quem executa: **<agente | dono | externo>** · Repo do codigo: `<repo>` · Base: `<branch>@<commit>` · Plano: `docs_projeto/.../<Nome>.md`
```

- **Dependencias nao vao no corpo**: a fonte e a relacao nativa (aba Relationships), gerada pelo manifesto.
  Texto no corpo deriva e ninguem confere.
- Separe "visto em host/mock" de "visto no ambiente real"; verde contra mock nao fecha issue que pede o real.
- Escopo novo descoberto no meio vira **issue nova**, nao adendo.
- Envie corpo por `--body-file` (UTF-8), nunca por string com escapes.

## 5. Tamanho e prioridade

| Tamanho | Peso | Sinal |
|---|---|---|
| XS | 1 | Mudanca localizada, sem decisao de desenho |
| S | 2 | Um modulo, padrao existente, ate ~1 dia |
| M | 3 | Varios arquivos, alguma decisao de desenho, contrato tocado de leve |
| L | 5 | Atravessa camadas ou repositorios, muda contrato, esquema ou migracao |
| XL | 8 | Varias fatias dependentes, seguranca no centro, ou prova em ambiente real |

- Na duvida, o maior. Codigo sensivel sobe para pelo menos M. XL e sinal para quebrar.
- O **peso** mede progresso (secao 9): fechar 1 XL anda mais que fechar 4 XS.
- Grave no campo `Size` do Project e na label `size/X` (a `/issue` le a label).
- **Priority**: P0 bloqueia entrega agora; P1 caminho critico; P2 o resto. Prioridade **nao** e ordem.

## 6. Sequencia

- A ordem **sai do grafo de dependencias**, nao da cabeca: ordenacao topologica, desempatando por marco, depois
  prioridade, depois ID. O resultado vai para o campo numerico `Ordem` (de 10 em 10, para caber insercao).
- **Um unico campo `Ordem` para o Project inteiro.** Cada issue pertence a uma trilha, entao os numeros nao se
  misturam: a view filtra pela trilha. Nunca crie `Etapa <trilha>`/`Ordem <trilha>` por trilha — o Project
  tem teto de **50 campos** contando os nativos, e campos por trilha esgotam esse teto.
- **Caminho critico**: a corrente mais pesada (soma dos pesos) de issues abertas ligadas por dependencia. E ele
  que diz se o prazo do marco cabe.
- Issue sem dependencia entre si pode andar em paralelo (worktrees). A sequencia mostra isso: mesma "onda"
  topologica.

## 7. Bloqueio — interno x externo

| Tipo | Exemplo | Mecanismo |
|---|---|---|
| **Interno** | SU-19 so comeca quando SU-16 fechar | relacao nativa **blocked by** (`addBlockedBy`); aparece como bloqueada no repo e no Project; busca `is:blocked`, `blocked-by:`, `is:blocking` |
| **Externo** | espera laboratorio, placa, compra, resposta de cliente, decisao do dono | campo de texto `Bloqueio externo` (quem/o que e desde quando) + label `bloqueado` |

- Bloqueio interno nunca leva label: a relacao ja diz, e label manual deriva quando o bloqueador fecha.
- Bloqueio externo sempre diz **quem** destrava e **desde quando**: `Laboratorio (resposta a carta) desde 2026-10-12`.
- Ate 50 relacoes de cada tipo por issue. Confira que o grafo nao tem ciclo.

## 8. Status

| Status | Significa | Quem move |
|---|---|---|
| **Backlog** | planejada; algum bloqueador aberto | manifesto/checagem |
| **Ready** | todos os bloqueadores fechados; pode ser pega | checagem sugere, agente aplica |
| **In progress** | alguem trabalhando agora (limite WIP do projeto, padrao 3) | quem pega |
| **In review** | feita e commitada; espera prova em ambiente real, revisao ou decisao do dono | agente, com comentario de prova |
| **Done** | aceita | **so o dono** (fecha a issue) |

- Mover para In review vem com comentario: comando, saida, commit/PR e o que **nao** foi provado.
- Fechar aceitando risco e valido; o comentario registra o que ficou sem prova.
- O agente nunca fecha issue, nunca move para Done e nunca faz merge sem pedido explicito.
- PR usa `Refs #N`. `Closes #N` so quando o merge **e** o aceite (sem prova em ambiente real pendente).

### Workflows nativos do Project (configure uma vez)

| Workflow | Ajuste |
|---|---|
| Auto-add to project | ligado, filtro `is:issue` no repo de planejamento |
| Auto-add sub-issues to project | ligado |
| Item added to project | Status = Backlog |
| Item closed | Status = Done |
| Auto-close issue | ligado (Done fecha a issue) |
| Pull request linked to issue | Status = In progress |
| **Pull request merged** | **In review**, nao Done — senao o merge pula a prova e o aceite do dono |
| Item reopened | Status = In progress |

## 9. Progresso

Tres numeros por marco, sempre juntos:
- **Contagem**: fechadas / total (o que o milestone mostra nativamente).
- **Ponderado**: soma dos pesos fechados / soma dos pesos (secao 5). E o numero que se reporta.
- **Prazo**: dias ate o `due_on` x peso restante no caminho critico.

Onde aparece:
- Milestone (barra nativa) e campo `Sub-issues progress` do epico no Project.
- **Insights** do Project: grafico burn-up por milestone (historico, filtro `milestone:"..."`).
- **Status update do Project** (`createProjectV2StatusUpdate`: `ON_TRACK`, `AT_RISK`, `OFF_TRACK`,
  `COMPLETE`, com `targetDate`) postado quando um marco fecha, quando o caminho critico nao cabe no prazo, ou
  quando o dono pede. Corpo: o relatorio abaixo, curto.

Relatorio (`/trilha status <PREFIXO>`):

```
SU · Separacao legal do UMA 1.4 — 14/22 issues, 61% ponderado
M3 Memoria e integridade separadas — 4/6 (70%), prazo 2026-11-15 (31 d), caminho critico 13 de peso
  In review: SU-19 (XL) espera bancada
  Proximas prontas: SU-20 (M, P1)
  Bloqueio externo: SU-02 — Laboratorio (resposta a carta) desde 2026-10-12
Deriva: 2 achados (ver /trilha check)
```

## 10. Campos do Project (conjunto fixo)

| Campo | Tipo | Valores |
|---|---|---|
| `Status` | single select | Backlog, Ready, In progress, In review, Done |
| `Priority` | single select | P0, P1, P2 |
| `Size` | single select | XS, S, M, L, XL |
| `Trilha` | single select | uma opcao por trilha (`SU · Separacao legal`) — e por ela que as views fatiam |
| `Ordem` | numero | gerado pela sequencia (secao 6) |
| `Bloqueio externo` | texto | so bloqueio externo |
| `Start date` / `Target date` | data | opcional; so issues com data real, para o Roadmap |
| nativos | — | Milestone, Parent issue, Sub-issues progress, Labels, Linked pull requests |

Campo novo exige motivo escrito no `BOARD.md`. Antes de criar, conte os campos (`fields{totalCount}`; teto 50).

## 11. Views (conjunto fixo, criado uma vez)

| # | View | Layout | Filtro / arranjo |
|---|---|---|---|
| 1 | **Sequencia** | tabela | `is:open`; agrupar por Milestone; ordenar por Ordem; fatiar (slice) por Trilha |
| 2 | **Quadro** | board | colunas por Status; fatiar por Trilha |
| 3 | **Marcos** | roadmap | marcadores de Milestone; datas Start/Target date |
| 4 | **Prontas** | tabela | `status:Ready`; ordenar por Priority, depois Ordem |
| 5 | **Bloqueadas** | tabela | `is:blocked` (internas); se o Project nao aceitar o filtro, use a busca de issues ou o check |
| 6 | **Externo** | tabela | `label:bloqueado`; coluna Bloqueio externo |
| 7 | **Espera o dono** | tabela | `status:"In review"`; coluna Linked pull requests |
| 8 | **Triagem** | tabela | `no:milestone` ou `no:Size` — issue que entrou sem passar pela trilha |

Views por trilha nao sao necessarias: o slice por `Trilha` faz esse papel. A API cria view e filtro, mas
**nao agrupa, ordena nem fatia**: isso se faz na tela uma vez, no Project-modelo (secao 13).

## 12. Manifesto e scripts

O plano tem um manifesto ao lado, `docs_projeto/.../Roadmap/<Nome>.yml`. O manifesto e o que o script le; o
`.md` e o que as pessoas leem. Os dois saem do mesmo planejamento e o check confere os dois contra o GitHub.

```yaml
trilha: SU
nome: Separacao legal do UMA 1.4
repo: OWNER/REPO
plano: docs_projeto/.../Separacao_Legal_Do_UMA_1_4.md
epico: 232                      # preenchido pelo sync
marcos:
  - id: M1
    titulo: Fronteira definida
    entrega: Fronteira legal/nao legal aprovada
    prazo: 2026-11-15           # opcional
    milestone: 5                # preenchido pelo sync
issues:
  - id: SU-01
    titulo: Caminho decidido
    marco: M1
    tamanho: S
    prioridade: P1
    depende_de: []
    quem: dono
    numero: 233                 # preenchido pelo sync
  - id: SU-02
    titulo: Consulta escrita ao laboratorio
    marco: M1
    tamanho: XS
    prioridade: P0
    depende_de: [SU-01]
    quem: dono
```

- **`trilha:sync <manifesto>`** — idempotente; acha cada coisa pelo ID no titulo antes de criar. Cria/atualiza
  epico, milestones, issues (sub-issues do epico), relacoes blocked by (adiciona e **remove** as que sairam),
  campos e `Ordem`. Escreve de volta no manifesto os numeros criados. `--dry-run` mostra o plano de mudancas;
  rode sempre antes e mostre ao dono.
- **`trilha:check [<PREFIXO>]`** — so leitura. Saida `0` sem deriva, `1` com deriva (tabela do que), `2` nao
  conseguiu checar (sem `gh`, sem escopo, sem rede) — "nao achei" e "nao olhei" sao fatos diferentes. Confere:
  - issue sem milestone, Size, Priority, Trilha ou pai;
  - dependencia do manifesto sem relacao nativa, ou relacao nativa fora do manifesto; ciclo;
  - dependencia apontando para marco posterior;
  - Backlog com todos os bloqueadores fechados (deveria ser Ready); Ready/In progress com bloqueador aberto;
  - issue aberta em Done, ou fechada fora de Done; In progress acima do WIP;
  - label `bloqueado` sem `Bloqueio externo` (ou o contrario);
  - milestone com prazo vencido e issue aberta; caminho critico maior que o prazo;
  - criterio do "Sai quando" sem issue, ou issue do marco fora do "Sai quando".
- **`trilha:status [<PREFIXO>]`** — o relatorio da secao 9.

Se o projeto ainda nao tiver os scripts, o primeiro uso da skill os cria em `scripts/trilha/` (Node ou Python,
o que o projeto ja usar), com teste do calculo de ordem, caminho critico e deteccao de ciclo.

## 13. Project-modelo

Campos, views, workflows e Insights se configuram **uma vez** num Project-modelo e se copiam:
`gh project copy <N> --source-owner <OWNER> --target-owner <OWNER> --title "<Projeto>"` (copia campos, views,
workflows e Insights; draft items so se pedir). Depois da copia: apontar o Auto-add para o repo novo e criar as
opcoes de `Trilha`. Os IDs do Project novo (campos, opcoes, views) vao para `docs_projeto/BOARD.md`.

## 14. Roteiro

1. **Ler** o pedido, os docs e o codigo (busca com `explorer`); referencia externa vai ao `researcher` e vira
   ficha em `docs_projeto/referencias/`. Planejar uma trilha conta como M ou maior: faca as perguntas da regra
   3 do hook (escopo, marcos e prazos, o que e externo, criterio de aceite, o que fica fora). Se o projeto nao
   tiver `docs_projeto/BOARD.md` preenchido nem `.github/ISSUE_TEMPLATE/`, copie-os do `template_projetos` e
   preencha o `BOARD.md` com o dono antes de criar qualquer issue.
2. **Escrever** o plano `.md` (contexto, fronteira, alternativas como advogado do diabo, marcos com "Entrega" e
   "Sai quando", tabela de issues, lacunas) e o manifesto `.yml`.
3. **Calcular** sequencia, ondas paralelas e caminho critico; conferir ciclo e dependencia para marco posterior.
4. **Mostrar ao dono** marcos, tabela de issues, grafo e `trilha:sync --dry-run` **antes de criar qualquer coisa
   no GitHub** — criar issue e publicar. Ajuste ate ele aprovar.
5. **Sincronizar** (`trilha:sync`), depois **checar** (`trilha:check`). O `item-list` tem consistencia eventual:
   se faltar item logo apos criar, espere e releia antes de concluir que falhou.
6. **Registrar** no `BOARD.md` o que for novo (opcao de Trilha, milestones, faixa de issues) e no plano o numero
   de cada issue.

## 15. Manutencao

- Issue muda de estado → a linha dela no plano ganha estado, prova e link da nota de evidencia. O plano e o
  historico; o board e o agora.
- Dependencia nova ou removida → muda no manifesto e roda `trilha:sync`; nunca so na tela do GitHub.
- Fim de marco: `trilha:status`, conferir o "Sai quando", status update do Project, e o dono fecha o milestone.
- Divergencia board x plano: o plano vence; corrija o board e diga o que estava errado.

## 16. Pegadinhas do `gh` com Projects

- O token precisa do escopo `project` (`gh auth refresh -s project`); o login padrao nao da.
- `--owner "@me"` funciona onde o login literal as vezes responde `unknown owner type`.
- `item-edit` de single select exige `--project-id`, `--field-id` e `--single-select-option-id` (id da opcao,
  nunca o nome); `item-list` nao exporta campo de texto: leia por GraphQL `fieldValueByName`.
- Com Auto-add ligado, `item-add` logo apos `issue create` pode responder `Content already exists`: procure por
  GraphQL `issue(number){projectItems}` antes.
- Criar view e REST (`POST users/<OWNER>/projectsV2/<N>/views`, ou `orgs/<ORG>/...`), com ids numericos dos
  campos de `gh api users/<OWNER>/projectsV2/<N>/fields`; campo se cria por GraphQL `createProjectV2Field`.
  JSON com acento vai por `--input arquivo.json`.
- Para ler varios itens, consulte por issue; `items(last:N)` segue a ordem manual e pode nao trazer os
  recem-criados.
- `--format json > arquivo` funciona; encadear em `| node` sai vazio em alguns shells. Use o scratchpad.
