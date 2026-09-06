---
title: MCP Terminator (automacao desktop Windows)
source: https://github.com/mediar-ai/terminator
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, desktop, windows, teste, automacao, tema/tooling]
---

# MCP Terminator (automacao desktop Windows)

"Playwright para o desktop inteiro". Dirige qualquer aplicacao Windows pelas APIs nativas
de acessibilidade (UI Automation), com core em Rust e SDK no estilo Playwright.

O repo entrega o `terminator-mcp-agent`, servidor MCP com 50+ tools para interacao de UI,
gerenciamento de janela, automacao de browser e execucao de workflow.

## Instalacao

```bash
claude mcp add -s project -t stdio terminator -- npx -y terminator-mcp-agent@latest
```

Ha tambem `terminator-cli` (crates.io) e SDKs em Rust e TypeScript, para quem quiser usar
fora do contexto de agente.

## Como localiza elemento

Consulta a **arvore de acessibilidade do Windows** — a mesma interface que leitor de tela
usa — e casa elementos por atributo semantico: `role`, `name`, `ControlType`,
`AutomationId`.

A consequencia pratica importa: como mira **o que o elemento e**, e nao **onde ele esta na
tela**, nao quebra quando a janela move, o tema muda ou o DPI troca. E a diferenca entre
automacao de desktop que sobrevive a um update e automacao por coordenada que nao.

## Limites

- **Windows apenas.** Nao ha suporte macOS nem Linux.
- Depende de o app expor a arvore de acessibilidade. App que desenha tudo em canvas
  proprio (alguns Electron mal configurados, apps graficos) expoe pouco ou nada.
- Roda em segundo plano sem sequestrar cursor e teclado — mas ainda assim opera a maquina
  de verdade.

## Custo de contexto

**Alto**: 50+ tools. E o servidor mais caro do catalogo. Ligue por tarefa, desligue depois.

## Riscos

Este e o MCP de maior superficie de risco da lista: da ao agente controle de aplicacoes
desktop arbitrarias. Antes de ligar:

- Feche ou nao aponte para app com dado de producao, sistema financeiro ou credencial
  aberta.
- Prefira maquina ou VM de teste quando o workflow for destrutivo.
- Trate cada workflow novo como codigo a revisar, nao como comando a confiar.

## Alternativas consideradas

- **Windows-MCP** e variantes baseadas em visao: mais genericas, muito mais caras em token
  e menos deterministicas.
- **AppleScript MCP** cobre o caso macOS, que o Terminator nao atende.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 3.5
