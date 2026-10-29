---
name: issue
description: Conduz uma issue do comeco ao merge por fases F1 a F8 — le a issue, classifica, explora, pergunta, planeja, implementa por fatias com testes unitarios, testa, revisa, documenta, abre o PR e faz o merge na branch de origem. XS a M rodam numa sessao so, em Sonnet, sem subagentes; L e XL usam Plan, um implementer por fatia e reviewer, em Opus. Grava a fase e o modelo recomendado na statusline, move a issue no board (em andamento, em revisao ou feito) e so troca de modelo por /clear com handoff. Toda implementacao roda num worktree criado a partir da branch atual. Use quando o usuario pedir /issue, colar a URL ou o numero de uma issue, ou disser "pega a issue", "trabalha nessa issue", "implementa essa tarefa", "resolve essa issue e faz o PR".
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, Agent, AskUserQuestion, Skill
version: 2.0
---

# /issue — fluxo por fases

O catalogo dos agentes, a tabela por tamanho e o porque de cada regra estao em `docs_projeto/AGENTES.md`. Esta skill e o roteiro. Se o projeto tiver uma secao **Adaptacao local** no `AGENTES.md` (board, IDs de status, submodulos, portao de teste), ela vence este roteiro no que disser.

## Fases

Toda issue anda pelas mesmas oito fases. O tamanho decide quem executa cada uma.

| Fase | O que faz | XS a M: a propria sessao | L e XL: sessao e subagentes |
|---|---|---|---|
| F1 Classificar | Ler a issue, registrar na barra, achar o tamanho | sessao | sessao |
| F2 Explorar | Localizar o codigo afetado | sessao (Grep/Glob, so o trecho) | `explorer` (Haiku) |
| F3 Perguntar | Decisoes reais com o usuario | XS/S: 0 a 2; M: 5 ou mais | 5 ou mais |
| F4 Planejar | Fatias com criterio de prova | XS/S: sem plano; M: 3 a 6 linhas | `Plan` (Opus) e advisor |
| F5 Implementar | Worktree, board, codigo e unitarios | sessao | `implementer` (Opus), um por fatia |
| F6 Testar | Unitarios da fatia, portao do projeto, commit | sessao | sessao ou `worker` |
| F7 Revisar | Leitura adversaria do diff | so se for codigo sensivel (`reviewer`) | sempre (`reviewer`) |
| F8 Fechar | Docs, PR, CI, merge, board, relatorio | sessao | sessao |

**Ate M nao ha subagente.** Nem `explorer`, nem `implementer`, nem `worker`: a sessao faz tudo, em Sonnet. Numa M medida (n=1, `AGENTES.md` secao 7) isso custou cerca de 45% menos e levou cerca de 40% menos tempo que o fluxo com subagentes, com o mesmo resultado. Subagente fica em L e XL, onde isolar contexto, planejar com Opus e revisar de forma independente compensam.

## Regras de custo (valem em todas as fases)

- **Uma issue por sessao.** Ao terminar, sugira `/clear` antes da proxima.
- **Ate M:** leia so o trecho necessario (`offset`/`limit`), leituras independentes numa resposta, varias checagens num Bash, nada de reler o que ja esta na conversa.
- **L e XL: um `implementer` novo por fatia.** `SendMessage` so dentro da mesma fatia, para corrigir o que o teste apontou ou retomar agente que caiu por limite. Busca ampla no codigo vai para o `explorer`, que devolve `caminho:linha`.
- **O advisor entra em so tres momentos:** antes de executar o plano de uma L ou XL, quando o mesmo erro se repete e antes de declarar concluido.

## Modelo e fase na barra

- **Modelo recomendado para a sessao:** `sonnet` em XS a M; `opus` em L e XL (a sessao decide desenho com o usuario e concilia os achados do `reviewer`).
- **Fase na barra.** Ao entrar numa fase, grave-a no **mesmo Bash** do primeiro comando dela, na sessao principal: `node .claude/statusline/issue.js fase F5 --modelo sonnet; git branch --show-current`. Use `;`, nunca `&&`: falha da barra nao trava a issue. Nao gaste uma chamada so para isso. Fase sem Bash (F3, F4) nao grava e a barra fica na anterior. Em F1 ainda nao ha tamanho: `fase F1`, sem `--modelo`. Nao escreva marcador de fase no chat. Detalhes em `docs_projeto/STATUSLINE.md`.
- **Trocar de modelo so com `/clear` e handoff.** O cache e por modelo: um `/model` no meio da sessao regrava o contexto inteiro no preco do modelo novo. Se o modelo desta sessao (o do prompt do sistema; a barra mostra `⚠`) nao e o recomendado para o tamanho achado:
  1. grave o handoff (cabecalho e `## Achados`, abaixo);
  2. diga ao usuario os tres comandos e **pare**: `/clear`, `/model <recomendado>` e `/issue .claude/handoff/<issue>.md`;
  3. se o usuario preferir seguir no modelo atual, siga e avise que fica mais caro.

  A hora de decidir e logo depois da F1, com o contexto ainda pequeno. Reclassificar mais adiante (uma M que virou L) segue a mesma regra.

## Entrega e estados (valem em todos os tamanhos)

- **Chamar a `/issue` e o pedido de push, PR e merge.** A branch de destino e a que estava em checkout quando a implementacao comecou (F5.1), nao necessariamente `main`. Uma **Adaptacao local** que diga outra coisa vence.
- **Toda implementacao roda num worktree, em todos os tamanhos.** Ele nasce da branch atual na F5.1 e volta para ela pelo merge do PR na F8. Nenhum Edit, `implementer` ou commit da issue toca a arvore principal; ela so recebe o merge.
- **A issue anda no board em dois momentos:** **In progress** ao iniciar a implementacao (F5.1) e **In review** ou **Done** depois do merge (F8, passo 7). Nunca na F1: ler e perguntar nao e trabalhar.
- Comando, sempre na sessao principal: `node .claude/statusline/issue.js mover "<Status>" [ref] [--conferir]`. Sem `ref`, vale a issue registrada na F1. Aceita os nomes em ingles ou portugues (`In progress` acha `Em andamento`; `Done` acha `Feito`) e descobre os ids pelo item da issue, sem depender do `BOARD.md`.
- Saida 3 (issue fora de Project, ou board sem a opcao) ou 1 (`gh` falhou; sem escopo, `gh auth refresh -s project`): **avise e siga**. Nao trave a issue por causa do board; o aviso entra no relatorio final.
- Texto solto sem issue no GitHub: nao ha o que mover nem link para dar. Branch, PR e merge seguem.

## F1 · Ler e classificar

1. **Ler a issue.**
   - Entrada: URL ou numero (`gh issue view <n> --json number,title,body,labels,milestone,comments`) ou texto solto colado pelo usuario.
   - Entrada que e um caminho de handoff, ou issue que ja tem `.claude/handoff/<issue>.md` no checkout principal: leia-o e **retome da `proxima-fase`**, sem refazer o que ele registra.
   - Com a issue identificada, registre-a na statusline **na sessao principal**, antes de abrir qualquer agente: `node .claude/statusline/issue.js definir <n | owner/repo#n | URL>; node .claude/statusline/issue.js fase F1`. Issue de outro repo vai como `owner/repo#n` ou URL. Texto solto sem issue no GitHub nao registra issue, mas a fase vale.
   - Leia os links do corpo: docs do projeto, decisoes e issues relacionadas. Se a issue e os docs discordam, **os docs vencem**: aponte a divergencia.
   - Referencia externa (biblioteca, norma, API de terceiro) vai para o `researcher`, que arquiva a ficha em `docs_projeto/referencias/`.
2. **Classificar, na propria sessao.** Leia so o necessario para decidir: o corpo, a label `size/*` e um Grep/Glob nos pontos que a issue cita. Nao abra subagente para isso.

   | Tamanho | Sinal |
   |---|---|
   | XS | Uma mudanca localizada, sem decisao de desenho (texto, config, um teste) |
   | S | Um modulo, padrao ja existente no codigo, ate ~1 dia |
   | M | Varios arquivos de um repositorio, alguma decisao de desenho, ou contrato tocado de leve |
   | L | Atravessa camadas ou repositorios, muda contrato, esquema ou migracao |
   | XL | Varias fatias com dependencia entre si, seguranca ou dado de cliente no centro, ou prova em ambiente real |

   Desempate: na duvida entre dois tamanhos, **o maior**. Codigo sensivel (login, autorizacao, segredo, criptografia, dado de cliente) **sobe para pelo menos M**.
3. **Decidir o tamanho.** Sem label: use o seu e ofereca aplicar a label (`gh issue edit <n> --add-label size/M`). Com label: vale o **maior** dos dois. Se o seu for maior, diga por que e ofereca corrigir a label; se for menor, mantenha a label, porque so o usuario rebaixa.
4. **Conferir o modelo.** Compare o modelo desta sessao com o recomendado para o tamanho (secao "Modelo e fase na barra"). Diferente: faca a troca por handoff antes de seguir.

## F2 · Explorar

- **XS a M:** Grep/Glob e leia so o trecho que vai mudar, leituras independentes numa resposta.
- **L e XL:** abra o `explorer` (Haiku, o padrao dele) com o titulo, o corpo, o tamanho e o pedido de `caminho:linha`. A sessao usa o que ele devolver e nao le dezenas de arquivos.

## F3 · Perguntar

- **XS e S:** pergunte so o que for ambiguo, de 0 a 2 perguntas, como manda a regra 3 do hook.
- **M, L e XL:** pelo menos 5 perguntas de decisao real via `AskUserQuestion` (escopo, restricoes, estilo, aceite, casos de borda), com a recomendacao primeiro. Se uma resposta contrariar a recomendacao e invadir outra issue, pergunte de novo mostrando o custo.

## F4 · Planejar

O handoff fica em `.claude/handoff/<issue>.md` **do checkout principal**, por caminho absoluto, embora o trabalho rode no worktree: o worktree tem o proprio `.claude/` e some no fim (ignorado pelo git; `<issue>` e o numero ou um slug ASCII). Cabecalho, atualizado a cada fase:

```
issue: <ref ou slug>
tamanho: M
modelo: sonnet
proxima-fase: F5
base: <branch>              (a partir da F5.1)
worktree: <caminho absoluto>
branch: wt/issue-<n>
```

Abaixo dele, `## Achados` (caminho:linha, decisoes, respostas da F3: o que uma sessao nova precisa para retomar) e as fatias. **O plano e as fatias nao vao para o chat**: diga so quantas fatias sao e o caminho do arquivo.

- **XS e S:** sem plano formal.
- **M:** grave `## Fatias`, de 3 a 6 linhas: uma por fatia, com o que muda e o criterio de prova. Se alguma pedir uma decisao de desenho que nao cabe numa linha, ou se passar de 6, a issue e L: reclassifique, ofereca a label e siga como L.
- **L e XL:**
  1. Peca ao `Plan` com `model: opus` o plano em fatias que compilam e testam sozinhas, cada uma com criterio de prova.
  2. Grave-o em `## Plano`.
  3. **Advisor, momento 1:** consulte antes de executar. Se mudar o plano, regrave.

## F5 · Implementar

### F5.1 Iniciar

Logo antes do primeiro Edit (XS a M) ou do primeiro `implementer` (L, XL):

1. **Base:** `git branch --show-current`. Grave `base: <branch>` no handoff (em XS/S, guarde na sessao). HEAD solta, ou base que ja e branch de outra issue: pergunte.
2. **Worktree:** na arvore principal, `node .claude/skills/worktree/scripts/new.mjs issue-<n>` (texto solto: um slug curto). Cria `.claude/worktrees/issue-<n>` na branch `wt/issue-<n>`, a partir da base. Grave `worktree:` e `branch:` no handoff.
   - Dali em diante a sessao trabalha **dentro do worktree**: `cd` para ele no Bash, Edit e Read por caminho absoluto sob ele. A arvore principal nao e editada nem commitada ate o merge.
   - A issue altera `package.json`: o `node_modules` do worktree e vinculo para o da raiz, e instalar ali alteraria a raiz. Desfaca so o vinculo, da raiz do worktree, com `node --input-type=module -e "import {unlinkNodeModules} from '../../skills/worktree/scripts/lib/paths.mjs'; unlinkNodeModules('.')"` (nunca `rm -rf`), e instale as dependencias ali dentro.
   - Prova que pede o app rodando (dev server, e2e, build nativo) nao roda no worktree: fica para a arvore principal depois do merge e pesa no estado final (F8, passo 7).
3. **Testes:** se o projeto nao tiver framework de teste unitario, pare e proponha configurar um como fatia 0. Nao implemente sem onde por o teste.
4. **Board:** `issue.js mover "In progress"`. Se o `BOARD.md` tiver limite de WIP e ele estourar, avise.

### F5.2 Cada fatia

- **XS a M:** a propria sessao implementa a fatia, com os unitarios dela, lendo o codigo atual do worktree.
- **L e XL:** abra um `implementer` **novo**, com este briefing:
  - o caminho de `.claude/handoff/<issue>.md`;
  - o caminho absoluto do worktree, com a ordem de ler, editar, testar e commitar so ali, nunca na arvore principal;
  - qual fatia fazer;
  - a ordem de ler o codigo atual em vez de confiar no resumo;
  - a regra de testes unitarios abaixo.

  Acrescente o bloco `## Handoff — fatia <n>` que ele devolver ao arquivo de handoff.

**Testes unitarios.** Alem do portao do projeto, cada fatia entrega os unitarios do que mudou, em qualquer tamanho.

- Logica nova ou alterada ganha teste unitario, no framework e na pasta que o projeto ja usa.
- Bug ganha teste de regressao que falha sem a correcao.
- O unitario isola a unidade: sem rede, banco ou relogio real (dubles nas bordas). Teste com dependencia real e de integracao e conta no portao, nao aqui.
- Mudanca so de config, texto, docs ou estilo fica sem unitario, e o handoff diz por que.

## F6 · Testar

1. Rode **os unitarios da fatia e depois o portao de teste do projeto** (suite existente, build, typecheck), em comandos separados. Em L e XL pode mandar o `worker` rodar e devolver as duas saidas.
2. Falhou: corrija o que for trivial na propria sessao, que sai mais barato que reabrir um agente, ou, em L e XL, devolva ao mesmo `implementer` por `SendMessage`. **Advisor, momento 2:** se o mesmo erro voltar, consulte antes da terceira tentativa.
3. Verde nos dois: faca o commit da fatia com a skill `/commit`. Depois, atualize `proxima-fase` no handoff.

## F7 · Revisar

Para L e XL, ou para codigo sensivel em qualquer tamanho, abra **um ou dois** `reviewer` independentes sobre `git diff <base>...wt/issue-<n>` antes do merge. Achado que bloqueia volta como uma nova fatia. Fora disso, pule a F7: revisar sem necessidade foi cerca de 16% do custo de uma M.

## F8 · Fechar

1. **Docs:** rode a regra 2 do hook. Para mais de 3 arquivos de docs em L ou XL, use um `worker` com uma ficha de fatos ja conferidos.
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
9. **Relatorio.** Termine com: tamanho usado, modelo da sessao e agentes (ate M, nenhum), PR e merge, estado final no board (ou o aviso de que nao moveu), o que ficou pendente e a sugestao de `/clear`. **A ultima linha e a URL da issue.**
