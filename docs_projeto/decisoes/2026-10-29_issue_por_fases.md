---
title: Issue por fases, sessao unica ate M e troca de modelo por handoff
type: decisao
status: aprovado
created: 2026-10-29
updated: 2026-10-29
project: template_projetos
tags: [decisao, agentes, custo, issue, statusline, tema/tooling]
---

# 2026-10-29 — Issue por fases, sessao unica ate M e troca de modelo por handoff

Ajusta [[2026-10-15_classificacao_sonnet_e_plano_l_xl]] e [[2026-10-18_issue_entrega_e_estados]].

## O que mudou

1. **Fases.** A `/issue` (v2.0) anda por F1 Classificar, F2 Explorar, F3 Perguntar, F4 Planejar, F5 Implementar, F6 Testar, F7 Revisar e F8 Fechar. O tamanho decide quem executa cada uma.
2. **XS a M numa sessao so, em Sonnet, sem subagentes.** Nem `explorer`, nem `implementer`, nem `worker`. A classificacao deixa de ser do `explorer` em Sonnet e passa a ser da sessao (corpo, label e um Grep/Glob).
3. **L e XL mantem** `Plan` opus, `implementer` por fatia, `worker` e `reviewer` obrigatorio, e `explorer` em Haiku na F2.
4. **Fase na barra.** A skill grava `issue.js fase Fn --modelo <rec>` no mesmo Bash do primeiro comando de cada fase, no lugar de marcador em texto. `--modelo` e o recomendado para a sessao: `sonnet` em XS a M, `opus` em L e XL.
5. **Modelo so troca por `/clear` e handoff.** O cache e por modelo. O handoff ganha cabecalho (`tamanho`, `modelo`, `proxima-fase`, `base`, `worktree`, `branch`) e `## Achados`, e `/issue .claude/handoff/<issue>.md` retoma dali.
6. Arquivos: `.claude/skills/issue/SKILL.md`, `.claude/agents/implementer.md`, `.claude/statusline/` (comando `fase`, `lib/fase.js`), [[../AGENTES|AGENTES.md]], [[../ECONOMIA|ECONOMIA.md]], [[../STATUSLINE|STATUSLINE.md]] e `CLAUDE.md`.

## Por que

- Uma M rodada nos dois modos, mesma tarefa e mesmo avaliador: US$ 1,95 com subagentes contra US$ 1,02 em sessao unica (-47%, ~-44% corrigindo o preambulo), 50 contra 27 chamadas, 9,7 contra ~6 min, 23/23 nos dois. Tabela e limites em [[../AGENTES|AGENTES.md]] secao 7.
- O fluxo com subagentes paga dois contextos ao mesmo tempo (o do orquestrador e o de cada `implementer`), regrava ~48 mil tokens de preambulo por agente novo (~US$ 0,28) e perde informacao no repasse (uma string literal ficou fora do briefing e a fatia voltou).
- Marcador de fase em texto livre cobriu 4 das 8 fases; a barra e consultavel e o aviso `⚠` mostra o modelo errado sem custo de contexto.
- `/model` no meio da sessao regrava o contexto no preco do modelo novo. Estimativa: ~US$ 0,79 com 100 mil tokens em Opus, contra ~US$ 0,24 do preambulo de um `implementer`.

## Decisoes do usuario

- XS a M: sessao unica em Sonnet, com fases nomeadas, e o fluxo gravando a fase na barra com `issue.js fase` em vez de marcador em texto.
- L e XL: manter subagentes por fatia e revisor.
- Trocar de modelo: so com `/clear` e handoff.

## Riscos aceitos

- **Uma execucao por modo.** A direcao e clara, o percentual nao. Repetir 3 vezes daria a variancia.
- **L e XL nao foram medidos.** Num contexto bem maior, isolar fatias pode compensar mais, ou menos; a regra de manter subagentes ali e uma hipotese. A sessao `opus` em L/XL vem da pratica atual, nao de medicao: uma sessao Sonnet orquestrando subagentes Opus sairia mais barata e nao foi testada.
- **O custo da troca de modelo e estimativa**, calculada pelos precos calibrados, nao medida.
- **A sessao unica depende do modelo certo.** A barra avisa com `⚠`, mas nada impede de seguir no modelo errado; a skill so avisa que sai mais caro.
- **Fase sem Bash nao grava** (F3, F4): a barra pode ficar uma fase atras.

## Consequencias

- Projetos derivados continuam no fluxo antigo ate alguem copiar `.claude/skills/issue/`, `.claude/statusline/`, `.claude/agents/implementer.md` e os docs acima.
- Resolvido depois, fora desta decisao: testes que registravam uma issue sem cache faziam a statusline disparar o `gh` de verdade; `HALCYON_STATUSLINE_OFFLINE=1` desliga a rede nos testes ([[../AGENTES|AGENTES.md]] secao 7).
