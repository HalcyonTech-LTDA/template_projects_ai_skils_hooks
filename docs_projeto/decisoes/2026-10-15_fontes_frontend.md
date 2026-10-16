---
title: Fontes de frontend — Refero, Arc e Cult UI nas skills de design
type: decisao
status: aprovado
created: 2026-10-15
updated: 2026-10-15
project: template_projetos
tags: [decisao, skills, design, frontend, tema/tooling]
---

# 2026-10-15 — Fontes de frontend nas skills de design

## O que mudou

1. Novo `.claude/skills/_shared/fontes-frontend.md` — protocolo comum: pesquisa com
   referencia nomeada, reference lock, componente de registry antes de componente inventado,
   verificacao por screenshot, convivencia Arc + Cult, lista de vetados, portabilidade
2. Quatro skills ganharam um **passo 0** que aponta para o protocolo e repete as quatro regras
   inegociaveis: `design-taste-frontend`, `ui-ux-pro-max`, `frontend-design`,
   `redesign-existing-projects`. Ajustes pontuais onde o texto contradizia o protocolo:
   - `design-taste-frontend`: Arc e Cult na tabela 2.A; excecao a "um sistema por projeto"
   - `ui-ux-pro-max`: a saida do `--design-system` passa a ser suplemento — o lock vence
   - `frontend-design`: o "tom extremo" deriva da referencia principal, nao de uma lista
   - `redesign-existing-projects`: sequencia vira Scan → Diagnose → Reference → Fix → Verify,
     com screenshot antes e depois
3. `inject-rules.js` passou a listar so pastas com `SKILL.md`. Antes listava qualquer pasta —
   `obsidian-skills/` (pacote, nao skill) aparecia como skill, e `_shared/` apareceria
4. Contagem corrigida: **49 skills**. O "50" anterior contava `obsidian-skills/`
5. Fichas novas: [[../referencias/refero|refero]], [[../referencias/ui-arc|ui-arc]],
   [[../referencias/cult-ui|cult-ui]]. Secao 8 nova em [[../SKILLS|SKILLS.md]]

## Por que

Pedido: basear o frontend em uiarc.dev, refero.design e pro.cult-ui.com/illustrations, mais
as skills existentes, "para parar de fazer design de IA".

Ao ingerir, as tres nao eram a mesma coisa: Refero e acervo de referencia (sem codigo), Arc
e Cult sao registries de componente. A critica levantada antes de executar:

- Biblioteca de componente sozinha so troca um default por outro. O que ataca a causa do
  "design de IA" — decidir sem olhar nada — e a pesquisa obrigatoria antes do codigo
- Parte do Cult (border beam, halo, glow, vidro fosco) **e** a estetica de IA
- Arc e Cult colidem em nome de token e no seletor de tema escuro

## Decisoes do usuario

| Pergunta | Resposta |
|---|---|
| Escopo | Editar as skills existentes (nao criar skill nova, nao so documentar) |
| Plano Refero | Nao — so o metodo, sem MCP |
| Arc x Cult | Liberado misturar |
| Aceite | Referencias citadas antes de codar + revisao visual por screenshot |
| Skills-alvo | As quatro listadas acima |
| Skill `refero-design` | Absorver o metodo, nao instalar |
| Componentes "cara de IA" do Cult | Vetar nominalmente |
| Projeto sem React | Portar o codigo dos registries |

## Alternativas descartadas

- **Skill nova `frontend-sources`** orquestrando pesquisa → direcao → instalacao. Reprodutivel,
  mas soma uma skill as 15+ de design que ja colidem por gatilho
- **So documentacao** (fichas + precedencia em `SKILLS.md`). Barato, mas depende de o agente
  ler `SKILLS.md`; as skills continuariam mandando escolher estetica "de memoria"
- **Instalar `refero-design`**. Sua `description` se declara "Primary/default skill for UI
  design" e manda preterir as genericas — disputa direta com a arvore de precedencia

## Por que um arquivo compartilhado

Repetir o protocolo inteiro (~200 linhas) em quatro `SKILL.md` garante divergencia na
primeira correcao. Cada skill carrega so as quatro regras inegociaveis (funcionam mesmo se o
arquivo nao for lido) e aponta para `_shared/`. Custo: o ajuste de uma linha no hook.

## Consequencias

- `design-taste-frontend` e `redesign-existing-projects` **divergem do upstream** da
  `taste-skill`. O `computedHash` em `skills-lock.json` continua registrando a versao
  instalada do upstream, nao o conteudo atual — coerente com a politica de fork
  ([[2026-09-07_skills_taste]])
- Sem MCP do Refero, a pesquisa pelo site depende de navegador (Playwright ou Chrome):
  WebFetch nao renderiza o site
- Item **Arc Pro** nunca entra neste repositorio: a licenca proibe uso em template
- Propagar `_shared/`, as quatro skills e o hook para os projetos derivados por copia

## Riscos em aberto

- Lista de vetados do Cult foi feita sobre o `registry.json` de 2026-10-15. Componente novo
  com o mesmo efeito nao esta coberto pelo nome — so pelo criterio da secao 4
- Licenca Pro do Arc estava marcada como rascunho
- O MCP `shadcn` falhou ao conectar (timeout) na sessao desta decisao; e o caminho natural
  para instalar dos dois registries
