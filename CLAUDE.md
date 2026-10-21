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

## Statusline

`.claude/settings.json` liga a statusline de `.claude/statusline/`:
`#42 Titulo · In progress │ Opus 5.5 · high │ ctx 34% │ tok 4.6M (sub 870k)`. A issue e da sessao. Quem a grava
e o hook de `/issue <ref>` ou a skill `/issue`, no passo 1
(`node .claude/statusline/issue.js definir <ref>`). O status vem do board por um cache de 60 s,
renovado em segundo plano: a statusline nunca chama o `gh`. Os tokens somam a sessao inteira,
com subagentes e advisor, lidos dos transcripts. Detalhes em `docs_projeto/STATUSLINE.md`.

## Regras de comportamento (resumo)

1. Usar a skill que combinar com a tarefa; desenvolvimento passa por `/issue`, frente de trabalho por `/trilha`
2. Economia: poucas chamadas (leituras juntas, checagens num Bash so, sem reler) e modelo pelo tamanho. Ver `docs_projeto/ECONOMIA.md`
3. Perguntar so o ambiguo; 5 perguntas e 2 alternativas com tradeoffs so em tarefa M ou maior
4. Funcoes pequenas e modulos coesos; referencia nova em `docs_projeto/referencias/`; `docs_projeto/` atualizado no fim

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
| `/issue` | Conduzir uma issue ou tarefa de desenvolvimento do comeco ao merge. O `explorer` em Sonnet localiza o codigo e propoe o tamanho (vale o maior entre ele e a label `size/*`); subagente e modelo saem do tamanho, e plano formal so em L/XL. Cada fatia entrega testes unitarios alem do portao do projeto. Move a issue no board (In progress ao comecar; Done ou In review depois do merge, por `issue.js mover`), abre o PR para a branch de origem, faz o merge com squash e termina com a URL da issue. Toda implementacao roda num worktree (`/worktree`) criado da branch atual e volta para ela pelo merge do PR; usa `/commit` por dentro. |
| `/commit` | Gerar a mensagem e criar o commit. Le a convencao do proprio repositorio (`docs_projeto/COMMITS.md`, depois `CLAUDE.md`, depois o historico) antes de propor tipo e escopo. Nunca roda `git add` por conta propria. |
| `/worktree` | Rodar tarefas independentes em paralelo, uma janela `claude` por tarefa, com merge de volta serializado por fila. |

A skill `/worktree` traz os proprios scripts em
`.claude/skills/worktree/scripts/` e funciona sem `package.json`: sem projeto Node
ela apenas nao roda portao nenhum. Worktrees nascem em `.claude/worktrees/`, que e
ignorado pelo git.

## Agentes

`.claude/agents/` tem 5 subagentes de desenvolvimento (mais os 5 do blueprint de negocio, ver
"Padroes Halcyon"): `explorer` (haiku, busca so de leitura; sonnet ao classificar na `/issue`), `researcher`
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

`.claude/skills/` tem 116 skills (54 delas copiadas dos padroes Halcyon, abaixo). Skill nao custa contexto por sessao (so a `description`
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
as `blender-*` fazem asset e render. Precedencia em `docs_projeto/SKILLS.md` secao 9.

Toda tarefa de interface segue `.claude/skills/_shared/fontes-frontend.md`: referencia real
nomeada antes do codigo (Refero), componente de registry antes de inventado (Arc, Cult UI, beUI),
screenshot ao lado da referencia antes de entregar. As quatro skills de UI apontam para ele;
ver `docs_projeto/SKILLS.md` secao 8.

## Padroes Halcyon: skills `modern-*`

54 skills e 5 agentes vem copiados dos repos `HalcyonTech-LTDA/modern-*` do GitHub (Java,
Spring Boot, microsservicos, MongoDB, Docker, Git, k6, Postman/Newman, WireMock, Azure Bicep e
blueprint de negocio). A regra-guarda de cada stack fica em `.claude/skills/_shared/padroes-*.md`.
`docs_projeto/PADROES.md` e o catalogo: stack → skills → projeto inicial
(`java-clean-architecture-scaffolding` e o padrao para servico Java).

**Aqui a direcao se inverte.** A fonte e o repo `modern-*`, nao este template. Corrija la e
reimporte com `node .claude/scripts/importar-padroes.js`, que clona do GitHub e grava o commit
em `padroes-lock.json`. Precedencia contra as skills genericas: `docs_projeto/SKILLS.md` secao 10.

## Hardware: familia `pcb-*`

Cinco skills para projetar placas no KiCad 10, do requisito ao pedido na JLCPCB:
`pcb-projeto` (porta de entrada, fases e portoes), `pcb-componentes`, `pcb-esquematico`,
`pcb-layout` e `pcb-fabricacao`. Os scripts ficam todos em `.claude/skills/pcb-projeto/scripts/`
(stdlib; dois deles rodam no Python do KiCad) — copie a familia inteira. Precedencia e terceiros
na secao 7 do `docs_projeto/SKILLS.md`; onde cada coisa fica num projeto derivado em
`docs_projeto/docs_Template_Projeto/03_Hardware/README.md`.

## Este repositorio e a fonte das skills

`template_projetos` e a **origem canonica** de `.claude/skills/`. Alteracao numa
skill comeca aqui e desce por copia para os projetos derivados — nunca o contrario.
Se voce corrigir uma skill dentro de um projeto, replique a correcao aqui na mesma
tarefa, ou ela se perde no proximo projeto criado.

**Excecao: as skills `modern-*`** (e os 5 agentes do blueprint). A origem delas e o repo
`HalcyonTech-LTDA/modern-*` no GitHub. Ver "Padroes Halcyon" acima.

## Estrutura

- `.claude/settings.json` — versionado, hooks publicos
- `.claude/hooks/` — `inject-rules.js` (regras por prompt) e `limit-doc-lines.js` (teto de 300 linhas)
- `.claude/statusline/` — statusline, hook de captura da issue e CLI `issue.js`; estado em `~/.claude/halcyon-statusline/`, fora do repo
- `.claude/settings.local.json` — ignorado pelo git, config pessoal e bloco `env` com segredos
- `.mcp.json.example` — nucleo de MCPs comentado; copiar para `.mcp.json` e podar
- `.claude/skills/` — skills locais do projeto (fonte canonica)
- `.claude/skills/_shared/` — texto comum a varias skills (nao e skill; o hook ignora)
- `skills-lock.json` — procedencia das skills vindas de `Leonxlnx/taste-skill`; versionado, nao atualizar
- `padroes-lock.json` — repo, commit e versao de cada padrao `modern-*` copiado; gravado pelo script
- `.claude/scripts/importar-padroes.js` — reimporta os padroes Halcyon do GitHub
- `docs_projeto/PADROES.md` — catalogo dos padroes por stack e projeto inicial
- `.claude/worktrees/` — worktrees de agentes, ignorado pelo git
- `.claude/agents/` — subagentes do projeto (fonte canonica)
- `.claude/handoff/` — handoff entre fatias da skill `/issue`, ignorado pelo git
- `docs_projeto/AGENTES.md` — catalogo dos agentes e do fluxo por tamanho (fonte canonica)
- `docs_projeto/SKILLS.md` — catalogo e precedencia das skills (fonte canonica)
- `docs_projeto/BOARD.md` — molde dos IDs do board do GitHub; preenchido em cada projeto derivado
- `.github/ISSUE_TEMPLATE/` — formularios de issue (tarefa, epico, bug); issue em branco desligada
- `docs_projeto/` — documentacao do projeto (atualizar sempre)
