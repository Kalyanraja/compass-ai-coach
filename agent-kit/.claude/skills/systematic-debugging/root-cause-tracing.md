# Root cause tracing

Adapted from obra/superpowers (MIT). Bugs often surface deep in the call stack. Fix where the bad value is born, not where it explodes.

## Process
1. **Observe the symptom**: the exact error and location.
2. **Find the immediate cause**: the line that directly fails.
3. **Ask what called it, with what value**: walk up the callers (`find usages`, stack trace).
4. **Keep tracing** until you reach the value's origin: input, config, test setup, default, race.
5. **Fix at the source**, then add validation at the layers in between (`defense-in-depth.md`).

## When you cannot trace by reading
Add temporary instrumentation right before the failing operation:
- log the suspicious arguments, current directory, relevant config, and a stack trace (`new Error().stack`, `Thread.dumpStack()`, `Environment.StackTrace`, `traceback.print_stack()`)
- log to stderr in tests so the test runner does not swallow it
- never log secrets or personal data
Run once, read the stack, find the test or caller that passes the bad value.

## Finding which test pollutes shared state
Run test files one at a time (bisect) until the polluting file appears. Then trace inside that file.

## Output
```
Symptom: <error> at <file:line>
Chain: <origin file:line> -> <caller> -> ... -> <symptom>
Origin: <why the bad value exists>
Fix at source: <change>
Layer checks added: <list>
```

## Safety
- A human reviews every change before merge.
