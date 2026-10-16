---
title: Padroes Halcyon copiados do GitHub para o template
type: decisao
status: aprovado
created: 2026-10-15
updated: 2026-10-15
project: template_projetos
tags: [decisao, skills, padroes, agentes, tema/tooling]
---

# 2026-10-15 — Padroes Halcyon (`modern-*`) no template

## O que mudou

1. 54 skills de 11 repos `HalcyonTech-LTDA/modern-*` copiadas para `.claude/skills/`
   (62 → 116 skills)
2. A regra-guarda de cada repo (`rules/*.md`) virou `.claude/skills/_shared/padroes-<stack>.md`
3. 5 agentes do blueprint de negocio convertidos para o formato do Claude Code em `.claude/agents/`
4. Script `.claude/scripts/importar-padroes.js`: clona do GitHub, substitui o que gerencia e
   grava a procedencia em `padroes-lock.json`
5. Docs: [[../PADROES|PADROES.md]] (novo), [[../SKILLS|SKILLS.md]] secao 10, [[../AGENTES|AGENTES.md]],
   `CLAUDE.md`, ficha [[../referencias/padroes-halcyon|padroes-halcyon]]

## Por que

O usuario pediu que 15 repos de `Desenvolvimento/Tools/` virassem padroes de desenvolvimento
dos projetos, **pelo caminho do GitHub e nao pelo disco local**. Onze sao plugins do Claude Code.
Tres sao projetos iniciais: dois Java e um mobile. O ultimo, `halcyon-plugins`, e o marketplace
que lista os plugins, e ele nunca foi publicado.

A recomendacao inicial era registrar o marketplace no `settings.json` e ligar plugin por stack.
O usuario escolheu **copiar** e **nao publicar o marketplace**. A copia tem uma vantagem: o
projeto derivado nasce com os padroes sem instalar nada. Tem tambem um custo: uma segunda copia
que pode divergir. O script existe para pagar esse custo. A fonte continua sendo o repo
`modern-*`, e a reimportacao e um comando so.

O GitHub era a fonte certa: no dia da importacao, o Bicep tinha 8 skills no GitHub e 4 na
pasta local.

## Desenho

- **Guardrail fora, regra dentro de `_shared/`.** O guardrail do plugin (`claude/skills/*`)
  aponta para `${CLAUDE_PLUGIN_ROOT}/rules/`, que nao existe fora de plugin. O guardrail do
  Spring tambem tinha o mesmo nome da skill (`modern-spring-boot-conventions`). Copiar a regra
  para `_shared/` resolve as duas coisas, e o hook ignora a pasta
- **Lock proprio.** O `computedHash` do `skills-lock.json` vem do CLI `skills` e nao bate com o
  sha256 do arquivo. Em vez de inventar hash, o `padroes-lock.json` guarda repo, commit e versao
- **Script recusa sobrescrever** skill ou agente que nao esteja no lock. Os 5 agentes de
  desenvolvimento estao protegidos por nome
- **Orquestrador como sessao principal.** No Claude Code subagente nao chama subagente, por isso:
  `claude --agent blueprint-orchestrator-agent`, com `tools: Agent(...)` restrito aos quatro

## Decisoes do usuario

| Pergunta | Resposta |
|---|---|
| Como chegam aos projetos | Copiar as skills |
| Marketplace `halcyon-plugins` | Nao publicar, nem publico nem privado |
| Projeto inicial Java | `java-clean-architecture-scaffolding` (`ms-template-java` fica como referencia) |
| Colisao com skills do template | Precedencia escrita e teste |
| Blueprint de negocio | Copiar skills e agentes |
| Fonte | GitHub, nunca caminho local |

## Riscos aceitos

- **116 descricoes de skill no prompt** e 10 agentes. Projeto derivado poda as stacks que nao usa
  (PADROES secao 4)
- **Copia diverge da origem** se alguem editar aqui. Mitigacao: aviso no cabecalho de cada
  regra-guarda e direcao invertida declarada no `CLAUDE.md`
- **O blueprint nao valida ideia.** No vault, ideia de produto passa pelo funil de contraprova
  antes

## Teste

O script rodou duas vezes com resultado identico (o sha256 agregado nao mudou). Nao ha `name:`
duplicado nem referencia a `CLAUDE_PLUGIN_ROOT` ou caminho local. O hook `inject-rules.js` lista
as 116 skills e os 10 agentes. Os 5 agentes do blueprint carregaram como tipos validos na sessao.
