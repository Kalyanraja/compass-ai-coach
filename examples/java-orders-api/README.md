# java-orders-api (SYNTHETIC FIXTURE)

> Everything in this folder is synthetic. It is a static fixture for Compass AI
> Workflow Coach demos and tests. It is not built or run, and it does not
> describe any real company, service or person.

A small Spring Boot style service for creating and reading orders.

- `POST /orders` creates an order
- `GET /orders/{id}` returns an order

## Layout

| Path | What it is |
| --- | --- |
| `pom.xml` | Maven build, Java 17, spring-boot-starter-web, spring-boot-starter-test, junit-jupiter |
| `src/main/java/com/example/orders/` | Controller, service, `Order` record |
| `src/main/resources/openapi.yaml` | OpenAPI 3.0.3 spec for the two operations |
| `src/main/resources/application.yml` | Port and logging, no secrets |
| `src/test/java/.../OrderControllerTest.java` | JUnit 5 + MockMvc, 2 tests |
| `standards/api-standard.md` | Synthetic API standard, STD-API-1 to STD-API-5 |
| `docs/stories/ORD-12.md` | Story: cancel an order, happy path only |
| `recorded/surefire-TEST-OrderControllerTest.xml` | Hand-written surefire report, 1 pass, 1 fail |
| `.github/workflows/ci.yml` | Maven CI workflow (not run) |

Tester notes (seeded issues and expected results) are in `../TESTER-NOTES.md`, outside this project folder.
