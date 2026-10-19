# Hooks do projeto

Este repositorio versiona tres hooks:

- `UserPromptSubmit` — injeta seis regras obrigatorias em cada mensagem do usuario.
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

### 1. Consulta de skills (por prompt)
Antes de planejar ou agir, o Claude lista as skills em `.claude/skills/` e
invoca a que combinar com a tarefa via Skill tool. O proprio hook lista as
skills disponiveis no contexto injetado (so pastas com `SKILL.md`; `_shared/` e
`obsidian-skills/` ficam de fora) e, se `.claude/agents/` existir, os
subagentes do projeto, apontando a skill `/issue` para tarefa de desenvolvimento
(ver [[AGENTES]]).

### 2. Atualizacao de documentacao
Ao final de qualquer alteracao de codigo, ou quando o usuario citar referencias,
o Claude deve atualizar `docs_projeto/` com o que mudou ou foi aprendido.

### 3. Minimo de 5 perguntas
Para qualquer pedido nao-trivial, o Claude chama `AskUserQuestion` com pelo
menos 5 perguntas cobrindo: escopo, restricoes tecnicas, preferencias,
criterios de aceite e edge cases. Excecoes: leitura factual pura, e issue ou
tarefa que a skill `/issue` classificou como XS ou S — nela o Claude pergunta so
o que for ambiguo (0 a 2 perguntas). A excecao existe porque uma correcao de uma
linha nao justifica 5 perguntas, e cada rodada de perguntas tambem custa contexto.

### 4. Advogado do diabo
Em todo prompt, o Claude critica a abordagem proposta, aponta riscos, invalida
premissas fracas e apresenta no minimo 2 caminhos alternativos com tradeoffs.

### 5. Qualidade arquitetural
Atencao continua a complexidade ciclomatica, organizacao de pastas, separacao
de responsabilidades, arquitetura limpa e abstracao em arquivos coesos.

### 6. Ingestao de referencias
Quando o usuario cita URL, biblioteca ou conceito que o Claude nao domina, ele
ingere via defuddle/WebFetch e salva um resumo em
`docs_projeto/referencias/<slug>.md` antes de prosseguir.

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
`<project-rules>...</project-rules>` para deixar claro de onde veio a injecao.
