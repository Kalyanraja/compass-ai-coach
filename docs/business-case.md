# Business case

All figures with a source are cited in [research/evidence.md](research/evidence.md). Everything labeled **assumption** is ours and should be replaced with real pilot numbers.

## The problem, in numbers

- AI adoption is near universal: DORA 2025 reports 90% adoption, with a median of 2 hours a day using AI.
- Adoption alone does not improve delivery. DORA 2024 estimated that each 25% increase in AI adoption came with a 7.2% drop in delivery stability and a 1.5% drop in throughput. Teams that work in small batches see the benefit amplified.
- Experienced developers can get slower. In METR's 2025 study they took 19% longer on familiar code, while believing they were 20% faster.
- Prompt quality matters: ambiguous or incomplete task descriptions cut first-try correctness by 20-30%.
- Usage dashboards show who used which tool. They do not show which practices work, and individual-level usage data creates privacy and trust problems. SPACE guidance says activity metrics should never be used alone to reward or penalize, and results should be reported only as team aggregates.

## Current state vs future state

| | Current state | With Compass |
|---|---|---|
| Engineer | Has tools, little guidance. Picks the convenient tool. Writes underspecified prompts. Learns by trial and error. | Gets one evidence-backed next step, privately. Gets a complete prompt for the right tool in three clicks. Uses ready-made files in the repo. |
| Manager | Sees license and usage counts, or nothing. Risks drifting into individual monitoring. | Sees team patterns shared by 5 or more engineers, with a concrete enablement action and kit files. |
| Leader | Can't tell whether the AI investment changes delivery. | Sees portfolio patterns and practices associated with better signals, labeled non-causal, with a pilot plan to measure. |
| AI enablement team | Writes generic training. | Targets enablement at observed gaps. Ships practices as files that work in every repo. |

## Value model (transparent)

```
Annual value V = N x E x H x W x R
  N  engineers in scope
  E  share who act on Compass recommendations          (assumption)
  H  hours saved per engaged engineer per week          (assumption)
  W  working weeks per year = 46                        (assumption)
  R  loaded hourly rate = about $112                    (derived: BLS median wage / (1 - 32.6% benefits) / 1,800 h)
ROI = (V - C) / C
```

For N = 1,000 engineers:

| Scenario | E | H (hours/week) | Capacity hours/year | Value V | ROI at C = $150k | ROI at C = $500k |
|---|---|---|---|---|---|---|
| Conservative | 30% | 0.5 | 6,900 | $0.77M | 415% | 55% |
| Expected | 50% | 1.5 | 34,500 | $3.86M | 2,476% | 673% |
| Optimistic | 70% | 3.0 | 96,600 | $10.8M | 7,113% | 2,064% |

**Cost assumptions.** C = $150k/year assumes the deterministic design here: no license, no inference cost, and roughly one engineer maintaining rules and the agent kit. C = $500k is a stress case with a hosted service and an enablement team.

**Plausibility.** 0.5 hours a week is about 1.2% of a working week, which is below the 2.5% of developer time that flaky tests alone consumed in one industrial study. 3 hours a week is about 7%, well under the maintenance and inefficiency shares reported by Stripe and Atlassian.

**Caveats.** Saved time is capacity, not cash. The quality upside (fewer incidents, lower change-fail rate) is excluded, which keeps the model conservative. The pilot should measure team-level aggregates before and after on the same services, never individuals.

## Value by rubric category

- **Productivity:** fewer review rounds and shorter PR cycle time (P1, P2), less time writing tests (P3), fewer stuck agent sessions (P4, P5).
- **Cost:** no new licenses. Better use of existing Copilot, Claude Code and Devin seats. Routes deterministic chores away from AI, which saves tokens and premium requests.
- **Risk reduction:** a sensitive-data warning before anything is pasted into AI, test evidence required before "done", flaky-test hardening, no employee monitoring.
- **Developer experience:** private, optional, explainable coaching that engineers control.
- **Delivery time:** smaller PRs and first-pass CI shorten lead time.

## Competitive landscape

| | Copilot usage metrics | Microsoft AI-Engineering-Coach | Engineering-intelligence platforms (DX, LinearB, Jellyfish, Swarmia, Faros, Flow) | **Compass** |
|---|---|---|---|---|
| Primary user | Admins | Individual engineer | Leaders | **Engineer first, then manager** |
| Signals | AI telemetry | Local AI session logs | Delivery plus adoption | **AI usage patterns plus delivery signals** |
| Output | Charts | Prompt-hygiene rules | Dashboards | **Next-best practice, prompt or agent, with cited evidence and a ready prompt** |
| Manager visibility | User-level available | None | Team, often individual | **k-anonymous only, no drill-down, differencing protection** |
| Ranking or scoring people | Possible | Personal scores | Varies | **None, by design and by test** |
| Needs new licenses or cloud | Included | No | Yes | **No** |

Compass reuses ideas from AI-Engineering-Coach (rules, anti-patterns), Superpowers and Spec Kit (workflow discipline) in the agent kit, with attribution in [NOTICE.md](../NOTICE.md).
