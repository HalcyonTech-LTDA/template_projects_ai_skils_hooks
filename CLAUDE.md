# CLAUDE.md

Instrucoes para o Claude Code neste repositorio.

## Hooks ativos

`.claude/settings.json` define um hook `UserPromptSubmit` que injeta as regras
do projeto a cada prompt do usuario. O script vive em
`.claude/hooks/inject-rules.js` (Node, cross-platform).

Para inspecionar o que e injetado:
```
echo "{}" | node .claude/hooks/inject-rules.js
```

## Regras de comportamento (resumo)

1. Consultar skills em `.claude/skills/` antes de qualquer tarefa
2. Atualizar `docs_projeto/` ao final de mudancas e quando absorver referencias novas
3. Minimo de 5 perguntas via AskUserQuestion (exceto leitura factual)
4. Atuar como advogado do diabo: criticar, invalidar, oferecer caminhos alternativos
5. Atencao a complexidade, organizacao de pastas e arquitetura limpa
6. Ingerir referencias citadas pelo usuario para `docs_projeto/referencias/`

Detalhes completos em `docs_projeto/HOOKS.md`.

## Skills de fluxo

Duas skills governam como o trabalho entra no repositorio:

| Skill | Quando |
|---|---|
| `/commit` | Gerar a mensagem e criar o commit. Le a convencao do proprio repositorio (`docs_projeto/COMMITS.md`, depois `CLAUDE.md`, depois o historico) antes de propor tipo e escopo. Nunca roda `git add` por conta propria. |
| `/worktree` | Rodar tarefas independentes em paralelo, uma janela `claude` por tarefa, com merge de volta serializado por fila. |

A skill `/worktree` traz os proprios scripts em
`.claude/skills/worktree/scripts/` e funciona sem `package.json`: sem projeto Node
ela apenas nao roda portao nenhum. Worktrees nascem em `.claude/worktrees/`, que e
ignorado pelo git.

## MCPs

`docs_projeto/MCPS.md` e o catalogo curado de servidores MCP para projetos derivados:
nucleo, opcionais, anti-lista, politica de segredo e de escopo. Ficha tecnica de cada
servidor em `docs_projeto/referencias/mcp-*.md`.

Duas regras que valem antes de ligar qualquer coisa:

- **3 a 6 servidores ativos por projeto.** Toda tool de todo MCP ligado entra no prompt de
  toda sessao, usada ou nao.
- **Antes de instalar, veja se uma tool nativa ja resolve.** `filesystem`, `git`, `fetch` e
  `shell` duplicam Read/Edit/Bash/WebFetch e sao custo puro — ver a anti-lista na secao 5.

`.mcp.json.example` na raiz traz o nucleo comentado. Copie para `.mcp.json` e apague o que
o projeto nao usa. Segredo nunca entra no `.mcp.json`: use OAuth ou o bloco `env` do
`.claude/settings.local.json` com `${VAR}`.

Como as skills, este catalogo e **fonte canonica** — correcao comeca aqui.

## Skills

`.claude/skills/` tem 49 skills. Skill nao custa contexto por sessao (so a `description`
entra no prompt), mas **colide por gatilho**: mais de 15 delas descrevem design de interface.

`docs_projeto/SKILLS.md` e o catalogo decisorio — arvore de precedencia de qual usar quando,
quais sao mutuamente exclusivas e quais estao inertes. Leia antes de invocar skill de design.

Duas regras que valem sempre:

- **Uma skill estetica por tarefa.** `minimalist-ui` e `industrial-brutalist-ui` juntas
  produzem output incoerente.
- **Nao rode `npx skills update`.** As 13 skills de `Leonxlnx/taste-skill` sao fork proprio;
  `skills-lock.json` e registro de procedencia, nao mecanismo de atualizacao.

## Este repositorio e a fonte das skills

`template_projetos` e a **origem canonica** de `.claude/skills/`. Alteracao numa
skill comeca aqui e desce por copia para os projetos derivados — nunca o contrario.
Se voce corrigir uma skill dentro de um projeto, replique a correcao aqui na mesma
tarefa, ou ela se perde no proximo projeto criado.

## Estrutura

- `.claude/settings.json` — versionado, hooks publicos
- `.claude/settings.local.json` — ignorado pelo git, config pessoal e bloco `env` com segredos
- `.mcp.json.example` — nucleo de MCPs comentado; copiar para `.mcp.json` e podar
- `.claude/skills/` — skills locais do projeto (fonte canonica)
- `skills-lock.json` — procedencia das skills vindas de `Leonxlnx/taste-skill`; versionado, nao atualizar
- `.claude/worktrees/` — worktrees de agentes, ignorado pelo git
- `docs_projeto/SKILLS.md` — catalogo e precedencia das skills (fonte canonica)
- `docs_projeto/` — documentacao do projeto (atualizar sempre)
