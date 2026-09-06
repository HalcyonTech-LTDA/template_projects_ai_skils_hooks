---
title: MCP Playwright
source: https://github.com/microsoft/playwright-mcp
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, playwright, browser, teste, tema/tooling]
---

# MCP Playwright

Automacao de browser para o agente. Cobre Chromium, Firefox e WebKit e entrega snapshot
por **arvore de acessibilidade**, nao por screenshot.

Pacote npm: `@playwright/mcp`

## Instalacao

```bash
claude mcp add -s project -t stdio playwright -- npx -y @playwright/mcp@latest
```

## Playwright ou Chrome DevTools?

A escolha nao e de preferencia, e de tarefa:

| | Playwright MCP | Chrome DevTools MCP |
|---|---|---|
| Browsers | Chromium, Firefox, WebKit | So Chromium |
| Como enxerga a pagina | Arvore de acessibilidade | Screenshot + chamadas CDP |
| Forte em | **Dirigir**: E2E, fluxo, regressao | **Depurar**: performance, rede, trace |
| Custo em token | Menor (texto estruturado) | Maior (imagem) |
| Determinismo | Alto | Menor |

Regra pratica: **Playwright para dirigir, Chrome DevTools para depurar.** Rodar os dois ao
mesmo tempo so se justifica em investigacao de performance de um fluxo especifico — e
ainda assim custa ~50 tools somadas.

## Custo de contexto

Medio, ~25 tools.

## Pegadinhas

- Primeira execucao baixa os binarios de browser. Em CI ou maquina limpa, isso demora.
- O snapshot de acessibilidade e excelente em app bem marcado e pobre em app que abusa de
  `div` sem role. Nesse caso o agente cai para coordenada, e a fragilidade volta.
- Nao substitui a suite de teste do projeto. Serve para explorar, reproduzir bug e
  verificar mudanca — o teste versionado continua sendo codigo no repo.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 3.4
- [[mcp-chrome-devtools]]
- Skill relacionada no repo: `senior-qa`
