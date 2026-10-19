---
name: issue
description: Conduz uma issue do comeco ao merge escolhendo agentes e modelos pelo tamanho (XS a XL) — le a issue, classifica, pergunta, planeja, implementa por fatias com testes unitarios e handoff escrito, move a issue no board (em andamento, em revisao ou feito), revisa, documenta, abre o PR e faz o merge na branch de origem. Toda implementacao roda num worktree criado a partir da branch atual. Use quando o usuario pedir /issue, colar a URL ou o numero de uma issue, ou disser "pega a issue", "trabalha nessa issue", "implementa essa tarefa", "resolve essa issue e faz o PR".
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, Agent, AskUserQuestion, Skill
version: 1.3
---

# /issue — fluxo de agentes por tamanho

O catalogo dos agentes, a tabela completa e o porque de cada regra estao em `docs_projeto/AGENTES.md`. Esta skill e o roteiro. Se o projeto tiver uma secao **Adaptacao local** no `AGENTES.md` (board, IDs de status, submodulos, portao de teste), ela vence este roteiro no que disser.

## Regras de custo (valem em todos os passos)

- **Uma issue por sessao.** Ao terminar, sugira `/clear` antes da proxima.
- **Um `implementer` novo por fatia.** `SendMessage` so dentro da mesma fatia, para corrigir o que o teste apontou ou retomar agente que caiu por limite.
- **Busca no codigo vai para o `explorer`**, que devolve `caminho:linha`. Nao leia dezenas de arquivos na sessao principal.
- **O advisor entra em so tres momentos:** antes de executar o plano de uma L ou XL, quando o mesmo erro se repete e antes de declarar concluido.

## Entrega e estados (valem em todos os tamanhos)

- **Chamar a `/issue` e o pedido de push, PR e merge.** A branch de destino e a que estava em checkout quando a implementacao comecou (passo 4.3), nao necessariamente `main`. Uma **Adaptacao local** que diga outra coisa vence.
- **Toda implementacao roda num worktree, em todos os tamanhos.** Ele nasce da branch atual no passo 4.3 e volta para ela pelo merge do PR no passo 5.6. Nenhum Edit, `implementer` ou commit da issue toca a arvore principal; ela so recebe o merge.
- **A issue anda no board em dois momentos:** **In progress** ao iniciar a implementacao (4.3) e **In review** ou **Done** depois do merge (5.7). Nunca no passo 1: ler e perguntar nao e trabalhar.
- Comando, sempre na sessao principal: `node .claude/statusline/issue.js mover "<Status>" [ref] [--conferir]`. Sem `ref`, vale a issue registrada no passo 1. Aceita os nomes em ingles ou portugues (`In progress` acha `Em andamento`; `Done` acha `Feito`) e descobre os ids pelo item da issue, sem depender do `BOARD.md`.
- Saida 3 (issue fora de Project, ou board sem a opcao) ou 1 (`gh` falhou; sem escopo, `gh auth refresh -s project`): **avise e siga**. Nao trave a issue por causa do board; o aviso entra no relatorio final.
- Texto solto sem issue no GitHub: nao ha o que mover nem link para dar. Branch, PR e merge seguem.

## 1. Ler a issue

- Entrada: URL ou numero (`gh issue view <n> --json number,title,body,labels,milestone,comments`) ou texto solto colado pelo usuario.
- Com a issue identificada, registre-a na statusline **na sessao principal**, antes de abrir qualquer agente: `node .claude/statusline/issue.js definir <n | owner/repo#n | URL>`. Issue de outro repo vai como `owner/repo#n` ou URL. Texto solto sem issue no GitHub nao registra nada. Detalhes em `docs_projeto/STATUSLINE.md`.
- Leia os links do corpo: docs do projeto, decisoes e issues relacionadas. Se a issue e os docs discordam, **os docs vencem**: aponte a divergencia.
- Referencia externa (biblioteca, norma, API de terceiro) vai para o `researcher`, que arquiva a ficha em `docs_projeto/referencias/`.

## 2. Localizar e classificar

Abra o `explorer` com **`model: sonnet`** (o padrao dele e Haiku; aqui ele tambem julga o tamanho). A sessao principal nao le o codigo para classificar: usa o que ele devolver. Briefing:

- titulo, corpo e label `size/*` da issue, se houver;
- a tabela abaixo e as regras de desempate;
- o pedido: caminhos afetados (`caminho:linha`), tamanho proposto, uma frase de justificativa e, se ficou entre dois tamanhos, quais.

| Tamanho | Sinal |
|---|---|
| XS | Uma mudanca localizada, sem decisao de desenho (texto, config, um teste) |
| S | Um modulo, padrao ja existente no codigo, ate ~1 dia |
| M | Varios arquivos de um repositorio, alguma decisao de desenho, ou contrato tocado de leve |
| L | Atravessa camadas ou repositorios, muda contrato, esquema ou migracao |
| XL | Varias fatias com dependencia entre si, seguranca ou dado de cliente no centro, ou prova em ambiente real |

Desempate: na duvida entre dois tamanhos, **o maior**. Codigo sensivel (login, autorizacao, segredo, criptografia, dado de cliente) **sobe para pelo menos M**.

Decisao:

1. **Sem label:** use o tamanho proposto. Diga qual e por que em uma frase e ofereca aplicar a label (`gh issue edit <n> --add-label size/M`).
2. **Com label:** vale o **maior** entre a label e o proposto. Se o `explorer` propuser maior, diga por que e ofereca corrigir a label. Se propuser menor, mantenha a label: so o usuario rebaixa.

## 3. Perguntar

- **XS e S:** pergunte so o que for ambiguo, de 0 a 2 perguntas, como manda a regra 3 do hook.
- **M, L e XL:** pelo menos 5 perguntas de decisao real via `AskUserQuestion` (escopo, restricoes, estilo, aceite, casos de borda), com a recomendacao primeiro. Se uma resposta contrariar a recomendacao e invadir outra issue, pergunte de novo mostrando o custo.

## 4. Executar pelo tamanho

| Tamanho | Planejar | Implementar | Testar | Revisar |
|---|---|---|---|---|
| XS / S | Na propria sessao, sem plano formal | Na propria sessao | Na propria sessao ou `worker` | Se for codigo sensivel |
| M | Lista curta de fatias na sessao, sem `Plan` e sem advisor | `implementer` com `model: sonnet`, um por fatia | `worker` | Se for codigo sensivel |
| L / XL | `Plan` com `model: opus` | `implementer` (Opus), um por fatia | `worker` | **Sempre**, com o `reviewer` |

O handoff fica em `.claude/handoff/<issue>.md` **do checkout principal**, por caminho absoluto, embora o trabalho rode no worktree: o worktree tem o proprio `.claude/` e some no fim (ignorado pelo git; `<issue>` e o numero ou um slug ASCII).

**O plano e as fatias nao vao para o chat.** Diga so quantas fatias sao e o caminho do arquivo.

### 4.1 Fatias da M

1. Com os achados do `explorer`, grave no handoff uma secao `## Fatias` de 3 a 6 linhas: uma por fatia, com o que muda e o criterio de prova.
2. Se alguma fatia pedir uma decisao de desenho que nao cabe numa linha, ou se passar de 6 fatias, a issue e L: reclassifique, ofereca a label e siga 4.2.

### 4.2 Plano da L e XL

1. Peca ao `Plan` o plano em fatias que compilam e testam sozinhas, cada uma com criterio de prova.
2. Grave o plano no handoff, secao `## Plano`.
3. **Advisor, momento 1:** consulte antes de executar. Se mudar o plano, regrave.

### 4.3 Iniciar a implementacao

Logo antes do primeiro Edit (XS/S) ou do primeiro `implementer` (M, L, XL):

1. **Base:** `git branch --show-current`. Grave `base: <branch>` no topo do handoff (em XS/S, guarde na sessao). HEAD solta, ou base que ja e branch de outra issue: pergunte.
2. **Worktree:** na arvore principal, `node .claude/skills/worktree/scripts/new.mjs issue-<n>` (texto solto: um slug curto). Cria `.claude/worktrees/issue-<n>` na branch `wt/issue-<n>`, a partir da base. Grave `worktree: <caminho absoluto>` e `branch: wt/issue-<n>` no handoff, abaixo da base.
   - Dali em diante a sessao trabalha **dentro do worktree**: `cd` para ele no Bash, Edit e Read por caminho absoluto sob ele. A arvore principal nao e editada nem commitada ate o merge.
   - A issue altera `package.json`: o `node_modules` do worktree e vinculo para o da raiz, e instalar ali alteraria a raiz. Desfaca so o vinculo, da raiz do worktree, com `node --input-type=module -e "import {unlinkNodeModules} from '../../skills/worktree/scripts/lib/paths.mjs'; unlinkNodeModules('.')"` (nunca `rm -rf`), e instale as dependencias ali dentro.
   - Prova que pede o app rodando (dev server, e2e, build nativo) nao roda no worktree: fica para a arvore principal depois do merge e pesa no estado final (passo 5.7).
3. **Testes:** se o projeto nao tiver framework de teste unitario, pare e proponha configurar um como fatia 0. Nao implemente sem onde por o teste.
4. **Board:** `issue.js mover "In progress"`. Se o `BOARD.md` tiver limite de WIP e ele estourar, avise.

### 4.4 Cada fatia

1. Abra um `implementer` **novo**, com este briefing:
   - o caminho de `.claude/handoff/<issue>.md`;
   - o caminho absoluto do worktree, com a ordem de ler, editar, testar e commitar so ali, nunca na arvore principal;
   - qual fatia fazer;
   - a ordem de ler o codigo atual em vez de confiar no resumo;
   - a regra de testes unitarios abaixo.
2. Acrescente o bloco `## Handoff — fatia <n>` que ele devolver ao arquivo de handoff.
3. Rode **os unitarios da fatia e depois o portao de teste do projeto** (suite existente, build, typecheck), em comandos separados, ou mande o `worker` rodar e devolver as duas saidas.
4. Falhou: corrija o que for trivial na propria sessao, que sai mais barato que reabrir o agente, ou devolva ao mesmo `implementer` por `SendMessage`. **Advisor, momento 2:** se o mesmo erro voltar, consulte antes da terceira tentativa.
5. Verde nos dois: faca o commit da fatia com a skill `/commit`.

**Testes unitarios.** Alem do portao do projeto, cada fatia entrega os unitarios do que mudou. XS e S seguem a mesma regra, na propria sessao.

- Logica nova ou alterada ganha teste unitario, no framework e na pasta que o projeto ja usa.
- Bug ganha teste de regressao que falha sem a correcao.
- O unitario isola a unidade: sem rede, banco ou relogio real (dubles nas bordas). Teste com dependencia real e de integracao e conta no portao, nao aqui.
- Mudanca so de config, texto, docs ou estilo fica sem unitario, e o handoff diz por que.

### 4.5 Revisao

Para L e XL, ou para codigo sensivel, abra **um ou dois** `reviewer` independentes sobre `git diff <base>...wt/issue-<n>` antes do merge. Achado que bloqueia volta como uma nova fatia.

## 5. Fechar

1. **Docs:** rode a regra 2 do hook. Para mais de 3 arquivos de docs, use um `worker` com uma ficha de fatos ja conferidos.
2. **Aceite:** marque os criterios de aceite cumpridos no corpo da issue.
3. **Advisor, momento 3:** consulte antes de abrir o PR, com o trabalho ja commitado.
4. **PR:** de dentro do worktree, `git push -u origin wt/issue-<n>` e `gh pr create --base <base>`. O titulo segue a convencao de commit do projeto. O corpo traz resumo, prova (comandos e saidas dos unitarios e do portao) e `Refs #N` (`Refs owner/repo#N` se a issue mora noutro repo). **Nunca `Closes`/`Fixes`**, nem em commit: o estado final e posto no passo 7, e o fechamento automatico disputaria com o workflow "PR merged".
5. **CI:** se o repo tem workflow em `.github/workflows/` que roda em `pull_request`, `gh pr checks <pr> --watch --fail-fast`. Logo apos o `pr create` os checks podem ainda nao ter registrado ("no checks reported"): com workflow no repo, repita uma vez antes de seguir. Sem workflow, o portao local ja rodou e e o unico; siga.
6. **Merge na branch atual:** `gh pr merge <pr> --squash --delete-branch`. Depois, de volta na arvore principal (`cd` para a raiz, que segue na base): `git pull --ff-only` e `node .claude/skills/worktree/scripts/clean.mjs --remove issue-<n>`. O merge vai pelo PR, nao pelo `merge.mjs` da `/worktree`.
   - Saida diferente de zero nao prova que o merge falhou: o `--delete-branch` tenta trocar para a base, que ja esta em checkout na arvore principal, e o git recusa. Confira com `gh pr view <pr> --json state,mergedAt` antes de concluir.
   - Saia do worktree antes do `clean.mjs`: no Windows, um shell parado la dentro impede apagar a pasta.
   - CI vermelho, conflito, branch protegida pedindo review ou merge que de fato nao aconteceu: **pare**.
   - O PR fica aberto e a issue fica In progress.
   - Comente na issue o link do PR e o motivo, e reporte. Nao force e nao contorne a protecao.
7. **Estado final.** Primeiro comente a prova na issue (`gh issue comment`): comandos e saidas, link do PR e o que **nao** foi provado. Depois:
   - **Done** quando todo criterio de aceite foi provado por teste automatizado nesta issue: `issue.js mover "Done" --conferir` e, se ela seguir aberta, `gh issue close <n> --reason completed` (com `-R owner/repo` se a issue mora noutro repo).
   - **In review** quando algum criterio depende de ambiente real, UI vista por gente, hardware, servico externo ou dado de producao: `issue.js mover "In review" --conferir`. Nao feche.
   - Na duvida, In review. O `--conferir` espera 10 s e reaplica se o workflow do board tiver passado por cima.
8. **Trilha:** se a issue pertence a uma (`/trilha`), atualize a linha dela no plano com estado, prova e link (secao 15 da `/trilha`).
9. **Relatorio.** Termine com: tamanho usado, agentes e modelos, PR e merge, estado final no board (ou o aviso de que nao moveu), o que ficou pendente e a sugestao de `/clear`. **A ultima linha e a URL da issue.**
