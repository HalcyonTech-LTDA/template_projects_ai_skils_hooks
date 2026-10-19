---
name: worktree
description: Roda tarefas independentes em paralelo, cada uma num git worktree isolado com sua propria janela claude, e devolve o trabalho para a branch principal por rebase + fast-forward serializado. Use quando o usuario pedir /worktree, "cria um worktree", "roda essas tarefas em paralelo", "isola essa tarefa", "mescla o worktree" ou similar.
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
version: 1.0
---

# Worktrees de agentes

Varias tarefas independentes, uma janela `claude` por tarefa, sem colisao entre
sessoes. **So a arvore principal compila e roda o app**; worktrees escrevem codigo
e rodam teste unitario. Nenhum deles sobe dev server, entao nao existe disputa de porta.

## Comandos

Os scripts vivem dentro desta skill. Chame por caminho.

**Na arvore principal:**

```bash
node .claude/skills/worktree/scripts/new.mjs <nome> [--from <ref>]
node .claude/skills/worktree/scripts/clean.mjs                            # lista
node .claude/skills/worktree/scripts/clean.mjs --remove <nome> [--force]
node .claude/skills/worktree/scripts/clean.mjs --prune
```

**De dentro de um worktree** (na raiz dele):

```bash
node ../../skills/worktree/scripts/merge.mjs [--skip-tests]
```

Use `../../skills/...` aqui, e nao `.claude/skills/...`: de
`<raiz>/.claude/worktrees/<nome>/`, esse caminho resolve para a copia da skill na
**arvore principal**, o que funciona mesmo antes de a skill estar commitada. A
forma `.claude/skills/...` so funciona depois que o repositorio versionar a skill.

Se o repositorio tiver atalhos em `package.json`, prefira-os:
`npm run wt:new -- <nome>`, `npm run wt:list`, `npm run wt:merge`,
`npm run wt:clean -- --remove <nome>`.

## Quando usar

- O usuario tem **N tarefas que nao dependem entre si** e quer paraleliza-las.
- O usuario pede explicitamente worktree/isolamento para uma tarefa.

- A skill `/issue`, sempre: toda implementacao de issue roda num worktree e volta pelo
  merge do PR, nao pelo `merge.mjs` (secao 4.3 dela).

## Quando NAO usar

Os casos abaixo valem para tarefas avulsas. Na `/issue` o worktree e obrigatorio e ela
diz como tratar `package.json` e prova com o app rodando.

- Tarefa unica, ou tarefas que se encostam nos mesmos arquivos — o custo de
  merge supera o ganho.
- Tarefa que precisa **rodar o app** (dev server, build nativo, e2e). Isso e da
  arvore principal.
- Tarefa que altera `package.json` — o `node_modules` do worktree e um vinculo
  para a raiz, entao o teste rodaria contra as dependencias erradas. Faca na
  arvore principal.

## Fluxo

### Na arvore principal — abrir as frentes

```bash
node .claude/skills/worktree/scripts/new.mjs tarefa-a
node .claude/skills/worktree/scripts/new.mjs tarefa-b
```

Cria `.claude/worktrees/<nome>` na branch `wt/<nome>`, a partir da branch que a
arvore principal tem em checkout, e vincula `node_modules` quando existir.

Diga ao usuario para abrir **uma janela por tarefa**:

```bash
cd .claude/worktrees/tarefa-a && claude
```

**Nomes curtos.** O script recusa nomes que estourem o MAX_PATH do Windows, mas
o limite chega antes do que parece em repos com caminhos longos.

### Dentro do worktree — trabalhar e devolver

1. Trabalhe normalmente. Voce ja esta na branch certa; **nao de checkout da
   branch alvo** — o git proibe, e e essa proibicao que evita a colisao.
2. Commite. O merge exige a arvore do worktree limpa.
3. Rode o merge, da raiz do worktree:

```bash
node ../../skills/worktree/scripts/merge.mjs
```

O script, nessa ordem: pega a fila de merge (lock), revalida, rebaseia sobre a
branch alvo, roda os portoes, e faz `git merge --ff-only` **na arvore principal**.

### De volta na arvore principal — fechar

```bash
node .claude/skills/worktree/scripts/clean.mjs --remove tarefa-a
```

Worktree fechado e branch apagada. Worktree orfao nao some sozinho.

## Portoes

Detectados a partir do `package.json` do worktree:

| Situacao | O que roda |
|---|---|
| Script `typecheck` | `npm run typecheck` (obrigatorio) |
| Sem script, mas com `tsconfig.json` | `npx tsc --noEmit` (obrigatorio) |
| Script `test` | `npm test` (pulavel com `--skip-tests`) |
| Sem `package.json`, ou sem `node_modules` | nenhum portao, e isso e reportado |

Portao obrigatorio que falha aborta o merge: nada entra na branch alvo.

## Erros e o que fazer

| Mensagem | Causa | Acao |
|---|---|---|
| `rode este comando de dentro de um worktree` | `merge.mjs` chamado da raiz | `cd` para o worktree |
| `ha alteracoes nao commitadas neste worktree` | trabalho solto | commite antes |
| `a arvore principal tem edicao pendente nos arquivos que este merge reescreve` | colisao real | o usuario commita ou guarda essas edicoes na arvore principal |
| `rebase ... conflitou` | duas frentes no mesmo arquivo | resolva **dentro do worktree** com `git rebase <alvo>`, depois repita o merge |
| `aguardando a fila de merge` | outro agente esta mesclando | espere; o lock e liberado ao fim |
| `o nome ... estoura o MAX_PATH` | nome longo demais | encurte o nome |
| `desregistrado, mas o diretorio ficou em disco` | shell com o `cwd` la dentro (Windows) | feche o shell, apague a pasta, rode `--prune` |

Fila travada por um processo morto: o lock expira em 20 min. Para forcar,
apague `.git/wt-merge.lock`.

## Nunca faca

- `rm -rf` num worktree enquanto o vinculo `node_modules` existir — a remocao
  pode descer por ele e apagar as dependencias da raiz. Use sempre o `clean.mjs`,
  que desfaz o vinculo primeiro.
- Checkout da branch alvo dentro de um worktree.
- Rodar dev server, build nativo ou e2e dentro de um worktree.
- Tratar worktree como sandbox: ele isola a arvore de trabalho **deste** repo e
  nada mais. Caminhos absolutos para fora continuam alcancaveis.

## Estrutura

```
scripts/
  new.mjs      cria worktree, vincula deps, guarda de MAX_PATH
  merge.mjs    fila -> rebase -> portoes -> fast-forward
  clean.mjs    lista / remove / prune
  lib/
    git.mjs    wrapper fino sobre o executavel git
    paths.mjs  resolucao de caminhos e o vinculo node_modules
    gates.mjs  deteccao dos portoes a partir do package.json
    lock.mjs   mutex entre processos via mkdir atomico
    run.mjs    execucao dos portoes com stdio herdado
```
