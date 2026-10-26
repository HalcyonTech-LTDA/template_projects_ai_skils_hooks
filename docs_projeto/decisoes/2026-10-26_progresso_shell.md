---
title: Plugin progresso-shell no template
type: decisao
status: aprovado
created: 2026-10-26
updated: 2026-10-26
project: template_projetos
tags: [decisao, claude-code, plugin, testes, tema/tooling]
---

# 2026-10-26 — Progresso de testes e shell na linha de status

## O que mudou

1. Plugin novo em `.claude/skills/progresso-shell/` (hooks, parser, 15 testes unitarios)
2. Doc nova: [[../PROGRESSO_SHELL|PROGRESSO_SHELL.md]]
3. `CLAUDE.md`, [[../SKILLS|SKILLS.md]] e o indice de `docs_projeto/` citam o plugin
4. `.gitignore` ignora os tipos que o Claude Code grava em `.claude-plugin/types/`

## Por que

O usuario pediu para ver no proprio Claude Code a fase de um comando em andamento:
`0/12 testes`, `10% de shell`, `1/10 testes unitarios`.

## Alternativas consideradas

| Opcao | Por que nao |
|---|---|
| Hook `PreToolUse` + statusline do template | So texto na statusline e atualizacao lenta (`refreshInterval`) |
| Plugin habilitado por marketplace no `settings.json` | Mais configuracao; a pasta em `.claude/skills/` ja carrega sozinha |

| Desenhar no spinner ("Sauteing...") | Primeira versao. O spinner e redesenhado o tempo todo e o texto aparecia so por um instante |

Escolhido: plugin do Claude Code com `$.ui.status`, a linha fixa embaixo da caixa de escrita.
O resultado do ultimo teste fica ate o proximo. Feito e provado primeiro como mod da sessao e
depois trazido para ca.

## Prova

- `claude plugin test`: 15 testes passam
- `claude plugin validate`: passa; os avisos sao de publicacao (README, licenca, icone)
- Sessao nova `claude -p` dentro do worktree: o plugin carregou de `.claude/skills/` e gravou
  o log do Bash
- Wrapper no Git Bash: saida intacta, codigo de saida preservado, `cd` mantido
- `tsc --noEmit` no plugin: sem erros
- O usuario viu o progresso de uma suite `node --test` no spinner (versao 1)

## Nao provado

- Pedido de permissao extra no modo padrao com regras `Bash(...)`
- Ferramenta PowerShell (fora do escopo)
