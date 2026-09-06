---
title: MCP Figma (Dev Mode)
source: https://developers.figma.com/docs/figma-mcp-server/
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, figma, design, tema/tooling]
---

# MCP Figma (Dev Mode)

Expoe a estrutura viva da camada selecionada no Figma: hierarquia, auto-layout, variantes,
estilos de texto e referencias de token. Transforma frame em codigo com os valores reais
do design, em vez de o modelo chutar espacamento e cor a partir de um print.

## Dois servidores, nao equivalentes

| | Remoto | Desktop |
|---|---|---|
| Endpoint | `https://mcp.figma.com/mcp` | `http://127.0.0.1:3845/mcp` |
| Plano/seat | Todos os seats e planos | Seat **Dev ou Full** em plano pago |
| Instalacao | Nenhuma, OAuth | App Figma desktop aberto, Dev Mode, servidor ligado no painel |
| Disponibilidade | Sempre | Morre quando o app Figma fecha |

O remoto e o caminho preferido pela propria Figma.

```bash
# Remoto
claude mcp add -s project -t http figma https://mcp.figma.com/mcp

# Desktop
claude mcp add -s project -t http figma-desktop http://127.0.0.1:3845/mcp
```

Atencao ao path: o endpoint desktop atual e `/mcp`. O `/sse` antigo esta obsoleto.

## Capacidades

- **Geracao de codigo** a partir do frame selecionado
- **Extracao de design**: variaveis, componentes, dados de layout
- **Operacoes de canvas**: criar e modificar conteudo Figma a partir do cliente MCP
- **Code Connect**: consistencia entre componente do design e componente do codigo
- **Recursos Make**

## Custo de contexto

Baixo. Um punhado de tools.

## Pegadinhas

- O servidor desktop depende do app aberto. Tools sumiram do `/mcp`? O Figma fechou.
- O agente precisa de uma **selecao ativa** ou de um link de node. Sem isso as tools nao
  tem o que ler.
- Gerar codigo direto do Figma sem revisao produz markup fiel e arquitetura ruim. Use como
  fonte de **valores** (tokens, espacamento, tipografia), nao como gerador final.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 3.2
- Skills relacionadas no repo: `frontend-design`, `ui-ux-pro-max`, `ui-design-system`
