---
title: MCP mobile-next (mobile-mcp)
source: https://github.com/mobile-next/mobile-mcp
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, mobile, ios, android, teste, tema/tooling]
---

# MCP mobile-next (mobile-mcp)

Automacao mobile agnostica de plataforma: mesma interface para iOS e Android, em
simulador, emulador ou device fisico. Sem XCUITest, sem Espresso, sem cola por plataforma.

Pacote npm: `@mobilenext/mobile-mcp`

## Instalacao

```bash
claude mcp add -s project -t stdio mobile -- npx -y @mobilenext/mobile-mcp@latest
```

Tambem roda como servidor HTTP: `npx @mobilenext/mobile-mcp@latest --listen 3000`.

## Pre-requisitos

| Alvo | Exige |
|---|---|
| Android (Windows, macOS, Linux) | Node 20+, Android Platform Tools (`adb`), emulador ou device com depuracao USB |
| iOS | Node 20+, Xcode command line tools, Simulator aberto — **so em macOS** |

**No Windows so ha caminho Android.** Nao existe simulador iOS fora do macOS.

## Tools (~30, em seis grupos)

| Grupo | Qtd | Exemplos |
|---|---|---|
| Gerenciamento de device | 6 | listar devices, tamanho de tela, orientacao, localizacao, clipboard |
| Devices remotos / nuvem | 3 | autenticacao, listar remotos, alocar e liberar |
| Gerenciamento de app | 6 | listar, abrir, encerrar, instalar, desinstalar |
| Interacao com tela | 8 | screenshot, listar elementos, tap, swipe, gravacao |
| Entrada e navegacao | 3 | digitar, botoes de hardware, abrir URL |
| Logs e crash | 3 | logs do device, listar e obter crash reports |

## Por que ele e barato apesar de 30 tools

Trabalha sobre a **arvore de acessibilidade nativa**, nao sobre imagem. Nao gasta token de
visao a cada passo, e o resultado e deterministico: nao quebra quando a tela muda de DPI
ou de tema. Screenshot existe como fallback (tap por coordenada) quando o elemento nao
esta exposto na arvore.

## Riscos

- Dirige device de verdade. Instalar, desinstalar e limpar dados sao operacoes reais.
- Nunca aponte para device com conta de producao ou dado de cliente.
- ~30 tools carregadas em sessao que nao e mobile e desperdicio puro — ligue por tarefa.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 3.3
- Skill relacionada no repo: `mobile-design`
