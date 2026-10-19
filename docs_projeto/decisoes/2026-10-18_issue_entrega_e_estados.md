---
title: /issue com testes unitarios, estados no board, PR e merge
type: decisao
status: aprovado
created: 2026-10-18
updated: 2026-10-18
project: template_projetos
tags: [decisao, issue, board, testes, pr, tema/tooling]
---

# 2026-10-18 — /issue com testes unitarios, estados no board, PR e merge

## O que mudou

1. A skill `/issue` (v1.2) passou a fazer o que antes vinha colado num prompt a cada issue:
   - "coloque em andamento ao iniciar";
   - "em revisao se precisar testar, done se nao";
   - "faca o PR e o merge com a branch atual";
   - terminar com o link da issue.
2. Cada fatia entrega **testes unitarios** do que mudou, alem do portao de teste do projeto. O
   `implementer` escreve e roda so os arquivos de teste dele. Projeto sem framework de teste para
   antes da primeira fatia.
3. `issue.js mover "<Status>" [ref] [--conferir]` na CLI da statusline (`lib/mover.js`, com teste em
   `testes/mover.test.js`). Descricao em [[../STATUSLINE]].
4. A `/trilha` secao 8 ganhou a excecao: a `/issue` e o pedido explicito de merge e de Done.

## Por que assim

- **Dentro da `/issue`, e nao com flag.** Foi escolha do usuario: o prompt colado era o mesmo em toda
  issue, e chamar `/issue 42` vira o pedido.
- **Done decidido por criterio, nao por pergunta.** Done so quando todo criterio de aceite foi provado
  por teste automatizado. Ambiente real, UI, hardware ou servico externo vao para In review. Na duvida,
  In review. Isso conserva o que a `/trilha` protegia, o aceite do dono quando ha prova pendente.
- **Estado final depois do merge, com conferencia.** O workflow nativo "PR merged → In review" roda
  em segundo plano e desfaria um Done posto antes. O `--conferir` espera, rele e reaplica uma vez.
- **Sempre `Refs`, nunca `Closes`.** O fechamento automatico e o workflow do merge disputariam o
  status. A `/issue` poe o status e fecha a issue ela mesma.
- **Ids pelo item da issue.** O `BOARD.md` do template e um molde vazio, e os boards reais usam nomes
  em portugues (TelemeVisus: `Em andamento`, `Em revisão`, `Feito`). A consulta GraphQL descobre
  tudo a partir do item, e os nomes em ingles e portugues sao sinonimos.
- **Falha para e reporta.** Sem board, o fluxo avisa e segue. CI vermelho, conflito ou branch
  protegida param antes do merge, com o PR aberto e a issue em In progress.
- **Squash esperando o CI.** Foi escolha do usuario. Um commit por issue na base, e o CI so e esperado
  quando o repo tem workflow de `pull_request`.

## Alternativas descartadas

- **Flag `--entregar`:** mantinha o comportamento antigo como padrao, e o prompt continuaria sendo
  colado.
- **So na Adaptacao local de cada projeto:** o template nao mudaria, e cada derivado reescreveria a
  mesma regra.
- **Ids lidos do `BOARD.md`:** quebra enquanto o molde esta vazio e duplica o que o item ja diz.
- **Fatia de testes separada, escrita pelo `worker`:** mais barata, mas o teste e escrito olhando o
  codigo pronto.

## Nao provado

O `item-edit` nao foi executado contra um board real, para nao mexer em issue de producao. A consulta
e a escolha de opcao foram conferidas sem escrita na TelemeVisus#159. A primeira `/issue` real prova o
resto.
