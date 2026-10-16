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

## Teto de 300 linhas na documentacao

`CLAUDE.md` e todo `.md` de `docs_projeto/` tem **no maximo 300 linhas**. Passou, divida:
secao mais autonoma vai para arquivo irmao, resumo com link fica no lugar. Um hook
`PostToolUse` (`.claude/hooks/limit-doc-lines.js`) confere depois de todo Write/Edit e
devolve o erro na hora. Skills e agentes ficam fora. Regra em `docs_projeto/CONVENCOES.md`
secao 7; varredura completa com `node .claude/hooks/limit-doc-lines.js --all`.

## Skills de fluxo

Quatro skills governam como o trabalho entra no repositorio:

| Skill | Quando |
|---|---|
| `/trilha` | Planejar e controlar uma frente de trabalho no GitHub: epico, marcos (milestones), issues em sequencia, dependencias nativas (blocked by), progresso dos marcos e checagem de deriva do board. So issues, nunca draft. IDs do board em `docs_projeto/BOARD.md`. |
| `/issue` | Conduzir uma issue ou tarefa de desenvolvimento do comeco ao merge. Classifica o tamanho (label `size/*` ou estimativa declarada) e escolhe subagente e modelo por ele. Usa `/worktree` e `/commit` por dentro. |
| `/commit` | Gerar a mensagem e criar o commit. Le a convencao do proprio repositorio (`docs_projeto/COMMITS.md`, depois `CLAUDE.md`, depois o historico) antes de propor tipo e escopo. Nunca roda `git add` por conta propria. |
| `/worktree` | Rodar tarefas independentes em paralelo, uma janela `claude` por tarefa, com merge de volta serializado por fila. |

A skill `/worktree` traz os proprios scripts em
`.claude/skills/worktree/scripts/` e funciona sem `package.json`: sem projeto Node
ela apenas nao roda portao nenhum. Worktrees nascem em `.claude/worktrees/`, que e
ignorado pelo git.

## Agentes

`.claude/agents/` tem 5 subagentes: `explorer` (haiku, busca so de leitura), `researcher`
(sonnet, web), `worker` (sonnet, testes e docs), `implementer` (opus, uma fatia) e `reviewer`
(opus, revisao do diff). `docs_projeto/AGENTES.md` e o catalogo: tabela tamanho → modelo,
handoff entre fatias, os tres momentos do advisor e os numeros de custo que justificam tudo.

Tres regras que valem sempre:

- **Um `implementer` novo por fatia.** Estado entre fatias vai para `.claude/handoff/<issue>.md`
  (ignorado pelo git), nunca para um agente mantido vivo por `SendMessage`.
- **Uma issue por sessao**, `/clear` entre issues. O custo esta no contexto relido a cada
  chamada, nao na resposta.
- **Agente de projeto vence agente de usuario com o mesmo nome.** Nao mantenha copias destes
  cinco em `~/.claude/agents/`.

Como as skills, os agentes e o `AGENTES.md` sao **fonte canonica** — correcao comeca aqui.

## MCPs

`docs_projeto/MCPS.md` e o catalogo curado de servidores MCP para projetos derivados:
nucleo, opcionais, anti-lista, politica de segredo e de escopo. Fichas do nucleo (comando,
credencial, limites) em `docs_projeto/MCPS_NUCLEO.md`; ficha tecnica de cada servidor em
`docs_projeto/referencias/mcp-*.md`.

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

`.claude/skills/` tem 57 skills. Skill nao custa contexto por sessao (so a `description`
entra no prompt), mas **colide por gatilho**: mais de 15 delas descrevem design de interface.

`docs_projeto/SKILLS.md` e o catalogo decisorio — arvore de precedencia de qual usar quando,
quais sao mutuamente exclusivas e quais estao inertes. Leia antes de invocar skill de design.

Duas regras que valem sempre:

- **Uma skill estetica por tarefa.** `minimalist-ui` e `industrial-brutalist-ui` juntas
  produzem output incoerente.
- **Nao rode `npx skills update`.** As 13 skills de `Leonxlnx/taste-skill` e as 6 skills 3D de
  terceiros sao fork proprio; `skills-lock.json` e registro de procedencia, nao mecanismo de
  atualizacao.

Sete skills de 3D, todas so texto: `3d-web-experience` decide a stack, `three-best-practices`
ou `r3f-best-practices` implementa, `cad-parametrico` faz peca para fabricar (mm, STEP/STL) e
as `blender-*` fazem asset e render. Precedencia em `docs_projeto/SKILLS.md` secao 8.

Toda tarefa de interface segue `.claude/skills/_shared/fontes-frontend.md`: referencia real
nomeada antes do codigo (Refero), componente de registry antes de inventado (Arc, Cult UI),
screenshot ao lado da referencia antes de entregar. As quatro skills de UI apontam para ele;
ver `docs_projeto/SKILLS.md` secao 7.

## Este repositorio e a fonte das skills

`template_projetos` e a **origem canonica** de `.claude/skills/`. Alteracao numa
skill comeca aqui e desce por copia para os projetos derivados — nunca o contrario.
Se voce corrigir uma skill dentro de um projeto, replique a correcao aqui na mesma
tarefa, ou ela se perde no proximo projeto criado.

## Estrutura

- `.claude/settings.json` — versionado, hooks publicos
- `.claude/hooks/` — `inject-rules.js` (regras por prompt) e `limit-doc-lines.js` (teto de 300 linhas)
- `.claude/settings.local.json` — ignorado pelo git, config pessoal e bloco `env` com segredos
- `.mcp.json.example` — nucleo de MCPs comentado; copiar para `.mcp.json` e podar
- `.claude/skills/` — skills locais do projeto (fonte canonica)
- `.claude/skills/_shared/` — texto comum a varias skills (nao e skill; o hook ignora)
- `skills-lock.json` — procedencia das skills vindas de `Leonxlnx/taste-skill`; versionado, nao atualizar
- `.claude/worktrees/` — worktrees de agentes, ignorado pelo git
- `.claude/agents/` — subagentes do projeto (fonte canonica)
- `.claude/handoff/` — handoff entre fatias da skill `/issue`, ignorado pelo git
- `docs_projeto/AGENTES.md` — catalogo dos agentes e do fluxo por tamanho (fonte canonica)
- `docs_projeto/SKILLS.md` — catalogo e precedencia das skills (fonte canonica)
- `docs_projeto/BOARD.md` — molde dos IDs do board do GitHub; preenchido em cada projeto derivado
- `.github/ISSUE_TEMPLATE/` — formularios de issue (tarefa, epico, bug); issue em branco desligada
- `docs_projeto/` — documentacao do projeto (atualizar sempre)
