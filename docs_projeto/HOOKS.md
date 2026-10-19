# Hooks do projeto

Este repositorio versiona tres hooks:

- `UserPromptSubmit` — injeta quatro regras curtas (~0,7 KB) em cada mensagem do usuario.
- `UserPromptSubmit` — `.claude/statusline/hook-capturar-issue.js`: prompt que comeca com
  `/issue <ref>` liga a sessao a issue na statusline. Qualquer outro prompt sai com 0 e sem saida.
  Detalhes em [[STATUSLINE]].
- `PostToolUse` — depois de todo Write/Edit, confere o teto de 300 linhas da documentacao.

## Arquivos

| Caminho | Papel |
|---|---|
| `.claude/settings.json` | Registra os hooks, versionado no git |
| `.claude/hooks/inject-rules.js` | Script Node cross-platform que monta o lembrete |
| `.claude/hooks/limit-doc-lines.js` | Script Node que confere o teto de linhas dos docs |
| `.claude/statusline/hook-capturar-issue.js` | Liga a sessao a issue de `/issue <ref>` para a statusline ([[STATUSLINE]]) |
| `.claude/settings.local.json` | Configuracoes pessoais, **ignoradas pelo git** |

## Regras injetadas

O texto injetado e relido em toda chamada da sessao e acumula a cada prompt. Por isso ele
cabe em quatro linhas e o detalhe fica aqui. Ate 2026-10-18 eram seis regras em 5,3 KB, com a
lista de skills e agentes que o prompt do sistema ja traz ([[ECONOMIA]]).

### 1. Skills e fluxo
O Claude usa a skill que combinar com a tarefa. Tarefa de desenvolvimento passa pela `/issue`,
que escolhe agente e modelo pelo tamanho ([[AGENTES]]). Frente de trabalho no GitHub (marcos,
sequencia, bloqueios) passa pela `/trilha`. O hook nao lista as skills: elas ja estao no prompt do
sistema, com descricao.

### 2. Economia
Poucas chamadas por tarefa: leituras independentes numa so resposta, varias checagens num unico
Bash, nada de reler o que ja esta na conversa. Modelo escolhido pelo tamanho da tarefa. Detalhe e
numeros em [[ECONOMIA]].

### 3. Perguntas e alternativas, pelo tamanho
O Claude pergunta so o que for ambiguo. Em tarefa M ou maior (criterio da `/issue`), chama
`AskUserQuestion` com pelo menos 5 perguntas (escopo, restricoes tecnicas, estilo, criterios de
aceite e edge cases) e, antes de executar, critica a abordagem e apresenta 2 alternativas com
tradeoffs. Em XS e S, de 0 a 2 perguntas e nenhuma rodada de alternativas: uma correcao de uma
linha nao justifica o turno extra, e cada turno custa contexto.

### 4. Qualidade e documentacao
Funcoes pequenas, modulos coesos, separacao de responsabilidades; funcao monolitica e quebrada
em modulos. Referencia que o Claude nao domina (URL, biblioteca, conceito) e ingerida e resumida
em `docs_projeto/referencias/<slug>.md`. Toda mudanca termina com `docs_projeto/` atualizado.

## Teto de linhas da documentacao (PostToolUse)

`CLAUDE.md` e todo `.md` de `docs_projeto/` tem no maximo **300 linhas** (regra em
[[CONVENCOES|CONVENCOES.md]] secao 7). O hook roda com matcher `Write|Edit`, le o
`file_path` do payload e:

- arquivo fora do escopo, ou dentro do teto → sai com 0, silencioso;
- arquivo no escopo acima de 300 linhas → escreve no stderr qual arquivo e quantas
  linhas, e sai com **codigo 2**. A escrita ja aconteceu; o codigo 2 devolve a mensagem
  ao Claude, que deve dividir o arquivo antes de seguir.

Foi escolhido `PostToolUse` e nao `PreToolUse` porque dividir um arquivo exige escrever
um pedaco de cada vez: bloquear a escrita travaria a propria correcao. E foi escolhido
hook e nao uma setima regra no `inject-rules.js` porque a regra textual custa contexto
em todo prompt e nao confere nada.

Skills e agentes ficam fora: muitas skills sao fork de terceiros com centenas de linhas.

## Como testar localmente

```powershell
echo "{}" | node .claude/hooks/inject-rules.js
node .claude/hooks/limit-doc-lines.js --all
echo '{"session_id":"x","prompt":"/issue 1","cwd":"."}' | node .claude/statusline/hook-capturar-issue.js
```

A primeira saida e o bloco de regras injetado em cada turno. A segunda lista os docs
acima do teto (codigo 1) ou confirma que nenhum passou (codigo 0).

## Como desativar temporariamente

Edite `.claude/settings.json` e remova o bloco `UserPromptSubmit`, ou use
`/hooks` no Claude Code para gerenciar interativamente. Nao apague o script
`inject-rules.js` — ele pode ser util mais tarde.

## Como estender

Para adicionar uma nova regra, edite a string `rules` em
`.claude/hooks/inject-rules.js`. Mantenha o conteudo dentro do bloco
`<project-rules>...</project-rules>` para deixar claro de onde veio a injecao. Cada linha
nova custa em toda chamada de toda sessao: prefira detalhar aqui e deixar no hook so a frase.
