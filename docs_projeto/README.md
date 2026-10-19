---
title: docs_projeto
type: readme
status: aprovado
created: 2026-05-28
updated: 2026-10-15
tags: [readme, indice]
---

# docs_projeto

Documentacao do **repositorio template** e do **template de projeto** que ele entrega.

## Indice

### Sobre o repo template

- [[HOWTO]] — como clonar este repo e iniciar um projeto novo
- [[CONVENCOES]] — schema de properties, naming, tags, IDs
- [[HOOKS]] — regras do projeto injetadas via hook do Claude Code
- [[STATUSLINE]] — barra com a issue da sessao, status do board, modelo, esforco, contexto e tokens da sessao com subagentes
- [[MCPS]] — catalogo de servidores MCP: quais ligar, quando desligar, custo de contexto
- [[SKILLS]] — catalogo de skills e precedencia entre as de design (qual usar quando)
- [[PADROES]] — padroes Halcyon (`modern-*`): skills por stack, projeto inicial e script de importacao do GitHub
- [[COMMITS]] — convencao de commits e a skill `/commit` (preencher por projeto)
- [[WORKTREES]] — agentes paralelos em worktrees e a skill `/worktree`
- [[AGENTES]] — subagentes do projeto e a skill `/issue`: qual agente e modelo por tamanho de tarefa
- [[BOARD]] — IDs e ajustes do board do GitHub deste projeto; o metodo esta na skill `/trilha`
- [[decisoes/README|decisoes/]] — registros de mudancas estruturais neste repo
- [[referencias/README|referencias/]] — resumos de links/normas/bibliotecas citadas

### Template de projeto (entregue para novos projetos)

- [[docs_Template_Projeto/Home|docs_Template_Projeto]] — esqueleto a ser duplicado
- [[docs_Template_Projeto/_templates/README|Templates Obsidian]] — moldes de notas

### Views (bases cross-projeto)

- [[_views/Documentos_por_Clausula.base|Documentos por clausula]]
- [[_views/Rascunhos_Pendentes.base|Rascunhos pendentes]]
- [[_views/Documentos_Obsoletos.base|Documentos obsoletos]]

## Para que existe esta pasta

Duas funcoes:

1. **Documentar o proprio repo template** (HOWTO, CONVENCOES, HOOKS, decisoes/, referencias/) — vive aqui apenas.
2. **Carregar o template de projeto** (`docs_Template_Projeto/`) que sera duplicado para cada projeto novo.

Quando clonar para um projeto real, a parte 1 e opcional (pode deletar) e a parte 2 e o que voce de fato usa.
