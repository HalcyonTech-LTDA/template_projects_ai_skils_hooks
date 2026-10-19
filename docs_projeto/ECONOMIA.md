---
title: Economia de contexto
type: convencao
status: aprovado
created: 2026-10-18
updated: 2026-10-18
project: template_projetos
tags: [convencao, custo, tokens, claude-code, tema/tooling]
---

# Economia de contexto

Como gastar menos token por tarefa. Vale na sessao principal e em todo subagente. A regra 2 do
hook (`inject-rules.js`) e o lembrete curto; este arquivo e o detalhe.

> **Este arquivo e a fonte canonica.** Como [[AGENTES]], a correcao comeca aqui e desce por copia
> para os projetos derivados.

## 1. De onde vem o custo

O modelo nao guarda memoria entre chamadas. Cada chamada (cada ida e volta de ferramenta) reenvia
o contexto inteiro: prompt do sistema, `CLAUDE.md`, descricoes de skills, agentes e tools, a
conversa e todo resultado de ferramenta ate ali.

O *prompt caching* da API evita reprocessar o **comeco identico** desse texto. Ele fica no
servidor, vale para a sessao e expira (5 min no padrao, 1 h em algumas contas). Nao e cache do
projeto: `/clear` ou sessao nova gravam o preambulo de novo.

| Tipo de token | Preco relativo a entrada normal |
|---|---|
| Leitura de cache | ~0,1x |
| Gravacao de cache | 1,25x (prazo de 5 min) ou 2x (prazo de 1 h) |
| Saida | a mais cara por token, mas pequena em volume |

A conta e **chamadas x tamanho do contexto**. Medicao de 2026-10-18, numa tarefa M deste repo:

- 8,55 M tokens no total; 7,19 M (84%) foram leitura de cache: 51 chamadas de ~145 mil cada.
- A saida do modelo foi 0,06 M. O trabalho em si quase nao pesa.
- A sessao comecou com 72 mil tokens antes de qualquer trabalho e terminou perto de 200 mil.

A statusline soma tokens brutos ([[STATUSLINE]]); o custo real e menor, mas a cota de uso conta.

## 2. Menos chamadas

E a alavanca principal.

- **Leituras independentes numa so resposta**, em paralelo, nunca uma por turno.
- **Varias checagens num unico Bash**: `git status`, `grep` e `wc` no mesmo comando.
- **Nao reler o que ja esta na conversa**, nem conferir um arquivo logo depois do Edit: o Edit
  falha se nao aplicar.
- **Ler so o trecho necessario**: `offset`/`limit` ou `grep -n` em vez do arquivo inteiro.
- **Mudanca mecanica em varios arquivos e um script**, nao N chamadas de Edit.
- **Nao narrar opcoes que nao vai seguir.** A saida tambem vira contexto relido.

## 3. Contexto menor

- **Uma tarefa por sessao**, `/clear` entre tarefas; `/compact` quando passar de ~120 mil tokens.
- **Hook por prompt curto.** O texto de um `UserPromptSubmit` acumula a cada prompt. O
  `inject-rules.js` tinha 5,3 KB (com a lista de skills que o prompt do sistema ja traz) e caiu
  para 0,7 KB.
- **`CLAUDE.md` so com o essencial.** O resto vai para arquivo lido sob demanda, com link.
  `CLAUDE.md` de pasta-mae entra em todo projeto abaixo dela.
- **3 a 6 MCPs ativos** ([[MCPS]]).

## 4. Modelo pela tarefa

| Tarefa | Onde roda | Modelo |
|---|---|---|
| Pergunta, edicao pequena, issue XS/S | sessao principal | Sonnet (`/model sonnet`) |
| Issue M | sessao principal + `implementer` | `implementer` sonnet, um por fatia |
| Issue L/XL, decisao de desenho | `Plan` + `implementer` | Opus |
| Busca que varre muitos arquivos | `explorer` | Haiku |
| Uma ou duas leituras | na propria sessao | o que estiver |
| Pesquisa na web | `researcher` | Sonnet |

- **Subagente nao e gratis.** Ele comeca com o proprio preambulo, de dezenas de milhares de
  tokens. Compensa quando a busca levaria muitas chamadas; para uma ou duas leituras, nao.
- **Leitura de cache do Sonnet custa bem menos que a do Opus.** Numa sessao longa, e ali que esta
  a diferenca.
- **`effort` baixo reduz a saida, nao o contexto** ([[AGENTES]] secao 1).
- **Advisor so nos tres momentos** de [[AGENTES]] secao 5, nunca em XS, S ou M.

## 5. Onde a regra vive

- Regra 2 do hook: lembrete a cada prompt nos projetos derivados.
- Este arquivo: o detalhe e os numeros.
- Fora dos derivados, copie o resumo da secao 2 e da 4 para o `~/.claude/CLAUDE.md` da maquina.
