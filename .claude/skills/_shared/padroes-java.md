# Padroes java (importado)

Origem: https://github.com/HalcyonTech-LTDA/modern-java-best-practices/blob/0cf5920ca9d718fb0393bd78bb2bb6f0c7a37819/rules/modern-java-engineering.md (versao 1.3.0)
Gerado por `.claude/scripts/importar-padroes.js`. Nao edite aqui: corrija no repo de origem e rode o script de novo.

# Modern Java Engineering Guardrails & Skill Router

When generating, refactoring, reviewing, or testing Java code and Gradle builds, strictly adhere to the Modern Java Standard Baseline and the corresponding specialized skills:

| When working on... | Consult & Activate Skill | Key Focus Areas |
| :--- | :--- | :--- |
| **Domain & Language Idioms** | `modern-java-idioms` | OOP vs DOP synergy, records, compact constructors, pattern matching with `switch`, Sequenced Collections, Gatherers, and FFM API. |
| **Architecture & Boundaries** | `modern-java-clean-architecture` | Screaming architecture, feature-first packages, framework-free domain/application, Inbound/Outbound Ports, Anti-Corruption Layers. |
| **Concurrency & Async Tasks** | `modern-java-concurrency` | Virtual Thread per-task executors, `CompletableFuture` orchestration, and eliminating carrier thread pinning. |
| **Automated Testing & Quality** | `modern-java-testing` | In-Memory Fakes over Mocks, Singleton Testcontainers (`@ServiceConnection`), RestAssured, mutation testing (Pitest), and determinism (`Clock`, Awaitility). |
| **Gradle Builds & Dependencies** | `modern-gradle-conventions` | Kotlin DSL (`.gradle.kts`), `build-logic` convention plugins, Version Catalogs (`libs.versions.toml`), and Java toolchains. |

---

## Non-Negotiable Guardrails (Absolute Invariants)

1. **Production-Strict (No Previews)**: Never generate or rely on preview features requiring `--enable-preview` (such as `StructuredTaskScope` or `ScopedValue` in non-final releases). Use only 100% standardized Java 21+ language features and APIs.
2. **Zero Framework Leakage in Business Logic**: Never place framework annotations (Spring `@Component`, `@Service`, `@Transactional`, JPA `@Entity`, Jackson `@JsonProperty`) in `domain` or `application` packages. All framework wiring resides strictly in `infrastructure`.
3. **Strict Anti-Lombok**: Prohibit `@Data`, `@Getter`, `@Setter`, `@Builder`, and `@AllArgsConstructor`. Use native Java `record`s with compact constructors. Lombok is permitted solely for `@Slf4j` when `System.Logger` is absent.
4. **Virtual Threads Policy**: Never pool virtual threads (`Executors.newVirtualThreadPerTaskExecutor()`). Never execute blocking I/O inside `synchronized` blocks/methods (use `ReentrantLock` to prevent carrier thread pinning). Confine CPU-heavy computation to platform thread pools (`ForkJoinPool.commonPool()`).
5. **Deterministic Testing**: Never use `Thread.sleep()` (mandate Awaitility). Always inject `java.time.Clock` instead of calling `Instant.now()`. Ban JUnit 4 (`org.junit.*`); use JUnit 5 exclusively. Name unit tests `<TargetClass>Test` and integration tests `<TargetClass>IntegrationTest`.
6. **Exclusive Kotlin DSL**: Prohibit generating new Groovy (`.gradle`) scripts. Declare all dependencies and plugins exclusively in `gradle/libs.versions.toml`.

Consult the corresponding skill for complete design patterns, recipes, and detailed guides.
