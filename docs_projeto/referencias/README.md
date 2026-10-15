---
title: Referencias externas
type: readme
status: aprovado
created: 2026-05-28
updated: 2026-10-15
tags: [readme, referencias]
---

# Referencias externas

Resumos de URLs, bibliotecas, normas ou conceitos citados durante o desenvolvimento que **nao** sao especificos a um projeto (esses ficam em `docs_Template_Projeto/10_Referencias/`).

> Regra 6 do projeto: se o usuario cita um link/biblioteca/conceito que o Claude nao domina, o Claude ingere via defuddle/WebFetch e salva um resumo aqui antes de prosseguir.

## Convencao

- Um arquivo por referencia: `<slug-da-referencia>.md`
- Frontmatter minimo: `title`, `source` (URL ou citacao), `type: referencia`, `tags`, `created`, `updated`
- Referencia de ferramenta viva (MCP, CLI, SDK) leva tambem `verificado_em` — a data em que o comando foi conferido na fonte
- Conteudo: resumo executivo + trechos relevantes citaveis + link/fonte

## Indice

### Claude Code

- [[claude-code-mcp-configuracao]] — escopos, expansao de `${VAR}`, OAuth, aprovacao de `.mcp.json`
- [[skills-taste-leonxlnx]] — pacote de 13 skills de design; flags do CLI `skills` e armadilhas

### Frontend — referencia e componentes

Protocolo de uso em `.claude/skills/_shared/fontes-frontend.md`; precedencia em [[../SKILLS|SKILLS.md]] secao 7.

- [[refero]] — acervo de telas e fluxos reais. Fonte de pesquisa; MCP pago nao usado
- [[ui-arc]] — componentes React animados, CSS modules sem Tailwind. Tokens colidem com shadcn
- [[cult-ui]] — registry shadcn com ilustracoes; Pro virou gratis. Tem lista de vetados

### Servidores MCP — nucleo

Catalogo decisorio e criterio de escolha em [[../MCPS|MCPS.md]].

- [[mcp-github]] — PRs, issues, code search. Alto custo de contexto; limite os toolsets
- [[mcp-figma]] — Dev Mode: design vira codigo com os valores reais; no Starter, 20 leituras por mes
- [[mcp-mobile-next]] — automacao iOS/Android por arvore de acessibilidade
- [[mcp-playwright]] — teste de aplicacao web, cross-browser
- [[mcp-terminator]] — automacao de app desktop, **Windows apenas**
- [[mcp-supabase]] — schema, migracoes, Edge Functions
- [[mcp-vercel]] — deploys, logs de build, dominios
- [[mcp-google-workspace]] — Gmail, Drive, Calendar. Ler a secao de risco antes de ligar

### Servidores MCP — opcionais

- [[mcp-context7]] — docs atualizadas de bibliotecas. Melhor custo/beneficio do catalogo
- [[mcp-chrome-devtools]] — performance e rede. Depurar, nao dirigir
- [[mcp-sentry]] — erro de producao com stack trace no contexto
- [[mcp-notion]] — base de conhecimento externa
