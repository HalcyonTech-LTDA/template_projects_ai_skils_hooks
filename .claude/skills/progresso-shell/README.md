# progresso-shell

Plugin do Claude Code (nao e skill). Fixa embaixo da caixa de escrita o progresso do comando Bash em
andamento: `▶ Testes unitários 4/12 · 1 falha`, `▶ Shell 45%`, `✔ Testes 12/12`.

Carrega sozinho por estar em `.claude/skills/progresso-shell/`. Para levar a um projeto
derivado, copie a pasta inteira.

```bash
claude plugin validate .claude/skills/progresso-shell
claude plugin test .claude/skills/progresso-shell
```

Como funciona, limites e como estender: `docs_projeto/PROGRESSO_SHELL.md`.
