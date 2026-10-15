# Responsible AI and guardrails

## Principles built into the product

| Principle | How Compass enforces it |
|---|---|
| Enablement, not evaluation | No score, rank, rating or label for any person exists in the data model or API. The compliance check fails the build if a ranking-style route appears. Teams are listed alphabetically, never ordered by performance. |
| Privacy by design | Individual coaching is visible only to the engineer. Manager and leader views use k-anonymous aggregates (k = 5), hide small patterns, and exclude small teams from totals. |
| Data minimization | Metadata only: no source code, prompt content, free text or PII. The prompt coach processes pasted text in memory and never stores it. |
| Explainability | Every recommendation names the rule, the threshold (a fixed practice guideline, not a peer comparison), the signals, the evidence records and a cited source. |
| Human oversight | Recommendations are optional. Engineers dismiss or give feedback. Generated prompts tell agents to plan first and wait for approval. Nothing is applied automatically. |
| Honesty about uncertainty | Simulations are labeled "simulated" with documented assumptions. Correlations are labeled "association, not causation". Seeded evaluation results are described as regression tests, not held-out accuracy. |
| Fairness | Rules use fixed practice thresholds, so the same behavior gets the same suggestion regardless of team or seniority. Persona context changes *how* advice is phrased and which tool is suggested, never *whether* someone is flagged. Recommend monitoring recommendation rates by team in aggregate during a pilot. |
| Safe AI usage | The sensitive-data scan runs before any prompt is generated. Every agent-kit file forbids secrets, PII and production data, and requires test evidence and human review before merge. |

## Framework mapping

| Framework | Compass control |
|---|---|
| NIST AI RMF, **Govern** | Owner and operational model ([nfr-security.md](nfr-security.md)); eval gate on rule changes |
| NIST AI RMF, **Map** | Documented intended use (coaching) and prohibited use (performance evaluation) |
| NIST AI RMF, **Measure** | `python -m compass eval` (quality), `python -m compass compliance` (data), access audit |
| NIST AI RMF, **Manage** | k threshold, suppression, delete-my-data, kill switch (stop the service; no downstream automation) |
| ISO/IEC 42001 A.5 (impact assessment) | Recommended before pilot: misuse scenarios such as de-anonymization or ranking attempts, with tested mitigations |
| ISO/IEC 42001 A.8 (information for users) | "Why" and evidence on every recommendation; "How it works" page |
| ISO/IEC 42001 A.9.5 (human oversight) | Engineer control; plan-first prompts; human review before merge |

## Prohibited uses (state these in any rollout)

- Using Compass output in performance reviews, compensation, promotion or staffing decisions.
- Re-identifying engineers from aggregated views or combining them with other data to do so.
- Lowering k below 5, or exporting raw signals to managers.
