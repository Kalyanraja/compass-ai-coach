# Example fixtures (SYNTHETIC)

> Everything under `examples/` is synthetic. These are made-up projects for
> demoing and testing Compass AI Workflow Coach. They contain seeded defects,
> gaps and a fake credential on purpose. No real companies, people, services or
> secrets are involved.

| Fixture | Runnable | What it demonstrates |
| --- | --- | --- |
| [`java-orders-api/`](java-orders-api/) | No (static) | **Missing API requirements**: OpenAPI spec breaks synthetic standard STD-API-1 (no `X-Correlation-Id`), STD-API-2 (no 400 on POST), STD-API-3 (no bearer auth). Story ORD-12 has happy-path-only criteria. No AGENTS.md. Recorded surefire report with 1 pass, 1 fail. |
| [`py-login-service/`](py-login-service/) | Yes, stdlib only | **Test detecting a seeded defect** (wrong password of the same length accepted). **Defect fix without repro evidence** (`fixes/fix-no-repro.diff`) vs fix with a regression test (`fixes/fix-with-repro.diff`). **Security findings**: synthetic credential in `config/settings.ini`, `shell=True` in `login_service/admin.py`. Vague UAT defect report. Has AGENTS.md. |
| [`legacy-batch-unknown/`](legacy-batch-unknown/) | No | **Unknown stack fallback**: COBOL-like and JCL-like files. The coach should say "unknown" and ask, not guess. |

## Quick check

```
cd examples/py-login-service
python -m unittest discover -s tests -t .
```

Expected: `Ran 4 tests`, `FAILED (failures=1)`. Seeded issues and expected results are in [TESTER-NOTES.md](TESTER-NOTES.md), kept outside the fixture folders so they never end up in a work package.
