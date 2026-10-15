# LOGIN-3: Create tests for the login feature

> SYNTHETIC user story for demo purposes. Not from a real backlog.

## Story

As a developer on the login service,
I want automated tests that cover how sign-in behaves,
so that regressions in password checking are caught before UAT.

## Acceptance criteria

1. **Given** a known user and the correct password, **when** `authenticate` is called, **then** it returns `True`.
2. **Given** a known user and a wrong password, **when** `authenticate` is called, **then** it returns `False`, including when the wrong password has the same length as the correct one.
3. **Given** an unknown username, **when** `authenticate` is called, **then** it returns `False`.
4. Tests run with the standard library only: `python -m unittest discover -s tests -t .`
5. Tests do not print or log passwords.

## Out of scope

- Account lockout after repeated failures (tracked separately, not implemented yet).
