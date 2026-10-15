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

## Seeded gaps (for testers)

The spec in `src/main/resources/openapi.yaml` deliberately breaks the synthetic standard:

- **STD-API-1** - no operation declares the `X-Correlation-Id` header parameter.
- **STD-API-2** - `POST /orders` has no `400` response and there is no error schema with `code` and `message`.
- **STD-API-3** - no `components.securitySchemes` and no `security` block.
- **STD-API-4** - satisfied: `CreateOrderRequest` has a `required` list (a control, should not be flagged).

Other things the coach should notice:

- `docs/stories/ORD-12.md` only has a happy-path Given/When/Then. Nothing about
  auth, error responses, headers, or what happens when the order is already
  shipped or cancelled. The coach should ask about these.
- There is **no AGENTS.md** on purpose, so "agent instructions present" should
  come back as missing or unknown.
- `recorded/surefire-TEST-OrderControllerTest.xml` is recorded sample evidence:
  `createOrderReturns201` passes, `createOrderWithMissingFieldsReturns400` fails
  with `Status expected:<400> but was:<500>`. It was hand-written, not produced
  by a build.
