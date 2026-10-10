---
title: MCP Figma (Dev Mode)
source: https://developers.figma.com/docs/figma-mcp-server/
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-27
verificado_em: 2026-09-27
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
| Plano/seat | Todos os seats e planos, com limite de chamadas (abaixo) | Seat **Dev ou Full** em plano pago |
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

## Limites de chamadas

Verificado em 2026-09-27. O limite por minuto soma com o diario ou o mensal.

| Seat | Starter | Professional | Organization | Enterprise |
|---|---|---|---|---|
| View, Collab | Ate 20/mes | Ate 6/mes | Ate 6/mes | Ate 6/mes |
| Dev, Full | Ate 20/mes (o Starter tem um limite so) | Ate 200/dia, 10/min | Ate 200/dia, 15/min | Ate 600/dia, 20/min |

- **O limite vale para as tools que leem do Figma.**
  - Isentas nomeadas: `add_code_connect_map`, `create_new_file` e `whoami`.
  - A doc diz que "algumas" tools de escrita sao isentas, mas nao cita a `use_figma`.
- **`whoami` mostra o plano e o seat sem gastar chamada.** Rode antes de planejar um ciclo de
  design para codigo.
- **Escrever no canvas (`use_figma`)** e gratis durante o beta, aberto em 2026-03-24. A Figma
  anunciou que vira API paga por uso, sem dizer o preco.
- **Preco do Professional,** por seat, na pagina de precos em 2026-09-27:
  - Full: US$ 16/mes;
  - Dev: US$ 12/mes;
  - Collab: US$ 3/mes.

  E o que tira do limite de 20/mes, desde que o seat seja Full ou Dev.

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
- **No Starter, o ciclo de design para codigo nao fecha.** Cada tela gasta varias leituras:
  estrutura, contexto de cada secao e screenshot para conferir. As 20 do mes acabam em
  poucas telas, e escrever no canvas nao ajuda a ler de volta.

## Fontes

| Fonte | Data | O que sustenta |
|---|---|---|
| [Rate limits & access](https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/) | acesso em 2026-09-27 | Tabela de limites e tools isentas |
| [Guide to the Figma MCP server](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server) | acesso em 2026-09-27 | Remoto em todos os seats e planos; desktop so em Dev ou Full pago; escrita no canvas gratis no beta |
| [Agents, meet the Figma canvas](https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/) | publicado em 2026-03-24 | Escrita no canvas gratis no beta; depois, API paga |
| [Plans & Pricing](https://www.figma.com/pricing/) | acesso em 2026-09-27 | Preco por seat do Professional |

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 3.2
- Skills relacionadas no repo: `frontend-design`, `ui-ux-pro-max`, `ui-design-system`
