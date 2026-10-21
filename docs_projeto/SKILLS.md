---
title: Catalogo de skills e precedencia de design
type: convencao
status: aprovado
created: 2026-09-07
updated: 2026-10-15
project: template_projetos
tags: [convencao, skills, design, claude-code, tema/tooling]
---

# Catalogo de skills e precedencia de design

Este repositorio carrega **116 skills** em `.claude/skills/` (62 proprias ou de fork e 54
copiadas dos padroes Halcyon, secao 10) (mais `obsidian-skills/`, que e
pacote e nao skill, e `_shared/`, que guarda texto comum a varias skills). Diferente dos MCPs, skill
nao custa contexto por sessao: so a `description` de cada uma entra no prompt, e o corpo
so e lido quando a skill dispara. O custo real e outro — **colisao de gatilho**: com 20+
skills descrevendo "design de interface", o modelo escolhe uma diferente a cada sessao e
o resultado deixa de ser reproduzivel.

Este documento resolve isso. Ele **nao** e uma lista de instalacao; e a ordem de
precedencia que o agente deve seguir quando mais de uma skill parece caber.

> **Este arquivo e a fonte canonica.** Assim como `.claude/skills/` e `MCPS.md`, correcao
> comeca aqui e desce por copia para os projetos derivados.

## 1. A regra: uma skill estetica por tarefa

As skills de direcao de arte sao **mutuamente exclusivas**. Carregar `minimalist-ui` e
`industrial-brutalist-ui` na mesma tarefa produz output incoerente — uma proibe gradiente
e sombra pesada, a outra pede degradacao analogica e contraste extremo de escala.

Escolha **uma** e siga ate o fim. Skills de processo (seção 4) podem acumular.

## 2. Arvore de decisao

Leia de cima para baixo; para na primeira que casar.

| Se a tarefa e... | Use | Por que nao a de baixo |
|---|---|---|
| Redesign / auditoria de projeto **que ja existe** | `redesign-existing-projects` | Ela audita antes de mexer. As outras assumem folha em branco e reescrevem o que funcionava |
| O usuario **nomeou** o estilo (minimalista, brutalista, "caro") | `minimalist-ui` / `industrial-brutalist-ui` / `high-end-visual-design` | Style lock explicito vence inferencia. `design-taste-frontend` iria inferir outra direcao |
| Landing page, portfolio, site de marketing | `design-taste-frontend` | E a default v2: le o brief e infere a direcao. Nao use as tres acima sem o usuario pedir |
| Motion pesado, GSAP, ScrollTrigger, pin/scrub | `gpt-taste` | Unica com esqueleto de codigo GSAP e estrutura AIDA |
| Dashboard, tabela de dados, UI de produto multi-step | `ui-ux-pro-max` | `design-taste-frontend` **se exclui** disso explicitamente ("not dashboards, not data tables") |
| Componente isolado ou artifact claude.ai | `frontend-design` + `artifacts-builder` | Skills de landing page trazem estrutura de pagina inteira que sobra aqui |
| Tokens, escala tipografica, handoff para dev | `ui-design-system` | Ortogonal — pode combinar com a estetica escolhida |
| App mobile (RN / nativo) | `mobile-design` | As taste-skills sao web-first |
| Qualquer coisa 3D (cena web, peca, Blender) | ver secao 9 | Sete skills 3D com gatilhos que se sobrepoem |
| Texto de venda, headline, CTA | `copywriting` | — |

## 3. Skills que exigem gerador de imagem — inertes hoje

Quatro skills do pacote `taste-skill` assumem que o agente **gera imagens**:

| Skill | Estado neste stack |
|---|---|
| `imagegen-frontend-web` | **Inerte.** So gera imagem, nao escreve codigo |
| `imagegen-frontend-mobile` | **Inerte.** Idem, para telas mobile |
| `brandkit` | **Inerte.** Board de identidade visual, so imagem |
| `image-to-code` | **Degradada.** Escrita para o Codex; o passo "gere a imagem de referencia primeiro" nao roda aqui. Sobra a parte de analise/implementacao |

O catalogo de MCPs (`MCPS.md`) **nao tem servidor de geracao de imagem**. Enquanto isso
nao mudar, essas quatro nao devem ser invocadas — foram instaladas por decisao de manter
o pacote upstream integro, nao porque funcionam.

Se algum dia entrar um MCP de imagem no catalogo, revisite esta secao.

## 4. Skills de processo — acumulam

Estas nao competem com as esteticas e podem rodar junto:

- `full-output-enforcement` — proibe placeholder e `// resto do codigo aqui`. Util em
  geracao longa; e o antidoto direto para truncamento
- `clean-code`, `software-architecture`, `code-reviewer`, `systematic-debugging`
- `react-best-practices`, `nextjs-best-practices`, `tailwind-patterns`,
  `web-performance-optimization`
- `commit`, `worktree` — fluxo de entrada de trabalho no repo
- `issue` — conduz uma issue pelo tamanho, escolhendo subagente e modelo; usa `commit` e
  `worktree` por dentro. Catalogo dos agentes em [[AGENTES]]
- `trilha` — planeja e controla uma frente de trabalho no GitHub (marcos, sequencia, bloqueios,
  progresso); cria as issues que a `issue` conduz. IDs do board em [[BOARD]]

## 5. Casos especiais

- **`stitch-design-taste`** nao produz UI: produz um `DESIGN.md` para o Google Stitch
  consumir. So use se o projeto de fato passa pelo Stitch.
- **`design-taste-frontend-v1`** existe so para compatibilidade. A v2 e uma reescrita.
  Nao invoque a v1 sem motivo explicito; ela vai divergir da v2 no mesmo brief.

## 6. Politica de upstream: fork proprio

As 13 skills do pacote `Leonxlnx/taste-skill` foram copiadas uma vez e **nao seguem o
upstream**. Nao rode `npx skills update` neste repositorio.

Motivo: o autor declara a v2 como "experimental, actively iterating". Um update silencioso
mudaria o comportamento do agente em 8 repositorios sem revisao.

O `skills-lock.json` na raiz e versionado como **registro de procedencia** (origem, caminho
no upstream, hash do conteudo instalado) — nao como mecanismo de atualizacao. Para trazer
mudanca do upstream, faca deliberadamente: leia o diff, decida, e propague por copia.

Ficha da referencia em [[referencias/skills-taste-leonxlnx]].

A mesma politica vale para as 6 skills 3D de terceiros (secao 9): `three-best-practices` e
`r3f-best-practices` (`emalorenzo/three-agent-skills`) e as quatro `blender-*`
(`TerminalSkills/skills`). Commit de origem e sha256 do upstream no `skills-lock.json`.

## 7. Eletronica e PCB: a familia `pcb-*`

Cinco skills proprias (nao vem de terceiros) para projetar placas no **KiCad 10**, do
requisito ao pedido na JLCPCB. Diferente das esteticas, elas **acumulam**: cada uma cobre uma
fase, e a `pcb-projeto` e a porta de entrada.

| Se a tarefa e... | Use |
|---|---|
| Placa nova, mudanca que atravessa fases, ou nao esta claro por onde comecar | `pcb-projeto` |
| Escolher ou trocar peca, BOM, codigo LCSC, footprint, datasheet | `pcb-componentes` |
| Gerar, editar ou revisar esquematico; ERC; netlist | `pcb-esquematico` |
| Posicionar, rotear (Freerouting nos sinais simples), regras, stack-up, DRC | `pcb-layout` |
| Gerber, BOM/CPL da JLC, portao de liberacao, pedido | `pcb-fabricacao` |

- **Toolkit unico:** os scripts vivem em `.claude/skills/pcb-projeto/scripts/` (catalogo no
  `README.md` de la) e as outras quatro apontam para eles. Copie a familia **inteira** para um
  projeto derivado; uma skill sozinha fica sem os scripts.
- **Prova mecanica:** nada e declarado pronto sem o `kicad-cli` (ERC e DRC com
  `--exit-code-violations`, netlist comparada com a spec).
- **Portoes humanos:** revisao do esquematico antes do layout e liberacao antes do pedido, como
  notas `type: gate` em `03_Hardware/`. O agente prepara e verifica; quem aprova e uma pessoa.
- **Dependencia de versao:** dois scripts usam o SWIG `pcbnew`, que sai no KiCad 11.

### Terceiros relacionados (nao instalados)

- `aklofas/kicad-happy` (MIT, 11 skills de analise: revisao, SPICE, EMC, BOM, sourcing). Fica
  **fora** do template: as descricoes disputam gatilho com a familia (a `bom` diz "ALWAYS
  trigger") e sao ~100 mil linhas nao revisadas. Quem quiser segunda opiniao antes do portao 2
  instala no escopo do usuario. Precedencia: para gerar, editar, verificar e liberar, `pcb-*`
  vence; `kicad-happy` so como revisao extra.
- `copperheadhq/copperhead` (Apache-2.0, pre-1.0): agente de IA em CLI que edita o KiCad e roda
  ERC/DRC. So `check` e `score schematic` (sem LLM) como verificacao extra; o loop `do`/`create`
  e um segundo agente e nao roda junto da familia. Ficha [[referencias/copperhead]].
- MCP de KiCad: ver [[MCPS]], secao 4.1.

Decisao e alternativas em [[decisoes/2026-10-12_skills_pcb_kicad]]. Fichas em
[[referencias/README|referencias/]], secao "Eletronica e PCB".

## 8. Fontes de frontend — protocolo comum

A arvore da secao 2 escolhe **a estetica**. Ela nao diz de onde vem a evidencia nem o
codigo. Isso fica num arquivo so, lido pelas quatro skills que produzem interface:

`.claude/skills/_shared/fontes-frontend.md`

| Skill | Onde o protocolo entra |
|---|---|
| `design-taste-frontend` | `STEP 0`, antes da inferencia de brief |
| `ui-ux-pro-max` | `Step 0`, antes do `--design-system` (que vira suplemento) |
| `frontend-design` | `Step 0`, antes do Design Thinking |
| `redesign-existing-projects` | Passo `Reference` entre Diagnose e Fix, mais `Verify` no fim |

As quatro regras que cada skill repete inline:

1. **2 a 3 referencias reais nomeadas antes do codigo**, com o que cada uma contribui, e o
   reference lock escrito. Ordem: do usuario → refero.design pelo navegador → galeria da
   secao (navbar, footer, CTA, 404, bento, motion) → produtos reais
2. **Componente de registry antes de componente inventado**: Arc (`@uiarc/*`), Cult UI
   (`@cult-ui/*`) ou beUI (`@beui/*`), lendo o `.md` do componente
3. **Vetados do Cult**: `border-beam-*`, `halo-*`, `cosmic-button`, `metal-button`,
   `gradient-*`, `bg-animated-gradient`, `circuit-board`, `distorted-glass`; **do beUI**:
   `shader-background`, `tilt-card`, `MetallicButton`
4. **Screenshot em 1440px e 390px ao lado da referencia principal** antes de entregar

| Fonte | Papel | Ficha |
|---|---|---|
| Refero | Referencia — o que olhar. Sem MCP (pago) | [[referencias/refero]] |
| Galerias de secao | Referencia de um bloco (navbar, footer, CTA, 404, bento, motion). Nunca a principal | [[referencias/galerias-de-secao]] |
| Arc | Componente animado, CSS modules, sem Tailwind | [[referencias/ui-arc]] |
| Cult UI | Ilustracao, device frame, secao de marketing (Tailwind) | [[referencias/cult-ui]] |
| beUI | Controle com motion, UI de chat e agente, charts; codigo React Native (Tailwind) | [[referencias/beui]] |

Arc, Cult e beUI podem conviver, mas os tokens tem os mesmos nomes e o tema escuro usa seletores
diferentes (Cult e beUI seguem o shadcn; o atrito e com o Arc) — regra na secao 3 do arquivo compartilhado.

`_shared/` nao e skill (nao tem `SKILL.md`); o hook so lista pastas com `SKILL.md`.
Decisoes em [[decisoes/2026-10-15_fontes_frontend]] e [[decisoes/2026-10-21_beui]].

## 9. 3D — precedencia

Sete skills. Todas sao **so texto**: nenhuma traz script, servidor ou container. Ficam
inertes em projeto sem 3D (so a `description` entra no prompt) — custo aceito.

| Se a tarefa e... | Use | Acumula com |
|---|---|---|
| Decidir **se** o site tem 3D e com qual stack (Spline, R3F, three puro) | `3d-web-experience` | a de implementacao abaixo |
| Implementar ou revisar cena **Three.js puro** (import maps, WebGPU, TSL) | `three-best-practices` | `3d-web-experience` |
| Implementar ou revisar cena em **React** (`@react-three/*`) | `r3f-best-practices` | `3d-web-experience` |
| **Peca para fabricar**: gabinete, suporte, cota em mm, STEP/STL/3MF | `cad-parametrico` | nada 3D |
| Asset, cena, render ou animacao **no Blender** via `bpy` | `blender-scripting` | `blender-render-automation`, `-animation`, `-compositing` |
| Figura isometrica explicativa para docs | **nenhuma instalada** | ver abaixo |

Exclusoes:

- **`three-best-practices` x `r3f-best-practices`**: uma por projeto, pela stack do
  `package.json`. R3F ja encapsula o loop e o dispose que a outra ensina a fazer a mao
- **`cad-parametrico` x `blender-*`**: a pergunta e "vai ser fabricado?". Sim → CAD (mm,
  STEP, folga de encaixe). Nao → Blender (metro, malha, render). A `description` das duas
  ja exclui a outra
- Skill 3D nao e direcao de arte: cena 3D numa landing page usa **tambem** uma estetica da
  secao 2, e a regra de uma estetica por tarefa continua valendo

Guardas do fork (bloco logo abaixo do frontmatter de cada uma): `three`/R3F conferem a
versao no `package.json` antes de aplicar regra de API 0.182+; Blender comeca cena nova com
`read_factory_settings(use_empty=True)`, nunca sobrescreve o `.blend` de entrada e nao usa
`/tmp` fixo.

**`anatomy` ficou de fora.** O produto dela e o `kit/` em Node mais checagem no Chrome, e o
`publish.mjs` usa rede — contradiz "so texto". E a `description` disputa gatilho com as
esteticas ("landing page", "even if they never say isometric"). Se entrar, entra com o
`kit/` auditado e com a regra: **so figura de documentacao, nunca UI de produto**.

Fichas: [[referencias/skill3d-three-agent-skills]], [[referencias/skill3d-terminalskills]],
[[referencias/skill3d-anatomy]], [[referencias/skill3d-cad-agent]], [[referencias/enclose]]
(fonte das regras de fixacao e da prova de montabilidade da `cad-parametrico`). Decisao em
[[decisoes/2026-10-15_skills_3d]].

## 10. Padroes Halcyon (`modern-*`) — precedencia

54 skills copiadas dos repos `HalcyonTech-LTDA/modern-*` do GitHub. Catalogo por stack,
projeto inicial e script de importacao em [[PADROES]]. A fonte e o repo de origem, e nao este
template: nao edite a copia.

Regra geral: **dentro da ferramenta dela, a skill `modern-*` vence a generica.** A generica
continua valendo fora desse recorte.

| Tema | Vence | Fica para a generica |
|---|---|---|
| Codigo Java, Gradle, testes JVM | `modern-java-*`, `modern-gradle-conventions` | `clean-code` e `software-architecture` em principio geral, sem regra de Java |
| Spring Boot e microsservicos | `modern-spring-boot-conventions`, `modern-microservices-*` | `senior-backend` e `senior-architect` (cobrem Node, Go e Python, nao Spring) |
| Dockerfile, Compose, `.dockerignore` | `modern-docker*`, `modern-compose-workflows` | `docker-expert` so em diagnostico de container que ja existe |
| Mensagem de commit | `/commit` conduz o fluxo e le `modern-git-commit-craftsmanship` como referencia de conteudo | — |
| Worktree, rebase, recuperacao | `/worktree` conduz o paralelismo; `modern-git-*` ensina o comando | — |
| MongoDB | `modern-mongodb-*` | `supabase-postgres-best-practices` e Postgres, nao concorre |
| Carga, API e mocks HTTP | `modern-k6-*`, `modern-postman-*`/`modern-newman-*`, `modern-wiremock-*` | `senior-qa` (foco em JS/React) |
| Infra Azure em Bicep | `modern-bicep-*` | `senior-devops` em CI/CD generico e outras nuvens |
| Concepcao de empresa | `modern-business-blueprint-orchestrator` e agentes do blueprint | `copywriting`, `ux-researcher-designer` |

`/commit` e `modern-git-commit-craftsmanship` nao sao exclusivas. A convencao do repositorio
(`docs_projeto/COMMITS.md`) vence as duas, e a skill de git so preenche o que ela nao define.

**Procedencia.** As copias nao entram no `skills-lock.json`: o hash de la vem do CLI `skills` e
nao e reproduzivel a mao. O registro fica em `padroes-lock.json` (repo, commit e versao de cada
origem), regravado pelo `.claude/scripts/importar-padroes.js`. Decisao em
[[decisoes/2026-10-15_padroes_halcyon]].
