---
title: Agentes e fluxo de issue por tamanho
type: convencao
status: aprovado
created: 2026-10-10
updated: 2026-10-29
project: template_projetos
tags: [convencao, agentes, subagentes, custo, claude-code, tema/tooling]
---

# Agentes e fluxo de issue por tamanho

Este repositorio traz **5 subagentes** em `.claude/agents/` e a skill `/issue`, que anda a issue por
oito fases (F1 a F8) conforme o tamanho da tarefa. Ate M a `/issue` roda **numa sessao so, em
Sonnet, sem subagentes**; L e XL usam subagentes. O objetivo e gastar o modelo caro onde o desenho
e o codigo importam, e o barato no resto, sem deixar o contexto crescer sem limite.

> **Este arquivo e a fonte canonica.** Como `.claude/skills/`, `SKILLS.md` e `MCPS.md`, a correcao
> comeca aqui e desce por copia para os projetos derivados. Projeto derivado acrescenta so a
> secao **Adaptacao local** no fim.

## 1. Por que o custo esta no contexto, nao na resposta

Medicao de uma semana real (2026-10-02 a 09, ~6.000 chamadas, num projeto derivado):

- 2,05 bilhoes de tokens lidos do cache contra 3,9 milhoes de saida. A saida foi ~7% do custo.
- 61% do contexto lido veio de chamadas com mais de 400 mil tokens de contexto.
- Um unico implementador continuado por `SendMessage` atraves de 9 fatias fez 1.338 chamadas e
  chegou a 966 mil tokens: mais caro que qualquer sessao principal da semana.

Consequencias que viraram regra:

1. **Esforco (`effort`) baixo nao economiza muito.** Ele reduz a saida, nao o contexto relido.
2. **Uma issue por sessao, `/clear` entre issues**, e compactacao automatica ligada.
3. **Em L e XL, um `implementer` novo por fatia**, com o estado num arquivo de handoff, nunca na
   memoria de um agente vivo.
4. **Em L e XL, a busca exploratoria vai para o `explorer`** (Haiku), que devolve `caminho:linha`
   em vez de encher a sessao principal com arquivos inteiros.
5. **Poucas chamadas e modelo pela tarefa** em toda sessao, com ou sem `/issue`: [[ECONOMIA]].
6. **Ate M, subagente nao paga.** Cada agente novo regrava o proprio preambulo e o orquestrador
   continua relendo o contexto dele: secao 7.

## 2. Os agentes

| Agente | Modelo | Effort | Ferramentas | Papel |
|---|---|---|---|---|
| `explorer` | haiku | — | Read, Grep, Glob, Bash (so leitura) | Achar onde esta X, quem chama Y. Devolve `caminho:linha`. Na `/issue`, so em L e XL |
| `researcher` | sonnet | medium | Web, leitura, Write (so `referencias/`) | Pesquisa externa com URL em cada afirmacao |
| `worker` | sonnet | medium | todas | Rodar testes, bancada, docs por ficha de fatos. Nao decide desenho, nao commita. Na `/issue`, so em L e XL |
| `implementer` | opus | high | todas | Uma fatia de um plano aprovado (L e XL), com os testes unitarios dela. Compila e roda so os testes da fatia; termina com handoff |
| `reviewer` | opus | high | Read, Grep, Glob, Bash (so leitura) | Revisao independente do diff antes do merge |

O planejamento usa o agente embutido `Plan` com `model: opus`. Nao ha arquivo para ele.

**Cada `description` entra em todo prompt de toda sessao**, como as tools de MCP. Crie agente novo so
para um papel que nenhum dos cinco cobre.

**Agentes do blueprint de negocio.** Outros 5 agentes vem copiados do repo
[modern-business-blueprint-plugin](https://github.com/HalcyonTech-LTDA/modern-business-blueprint-plugin):
`blueprint-orchestrator-agent` e quatro especialistas (`business-strategist-agent`,
`product-gtm-lead-agent`, `corporate-architect-agent`, `finance-venture-agent`). Eles entram
porque cobrem um papel que nenhum dos cinco cobre (conceber uma empresa a partir de uma ideia),
e nao participam da `/issue`. O orquestrador roda como sessao principal
(`claude --agent blueprint-orchestrator-agent`), porque subagente nao chama subagente. Detalhes
em [[PADROES]] secao 3. Nao edite os cinco aqui: eles sao regravados pelo script de importacao.

**Agente de projeto vence agente de usuario com o mesmo nome** (`~/.claude/agents/`). Nao mantenha
copias globais com estes nomes: elas divergem e so valem fora dos projetos derivados.

## 3. Tamanho, fases e modelo

Quem classifica e a propria sessao, na F1: le o corpo da issue e a label e faz um Grep/Glob nos
pontos que ela cita. Vale o **maior** entre o tamanho achado e a label `size/XS` … `size/XL`: a
label nunca e rebaixada sem o usuario. Na duvida, o maior. Codigo sensivel (login, autorizacao,
segredo, criptografia, dado de cliente) e no minimo M.

As fases sao F1 Classificar, F2 Explorar, F3 Perguntar, F4 Planejar, F5 Implementar, F6 Testar,
F7 Revisar e F8 Fechar. O tamanho decide quem executa cada uma:

| Tamanho | Sessao | Perguntas (F3) | Planejar (F4) | Implementar (F5) | Testar (F6) | Revisar (F7) |
|---|---|---|---|---|---|---|
| XS / S | sonnet | 0 a 2, so o ambiguo | — | Na sessao | Na sessao | Se sensivel |
| M | sonnet | 5 ou mais | Lista de fatias na sessao | Na sessao, uma fatia por vez | Na sessao | Se sensivel |
| L / XL | opus | 5 ou mais | `Plan` opus | `implementer` opus, um por fatia | Sessao ou `worker` | **Sempre** (`reviewer`) |

A regra 3 do hook (`HOOKS.md`) escala as perguntas pelo tamanho do mesmo jeito. Em F2, XS a M leem
o trecho que vao mudar; L e XL usam o `explorer`. O `reviewer` de uma issue sensivel e
independente em qualquer tamanho.

**Modelo da sessao e troca.** A coluna *Sessao* e o modelo recomendado e vai para a barra
(`issue.js fase F5 --modelo sonnet`, ver [[STATUSLINE]]); `⚠` aparece quando o modelo ativo nao o
contem. O cache e por modelo: um `/model` no meio da sessao regrava o contexto inteiro no preco do
modelo novo (estimativa pelos precos calibrados, nao medida: ~US$ 0,79 numa sessao Opus com 100 mil
tokens, contra ~US$ 0,24 do preambulo de um `implementer` novo). **A troca so acontece por `/clear`
e handoff**, logo depois da F1, com o contexto ainda pequeno: a sessao grava o handoff, diz os tres
comandos (`/clear`, `/model <modelo>`, `/issue .claude/handoff/<issue>.md`) e para. Se o usuario
preferir ficar no modelo atual, a `/issue` segue e avisa que sai mais caro.

**Testar, em todos os tamanhos, sao duas coisas.** Cada fatia entrega os testes unitarios do que mudou:
logica nova ou alterada ganha teste, e bug ganha teste de regressao. Quem escreve e o `implementer`
em L/XL, ou a propria sessao ate M. A fatia so fica verde com esses unitarios **e** o portao de
teste do projeto passando. Projeto sem framework de teste para antes da primeira fatia.

**Entrega, em todos os tamanhos:**
- toda implementacao num worktree (`/worktree`, nome `issue-<n>`, branch `wt/issue-<n>`) criado a partir da branch atual; a arvore principal so recebe o merge;
- a issue vai para In progress ao iniciar a implementacao;
- PR com `Refs #N` e base na branch de origem, espera o CI se houver e faz o merge com squash;
- depois do merge, a issue vai para Done se todo criterio de aceite foi provado por teste automatizado, e para In review se nao foi;
- CI vermelho ou conflito param o fluxo com o PR aberto;
- o relatorio termina com a URL da issue.

Passo a passo na skill (secao "Entrega e estados", F5.1 e F8).

**Plano formal (`Plan` opus + advisor) so em L e XL.** Na M, a propria sessao escreve de 3 a 6
linhas de fatias a partir do que leu na F2. Se uma fatia pedir decisao de desenho que nao cabe numa
linha, ou passar de 6 fatias, a issue e L. Em nenhum tamanho o plano vai para o chat: fica no
handoff, e a sessao diz so quantas fatias sao.

## 4. Handoff

- Arquivo: `.claude/handoff/<issue>.md` do **checkout principal**, ignorado pelo git, sempre por caminho absoluto, porque a issue roda num worktree (que tem o proprio `.claude/` e some no fim). Sobrevive a `/clear` e a troca de sessao.
- Cabecalho: `issue`, `tamanho`, `modelo` (o recomendado), `proxima-fase`, `base`, `worktree` e `branch`. E ele que deixa uma sessao nova retomar de onde a anterior parou.
- Secoes: `## Achados` (caminho:linha, decisoes e respostas da F3), `## Fatias` (M, escrita pela sessao) ou `## Plano` (L/XL, do `Plan`, depois do advisor), e em L/XL um `## Handoff — fatia <n>` por fatia, no formato que o `implementer` devolve.
- Serve a dois usos: passar o estado entre `implementer` (L/XL) e trocar de modelo ou retomar depois de `/clear` (qualquer tamanho).
- O handoff e um resumo: quem retoma le o codigo atual e o codigo vence.
- Ao terminar a issue, o arquivo pode ser apagado. O que importa para o futuro vai para `docs_projeto/`.

## 5. O advisor

Se o advisor estiver ligado (`/advisor <modelo>`), ele e consultado em so tres momentos:

1. Antes de executar o plano de uma issue L ou XL. A M nao tem plano formal e nao consulta aqui.
2. Quando o mesmo erro se repete: antes da terceira tentativa.
3. Antes de declarar a issue concluida, com o trabalho ja commitado.

Cada consulta le a conversa inteira, a um preco por token maior que o do Opus. Por isso, so nestes tres momentos.

## 6. Revisao: quando e por que

O `reviewer` e obrigatorio em L/XL e em qualquer tamanho que toque codigo sensivel. Num projeto
derivado, duas revisoes independentes de um diff de login com TOTP, ja com CI verde, acharam:
uma corrida que contornava o bloqueio, uma sessao que sobrevivia a troca de senha, um token no
log do proxy e uma regra de planta ignorada. Teste verde nao substitui leitura adversaria.
Fora desses casos, revisar nao compensa: numa M sem codigo sensivel a revisao foi 16% do custo.

## 7. Medicao: M com e sem subagentes

Em 2026-10-29 a mesma issue M (a statusline mostrar a fase da `/issue` e o modelo recomendado: 3
arquivos de codigo, testes e doc) rodou uma vez em cada modo, ambos em Sonnet, com o mesmo avaliador
(23 criterios de aceite) e custo calculado dos transcripts, com precos calibrados pelo `costUSD`
oficial. O fluxo antigo era `explorer`, `implementer` por fatia e sessao orquestradora.

| | Com subagentes | Sessao unica |
|---|---|---|
| Custo | US$ 1,95 (US$ 2,95 com a sessao em Opus) | US$ 1,02 (~1,10 se fosse a sessao principal) |
| Chamadas ao modelo | 50 | 27 |
| Tokens de contexto processados | 3,92 M | 2,49 M |
| Tempo | 9,7 min | ~6 min |
| Aceite do avaliador | 23/23 | 23/23 |
| Testes novos | 24 | 21 |

Por que a sessao unica saiu mais barata: o orquestrador relia o proprio contexto (73 mil → 135 mil
tokens) enquanto cada `implementer` pagava o dele; quatro agentes regravaram ~48 mil tokens de
preambulo (~US$ 0,28, 14% do total); e um briefing sem a string literal fez a fatia 2 sair errada e
voltar para correcao. A sessao unica nao perde nada no repasse.

Limites da medida: uma execucao por modo; o fluxo com subagentes rodou primeiro e o orquestrador
ja conhecia o codigo (o que o favorece); a sessao unica rodou como subagente, com preambulo menor
(corrigido acima), e fez uma revisao opcional que custou US$ 0,17; perguntas, PR e merge ficaram de
fora; L/XL e a troca de modelo nao foram medidos. A sessao unica marcou so 4 das 8 fases em texto
livre, por isso a fase vai para a barra e nao para o chat.

Resolvido: testes da statusline que registravam uma issue sem cache faziam o `statusline.js`
disparar o `atualizar-board.js`, que chamava o `gh` de verdade (houve uma consulta de leitura num
repo inexistente). `HALCYON_STATUSLINE_OFFLINE=1` desliga o `gh` e os testes ja a definem
(`docs_projeto/STATUSLINE.md`).

## Adaptacao local

> Projeto derivado: descreva aqui o que muda no fluxo — board e IDs de status, submodulos e ordem
> de commit, portao de teste, onde fica a bancada. A skill `/issue` le esta secao e ela vence o
> roteiro generico. No template, fica vazia.
