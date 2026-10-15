# AGENTS.md (SYNTHETIC FIXTURE)

Instructions for coding agents working in this folder.

## Build and test

- No install step. Python 3.9+ standard library only.
- Run tests from this folder: `python -m unittest discover -s tests -t .`
- Verbose: `python -m unittest discover -s tests -t . -v`

## Conventions

- Keep the package dependency free. Do not add third-party packages.
- Tests use `unittest`, one file per area under `tests/`, named `test_*.py`.
- Every bug fix ships with a regression test that fails before the fix.
- Never log or print passwords, hashes or settings values.
- Do not run `login_service/admin.py` functions from tests.
