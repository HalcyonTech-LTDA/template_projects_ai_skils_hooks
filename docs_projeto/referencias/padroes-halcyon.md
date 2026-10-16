---
title: Padroes Halcyon - repos modern-* e projetos iniciais no GitHub
source: https://github.com/HalcyonTech-LTDA
type: referencia
status: aprovado
tags: [referencia, skills, padroes, java, spring, tema/tooling]
created: 2026-10-15
updated: 2026-10-15
verificado_em: 2026-10-15
---

# Padroes Halcyon (HalcyonTech-LTDA)

Metodo: `gh repo view` em cada repo e clone raso do `main` pelo script de importacao, em
2026-10-15. Os commits abaixo sao os da importacao. O valor vivo esta em `padroes-lock.json`.

## 1. Repos de padrao (copiados para `.claude/skills/`)

Todos sao publicos, tem licenca MIT e funcionam como plugin do Antigravity e do Claude Code. A
anatomia e a mesma em todos: `skills/<nome>/SKILL.md` com `references/`, `rules/<x>.md` com
`trigger: model_decision`, `claude/skills/` com o guardrail gerado e `installed_version.json`.

| Repo | Commit | Versao | Skills |
|---|---|---|---|
| [modern-java-best-practices](https://github.com/HalcyonTech-LTDA/modern-java-best-practices) | `0cf5920` | 1.3.0 | 5 |
| [modern-spring-boot-best-practices](https://github.com/HalcyonTech-LTDA/modern-spring-boot-best-practices) | `b65d98c` | 1.0.0 | 1 |
| [modern-spring-boot-microservices-best-practices](https://github.com/HalcyonTech-LTDA/modern-spring-boot-microservices-best-practices) | `2694066` | 1.0.0 | 5 |
| [modern-mongodb-best-practices](https://github.com/HalcyonTech-LTDA/modern-mongodb-best-practices) | `a97c77c` | 1.0.0 | 4 |
| [modern-docker-best-practices](https://github.com/HalcyonTech-LTDA/modern-docker-best-practices) | `29a41c1` | 1.0.0 | 3 |
| [modern-git-best-practices](https://github.com/HalcyonTech-LTDA/modern-git-best-practices) | `0f238ee` | 1.0.0 | 4 |
| [modern-k6-best-practices](https://github.com/HalcyonTech-LTDA/modern-k6-best-practices) | `12be707` | 1.0.0 | 4 |
| [modern-postman-newman-best-practices](https://github.com/HalcyonTech-LTDA/modern-postman-newman-best-practices) | `7d5169a` | 1.0.0 | 4 |
| [modern-wiremock-best-practices](https://github.com/HalcyonTech-LTDA/modern-wiremock-best-practices) | `01e92c1` | 1.0.0 | 3 |
| [modern-azure-bicep-best-practices](https://github.com/HalcyonTech-LTDA/modern-azure-bicep-best-practices) | `052843d` | 1.0.0 | 8 |
| [modern-business-blueprint-plugin](https://github.com/HalcyonTech-LTDA/modern-business-blueprint-plugin) | `16546e2` | 1.2.0 | 13 + 5 agentes |

Pontos de atencao:

- Politica comum: so recurso de linguagem finalizado, sem `--enable-preview`. A linha de base
  e Java 21+, Spring Boot 3.x+, Gradle Kotlin DSL e regra anti-Lombok
- No Bicep, o `installed_version.json` continuou em 1.0.0 mesmo com 4 skills novas. A versao do
  repo nao basta para detectar mudanca; o commit, sim
- O guardrail `claude/skills/*` **nao** foi copiado (ver a decisao)

## 2. Projetos iniciais (nao copiados)

| Repo | Template no GitHub | Papel |
|---|---|---|
| [java-clean-architecture-scaffolding](https://github.com/HalcyonTech-LTDA/java-clean-architecture-scaffolding) | sim | **Padrao** para servico Java. Gerador interativo `init-project.sh` |
| [ms-template-java](https://github.com/HalcyonTech-LTDA/ms-template-java) | sim | Referencia: Java 26, Gradle com `build-logic`, Taskfile, Lefthook, CI, k6, Newman, WireMock, migrate-mongo, perfis `api` e `scheduling` |
| [scaffolding-app-IOS-Android](https://github.com/HalcyonTech-LTDA/scaffolding-app-IOS-Android) | nao | Template React Native nao executavel (sem entrypoint, Gradle e Xcode) |

## 3. Marketplace

`HalcyonTech-LTDA/halcyon-plugins` **nao existe no GitHub** em 2026-10-15. O template nao depende
dele. Se um dia for publicado, a alternativa a copia passa a ser `extraKnownMarketplaces` mais
`enabledPlugins` no `.claude/settings.json` do projeto, com skills namespaced
(`<plugin>:<skill>`).

Uso no template: [[../PADROES|PADROES.md]]. Decisao: [[../decisoes/2026-10-15_padroes_halcyon]].
