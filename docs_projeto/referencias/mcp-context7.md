---
title: MCP Context7
source: https://context7.com/docs/resources/all-clients
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, documentacao, tema/tooling]
---

# MCP Context7

Injeta documentacao **atual** da biblioteca que voce esta usando, na versao que voce esta
usando. Resolve a classe de bug mais chata de agente: API que existia no treinamento e nao
existe mais.

## Instalacao

```bash
claude mcp add -s user -t http context7 https://mcp.context7.com/mcp
```

Endpoint remoto, transporte HTTP streamable. Sem instalacao local.

## Custo de contexto

**Minimo** — cerca de 2 tools (resolver a biblioteca, buscar a doc).

## Por que ele e o melhor custo/beneficio do catalogo

Duas tools contra uma classe inteira de erro: metodo que nao existe, assinatura mudada,
padrao de uso obsoleto. Nao ha outro item da lista com essa relacao.

Se o projeto so puder ligar um MCP opcional, ligue este.

## Limites

- Cobre bibliotecas indexadas. Lib interna ou muito nova pode nao estar la.
- Nao substitui ler o codigo-fonte da dependencia quando o comportamento e sutil.
- Traz a doc, nao o julgamento: o modelo ainda pode escolher a API errada entre duas que
  existem.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 4
