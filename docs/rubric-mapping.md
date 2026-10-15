# Scoring rubric mapping

How Compass addresses each judging criterion, with the evidence to show.

## 1. Problem fit, innovation and user value (30%)

| Rubric item | Evidence |
|---|---|
| Problem understanding, acceptance-criteria coverage | All 14 acceptance criteria implemented and tested ([traceability](acceptance-criteria.md)); 34 tests pass |
| Originality | Combines three things that existing tools keep separate: private next-best-action coaching from delivery signals, a prompt coach that routes each task to the right approved tool (including "no AI needed"), and k-anonymous team insights with differencing protection. See the competitive table in [business-case.md](business-case.md). |
| Usefulness and simplicity | One double-click to run. Engineers reach a recommendation in two interactions and a ready prompt in three. |
| Differentiation | Coaches *how* AI is used, not *how much*. Evidence-cited and explainable. Works with tools people already have, without MCP or API keys. |
| Current vs future state | [business-case.md](business-case.md) |
| Customer journey | [user-guide.md](user-guide.md), [demo-script.md](demo-script.md) |

## 2. Business impact and implementation potential (25%)

| Rubric item | Evidence |
|---|---|
| Problem severity | DORA 2024: delivery stability fell about 7.2% for each 25% increase in AI adoption. METR 2025: experienced developers were 19% slower with AI. Usage dashboards can't explain either ([evidence](research/evidence.md)). |
| Impact magnitude, ROI | Transparent model with conservative, expected and optimistic scenarios. All inputs are labeled as assumptions ([business-case.md](business-case.md)). |
| Reusability across lines of business | No stack-specific code. The agent kit drops into any repo (`install-kit.bat`). Practices, rules and thresholds are data. Stack context covers Java, .NET, Python, TypeScript and Playwright. |
| Adoption potential | No new licenses and no new infrastructure: Python standard library only. Works offline. Pilot path in [roadmap.md](roadmap.md). |
| Implementation roadmap | [roadmap.md](roadmap.md) |

## 3. Technology excellence and AI (20%)

| Rubric item | Evidence |
|---|---|
| Architecture quality | Modular services with one responsibility each ([architecture.md](architecture.md)). Two physically separated stores. Role-based API. |
| Engineering excellence | Typed, documented Python. 34 acceptance tests. CI on Windows and Linux with Python 3.9 and 3.12. Deterministic synthetic data. |
| Effective AI usage | AI appears where it adds value: the agent kit makes Copilot, Claude Code and Devin better, and the prompt coach makes each prompt complete. The decision core is deterministic so it is explainable and testable. |
| Responsible AI | [responsible-ai.md](responsible-ai.md): no people scoring, human review points, NIST AI RMF and ISO/IEC 42001 mapping, non-causal labeling |
| Token and cost efficiency | The coach itself uses 0 tokens. Generated prompts aim to cut agent iterations by giving complete context up front, and research shows underspecified prompts reduce first-try correctness 20-30% ([evidence](research/evidence.md) row 32). |
| AI output quality | Recommendation eval at 100% on the team's 25 regression scenarios (target 80%). Prompt routing at 16/16 on the team's routing set. |
| Prompt strategy | 54-prompt library, 27 anti-patterns, tool-specific prompt shapes (plan first, evidence required, forbidden actions for Devin) |

## 4. Demo and delivery readiness (15%)

| Rubric item | Evidence |
|---|---|
| Working demonstration | `Start-Coach.bat`; [demo-script.md](demo-script.md) |
| Enterprise-approved frameworks | No third-party runtime dependencies. Python and SQLite from the standard library. Agent kit uses only official Copilot, Claude Code and Devin file formats. |
| Solution architecture | [architecture.md](architecture.md), plus the in-app "How it works" page |
| Completeness | README, setup, user guide, assumptions, limitations, roadmap |
| Code quality | Version-controlled, CI workflow, tests, MIT license, NOTICE for third-party material |

## 5. NFRs and operational governance (10%)

See [nfr-security.md](nfr-security.md): scalability path, security controls, reliability, performance figures, monitoring and operational model.
