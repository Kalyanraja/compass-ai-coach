---
description: 'Java conventions (Java 17+, Spring Boot friendly) and JUnit 5 test rules.'
applyTo: '**/*.java'
---
<!-- practice: P3 test-first-acceptance -->

# Java rules

## Code
- Target Java {{JAVA_VERSION}}. Use records for immutable data carriers, `Optional` for return values only (not fields or parameters).
- Constructor injection only; no field injection. Keep Spring components stateless.
- Prefer `final` locals and fields. Avoid nulls in public APIs; validate arguments with clear exceptions.
- Use specific exceptions; never catch `Exception` or `Throwable` and swallow it. Never `catch (...) {}`.
- Use try-with-resources for anything `AutoCloseable`.
- Use parameterized queries (`PreparedStatement`, JPA parameters). Never concatenate SQL.
- Log with SLF4J placeholders (`log.info("Saved order {}", id)`); never log secrets or personal data.

## Tests (JUnit 5)
- Static-import assertions explicitly (`import static org.junit.jupiter.api.Assertions.assertEquals;`).
- `assertEquals(expected, actual)`: expected first. Use a delta for floating point.
- Use `assertAll` for related properties, `assertThrows` (or `assertThrowsExactly` when the exact type is the contract) and inspect the message.
- Use `@ParameterizedTest` with `@CsvSource`/`@MethodSource` for input tables. `@DisplayName` for readable names.
- Do not mix JUnit 4 (`org.junit.Assert`) with JUnit 5.
- Prefer slice tests (`@WebMvcTest`, `@DataJpaTest`) over full `@SpringBootTest` when possible. Use Testcontainers or an in-memory equivalent approved by the team for integration tests.
- Run: `{{TEST_CMD}}` (for example `mvn -q test` or `./gradlew test`).

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
