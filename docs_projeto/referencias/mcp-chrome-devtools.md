---
title: MCP Chrome DevTools
source: https://github.com/ChromeDevTools/chrome-devtools-mcp
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, chrome, performance, debug, tema/tooling]
---

# MCP Chrome DevTools

Expoe o Chrome DevTools Protocol ao agente: trace de performance, waterfall de rede,
console, profiling. E a ferramenta de **depuracao**, nao de direcao.

## Instalacao

```bash
claude mcp add -s project -t stdio chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

## Contra o Playwright

| | Chrome DevTools | Playwright |
|---|---|---|
| Browsers | So Chromium | Chromium, Firefox, WebKit |
| Enxerga a pagina por | Screenshot + CDP | Arvore de acessibilidade |
| Forte em | Performance, rede, memoria | Fluxo, E2E, regressao |
| Custo em token | Maior (imagem) | Menor (texto) |

Regra: **Playwright dirige, Chrome DevTools investiga.** Se a pergunta e "por que esta
lento" ou "que requisicao esta falhando", e este. Se e "esse fluxo funciona", e o outro.

## Custo de contexto

Medio.

## Pegadinhas

- Abre e controla uma instancia do Chrome. Perfil separado evita bagunca no seu browser.
- Trace de performance e volumoso: peca a metrica especifica, nao o dump inteiro.
- Rodar junto com Playwright soma ~50 tools. So faz sentido em investigacao pontual.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 4
- [[mcp-playwright]]
- Skill relacionada no repo: `web-performance-optimization`
