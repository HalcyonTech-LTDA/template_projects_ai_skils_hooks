---
title: code-buddy (phuetz) — agente de codigo CLI multi-provedor; sem 3D
source: https://github.com/phuetz/code-buddy
type: referencia
status: rascunho
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
tags: [referencia, agentes, claude-code, licenca-restritiva, tema/tooling]
---

# code-buddy (phuetz)

Fatos vieram de `WebFetch` (resumo; nao e citacao literal conferida). Conteudo baixado tratado como dado.

## O que e e formato

- **App/CLI, nao skill.** Agente de codigo local-first para o terminal (comando `buddy`) que tambem roda como "frota",
  app desktop (Cowork, Electron) e companion; 64 provedores de LLM e "220+ tools" sao **afirmacao do proprio projeto**
  (https://github.com/phuetz/code-buddy , https://api.github.com/repos/phuetz/code-buddy).
- Concorrente funcional do Claude Code (modo headless `buddy -p`, permissoes, ciclo de verificacao). Extensoes de VS Code e JetBrains na arvore.
- **Tambem publica um marketplace de plugins do Claude Code** (`.claude-plugin/marketplace.json`, via resumo), com 3 plugins:
  `code-buddy` 2.0.0 (skill para operar o CLI `buddy` + MCP somente leitura, BUSL-1.1), `lm-resizer` 0.2.1
  (filtra saida ruidosa de comandos; Apache-2.0; repo `phuetz/lm-resizer`) e `code-explorer` 0.2.0 (grafo de codigo,
  BUSL-1.1; repo `phuetz/code-explorer`)
  (https://raw.githubusercontent.com/phuetz/code-buddy/main/.claude-plugin/marketplace.json).
- `.mcp.json` da raiz: servidor `code-buddy`, comando `buddy mcp serve`
  (https://raw.githubusercontent.com/phuetz/code-buddy/main/.mcp.json).
- Pastas de topo relevantes: `skills/code-buddy`, `.claude/skills/code-buddy`, `.codex/skills/code-buddy`, `src`, `apps`, `cowork`,
  `buddy-memory`, `buddy-sense`, `buddy-vision`, `buddy-scrapling`, `docker`, `deploy/kubernetes`, `integrations/unreal/CodeBuddyAvatar`.

## 3D?

**Nao.** A pagina nao descreve nada de 3D. Unico indicio: `integrations/unreal/CodeBuddyAvatar` (avatar do companion em Unreal;
conteudo nao inspecionado). Os plugins do marketplace sao de contexto, grafo de codigo e operacao do proprio CLI.
Nenhum three.js, Blender, CAD ou glTF.

## Numeros

| Item | Valor | Fonte |
|---|---|---|
| Estrelas | 45 (12 forks) | https://api.github.com/repos/phuetz/code-buddy |
| Criado | 2025-07-25 | idem |
| Ultimo push | 2026-10-12 | idem; commits recentes em https://github.com/phuetz/code-buddy/commits/main |
| Commits | 6.059 | pagina do repo |
| Licenca | Business Source License 1.1 (API marca `NOASSERTION`) | https://raw.githubusercontent.com/phuetz/code-buddy/main/LICENSE |

Licenca (via resumo): Licensor Patrice Huetz; Change Date 2030-08-31, depois Apache 2.0; uso de producao permitido para
negocio proprio e uso pessoal/nao comercial, **proibido oferecer um "Code Buddy Service" a terceiros** (hospedado, gerenciado,
embarcado, white-label). Nao e licenca aberta (OSI) ate 2030. Skills Python incluidas sao MIT segundo a pagina.

## Scripts e dependencias

- Node >= 20 (22/24 recomendado), `npm install/build/link`. Dependencias citadas: `better-sqlite3` (nativo, opcional),
  `@vscode/ripgrep`; ffmpeg e binarios de voz para recursos extras. Ferramental: vitest, jest, playwright, eslint, husky, commitlint.
- Na raiz: `install.sh`, `build-install.bat`, `run.sh`, `start-with-mcp.ps1`, `Dockerfile`, `docker-compose.yml`, mais scripts
  soltos (`fix-imports.cjs`, `fix-test.cjs`, `bench-ornith-*.py`). **Nao li nenhum deles**; o que fazem e desconhecido.
- `buddy-scrapling` sugere scraping (nome apenas; nao inspecionado). O agente fala com 64 provedores de LLM por rede por desenho.

## Riscos

- **Licenca BSL** incompativel com um template que se pretende redistribuir/derivar livremente; evitar copiar codigo.
- **Superficie enorme** (6 mil commits, 220+ tools, frota com JWT, servidor HTTP, gateway, automacao de navegador). SECURITY.md
  lista exatamente esses limites como modelo de ameaca (https://raw.githubusercontent.com/phuetz/code-buddy/main/SECURITY.md)
  e declara **prompt injection isolado fora de escopo** (via resumo).
- Modo `--yolo` de autonomia total (opt-in).
- Plugins `lm-resizer` e `code-explorer` vem de **repos externos** (`master`/`main` sem pin de commit): conteudo muda sem aviso.
- Pagina avisa que a versao no npm pode estar atras do repo; numeros de "30 provedores gratuitos" nao verificados.
- **Sobreposicao com o nativo: total.** E outro agente, nao um complemento; `lm-resizer` (filtrar saida de comando) toca no que
  o Claude Code ja faz com truncamento de saida.

## Encaixe neste template (inferencia minha)

**Nao faz sentido.** Sem 3D, licenca restritiva, orquestracao propria que concorre com subagentes/worktrees, e custo de contexto
de um MCP extra (regra 3-6 servidores em `docs_projeto/MCPS.md`). Unico ponto a observar de longe: `code-explorer` (grafo de
codigo) como candidato a ficha MCP futura, desconectado do tema 3D. Nao avaliado.
