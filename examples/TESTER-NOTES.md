# Tester notes for the synthetic fixtures

> These notes describe the seeded defects and gaps. They live OUTSIDE the fixture projects on purpose, so Compass never sends the answer key to an assistant inside a work package.

## java-orders-api

### Seeded gaps (for testers)

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

## py-login-service

## Expected results (as shipped)

| Test file | Tests | Expected |
| --- | --- | --- |
| `tests/test_login_smoke.py` | 2 | both pass (they are weak and do not catch the defect) |
| `tests/test_login_behaviour.py` | 2 | `test_unknown_user_is_rejected` passes, `test_wrong_password_same_length_is_rejected` **FAILS** |

Summary line: `Ran 4 tests` then `FAILED (failures=1)`, exit code 1.

## Fix diffs

Apply from this folder (use a copy if you want to keep the fixture intact):

| Diff | Changes | Tests after applying |
| --- | --- | --- |
| `fixes/fix-no-repro.diff` | `login_service/auth.py` only, no test added | `Ran 4 tests`, `OK` |
| `fixes/fix-with-repro.diff` | `login_service/auth.py` plus new `tests/test_regression_wrong_password.py` | `Ran 7 tests`, `OK` |

```
patch -p1 < fixes/fix-with-repro.diff
```

Both also pass `git apply --check`.

## Fix diffs

Apply from this folder (use a copy if you want to keep the fixture intact):

| Diff | Changes | Tests after applying |
| --- | --- | --- |
| `fixes/fix-no-repro.diff` | `login_service/auth.py` only, no test added | `Ran 4 tests`, `OK` |
| `fixes/fix-with-repro.diff` | `login_service/auth.py` plus new `tests/test_regression_wrong_password.py` | `Ran 7 tests`, `OK` |

```
patch -p1 < fixes/fix-with-repro.diff
```

Both also pass `git apply --check`.

### Seeded issues (for testers)

- **Defect** in `login_service/auth.py`: `authenticate` accepts a wrong password
  when it has the same length as the right one.
- **Missing feature**: lockout. `config/settings.ini` has `max_failed_attempts`
  and `lockout_minutes`, but nothing uses them.
- **Synthetic credential** in `config/settings.ini` (`admin_password`). It is
  fake and marked SYNTHETIC. It uses no real provider token format.
- **Shell injection risk** in `login_service/admin.py`: `subprocess.run(..., shell=True)`
  with a caller-supplied string. Never executed by the tests.
- **Weak tests** in `tests/test_login_smoke.py` pass even with the defect.
- **Vague defect report** in `docs/uat-defect-LOGIN-7.md`: no repro steps, no
  expected or actual results, so the coach should ask.
- `AGENTS.md` is present, so "agent instructions present" should be detected.
