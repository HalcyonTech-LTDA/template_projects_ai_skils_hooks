---
title: copperhead - agente de IA em CLI para projetos KiCad
source: https://github.com/copperheadhq/copperhead
type: referencia
status: aprovado
tags: [referencia, kicad, eletronica, agente, mcp, tema/hardware]
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
---

# copperhead (copperheadhq/copperhead)

Metodo: WebFetch no README, na documentacao (https://docs.copperhead.sh), no `ROADMAP.md`, no
`package.json` e na API publica do GitHub, em 2026-10-15. O WebFetch resume a pagina: tudo aqui e
"via resumo, nao conferido literalmente". Nada foi instalado nem executado.

## 1. O que e

- **Agente de IA de linha de comando para KiCad**: le e edita `.kicad_sch` e `.kicad_pcb` reais,
  guarda memoria do projeto em Markdown e roda ERC/DRC pelo `kicad-cli` ate passarem. Tagline
  "Cursor for circuit boards" (https://github.com/copperheadhq/copperhead, https://docs.copperhead.sh).
- **Nao e** autorouter, nem editor novo, nem formato novo: o KiCad continua sendo o editor. Exige
  aprovacao humana e usa o git como rede de seguranca (snapshot antes de editar, rollback se a
  verificacao falhar) (https://docs.copperhead.sh).
- Tem um **servidor MCP stdio experimental** (dependencia `@modelcontextprotocol/sdk`; README fala
  em 5 tools de alto nivel, nao listadas aqui). A interface MCP e declarada instavel
  (https://raw.githubusercontent.com/copperheadhq/copperhead/main/package.json).

## 2. Dados do repositorio (API do GitHub, 2026-10-15)

| Campo | Valor |
|---|---|
| Licenca | Apache-2.0 |
| Linguagem | TypeScript, Node >= 20 |
| Estrelas / forks | 548 / 118 |
| Criado | 2026-07-18 (cerca de 3 meses) |
| Ultimo commit | 2026-10-15 (release v0.12.0) |
| Ritmo de release | v0.8.1 (07-27), v0.9.0 (07-29), v0.10.0 (08-26), v0.11.0 (09-14), v0.12.0 (10-15) |
| Issues + PRs abertos | 221 (106 issues, 115 PRs) |

Fontes: https://api.github.com/repos/copperheadhq/copperhead,
https://api.github.com/repos/copperheadhq/copperhead/releases.

## 3. Requisitos e custo

- **KiCad >= 8** com `kicad-cli` no PATH; **Node >= 20**; projeto dentro de um repositorio git
  (https://docs.copperhead.sh/getting-started/quickstart/).
- **KiCad 10: nao verificado.** ">= 8" sugere que funcione, mas nada diz que foi testado no 10.
- **Windows: nao verificado.** O `install.sh` e so macOS/Linux; o `npm install -g` deve funcionar,
  sem confirmacao.
- **Backend de LLM obrigatorio** para os comandos de agente: Codex CLI (login), Claude Code
  (`claude setup-token` + `CLAUDE_CODE_OAUTH_TOKEN`), `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` ou endpoint
  compativel com OpenAI (Groq, OpenRouter, Gemini, Ollama local). Ferramenta gratuita; o custo e o
  do modelo, que a documentacao nao estima.

## 4. Comandos (https://docs.copperhead.sh/reference/cli/)

```bash
npm install -g copperhead      # ou: npx copperhead check
copperhead init                # na raiz de um projeto KiCad existente
copperhead check               # ERC, DRC, drift e restricoes — sem LLM e sem rede
copperhead do "<mudanca>"      # loop do agente: edita, verifica, faz rollback se falhar
copperhead draft schematic --intent ...   # desenho deterministico a partir de netlist/intent
copperhead score schematic     # nota de legibilidade do esquematico
copperhead create --brief <arquivo.md>    # projeto a partir de um brief; gera docs/BOM.md e outputs/BOM.csv
copperhead doctor | sync | repl | demo
```

Flags globais: `--repo`, `--json`. O README cita tambem `export bom` (JLCPCB, DigiKey, Mouser),
`mcp` e, num commit de 2026-10-15, `review`, que a pagina de CLI ainda nao documenta. README e
documentacao estao desencontrados.

## 5. Cobertura por fase (ROADMAP, que esta defasado em relacao a v0.12.0)

| Fase da familia `pcb-*` | copperhead |
|---|---|
| Componentes (`pcb-componentes`) | So proposta (pesquisa de peca, datasheet, estoque) |
| Esquematico (`pcb-esquematico`) | Entregue: desenho deterministico e score de legibilidade |
| Layout (`pcb-layout`) | Parcial: posicionamento rascunhado. **Roteamento fora de escopo** por decisao |
| ERC/DRC | Solido: `check` roda em CI com fixture real do KiCad |
| Fabricacao (`pcb-fabricacao`) | Pendente: `check --fab`, Gerber/furacao e BOM da JLC na Fase 2 |

Fonte: https://github.com/copperheadhq/copperhead/blob/main/ROADMAP.md.

## 6. Riscos

- **Projeto novo e pre-1.0**: superficie pode mudar entre releases. O README declara status inicial
  e diz que a suite de aceitacao ao vivo do loop do agente nao foi vista passando de ponta a ponta.
- **Agente dentro do agente**: rodar `copperhead do` a partir do Claude Code chama um segundo LLM,
  com custo e contexto proprios, e disputa a mesma tarefa com a familia `pcb-*`.
- **Seguranca**: o proprio projeto registra que a sandbox read-only do Codex nao restringe leitura
  (um `.env` do projeto pode ser lido). Com `--model cursor`, o uso de tokens aparece como 0.
- Promete "ERC/DRC clean", nao placa pronta para fabricar.

## 7. Como o template usa

Fora do nucleo, nao instalado. Detalhes e precedencia em
`.claude/skills/pcb-projeto/references/ferramentas.md`. Em resumo:

- **`copperhead check`** e o uso de menor risco: sem LLM, sem rede, so `kicad-cli`. Serve como
  segunda opiniao de ERC/DRC/drift antes de um portao, ao lado dos scripts da familia.
- **Ideias que valem copiar**, nao o codigo: snapshot git antes de editar e rollback automatico
  quando a verificacao falha; nota de legibilidade de esquematico; memoria do projeto em Markdown.
- **Nao usar** o loop `do`/`create` dentro de uma sessao que ja usa as skills `pcb-*`.
- O MCP experimental segue a regra de [[../MCPS|MCPS.md]] secao 4.1: escopo `local`, so em sessao
  exploratoria.

## 8. Nao verificado

KiCad 10, Windows, existencia e uso de `export bom`/`mcp`/`review` na v0.12.0, lista de tools do
MCP, custo de tokens por execucao, numero de mantenedores, qualidade real das edicoes, conteudo de
`docs/`, `integrations/` e `openspec/specs/SPEC.md`.
