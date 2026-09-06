---
title: Worktrees de agentes
type: convencao
status: aprovado
created: 2026-08-20
updated: 2026-08-20
tags: [worktree, git, claude-code, automacao, fluxo]
---

# Worktrees de agentes

Fluxo para rodar **varias tarefas independentes em paralelo**, cada uma com sua
propria janela `claude`, sem que as sessoes colidam no mesmo diretorio.

Premissa: **so a arvore principal compila e roda a aplicacao**. Worktrees escrevem
codigo e rodam teste unitario; nenhum deles sobe dev server, entao nao existe
disputa de porta.

Implementado pela skill `/worktree`, cujos scripts vivem em
`.claude/skills/worktree/scripts/`. Copiar a pasta da skill instala o fluxo inteiro.

## Comandos

Na arvore principal:

```bash
node .claude/skills/worktree/scripts/new.mjs <nome>
node .claude/skills/worktree/scripts/clean.mjs                            # lista
node .claude/skills/worktree/scripts/clean.mjs --remove <nome> [--force]
node .claude/skills/worktree/scripts/clean.mjs --prune
```

Da raiz de um worktree:

```bash
node ../../skills/worktree/scripts/merge.mjs [--skip-tests]
```

Projetos Node podem expor atalhos em `package.json` (`wt:new`, `wt:list`,
`wt:merge`, `wt:clean`).

## Decisoes e o porque

### O agente nunca da checkout da branch alvo

Git proibe a mesma branch em dois worktrees, e e essa proibicao que elimina a
colisao. O merge roda `git merge --ff-only` **na arvore principal**, via
`git -C <raiz>`, a partir do worktree. O worktree fica na branch dele do inicio ao fim.

### Rebase antes, fast-forward depois

O script rebaseia `wt/<nome>` sobre a branch alvo e so entao faz `--ff-only`. O
historico fica linear e o merge nunca conflita — se houvesse conflito, ele aparece
no rebase, dentro do worktree, onde o agente resolve.

### Fila de merge

Serializada por `mkdir` atomico em `.git/wt-merge.lock`. Dois agentes que terminam
juntos entram em fila em vez de disputar o indice. O lock guarda o dono, expira em
20 min e a espera maxima e de 15 min.

### Portoes detectados, nao fixos

Do `package.json` do worktree: script `typecheck` (ou `tsconfig.json` -> `npx tsc
--noEmit`) e script `test`. Sem `package.json` ou sem `node_modules`, nenhum portao
roda e isso e reportado — e o caso de um repositorio so de documentacao.

### A arvore principal nao precisa estar limpa

O merge so recusa se um arquivo **que o fast-forward vai reescrever** tiver edicao
pendente na arvore principal. E a mesma condicao que o git aplicaria, dita antes
para o erro sair legivel.

### `node_modules` e vinculo, nao copia

Junction no Windows (sem exigir admin), symlink de diretorio no resto. Custo zero
de disco. O preco: uma branch que altere `package.json` esta testando contra as
dependencias da raiz — o script avisa quando detecta.

### MAX_PATH

O prefixo `.claude/worktrees/<nome>/` soma ~20 chars mais o nome. Em repos com
caminhos longos, um nome grande estoura os 260 do Windows e o `git worktree add`
falha **pela metade**, deixando o worktree sem parte dos arquivos. O script calcula
o pior caminho antes de criar e recusa. **Use nomes curtos.**

## Armadilhas

**Nunca apague um worktree com `rm -rf` enquanto a junction existir.** O vinculo
`node_modules` aponta para a raiz e uma remocao recursiva pode descer por ele. O
`clean.mjs` desfaz o vinculo *antes* de chamar `git worktree remove`, nessa ordem,
por esse motivo.

**`git worktree remove` pode falhar pela metade no Windows.** Ele desregistra e so
entao apaga o diretorio; com um shell parado la dentro, o `rmdir` falha com o
registro ja desfeito. O `clean.mjs` detecta e termina a limpeza no lugar do git.

**Worktree nao e sandbox.** Ele isola a arvore de trabalho do *git deste repo* e
nada mais. Caminhos absolutos para fora continuam alcancaveis de dentro de qualquer
worktree.

**Cada worktree tem uma copia de `docs_projeto/`.** Um agente que atualiza a
documentacao la dentro nao muda nada na vault aberta na raiz — a alteracao so
aparece depois do merge. O Obsidian nao indexa `.claude/` (pasta com ponto), entao
os wikilinks nao duplicam.

**`.claude/worktrees/` e ignorado pelo git.**
