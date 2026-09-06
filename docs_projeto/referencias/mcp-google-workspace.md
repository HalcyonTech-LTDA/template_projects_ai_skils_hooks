---
title: MCP Google Workspace
source: https://developers.google.com/workspace/guides/configure-mcp-servers
type: referencia
status: aprovado
created: 2026-09-06
updated: 2026-09-06
verificado_em: 2026-09-06
tags: [referencia, mcp, google, gmail, drive, calendar, tema/tooling]
---

# MCP Google Workspace

Acesso a Gmail, Drive, Docs, Sheets, Slides, Calendar e Chat. **E o item do catalogo com
mais caminhos possiveis e menos equivalencia entre eles.** Escolha consciente.

## Tres caminhos

### 1. Conectores claude.ai (o que existe nesta conta)

Gmail, Google Calendar e Google Drive aparecem como **conectores claude.ai**, ao lado de
Figma e Notion. Nao sao configurados por `claude mcp add`: a autorizacao acontece nas
**configuracoes de conectores do claude.ai**, e ate ser feita as tools nao funcionam.

Vantagem: gerenciado, OAuth cuidado pela Anthropic, nada em disco.
Limite: o conjunto de tools e o que a Anthropic expoe, nao o que voce escolhe.

### 2. Servidores remotos oficiais do Google

O Google publica servidores MCP remotos por produto. O do Calendar, por exemplo:

```
https://calendarmcp.googleapis.com/mcp/v1
```

Exigem configurar um **cliente OAuth proprio** (client ID e secret) no Google Cloud e
registra-lo como conector customizado. Mais trabalho de setup, mais controle.

### 3. Implementacoes de terceiros

Projetos como `taylorwilsdon/google_workspace_mcp` e `aaronsb/google-workspace-mcp` cobrem
o Workspace inteiro num servidor so, rodando local.

Vantagem: cobertura ampla, controle total.
Risco: sao servidores de terceiro segurando credencial do seu Google. Auditar antes de
usar com conta corporativa nao e opcional.

## Recomendacao

Para este template: **caminho 1** (conector claude.ai), por ser o de menor superficie de
risco. Caminho 2 quando precisar de algo que o conector nao expoe. Caminho 3 so com conta
dedicada e apos leitura do codigo.

## Custo de contexto

Alto e muito variavel. Uma implementacao que cobre nove produtos Google passa facil de 60
tools.

## Risco de dado — leia antes de ligar

Este servidor da ao agente acesso de leitura ao **e-mail corporativo inteiro**. Nao e
comparavel a ligar um MCP de banco de dados de desenvolvimento:

- E-mail contem credencial, contrato, dado de cliente e conversa privada de terceiros que
  nao consentiram.
- Prompt injection via e-mail recebido e vetor real: basta alguem mandar uma mensagem com
  instrucao embutida para o agente que a le.
- Em sessao de codigo, o ganho e proximo de zero.

Ligue por tarefa especifica (ata de reuniao, requisito que veio por e-mail, planilha de
dados), desligue em seguida.

## Ver tambem

- [[../MCPS|Catalogo de MCPs]] secao 3.8
