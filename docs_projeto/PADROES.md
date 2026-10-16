---
title: Padroes Halcyon de engenharia
type: convencao
status: aprovado
created: 2026-10-15
updated: 2026-10-15
project: template_projetos
tags: [convencao, skills, padroes, java, spring, tema/tooling]
---

# Padroes Halcyon de engenharia

A Halcyon mantem seus padroes de engenharia em **repositorios proprios no GitHub**
(`HalcyonTech-LTDA/modern-*`). Este template traz uma **copia** das skills deles em
`.claude/skills/`, para que todo projeto derivado ja nasca com os padroes, sem instalar plugin
nem depender de marketplace.

> **A fonte e o GitHub, nao este repositorio.** Diferente das skills proprias do template,
> correcao num padrao comeca no repo `modern-*` dele e desce para ca pelo script de importacao
> (secao 4). Editar a copia aqui e perder a edicao na proxima importacao.

## 1. Stack → skills → padrao

Cada repo traz skills especializadas e uma regra-guarda (`rules/`), que vira
`.claude/skills/_shared/padroes-<stack>.md`. A regra-guarda diz qual skill usar para cada tipo
de tarefa e lista o que e inegociavel. **Leia a da stack antes de comecar.**

| Stack | Repo de origem | Skills | Regra-guarda |
|---|---|---|---|
| Java | [modern-java-best-practices](https://github.com/HalcyonTech-LTDA/modern-java-best-practices) | `modern-java-idioms`, `modern-java-clean-architecture`, `modern-java-concurrency`, `modern-java-testing`, `modern-gradle-conventions` | `padroes-java.md` |
| Spring Boot | [modern-spring-boot-best-practices](https://github.com/HalcyonTech-LTDA/modern-spring-boot-best-practices) | `modern-spring-boot-conventions` | `padroes-spring-boot.md` |
| Microsservicos Spring | [modern-spring-boot-microservices-best-practices](https://github.com/HalcyonTech-LTDA/modern-spring-boot-microservices-best-practices) | `modern-microservices-architecture-and-decomposition`, `-event-driven-and-data-consistency`, `-inter-service-communication`, `-observability-and-resilience-ops`, `-perimeter-gateway-and-security` | `padroes-spring-boot-microservices.md` |
| MongoDB | [modern-mongodb-best-practices](https://github.com/HalcyonTech-LTDA/modern-mongodb-best-practices) | `modern-mongodb-data-modeling`, `-indexing-and-queries`, `-migrations-and-lifecycle`, `-resilience-and-ops` | `padroes-mongodb.md` |
| Docker | [modern-docker-best-practices](https://github.com/HalcyonTech-LTDA/modern-docker-best-practices) | `modern-dockerfile-craftsmanship`, `modern-compose-workflows`, `modern-dockerignore-context` | `padroes-docker.md` |
| Git | [modern-git-best-practices](https://github.com/HalcyonTech-LTDA/modern-git-best-practices) | `modern-git-cli-and-workflows`, `-commit-craftsmanship`, `-rebase-and-history`, `-recovery-and-security` | `padroes-git.md` |
| Carga (k6) | [modern-k6-best-practices](https://github.com/HalcyonTech-LTDA/modern-k6-best-practices) | `modern-k6-test-craftsmanship`, `-workloads-and-thresholds`, `-orchestration-and-reporting`, `-living-documentation` | `padroes-k6.md` |
| API (Postman/Newman) | [modern-postman-newman-best-practices](https://github.com/HalcyonTech-LTDA/modern-postman-newman-best-practices) | `modern-postman-collection-craftsmanship`, `modern-postman-environments-and-secrets`, `modern-newman-orchestration-and-ci`, `modern-newman-living-documentation` | `padroes-postman-newman.md` |
| Mocks HTTP (WireMock) | [modern-wiremock-best-practices](https://github.com/HalcyonTech-LTDA/modern-wiremock-best-practices) | `modern-wiremock-declarative-stubs`, `-orchestration-and-testing`, `-living-documentation` | `padroes-wiremock.md` |
| Azure (Bicep) | [modern-azure-bicep-best-practices](https://github.com/HalcyonTech-LTDA/modern-azure-bicep-best-practices) | `modern-bicep-modular-architecture`, `-security-and-governance`, `-deployment-stacks-and-lifecycle`, `-testing-and-ci-cd`, `-container-apps-and-jobs`, `-cosmos-db`, `-api-management-and-policies`, `-workbooks-and-observability` | `padroes-azure-bicep.md` |
| Negocio | [modern-business-blueprint-plugin](https://github.com/HalcyonTech-LTDA/modern-business-blueprint-plugin) | 13 skills `modern-*` de estrategia, GTM, financas e governanca + 5 agentes (secao 3) | `padroes-business-blueprint.md` |

Nomes com `-` no inicio repetem o prefixo da primeira skill da linha. A lista exata, com o
commit de origem, esta em `padroes-lock.json` na raiz.

**Projeto derivado:** cite no `CLAUDE.md` a regra-guarda das stacks que ele usa (ex.: "antes de
codar, leia `.claude/skills/_shared/padroes-java.md` e `padroes-spring-boot.md`"). A
regra-guarda nao dispara sozinha; as skills disparam pela `description`, a regra so e lida se
alguem apontar para ela.

## 2. Projeto inicial por tipo

Os padroes dizem **como** escrever; o projeto inicial e **de onde** partir. Sempre pelo GitHub:

| Tipo de projeto | Partir de | Como |
|---|---|---|
| Servico Java (**padrao**) | [java-clean-architecture-scaffolding](https://github.com/HalcyonTech-LTDA/java-clean-architecture-scaffolding) | `gh repo create HalcyonTech-LTDA/<nome> --template HalcyonTech-LTDA/java-clean-architecture-scaffolding --private --clone` e depois `./init-project.sh` |
| Microsservico Java de referencia | [ms-template-java](https://github.com/HalcyonTech-LTDA/ms-template-java) | Consulta, nao ponto de partida: mostra os padroes aplicados juntos (Taskfile, CI, k6, Newman, WireMock, Mongo, Docker) |
| App mobile (React Native) | [scaffolding-app-IOS-Android](https://github.com/HalcyonTech-LTDA/scaffolding-app-IOS-Android) | `git clone --depth 1 https://github.com/HalcyonTech-LTDA/scaffolding-app-IOS-Android <nome>` e apague o `.git`. Nao executavel por design: faltam entrypoint, Gradle e Xcode |

Os dois repos Java estao marcados como template no GitHub; o mobile nao, por isso o clone.
A conta dona do repo novo (organizacao ou pessoal) se confirma com o usuario: nao ha regra.

## 3. Agentes do blueprint de negocio

O repo de negocio traz 5 agentes, convertidos para o formato do Claude Code em `.claude/agents/`:

| Agente | Papel | Como roda |
|---|---|---|
| `blueprint-orchestrator-agent` | Recebe a ideia bruta, despacha os especialistas, sintetiza o blueprint | **Sessao principal:** `claude --agent blueprint-orchestrator-agent` |
| `business-strategist-agent` | Categoria, motor economico, fosso | Subagente (sonnet) |
| `product-gtm-lead-agent` | Cabeca de praia, MVP, go-to-market | Subagente (sonnet) |
| `corporate-architect-agent` | Arquitetura tecnica, PI, governanca | Subagente (sonnet) |
| `finance-venture-agent` | Unit economics, P&L, capital, tese | Subagente (sonnet) |

O orquestrador nao funciona como subagente: no Claude Code um subagente nao chama outro. Por
isso ele roda como agente da sessao, com `tools: Agent(...)` restrito aos quatro especialistas.
A secao "Runtime Multi-Agent Execution Protocol (Antigravity CLI)" de
`_shared/padroes-business-blueprint.md` descreve a mesma sequencia no Antigravity; no Claude
Code, as etapas valem e o despacho e o de cima. O corpo dos agentes ainda cita
`subagent: true/false`, campo que o Claude Code ignora.

**Limite de uso na Halcyon.** O blueprint produz a concepcao de uma empresa a partir de uma
ideia; ele **nao valida** a ideia. No vault da Halcyon, ideia de produto so sobe pelo funil de
contraprova da Pesquisa & Inovacao. Use o blueprint depois da contraprova, nunca no lugar dela.

## 4. Atualizar e podar

```bash
node .claude/scripts/importar-padroes.js              # reimporta os 11 repos do GitHub (main)
node .claude/scripts/importar-padroes.js --only java  # so um repo, pelo nome curto
node .claude/scripts/importar-padroes.js --dry-run    # mostra o que faria
```

O script clona cada repo do GitHub, substitui as pastas que ele gerencia, regrava as
regras-guarda e os agentes, e grava commit e versao no `padroes-lock.json`. Ele recusa
sobrescrever skill ou agente que nao esteja no lock. Depois de rodar, leia o `git diff` antes de
commitar: e assim que mudanca de padrao entra revisada.

**Podar num projeto derivado.** As 54 skills somam descricoes em todo prompt. Um projeto que
nao usa uma stack apaga as pastas dela, a regra-guarda e a entrada do lock. A partir dai,
reimporta com uma execucao de `--only <curto>` por stack mantida (o flag aceita uma stack por
vez). Rodar sem `--only` traz de volta tudo o que foi podado.

Precedencia contra as skills genericas do template: [[SKILLS]] secao 10.
