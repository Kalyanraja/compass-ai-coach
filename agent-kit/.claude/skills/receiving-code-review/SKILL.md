---
name: receiving-code-review
description: Use when you receive code review feedback (from a human, Copilot code review, or another agent), before changing code, especially if a comment is unclear or seems technically wrong. Verify each item against the codebase, clarify first, push back with evidence when needed, and fix one item at a time with tests.
metadata:
  practice: P6 verify-before-done; P2 pr-readiness-selfcheck
  source: adapted from obra/superpowers receiving-code-review (MIT)
---

# Receiving Code Review

Technical evaluation, not performative agreement.

## Pattern
1. **Read** all feedback before reacting.
2. **Understand**: restate each item as a technical requirement. Unclear? Ask before implementing anything (items are often related).
3. **Verify** against the code: does the claim hold in this codebase? Would the change break something? Is there a reason for the current code?
4. **Evaluate**: correct for this stack and these constraints? Is the suggested feature actually used (search for callers)? If unused, propose removal (YAGNI).
5. **Respond**: a short technical acknowledgment, or reasoned pushback with evidence (test, file:line, docs).
6. **Implement** one item at a time: blocking issues (bugs, security) > simple fixes > complex changes. Test after each.

## Do not
- "You're absolutely right!", "Great point!", "Thanks for catching that" - state the fix instead.
- Implement before verifying, or implement the clear items and silently skip the unclear ones.
- Argue for style when the reviewer is right.

## Good responses
- "Fixed: null check added in `OrderService.java:42`, test `should_reject_null_customer`."
- "Checked: target runtime is X, which lacks this API, so the fallback stays. Alternative: drop support for X?"
- "Nothing calls this endpoint (searched). Remove it instead of extending it?"
- If you pushed back and were wrong: "Verified, you are right because <reason>. Fixing."

## Escalate to the human when
- Feedback conflicts with an earlier human decision or the spec.
- Feedback asks for an architectural change.

## Output
```
| # | Item | Verdict (accept / push back / clarify) | Evidence | Change | Test |
Verification: <full suite result>
```

## Safety
- Do not paste secrets or production data into review replies.
- Reply in the review thread; a human resolves threads and approves the PR.
