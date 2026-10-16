# Padroes mongodb (importado)

Origem: https://github.com/HalcyonTech-LTDA/modern-mongodb-best-practices/blob/a97c77ca94dbffd732d82950756e7a5bdcda15b1/rules/modern-mongodb-engineering.md (versao 1.0.0)
Gerado por `.claude/scripts/importar-padroes.js`. Nao edite aqui: corrija no repo de origem e rode o script de novo.

# Modern MongoDB Engineering Guardrails & Skill Router

When architecting, querying, indexing, configuring, containerizing, or migrating MongoDB databases and data models, strictly adhere to Modern MongoDB Engineering Standards and the corresponding specialized skills:

| When working on... | Consult & Activate Skill | Key Focus Areas |
| :--- | :--- | :--- |
| **Schema Design & Data Modeling** | `modern-mongodb-data-modeling` | Embedding vs referencing trade-offs, 16MB document limit boundaries, design patterns, declarative `$jsonSchema` validation, and strict BSON typing. |
| **Indexing & Query Performance** | `modern-mongodb-indexing-and-queries` | Compound indexing and ESR Rule (Equality, Sort, Range), covered queries, diagnostic profiling (`explain("executionStats")`), and `COLLSCAN` elimination. |
| **Resilience, Topology & Operations** | `modern-mongodb-resilience-and-ops` | Singleton `MongoClient` lifecycle, connection pooling, majority write/read concerns, causal consistency, and multi-document ACID transactions. |
| **Migrations, Schema Evolution & Runbooks** | `modern-mongodb-migrations-and-lifecycle` | Versioned migrations with `migrate-mongo`, distributed locking (`changelog_lock`), zero-downtime Expand/Contract, and living `README.md` runbooks. |

---

## Non-Negotiable Guardrails (Absolute Invariants)

1. **Declarative Server-Side Validation (`$jsonSchema`)**: Production collections must enforce server-side validation via `$jsonSchema` with strict levels. Do not rely solely on application-layer ORM/ODM validations.
2. **Strict BSON Typing & Bounded Document Growth**: Prohibit floating-point representations for currency (mandate `Decimal128` or minor units) and store timestamps as native UTC `Date`. Enforce document growth boundaries (16MB limit) using the Bucket, Subset, or referencing patterns.
3. **The ESR Rule & Production `COLLSCAN` Elimination**: Compound index keys must strictly follow the ESR sequence (Equality, Sort, Range). Prohibit unindexed collection scans (`COLLSCAN`), in-memory sort spills, and unindexed leading-wildcard regular expressions on production collections.
4. **Singleton Pooling & Majority Resilience**: Instantiate `MongoClient` as a bounded process-wide singleton. Production write mutations must specify `w: "majority"` with journal acknowledgement (`j: true`). Reserve multi-document ACID transactions strictly for cross-collection business invariants.
5. **Idempotent Migrations & Zero-Downtime Lifecycle**: Schema transformations must be orchestrated via versioned `migrate-mongo` scripts with distributed locking (`changelog_lock`). Apply high-traffic schema evolutions using the Expand/Contract pattern with batched cursor processing.
6. **Zero Secrets, Container Healthchecks & Dedicated Living Runbook**: Connection URIs and credentials must be resolved dynamically via environment variables. Automated setups must orchestrate container healthchecks via `mongosh`. Every directory housing migrations must maintain and atomically synchronize a dedicated living `README.md` runbook.

Consult the corresponding specialized skills for comprehensive architectural patterns, code blueprints, configuration templates, and testing runbooks.
