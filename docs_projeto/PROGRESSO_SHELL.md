---
title: Progresso de testes e shell na linha de status
type: convencao
status: aprovado
created: 2026-10-26
updated: 2026-10-26
project: template_projetos
tags: [convencao, claude-code, plugin, testes, tema/tooling]
---

# Progresso de testes e shell na linha de status

O plugin `progresso-shell` fixa embaixo da caixa de escrita do Claude Code uma linha com o
progresso do comando Bash em andamento (`$.ui.status`, ao lado dos avisos do proprio Claude
Code; nao mexe na statusline de `.claude/statusline/`):

| Situacao | A linha mostra |
|---|---|
| Runner imprime o total antes (pytest, cargo, TAP com `1..N`) | `▶ Testes unitários 4/12 · 1 falha` |
| Total so no fim (vitest, node --test, Gradle, Go, Maven por classe) | `▶ Testes 9 feitos · 1 falha`; no resumo final vira `12/12` |
| jest no reporter padrao (so arquivos ao vivo) | `▶ Testes · 3 arquivos` |
| Shell cuja saida traz percentual (npm install, docker build, curl) | `▶ Shell 45%` |
| Shell sem percentual | `▶ Shell · 230 linhas` |
| Teste terminou | `✔ Testes 12/12` ou `✖ Testes 12/12 · 1 falha`, fixo ate o proximo comando ou prompt |

O shell comum some ao terminar, e o proximo comando ou prompt apaga o resultado de teste. Ao
recarregar, o plugin limpa a linha que uma versao anterior tenha deixado. O rotulo sai
do comando: `e2e`, `playwright` ou `cypress` vira **Testes e2e**; `integra`, **Testes de
integração**; `unit`, **Testes unitários**; o resto, **Testes**.

So conta como teste o comando que **comeca** com o runner, em qualquer elo de `&&`, `;` ou `|`,
depois de variaveis (`FOO=1`) e de um lancador (`npx`, `python -m`, `uv run`, `poetry run`).
Runner citado entre aspas ou em heredoc nao conta: `git commit -m "add pytest"` e shell. Um
teste que termina sem contar nada (`0/?`) nao vira resultado fixo; a linha volta ao anterior.

A primeira versao desenhava no spinner ("Sauteing..."), mas o spinner e redesenhado o tempo
todo e o texto aparecia so por um instante. A linha de status fica parada.

## Onde mora e como carrega

`.claude/skills/progresso-shell/` e um **plugin**, nao uma skill: nao tem `SKILL.md`. O Claude
Code carrega sozinho um plugin que esteja em `.claude/skills/<nome>/` do projeto, sem
`settings.json` nem `/plugin install`. Copiar a pasta para um projeto derivado basta.

| Arquivo | Papel |
|---|---|
| `.claude-plugin/plugin.json` | Manifesto |
| `hooks/register.tsx` | Hooks: `tool.call` no Bash (embrulha, le o log a cada 1 s), `prompt.submit` e `session.start` (limpam) |
| `hooks/parse.ts` | Funcoes puras: classifica o comando, embrulha, le a saida, monta o texto |
| `hooks/parse.test.ts` | Testes unitarios do parser, com regressoes |
| `types/index.d.ts` | Tipos `Job` e `Progress` |

## Como funciona

Nenhum hook ve a saida do Bash enquanto ele roda: so o comando antes e o resultado no fim.
Por isso o plugin reescreve o comando para gravar a saida num log e le esse log a cada 1 s:

```bash
{ <comando>
} > >(tee '<TEMP>/claude-progresso/<tool_use_id>.log') 2>&1; __cc_rc=$?; wait $! 2>/dev/null; (exit $__cc_rc)
```

- O grupo `{ }` roda no shell atual: `cd` continua valendo e `exit` sai como antes.
- O codigo de saida do comando volta intacto; `wait $!` espera o `tee` esvaziar.
- stdout e stderr chegam juntos ao Claude (`2>&1`).
- Nao embrulha: `run_in_background`, comando com `&` solto (servidor em segundo plano), `exec`,
  comando vazio. Nesses casos a linha nao muda.
- Se o plugin falhar antes de chamar o Bash, o comando roda sem embrulho (falha aberta).

## Limites

- **So a ferramenta Bash.** Testes rodados pela ferramenta PowerShell nao mostram progresso.
- **Permissao:** a checagem pode ver o comando reescrito. No modo auto nao houve pedido extra;
  no modo padrao, regra como `Bash(npm test:*)` pode deixar de casar. Nao provado.
- **Total so quando o runner imprime.** Sem total, a linha conta os feitos.
- Dois Bash em paralelo: a linha segue o mais recente.
- O log fica em `%TEMP%/claude-progresso/` e e esvaziado no fim de cada comando.

## Testar e validar

```bash
claude plugin validate .claude/skills/progresso-shell
claude plugin test .claude/skills/progresso-shell
```

O repositorio nao tem `package.json`; estes dois comandos sao o portao do plugin. A API de
plugins do Claude Code esta em acesso antecipado e pode mudar entre versoes: rode os dois
depois de atualizar o Claude Code.

## Desenvolver

Edite os arquivos e o Claude Code recarrega o plugin quando o turno termina. Um parser novo
entra em `hooks/parse.ts` com o teste correspondente em `hooks/parse.test.ts`. O `validate`
exige que `$` so seja passado a funcoes declaradas no topo do arquivo. Os tipos que o Claude
Code grava em `.claude-plugin/types/` sao ignorados pelo git.

Decisao em [[decisoes/2026-10-26_progresso_shell]].
