# Defense in depth

Adapted from obra/superpowers (MIT). One check fixes the bug; checks at every layer make it impossible.

After finding a root cause caused by invalid data, add validation where the data crosses each layer:

| Layer | Check | Example |
|---|---|---|
| Entry point (API, CLI, message handler) | Reject invalid input with a clear error | empty ID, out-of-range amount |
| Business logic | Assert invariants the domain requires | order total equals sum of lines |
| Environment guard | Refuse dangerous operations in the wrong context | refuse to delete outside a temp dir in tests |
| Diagnostics | Log context before risky operations (no secrets) | operation, target, caller |

Rules:
- Fail fast with specific messages. Do not silently "fix" bad data.
- Each layer gets its own test proving it rejects the bad value.
- Do not duplicate business rules in many places; validate shape at the edge, meaning in the domain.

## Safety
- A human reviews every change before merge.
