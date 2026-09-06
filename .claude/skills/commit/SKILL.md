---
name: commit
description: Cria commits git bem formatados seguindo Conventional Commits, lendo os escopos, guardas de path e checagens do proprio repositorio. Use quando o usuario pedir /commit, "commita", "faz o commit", "gera a mensagem de commit" ou similar.
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
version: 2.0
---

# Git Commit

Gera e cria commits Conventional Commits a partir do que **ja esta staged**.

## Contrato desta skill

| Decisao | Comportamento |
|---|---|
| Staging | **Nunca** roda `git add`. So analisa `git diff --staged`. Vazio -> para e avisa. |
| Aprovacao | Mostra a mensagem e **espera confirmacao** antes de `git commit`. |
| Diff misto | Propoe split em varios commits; o usuario decide. |
| Checagens | Roda o que o repo oferecer e **reporta**; falha nao bloqueia o commit. |
| Idioma | Descricao em ingles, imperativo, minuscula, sem ponto final. |
| Rodape | Segue a convencao do repositorio (ver passo 0). |

---

## 0. Carregar a convencao do repositorio (sempre primeiro)

Esta skill nao carrega escopos nem guardas embutidos. Ela **le do repo**, nesta ordem:

1. `docs_projeto/COMMITS.md` — se existir, e a fonte canonica: tipos, escopos,
   guardas de path, rodape.
2. `CLAUDE.md` — secao sobre commits, se houver.
3. Derivar: `git log --oneline -40 --format='%s'` mostra os tipos e escopos que o
   repo ja usa. Siga o padrao existente em vez de inventar um novo.

Se nenhuma fonte existir, use Conventional Commits puro e escopos derivados da
estrutura de pastas de primeiro nivel.

## 1. Coletar estado

```bash
git status --short
git diff --staged --stat
git diff --staged
git log --oneline -10 --format='%s'
```

Se `git diff --staged --stat` vier vazio: pare, mostre `git status --short` e diga
que nada esta staged. **Nao** stageie nada por conta propria.

## 2. Guardas de path (bloqueante)

Recuse o commit se algum path staged cair em uma destas categorias:

| Categoria | Exemplos tipicos |
|---|---|
| Build gerado | `dist/`, `build/`, `android/`, `ios/`, `.expo/`, `*.tsbuildinfo` |
| Dependencias | `node_modules/`, `vendor/`, `.venv/` |
| Segredos e credenciais | `.env*`, `*.keystore`, `*.pem`, `id_rsa`, `*.p12` |
| Config pessoal | `.claude/settings.local.json`, `.vscode/settings.json` pessoal |
| Arvores read-only | qualquer repo/pasta que o `CLAUDE.md` declare somente-leitura |

As guardas especificas deste repositorio estao na fonte carregada no passo 0 e
**tem precedencia** — elas costumam existir por um motivo forte (certificacao,
metrologia, licenciamento), nao por estilo. Nomeie o motivo ao recusar.

Confirme com `git check-ignore -v <path>` antes de acusar um arquivo de ser gitignored.

## 3. Escolher tipo e escopo

**Tipos:** `feat` `fix` `docs` `style` `refactor` `test` `chore` `perf` `build` `ci` `revert`

**Escopo:** derive do path dominante do diff, usando a tabela do passo 0. Sem
tabela, use o primeiro segmento significativo do path (`src/core/nfc/` -> `nfc`,
`src/features/checkout/` -> `checkout`).

Escopo e opcional quando o diff e realmente transversal. **Nunca invente um escopo
que nao exista no repo.**

## 4. Detectar diff misto

Agrupe os paths staged por escopo. Se houver **mais de um grupo sem relacao
causal** (uma feature e a doc dela **estao** relacionadas; um fix em `auth` e um
refactor em `ui` **nao** estao), proponha o split:

```
Diff staged cobre 3 assuntos. Sugestao de split:

1. fix(nfc): guard against stale mailbox replies
   src/core/nfc/mailbox.ts, __tests__/core/nfc/mailbox.test.ts
2. refactor(ui): extract StatusPill from ParametersScreen
   src/ui/components/StatusPill.tsx, src/features/.../ParametersScreen.tsx
3. docs(testes): registra TP-009
   docs_projeto/.../TP-009_*.md

Aplico o split (reset + add por grupo) ou commito tudo junto?
```

Se o usuario aceitar, execute grupo a grupo:
`git reset` -> `git add <paths do grupo>` -> `git commit -m ...` -> proximo grupo.
Reencadear o staging assim e a **unica** situacao em que esta skill roda `git add`,
e sempre com paths explicitos, nunca `-A`.

## 5. Rodar as checagens (nao bloqueantes)

Pule se o diff staged so toca documentacao, `.claude/` ou `*.md`.

Descubra o que rodar a partir do `package.json` (ou do equivalente da stack):
script `typecheck` -> `npm run typecheck`; senao `tsconfig.json` -> `npx tsc --noEmit`;
script `test` -> `npm test`. Sem `package.json` ou sem dependencias instaladas,
nao ha checagem e isso deve ser dito.

Reporte o resultado em uma linha cada (`tsc: ok` / `jest: 32 suites, 724 testes, ok`).
Se falhar, **mostre a saida relevante** e diga explicitamente que esta commitando
mesmo assim — nunca esconda uma falha.

## 6. Verificar a documentacao

Muitos repositorios exigem que mudanca de codigo venha com a doc. Se a convencao
carregada no passo 0 (ou o `CLAUDE.md`) disser isso, e o diff tocar codigo sem
tocar a pasta de documentacao, avise antes de commitar:

> O diff mexe em `src/core/nfc/` mas nada na documentacao. A convencao do repo
> pede a doc junto. Quer que eu atualize antes, ou commito assim?

Aviso, nao bloqueio. A decisao e do usuario.

## 7. Montar a mensagem

```
<tipo>(<escopo>): <descricao em ingles, imperativo, <= 72 chars>

<corpo opcional: bullets com "- ", o PORQUE, nao o o-que>

<rodape opcional: BREAKING CHANGE:, Refs: ADR-00XX, Closes #N>
```

Regras da descricao:
- Imperativo (`add`, `fix`, `move`), nao `added`/`adds`.
- Minuscula inicial, sem ponto final.
- Descreve o efeito, nao o arquivo. `fix(nfc): retry only idempotent reads`,
  nao `fix(nfc): update mailbox.ts`.

Use o corpo quando o **porque** nao for obvio no diff. Cite a decisao quando
existir: `Refs: ADR-0011`, `Refs: RISCO-006`.

**Rodape de coautoria:** siga o repositorio. Se a convencao carregada no passo 0
proibir `Co-Authored-By` / `Generated with Claude Code`, nao os inclua; se o
historico do repo usar, mantenha. Na duvida, pergunte uma vez.

## 8. Confirmar e commitar

Mostre a mensagem final em bloco de codigo, com a lista de arquivos, e espere OK.
So entao:

```bash
git commit -m "$(cat <<'MSG'
feat(param): read calibration sheet from holding registers

- map sheet rows to the word order the firmware forces
- cap reads at the response buffer limit

Refs: ADR-0011
MSG
)"
```

Depois: `git log -1 --stat` para confirmar, e **pare**. Nao faca `git push`
a menos que o usuario peca.

---

## Nunca faca

- `git add -A` / `git add .` fora do fluxo de split aprovado.
- `git commit --no-verify` ou `--no-gpg-sign` sem o usuario pedir.
- `git commit --amend` em vez de um commit novo, salvo pedido explicito.
- `git push` sem pedido explicito.
- Commitar com o repo em rebase/merge sem avisar (`git status` mostra).
- Inventar escopo, tipo ou rodape que o repositorio nao usa.

## Exemplos

```
feat(nfc): enhance diagnostics and metrics tracking for NFC operations
```
```
fix(modbus): read back every write before reporting success

Out-of-range values are silently clamped and a write blocked by the
write-enable gate still returns the success echo.

Refs: CommInt/ModbusWrite.c:550-551,753-755
```
```
test(nfc): cover stale-reply detection in the fake adapter
```
```
docs(testes): registra TP-009, prova do livelock de bytes ISO
```
```
chore(claude): add the /worktree skill
```
