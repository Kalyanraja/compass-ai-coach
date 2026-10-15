---
description: 'TypeScript/JavaScript conventions and Jest/Vitest test rules.'
applyTo: '**/*.ts,**/*.tsx,**/*.js,**/*.jsx,**/*.mjs,**/*.cjs'
---
<!-- practice: P3 test-first-acceptance -->

# TypeScript / JavaScript rules

## Code
- `strict` TypeScript. No `any` without a comment; prefer `unknown` plus narrowing. Explicit return types on exported functions.
- `async`/`await` over raw promise chains. Always handle rejections; no floating promises.
- Prefer `const`, pure functions and immutable updates. Keep modules small with explicit exports.
- Validate external input at boundaries (for example with the repo's schema library, {{SCHEMA_LIB}}).
- Never use `eval`, `new Function`, or `innerHTML`/`dangerouslySetInnerHTML` with untrusted data.
- Never commit `.env` files or keys; read config from environment.

## Tests (Jest or Vitest)
- Files `*.test.ts` next to the code or in `__tests__/`. `describe` per unit, `it('should ... when ...')` per behavior.
- Use fake timers (`jest.useFakeTimers()` / `vi.useFakeTimers()`) instead of real waits.
- Mock modules at the boundary (`jest.mock`/`vi.mock` for HTTP, clock, storage); reset mocks in `afterEach`.
- For UI, query by role/label (Testing Library) and assert what the user sees.
- Avoid snapshot tests for logic; use explicit assertions.
- Run: `{{TEST_CMD}}` (for example `npm test -- --run` or `npx jest`).

## Safety
- No secrets, credentials, PII, customer or production data in prompts, code, tests, logs or commits.
- Back every claim that something works with evidence: the command you ran and its result.
- A human reviews every change before merge. Never merge, force-push or deploy.
