---
description: 'Python conventions (typed, PEP 8) and pytest rules.'
applyTo: '**/*.py'
---
<!-- practice: P3 test-first-acceptance -->

# Python rules

## Code
- Target Python {{PYTHON_VERSION}}. Add type hints to public functions; keep `mypy`/`pyright` clean if configured.
- Follow PEP 8 and the repo formatter ({{PY_FORMATTER}}, for example ruff or black). Do not reformat unrelated code.
- Raise specific exceptions. Never use bare `except:` or `except Exception: pass`.
- Use context managers (`with`) for files, connections and locks.
- SQL: use driver parameters (`cursor.execute(sql, params)`) or the ORM. Never f-string input into SQL or shell commands; avoid `shell=True`.
- Do not use `eval`, `exec` or `pickle` on untrusted data. Use `yaml.safe_load`.
- Log with `logging` and lazy formatting (`log.info("saved %s", order_id)`); never log secrets or personal data.

## Tests (pytest)
- Files `test_<module>.py`; functions `test_<behavior>_when_<condition>`.
- Use fixtures for setup; `tmp_path` for files; `monkeypatch` for env and time.
- Use `pytest.mark.parametrize` for input tables and `pytest.raises(..., match=...)` for errors.
- No `time.sleep` waits; poll a condition with a timeout or inject the clock.
- Run: `{{TEST_CMD}}` (for example `pytest -q`). Coverage: `pytest --cov={{PACKAGE}} --cov-report=term-missing`.

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
