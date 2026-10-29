---
title: Statusline com a issue da sessao
type: convencao
status: aprovado
created: 2026-10-18
updated: 2026-10-29
project: template_projetos
tags: [convencao, statusline, claude-code, issue, board, tema/tooling]
---

# Statusline com a issue da sessao

A barra de baixo do Claude Code mostra, em toda sessao deste repositorio e dos derivados:

```
#42 Login com TOTP · In progress │ F5 · rec. sonnet ⚠ │ Opus 5.5 · high │ ctx 34% │ tok 4.6M (sub 870k)
```

| Segmento | Fonte | Cor |
|---|---|---|
| `#42 Titulo` | issue registrada nesta sessao; titulo do GitHub, cortado em 30 caracteres | numero em negrito |
| status | campo Status do primeiro Project da issue; sem Project, `open`/`closed` | Backlog cinza, Ready azul, In progress amarelo, In review magenta, Done verde |
| `F5 · rec. sonnet ⚠` | fase da `/issue` e modelo recomendado, gravados por `issue.js fase`; secao "Fase da /issue" | `⚠` amarelo |
| modelo · esforco | `model.display_name` e `effort.level` do payload, valor ao vivo (inclui `/effort`) | — |
| `ctx` | `context_window.used_percentage`; `ctx —` no comeco da sessao | amarelo acima de 60%, vermelho acima de 80% |
| `tok` | tokens da sessao inteira (principal + subagentes + advisor) e, entre parenteses, a parte dos subagentes; `~` enquanto a leitura nao chegou ao fim | cinza |

Sem issue registrada, a linha comeca na fase (se houver) ou no modelo. O contexto aparece porque e ele, nao a resposta, que
define o custo ([[AGENTES]] secao 1). Pelo mesmo motivo o custo sai em tokens, nao em dolar.

## Arquivos

Tudo em `.claude/statusline/`, que se copia inteira para um projeto derivado:

| Caminho | Papel |
|---|---|
| `statusline.js` | Entrada do `statusLine`: le o payload no stdin e imprime a linha |
| `hook-capturar-issue.js` | Hook `UserPromptSubmit`: prompt que comeca com `/issue <ref>` liga a sessao a issue |
| `issue.js` | CLI `definir <ref>`, `mostrar` e `limpar` (skill `/issue`, passo 1), `mover "<Status>"` (F5.1 e F8, passo 7) e `fase [F1..F8]` |
| `atualizar-board.js` | Processo destacado que consulta o `gh` e grava o cache |
| `lib/` | `estado` (caminhos e arquivos), `referencia` (interpretar a ref), `board` (cache e `gh`), `rede` (chave `HALCYON_STATUSLINE_OFFLINE`), `tokens` (soma dos transcripts), `segmentos` (formatar), `registro` (ligar sessao a issue), `mover` (Status no board), `fase` (fase e modelo recomendado) |
| `testes/statusline.test.js` | Testes das partes puras |
| `testes/fase.test.js` | Testes da fase: estado, segmento, aviso, CLI `fase` e barra com estado corrompido |

Registro em `.claude/settings.json`: a chave `statusLine` (com `refreshInterval: 30`) e a segunda
entrada do `UserPromptSubmit`.

## Como a sessao sabe a issue

Duas portas gravam a mesma coisa, `~/.claude/halcyon-statusline/sessoes/<session_id>.json`:

1. **O hook**, quando o prompt comeca com `/issue 42`, `/issue owner/repo#42` ou `/issue <URL>`.
   Recebe `session_id` no payload.
2. **A skill `/issue`**, no passo 1, roda `node .claude/statusline/issue.js definir <ref>`. Cobre a
   issue que chegou por texto ("pega a issue 42"). A CLI le a sessao de `CLAUDE_CODE_SESSION_ID`,
   que o Claude Code poe no ambiente do Bash. Rode sempre **na sessao principal**: num subagente,
   a variavel pode nao ser a da sessao que mostra a barra.

Numero sem repo usa o `remote origin` do checkout. Issue que mora num repo de planejamento
diferente ([[BOARD]] secao 1) vai como `owner/repo#42` ou URL.

O estado fica **sob o home, nao no repo**. Hook, CLI e statusline rodam com `cwd` diferentes
(checkout principal x worktree), e o `session_id` ja e unico. Por isso nada entra no `.gitignore`.

**Ciclo:** a issue vale para a sessao. `/clear` ou sessao nova comecam sem issue, como manda a regra
de uma issue por sessao. `--resume` recupera. Arquivo de sessao, de cache, de tokens ou de fase sem uso
ha mais de 7 dias e apagado no proximo `definir` ou `fase <F1..F8>`.

## Fase da /issue e modelo recomendado

A skill `/issue` anda por fases F1..F8, e cada fase tem um modelo recomendado. A barra mostra em que
fase a sessao esta e avisa quando o modelo ativo nao e o recomendado.

**Como a skill grava.** Ao entrar numa fase, no **mesmo Bash** do primeiro comando dela e na sessao
principal, com `;` e nunca `&&` (falha da barra nao trava a issue): `issue.js fase F5 --modelo sonnet; git
branch --show-current`. O `--modelo` e o recomendado para a **sessao** (`sonnet` em XS a M, `opus` em L e XL),
igual em todas as fases; a F1 grava sem modelo, porque o tamanho ainda nao existe. Fase sem Bash (F3, F4)
nao grava. Com `⚠`, a skill faz a troca por `/clear` e handoff ([[AGENTES]] secao 3), nao por `/model`.

`node .claude/statusline/issue.js fase <F1..F8> [--modelo <nome>]` grava a fase da sessao
(`CLAUDE_CODE_SESSION_ID`) e o modelo recomendado, texto livre curto (`opus`, `sonnet`, `haiku`):

| Comando | Efeito |
|---|---|
| `fase F5 --modelo sonnet` | grava; imprime `statusline: F5 · rec. sonnet` |
| `fase F3` | grava so a fase; imprime `statusline: F3`. Cada gravacao substitui a anterior, inclusive o modelo |
| `fase` | imprime a fase atual, ou `statusline: nenhuma fase nesta sessao` |
| `fase --limpar` | remove a fase |
| `limpar` | remove a issue **e** a fase |

Fase fora de F1..F8 (`F0`, `F9`, `f5`, `5`) ou `--modelo` sem valor sai com codigo 1 e imprime o uso.
Sem `CLAUDE_CODE_SESSION_ID`, erro como nos outros comandos. O modelo vira uma linha de ate 20
caracteres, sem caractere de controle.

**Segmento**, entre a issue e o modelo, separado pelo mesmo `│`:

| Estado | Segmento |
|---|---|
| fase e modelo recomendado | `F5 · rec. sonnet` |
| ... e o modelo ativo nao contem o recomendado | `F5 · rec. sonnet ⚠` (`⚠` em amarelo) |
| fase sem modelo recomendado | `F3` |
| sem fase | nenhum; a linha sai como antes |

A comparacao e sem caixa, sobre `model.display_name` do payload (ou `model.id`, quando nao ha nome):
`Opus 5.5` contem `opus`, entao nao avisa. Payload sem modelo nenhum tambem avisa.

**Independe da issue.** A fase fica em `~/.claude/halcyon-statusline/fases/<session_id>.json`, arquivo
proprio, entao aparece mesmo quando a tarefa e texto solto e nenhuma issue foi registrada. Estado
ilegivel ou fora do formato (JSON quebrado, fase invalida) vale como "sem fase": a barra continua sem
lancar excecao e sem rede.

## Por que o status nao trava a barra

O `gh issue view` leva cerca de 1 s. A statusline tem debounce de 300 ms e e cancelada quando outro
evento chega, entao **ela nunca chama o `gh`**:

1. Le `~/.claude/halcyon-statusline/cache/<owner>__<repo>__<n>.json`.
2. Se o cache tem mais de 60 s, dispara `atualizar-board.js` destacado (`detached`, `windowsHide`,
   sem stdio) e imprime o que ja tem. Antes do primeiro cache, o status sai como `…`.
3. Uma trava `.lock` de 30 s impede que uma rajada de eventos abra varios `gh`.
4. O atualizador usa `GH_NO_UPDATE_NOTIFIER=1`, `GH_PROMPT_DISABLED=1` e timeout de 10 s.

**Token sem escopo de Project:** o `gh` recusa o pedido com `projectItems`, entao o atualizador
tenta de novo so com `state,title` e mostra `open`/`closed`.

**Falha do `gh`** (sem rede, token vencido, issue inexistente): fica o ultimo valor bom com `?` ao
lado. Sem valor nenhum, so `?`. A tentativa seguinte respeita os 60 s do cache.

Mais de um Project na issue: vale o primeiro que tiver Status.

## Tokens da sessao inteira

O payload da statusline so traz a sessao principal (`context_window.total_*`), e o `usage` de topo de
cada resposta **nao conta o advisor**: ele so aparece em `usage.iterations`, com `type: advisor_message`.
Por isso o numero sai dos transcripts:

- principal: `transcript_path` do payload;
- subagentes: `<pasta do transcript>/<session_id>/subagents/**/*.jsonl`, inclusive `workflows/<run>/`.

Regras da soma:

- Soma **todos** os tipos: entrada, criacao de cache, leitura de cache e saida. A leitura de cache
  domina o total e custa cerca de 0,1x a entrada, mas e ela que mede o contexto relido.
- Resposta com `usage.iterations` soma as iteracoes, advisor incluido. Sem iteracoes, usa o topo.
- Uma resposta em streaming grava varias linhas com o mesmo `message.id`: vale a ultima, sem somar duas vezes.
- Tokens de modelos diferentes entram no mesmo total. 1M de Haiku nao custa o mesmo que 1M de Opus.

**Leitura incremental.** O estado fica em `~/.claude/halcyon-statusline/tokens/<session_id>.json`, com o
offset, o total e a ultima mensagem de cada arquivo. Cada execucao le no maximo 4 MB, somando todos os
arquivos. Uma sessao longa retomada fecha a conta em poucas execucoes e mostra `~` ate la. Linha maior
que 4 MB (saida de ferramenta gigante) e pulada: linha de `usage` nunca e desse tamanho. Medido em
2026-10-18: 64 ms para ler 2,8 MB do zero e 7 a 10 ms nas execucoes seguintes.

## Mover a issue no board

`issue.js mover "<Status>" [ref] [--conferir]` muda o campo Status do primeiro Project da issue que tenha esse
campo, o mesmo que a barra mostra. Sem `ref`, vale a issue da sessao. A skill `/issue` chama no inicio da
implementacao (In progress) e depois do merge (In review ou Done).

- **Ids pelo item, nao pelo `BOARD.md`.** Uma consulta GraphQL traz item, Project, campo e opcoes, e o
  `gh project item-edit` aplica. Funciona com o `BOARD.md` ainda vazio.
- **Ingles e portugues.** `In progress`, `In review` e `Done` acham `Em andamento`, `Em revisao` e `Feito`,
  sem caixa e sem acento. O board do TelemeVisus usa os nomes em portugues (conferido em 2026-10-18).
- **`--conferir`** espera 10 s, rele e reaplica uma vez. O workflow "Pull request merged → In review" roda
  em segundo plano e pode passar por cima do Done.
- **Saidas:**
  - 0 moveu;
  - 3 nada a mover (issue fora de Project, ou board sem a opcao, e a mensagem lista as que existem);
  - 1 erro do `gh`, em geral falta de escopo: `gh auth refresh -s project`.
- Depois de mover, dispara a renovacao do cache, e a barra mostra o estado novo sem esperar 60 s.

## Comandos

```bash
node --test ".claude/statusline/testes/*.test.js"      # testes (Node 20+, sem package.json)
node .claude/statusline/issue.js mostrar               # sessao e cache desta sessao
node .claude/statusline/issue.js limpar                # tira a issue e a fase da barra
node .claude/statusline/issue.js fase F5 --modelo sonnet   # fase e modelo recomendado (sem argumento mostra; --limpar remove)
node .claude/statusline/issue.js mover "In review" --conferir   # move a issue da sessao no board
echo '{"model":{"display_name":"Opus 5.5"},"effort":{"level":"high"}}' | node .claude/statusline/statusline.js
```

`HALCYON_STATUSLINE_DIR` troca a pasta de estado. Os testes usam isso para nao tocar o home.

`HALCYON_STATUSLINE_OFFLINE=1` desliga toda chamada ao `gh`: `disparar` nao abre o atualizador e
`consultar` e `mover` falham na hora. Os tres arquivos de teste a definem, para que registrar uma
issue sem cache nunca consulte o GitHub. Qualquer outro valor mantem a rede ligada.

## Desligar ou trocar

O `settings.json` do projeto **vence a statusline pessoal** do `~/.claude/settings.json`. Para usar
a sua num projeto derivado, defina `statusLine` no `.claude/settings.local.json`, que vence o do
projeto e fica fora do git. A barra so aparece depois de aceitar o dialogo de confianca da pasta.

Validado em 2026-10-18 no Claude Code 2.1.303 (Windows, Git Bash): `$CLAUDE_PROJECT_DIR` expande no
comando, o `cwd` e a raiz do projeto, e `session_id` do payload e `CLAUDE_CODE_SESSION_ID` coincidem.
Schema do payload: <https://code.claude.com/docs/en/statusline>.
