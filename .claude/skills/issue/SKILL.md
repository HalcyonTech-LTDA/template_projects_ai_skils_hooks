---
name: issue
description: Conduz uma issue do comeco ao merge escolhendo agentes e modelos pelo tamanho (XS a XL) — le a issue, classifica, pergunta, planeja, implementa por fatias com handoff escrito, testa, revisa e documenta. Use quando o usuario pedir /issue, colar a URL ou o numero de uma issue, ou disser "pega a issue", "trabalha nessa issue", "implementa essa tarefa".
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, Agent, AskUserQuestion, Skill
version: 1.1
---

# /issue — fluxo de agentes por tamanho

O catalogo dos agentes, a tabela completa e o porque de cada regra estao em `docs_projeto/AGENTES.md`. Esta skill e o roteiro. Se o projeto tiver uma secao **Adaptacao local** no `AGENTES.md` (board, IDs de status, submodulos, portao de teste), ela vence este roteiro no que disser.

## Regras de custo (valem em todos os passos)

- **Uma issue por sessao.** Ao terminar, sugira `/clear` antes da proxima.
- **Um `implementer` novo por fatia.** `SendMessage` so dentro da mesma fatia, para corrigir o que o teste apontou ou retomar agente que caiu por limite.
- **Busca no codigo vai para o `explorer`**, que devolve `caminho:linha`. Nao leia dezenas de arquivos na sessao principal.
- **O advisor entra em so tres momentos:** antes de executar o plano de uma L ou XL, quando o mesmo erro se repete e antes de declarar concluido.

## 1. Ler a issue

- Entrada: URL ou numero (`gh issue view <n> --json number,title,body,labels,milestone,comments`) ou texto solto colado pelo usuario.
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

- **XS e S:** pergunte so o que for ambiguo, de 0 a 2 perguntas. Esta e a excecao a regra 3 do hook.
- **M, L e XL:** pelo menos 5 perguntas de decisao real via `AskUserQuestion` (escopo, restricoes, estilo, aceite, casos de borda), com a recomendacao primeiro. Se uma resposta contrariar a recomendacao e invadir outra issue, pergunte de novo mostrando o custo.

## 4. Executar pelo tamanho

| Tamanho | Planejar | Implementar | Testar | Revisar |
|---|---|---|---|---|
| XS / S | Na propria sessao, sem plano formal | Na propria sessao | Na propria sessao ou `worker` | Se for codigo sensivel |
| M | Lista curta de fatias na sessao, sem `Plan` e sem advisor | `implementer` com `model: sonnet`, um por fatia | `worker` | Se for codigo sensivel |
| L / XL | `Plan` com `model: opus` | `implementer` (Opus), um por fatia | `worker` | **Sempre**, com o `reviewer` |

O handoff fica em `.claude/handoff/<issue>.md` **do checkout principal**, por caminho absoluto, mesmo trabalhando num worktree: o worktree tem o proprio `.claude/` e some no fim (ignorado pelo git; `<issue>` e o numero ou um slug ASCII). Trabalhe num worktree (skill `/worktree`) quando houver outra sessao no mesmo repositorio ou quando a issue for L ou XL.

**O plano e as fatias nao vao para o chat.** Diga so quantas fatias sao e o caminho do arquivo.

### 4.1 Fatias da M

1. Com os achados do `explorer`, grave no handoff uma secao `## Fatias` de 3 a 6 linhas: uma por fatia, com o que muda e o criterio de prova.
2. Se alguma fatia pedir uma decisao de desenho que nao cabe numa linha, ou se passar de 6 fatias, a issue e L: reclassifique, ofereca a label e siga 4.2.

### 4.2 Plano da L e XL

1. Peca ao `Plan` o plano em fatias que compilam e testam sozinhas, cada uma com criterio de prova.
2. Grave o plano no handoff, secao `## Plano`.
3. **Advisor, momento 1:** consulte antes de executar. Se mudar o plano, regrave.

### 4.3 Cada fatia

1. Abra um `implementer` **novo**, com este briefing:
   - o caminho de `.claude/handoff/<issue>.md`;
   - qual fatia fazer;
   - a ordem de ler o codigo atual em vez de confiar no resumo.
2. Acrescente o bloco `## Handoff — fatia <n>` que ele devolver ao arquivo de handoff.
3. Rode o portao de teste do projeto, ou mande o `worker` rodar e devolver a saida.
4. Falhou: corrija o que for trivial na propria sessao, que sai mais barato que reabrir o agente, ou devolva ao mesmo `implementer` por `SendMessage`. **Advisor, momento 2:** se o mesmo erro voltar, consulte antes da terceira tentativa.
5. Verde: faca o commit da fatia com a skill `/commit`.

### 4.4 Revisao

Para L e XL, ou para codigo sensivel, abra **um ou dois** `reviewer` independentes sobre `git diff <base>...<branch>` antes do merge. Achado que bloqueia volta como uma nova fatia.

## 5. Fechar

1. Docs: rode a regra 2 do hook. Para mais de 3 arquivos de docs, use um `worker` com uma ficha de fatos ja conferidos.
2. Marque os criterios de aceite no corpo da issue e comente a prova (comando, saida, link do CI) **antes** do merge.
3. **Advisor, momento 3:** consulte antes de declarar concluido, com o trabalho ja commitado.
4. Se a issue pertence a uma trilha (`/trilha`): mova-a para **In review** com o comentario de prova e o que nao foi provado; Done e fechamento sao do dono. PR usa `Refs #N`, e `Closes #N` so quando o merge e o aceite.
5. PR e merge conforme o projeto. Nao use "closes #N" ou "fixes #N" em texto de commit se o projeto nao quiser fechamento automatico. Faca push so se o usuario pedir.
6. Termine com: tamanho usado, agentes e modelos usados, o que ficou pendente, e a sugestao de `/clear`.
