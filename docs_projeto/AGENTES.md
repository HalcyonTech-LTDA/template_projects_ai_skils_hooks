---
title: Agentes e fluxo de issue por tamanho
type: convencao
status: aprovado
created: 2026-10-10
updated: 2026-10-10
project: template_projetos
tags: [convencao, agentes, subagentes, custo, claude-code, tema/tooling]
---

# Agentes e fluxo de issue por tamanho

Este repositorio traz **5 subagentes** em `.claude/agents/` e a skill `/issue`, que os combina
pelo tamanho da tarefa. O objetivo e gastar o modelo caro onde o desenho e o codigo importam, e
o barato na busca e na execucao, sem deixar o contexto crescer sem limite.

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
3. **Um `implementer` novo por fatia**, com o estado num arquivo de handoff, nunca na memoria
   de um agente vivo.
4. **Busca exploratoria vai para o `explorer`** (Haiku), que devolve `caminho:linha` em vez de
   encher a sessao principal com arquivos inteiros.

## 2. Os agentes

| Agente | Modelo | Effort | Ferramentas | Papel |
|---|---|---|---|---|
| `explorer` | haiku | — | Read, Grep, Glob, Bash (so leitura) | Achar onde esta X, quem chama Y. Devolve `caminho:linha` |
| `researcher` | sonnet | medium | Web, leitura, Write (so `referencias/`) | Pesquisa externa com URL em cada afirmacao |
| `worker` | sonnet | medium | todas | Rodar testes, bancada, docs por ficha de fatos. Nao decide desenho, nao commita |
| `implementer` | opus (sonnet em M) | high | todas | Uma fatia de um plano aprovado. So compila; termina com handoff |
| `reviewer` | opus | high | Read, Grep, Glob, Bash (so leitura) | Revisao independente do diff antes do merge |

O planejamento usa o agente embutido `Plan` com `model: opus`. Nao ha arquivo para ele.

**Cada `description` entra em todo prompt de toda sessao**, como as tools de MCP. Crie agente novo so
para um papel que nenhum dos cinco cobre.

**Agente de projeto vence agente de usuario com o mesmo nome** (`~/.claude/agents/`). Nao mantenha
copias globais com estes nomes: elas divergem e so valem fora dos projetos derivados.

## 3. Tamanho e modelo

O tamanho vem da label `size/XS` … `size/XL` da issue. Sem label, a sessao estima pela tabela da
skill `/issue`, declara a escolha e oferece aplicar a label. Na duvida, o maior. Codigo sensivel
(login, autorizacao, segredo, criptografia, dado de cliente) e no minimo M.

| Tamanho | Perguntas | Planejar | Implementar | Testar | Revisar |
|---|---|---|---|---|---|
| XS / S | 0 a 2, so o ambiguo | Na sessao | Na sessao | Sessao ou `worker` | Se sensivel |
| M | 5 ou mais | `Plan` opus | `implementer` sonnet, um por fatia | `worker` | Se sensivel |
| L / XL | 5 ou mais | `Plan` opus | `implementer` opus, um por fatia | `worker` | **Sempre** (`reviewer`) |

A excecao de XS e S as 5 perguntas esta na regra 3 do hook (`HOOKS.md`).

## 4. Handoff entre fatias

- Arquivo: `.claude/handoff/<issue>.md`, ignorado pelo git. Sobrevive a `/clear` e a troca de sessao.
- Secoes: `## Plano` (do `Plan`, depois do advisor) e um `## Handoff — fatia <n>` por fatia, no
  formato que o `implementer` devolve.
- O handoff e um resumo: o `implementer` seguinte le o codigo atual e o codigo vence.
- Ao terminar a issue, o arquivo pode ser apagado. O que importa para o futuro vai para `docs_projeto/`.

## 5. O advisor

Se o advisor estiver ligado (`/advisor <modelo>`), ele e consultado em so tres momentos:

1. Antes de executar o plano de uma issue M, L ou XL.
2. Quando o mesmo erro se repete: antes da terceira tentativa.
3. Antes de declarar a issue concluida, com o trabalho ja commitado.

Cada consulta le a conversa inteira, a um preco por token maior que o do Opus. Por isso, so nestes tres momentos.

## 6. Revisao: quando e por que

O `reviewer` e obrigatorio em L/XL e em qualquer tamanho que toque codigo sensivel. Num projeto
derivado, duas revisoes independentes de um diff de login com TOTP, ja com CI verde, acharam:
uma corrida que contornava o bloqueio, uma sessao que sobrevivia a troca de senha, um token no
log do proxy e uma regra de planta ignorada. Teste verde nao substitui leitura adversaria.

## Adaptacao local

> Projeto derivado: descreva aqui o que muda no fluxo — board e IDs de status, submodulos e ordem
> de commit, portao de teste, onde fica a bancada. A skill `/issue` le esta secao e ela vence o
> roteiro generico. No template, fica vazia.
