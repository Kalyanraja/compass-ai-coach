# py-login-service (SYNTHETIC FIXTURE)

> Everything in this folder is synthetic. It is a runnable fixture for Compass AI
> Workflow Coach demos and tests. It has seeded defects and a seeded fake
> credential on purpose. Do not reuse any of it.

A tiny login module, Python standard library only.

## Run the tests

From this folder:

```
python -m unittest discover -s tests -t .
```

Verbose (one line per test, easy to parse):

```
python -m unittest discover -s tests -t . -v
```

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

## Seeded issues (for testers)

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
