# Compass: AI Engineering Enablement Coach - Evidence Brief

Research compiled: 2026-10-15. Scope: public, generic sources only.

**How to read this document**

- **SOURCED FACT**: stated by the linked source. Numbers are quoted as the source reports them.
- **OUR ASSUMPTION**: our inference, design choice, or model input. Not a claim from any source.
- Where a figure comes from a secondary summary (blog, slides, press coverage) rather than the primary paper, it is marked *(secondary)*. Verify against the primary before putting it on a slide.
- Most delivery evidence is correlational or survey-based. Only a few studies (Copilot RCT, Google RCT, Microsoft/Accenture field experiments, METR) are randomized.

---

## 1. Evidence linking practices to signals

### 1.1 PR size vs review effectiveness and speed

| # | SOURCED FACT | Source |
|---|---|---|
| 1 | SmartBear/Cisco study guidance: review no more than 200-400 LOC at a time; "beyond 400 LOC, the ability to find defects diminishes." | https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/ |
| 2 | Same source: keep inspection rate under 500 LOC/hour; limit sessions to about 60 minutes; a 200-400 LOC review over 60-90 minutes should find 70-90% of defects. | https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/ |
| 3 | Same source: lightweight review takes less than 20% of the time of formal inspection and finds about the same number of bugs. | https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/ |
| 4 | Secondary summary of the Cisco data: defect discovery rate per hour falls above 300 LOC, with "a significant tailing off above 500 LOC." *(secondary)* | https://tekin.co.uk/2020/05/proof-your-thousand-line-pull-requests-create-more-bugs |
| 5 | Google engineering practices: small CLs are "reviewed more quickly," "reviewed more thoroughly," "less likely to introduce bugs." "100 lines is usually a reasonable size for a CL"; "1000 lines is usually too large." No hard rule. | https://google.github.io/eng-practices/review/developer/small-cls.html |
| 6 | Google code review case study (Sadowski et al., ICSE-SEIP 2018): 12 interviews, 44 survey respondents, logs for 9 million reviewed changes. | https://research.google/pubs/modern-code-review-a-case-study-at-google/ |
| 7 | Same study, per course summary slides: median change about 24 lines; median time-to-approval under 4 hours; about 75%+ of changes have a single approver; over 80% of reviews finish in one address-and-resend round. *(secondary, verify in paper)* | https://plg.uwaterloo.ca/~migod/846/current/summaries/10-Youssef-GoogleCodeReview-slides.pdf |
| 8 | LinearB 2025 benchmarks: over 6.1 million PRs from 3,000 teams; PR size identified as the most significant driver of engineering velocity; smaller PRs are easier to review and contribute to faster cycle time. (Numeric tier thresholds are in images/PDF, not extracted here.) | https://linearb.io/blog/2025-engineering-benchmarks-insights ; PDF: https://assets.linearb.io/image/upload/v1731970015/resources/LinearB_2025_Benchmark_Report.pdf |
| 9 | DORA "Working in small batches": reduces feedback time; "acts as a safety net for AI adoption"; DORA research found "working in small batches amplifies the positive impact of AI adoption on product performance." Suggests a batch over one week is too big. | https://dora.dev/capabilities/working-in-small-batches/ |

### 1.2 Review latency and cycle time

| # | SOURCED FACT | Source |
|---|---|---|
| 10 | Meta: slower P75 Time In Review correlated with lower engineer satisfaction. A "Nudgebot" experiment cut average Time In Review 7% and cut diffs waiting more than 3 days by 12%. "Next Reviewable Diff" raised review actions/day 17%. | https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/ |
| 11 | Meta nudges paper won a Distinguished Paper Award at ESEC/FSE 2022. | https://2022.esec-fse.org/details/fse-2022-research-papers/26/Using-Nudges-to-Accelerate-Code-Reviews-at-Scale |

OUR ASSUMPTION: "review rounds" (address-and-resend iterations) is a useful Compass signal because Google reports most reviews finish in one round (row 7); a persistent multi-round pattern is a coaching cue (spec clarity, PR scoping), not a performance judgment.

### 1.3 Test-first / TDD and defects

| # | SOURCED FACT | Source |
|---|---|---|
| 12 | Nagappan, Maximilien, Bhat, Williams (Empirical Software Engineering 13(3), 2008), four industrial teams at Microsoft and IBM: "pre-release defect density of the four products decreased between 40% and 90%"; "15-35% increase in initial development time." | https://doi.org/10.1007/s10664-008-9062-z ; summary: https://neverworkintheory.org/2012/01/25/realizing-quality-improvement-through-test-driven-development.html |
| 13 | Microsoft Research blog describing the same study phrases it as TDD teams "60 to 90 percent better" on defect density and 15-35% longer. Use the 40-90% figure from the paper abstract. | https://www.microsoft.com/en-us/research/blog/exploding-software-engineering-myths/ |
| 14 | Same blog: higher code coverage alone was not the best predictor of post-release failures (Microsoft ESE group). | https://www.microsoft.com/en-us/research/blog/exploding-software-engineering-myths/ |

OUR ASSUMPTION: Compass should coach on "tests added with the change" and "test-first ordering" rather than raw coverage %, given row 14.

### 1.4 AI assistants: productivity and quality

| # | SOURCED FACT | Source |
|---|---|---|
| 15 | Peng et al. (2023) controlled experiment: Copilot group completed an HTTP server task in JavaScript 55.8% faster than control. | https://arxiv.org/abs/2302.06590v1 |
| 16 | Google enterprise RCT (96 Google engineers): AI cut time on task by about 21% (best estimate; CI described as "large"). Developers who spend more hours/day coding saw larger gains. | https://arxiv.org/abs/2410.12944v3 |
| 17 | Microsoft/Accenture/Fortune-100 field experiments (4,867 developers, 3 RCTs): average 26.08% increase in completed PRs/week; less experienced developers adopted more and gained more. | https://infoq.com/news/2024/09/copilot-developer-productivity/ ; paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4945566 |
| 18 | GitHub + Accenture: PRs per developer +8.69%; PR merge rate +15%; successful builds +84%; ~30% suggestion acceptance; 88% of Copilot characters retained. (Vendor research.) | https://github.blog/2024-05-13-research-quantifying-github-copilots-impact-in-the-enterprise-with-accenture/ |
| 19 | DORA 2024: per 25% increase in AI adoption, documentation quality +7.5%, code quality +3.4%, code review speed +3.1%, but delivery throughput -1.5% and delivery stability -7.2% (estimated). 75%+ rely on AI for at least one daily task; 39% report little or no trust in AI code. | https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report |
| 20 | DORA 2025 (~5,000 respondents): 90% AI adoption; over 80% say AI improved productivity; AI now associated with higher throughput but still with higher delivery instability; AI is "a mirror and a multiplier"; median 2 hours/day with AI. | https://blog.google/technology/developers/dora-report-2025/ ; https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report ; report PDF: https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf |
| 21 | DORA AI Capabilities Model (7): clear and communicated AI stance; healthy data ecosystems; AI-accessible internal data; strong version control practices; working in small batches; user-centric focus; quality internal platforms. *(secondary list; primary report at dora.dev)* | https://developertoolkit.ai/en/org/dora-ai-capabilities/ ; primary: https://dora.dev/ai/capabilities-model/report/ |
| 22 | METR (July 2025): 16 experienced OSS developers, 246 tasks on familiar large repos; AI use made tasks take 19% longer (95% CI +2% to +39%). Developers forecast 24% speedup and afterward still believed 20% speedup. | https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ |
| 23 | METR update (Feb 2026): 57 developers, 800+ tasks, late-2025 tools; estimates -18% (returning devs, CI -38% to +9%) and -4% (new devs, CI -15% to +9%) time change; METR calls it an "unreliable signal" due to selection bias (developers unwilling to work without AI). | https://metr.org/blog/2026-02-24-uplift-update/ |
| 24 | GitClear 2025: 211 million changed lines (2020-2024); copy/pasted lines grew faster than predicted; in 2024 copy/pasted lines exceeded moved (refactored) lines for the first time. | https://www.i-programmer.info/news/105-artificial-intelligence/17871-gitclear-reveals-ais-negative-impact-on-code-quality.html ; report: https://gitclear-public.s3.us-west-2.amazonaws.com/AI-Copilot-Code-Quality-2025.pdf |
| 25 | Atlassian DevEx 2025 (3,500 devs/managers): 68% save 10+ hours/week with AI, but 50% lose 10+ hours/week to organizational inefficiencies; developers spend 16% of time coding. | https://www.atlassian.com/blog/developer/developer-experience-report-2025 |

OUR ASSUMPTION: the evidence supports a "practice matters more than tool access" thesis. Speed gains are real in controlled tasks (rows 15-17) but can vanish or reverse for experts on familiar code (row 22), and stability can drop without small batches and testing (rows 9, 19, 20). This is the core rationale for coaching on *how* AI is used, not *how much*.

### 1.5 Repo instruction / context files for agents (AGENTS.md etc.)

| # | SOURCED FACT | Source |
|---|---|---|
| 26 | Lulla et al. (2026): 10 repos, 124 PRs; with AGENTS.md present, median agent runtime fell 28.64% and output tokens fell 16.58%, with comparable task completion. | https://arxiv.org/abs/2601.20404 |
| 27 | Gloaguen et al. (ETH Zurich / LogicStar, Feb 2026): LLM-generated context files slightly *reduced* success (about -0.5% SWE-bench Lite, -2% AGENTbench) and raised cost ~20-23%; developer-written files improved success ~4% on average but raised steps and cost (up to 19%). Authors recommend human-written files describe only minimal requirements. | https://arxiv.org/html/2602.11988v1 |
| 28 | Agent READMEs study: 2,303 context files from 1,925 repos; most cover testing (75.9%), implementation (70.8%), architecture (68.1%); few cover security (14.8%) or performance (14.5%). | https://arxiv.org/abs/2511.12884 |

OUR ASSUMPTION: Compass should recommend *short, human-curated* context files (build/test commands, conventions, guardrails) and flag missing security/performance guidance, not auto-generate long files. Evidence is early (2025-2026 preprints).

### 1.6 Flaky tests cost

| # | SOURCED FACT | Source |
|---|---|---|
| 29 | Google: almost 16% of tests have some flakiness; ~1.5% of test runs report a flaky result; ~84% of observed pass-to-fail transitions in post-submit involve a flaky test. | https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html |
| 30 | Memon et al., "Taming Google-Scale Continuous Testing" (ICSE-SEIP 2017): of 115,160 targets that both passed and failed, 46,694 were labeled flakes. | https://huang.isis.vanderbilt.edu/cs8395-f23/paper/google-testing-icse-seip-17.pdf |
| 31 | Leinen et al. (ICST 2024, industrial case, ~30 devs, 5 years): flaky tests consumed at least 2.5% of productive developer time (1.1% investigating, 1.3% repairing, 0.1% tooling). | https://conf.researchr.org/details/icst-2024/icst-2024-industry/1/Cost-of-Flaky-Tests-in-CI-An-Industrial-Case-Study |

### 1.7 Prompt / specification quality and LLM coding outcomes

| # | SOURCED FACT | Source |
|---|---|---|
| 32 | Larbi et al. (2025): imperfect task descriptions reduce Pass@1 by about 25-30% (ambiguous), 20-25% (incomplete), and up to 40% (contradictory) on average; GPT-4 HumanEval Pass@1 fell from 73.8% to 6.7% on contradictory descriptions; runnable-but-wrong code rose from 24% to 54-89%. Models could not reliably detect unclear prompts. | https://arxiv.org/html/2507.20439v1 |
| 33 | GitHub Spec Kit (Sept 2025): argues agents "need unambiguous instructions" and promotes spec-driven development where "intent is the source of truth." (Practitioner position, not an experiment.) | https://github.blog/ai-and-ml/github-copilot/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/ |

OUR ASSUMPTION: Compass can score prompt/spec *structure* (goal, constraints, acceptance criteria, examples) locally and privately, and suggest a better template. Note that some 2026 preprints report mixed effects of prompt wording, so recommendations should be framed as experiments, not rules.

---

## 2. Measurement frameworks and guidance against individual metrics

| # | SOURCED FACT | Source |
|---|---|---|
| 34 | SPACE (Forsgren, Storey et al., ACM Queue 2021): use "a handful of metrics across at least three dimensions"; include at least one perceptual (survey) measure; activity metrics "should never be used in isolation either to reward or to penalize developers"; for privacy "report only anonymized, aggregate results at the team or group level." | https://queue.acm.org/detail.cfm?id=3454124 |
| 35 | DORA metrics (5): change lead time, deployment frequency, failed deployment recovery time, change fail rate, deployment rework rate. Setting metrics as goals "increases the likelihood that teams will try to game the metrics"; meant for an application/service, not for comparing dissimilar teams. | https://dora.dev/guides/dora-metrics/ |
| 36 | DORA 2025 report: measurements "are taken at the application or service level"; best comparison is the same application over time. | https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf |
| 37 | DX Core 4: four dimensions (speed, effectiveness, quality, impact). Docs list PR throughput (speed), DXI (effectiveness), change fail % / defect ratio (quality), innovation ratio (impact). DX advises diffs per FTE be counterbalanced by DXI and used "by not setting targets or rewards tied to them." | https://docs.getdx.com/dx-core-4.md ; https://getdx.com/research/measuring-developer-productivity-with-the-dx-core-4/ |
| 38 | Goodhart (1975): "Any observed statistical regularity will tend to collapse once pressure is placed upon it for control purposes." Strathern (1997): "When a measure becomes a target, it ceases to be a good measure." | https://en.wikipedia.org/wiki/Goodhart%27s_law |
| 39 | k-anonymity (Sweeney 2002): each person's record cannot be distinguished from at least k-1 others in the release. Int. J. Uncertainty, Fuzziness and Knowledge-based Systems 10(5):557-570. | https://dataprivacylab.org/projects/kanonymity/index.html |
| 40 | Microsoft Viva Insights: minimum group size must be at least 5. | https://learn.microsoft.com/en-us/viva/insights/advanced/setup-maint/privacy-settings |
| 41 | Microsoft Copilot Dashboard: default minimum group size 10, minimum allowed 5; groups below threshold are not shown. | https://learn.microsoft.com/viva/insights/advanced/admin/manage-settings-copilot-dashboard |
| 42 | UK ICO worker-monitoring guidance: solely automated decisions with significant effects are restricted (UK GDPR Art. 22); human reviewers must meaningfully weigh and be able to override; tell workers and give "meaningful information about the logic involved." | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/what-do-we-need-to-do-if-we-use-monitoring-tools-that-use-solely-automated-processes/ |

Note: we did not find a public Google re:Work page specifying a minimum group size; we use the Microsoft thresholds (rows 40-41) as the cited industry practice.

OUR ASSUMPTIONS (design rules for Compass):
- Manager views require k >= 5 (floor), default k = 10, mirroring rows 40-41. Suppress any cell below k, and suppress complementary cells that would let a small group be derived by subtraction.
- No per-person score, rank, or leaderboard exists anywhere in the data model, so it cannot be exported.
- Each manager view combines at least three SPACE dimensions and includes one survey measure (row 34).
- Signals are never targets (rows 35, 38); recommendations are opt-in and engineer-owned.

---

## 3. Competitive landscape

| Product | What it does (SOURCED) | Individual coaching? | Privacy stance (SOURCED) | Source |
|---|---|---|---|---|
| GitHub Copilot usage metrics (dashboard + API) | 28-day usage trends, code generation and impact dashboards; NDJSON reports at enterprise, org, repo, and user level; GA Feb 2026. | No automated recommendations; user-level API is suggested for spotting training needs. | Admin-visible; user-level data exists; relies on IDE telemetry. No dedicated privacy section on the docs page. | https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/copilot-usage-metrics/copilot-metrics ; https://github.blog/changelog/2026-02-27-copilot-metrics-is-now-generally-available ; https://docs.github.com/en/rest/copilot/copilot-metrics |
| Microsoft AI-Engineering-Coach (community, MIT) | VS Code extension that reads your local AI session logs; 45 editable rules across prompt quality, session hygiene, review, tool mastery, context management; suggests skills; Learning Center quizzes; audits instruction files. | Yes, individual and self-only. | "No data leaves your machine" (some optional features call the Copilot LM). No team aggregation. Not an official Microsoft product. | https://github.com/microsoft/AI-Engineering-Coach |
| DX (getdx, acquired by Atlassian, ~$1B, announced Sept 18, 2025) | Engineering intelligence: DX Core 4, DXI surveys, AI measurement by commit/PR/team/agent, team dashboards, benchmarking. | Not described as individual coaching. | Not stated on homepage beyond policy links; advises no targets/rewards on diffs per FTE. | https://getdx.com/ ; https://siliconangle.com/2025/09/18/atlassian-acquires-developer-productivity-startup-dx-1b/ |
| LinearB | Workflow automation (PR routing, approvals), AI code review, AI impact and productivity insights, MCP server, resource allocation. | No dedicated coaching feature listed. | Compliance-focused messaging (audits, DPF, DPA); no individual-metrics stance on homepage. | https://linearb.io/ |
| Jellyfish AI Impact | Vendor-neutral AI adoption, spend, and delivery-outcome tracking across Copilot, Cursor, Claude Code, agents; tool comparison; Enablement Insights to find power users and gaps. | Manager-facing; identifies power users. | Links Trust Center; adoption data can show individual users. | https://jellyfish.co/platform/ai-impact/ |
| Swarmia | Engineering metrics, DORA, DevEx surveys, AI adoption and cost, investment balance. | Positions itself as helping managers "coach developers" with visibility of individual work. | SOC 2 Type 2; no explicit individual-data policy on the page. | https://www.swarmia.com/ ; https://www.swarmia.com/developer-productivity |
| Faros AI | AI coding impact across tools; adoption, acceptance, PR cycle time, PR size, review time, quality; cohort comparisons; power-user champions. (Page marked archived.) | Team-level; power-user identification optional. | "Dashboard data is at the team level"; individual identification optional; SOC 2, ISO 27001. | https://faros.ai/copilot-module |
| Flow (formerly Pluralsight Flow; acquired by Appfire, Feb 5, 2025) | SEI platform unifying Jira/GitHub/GitLab/ADO data into standardized, benchmarked productivity metrics for leaders. | Leader-facing; no individual coaching described. | Not stated in sources reviewed. | https://appfire.com/newsroom/appfire-acquires-flow |
| Microsoft Viva Insights / Copilot Dashboard | Workplace and Copilot adoption analytics for leaders. | Not engineering coaching. | Min group size >= 5; Copilot Dashboard default 10. | https://learn.microsoft.com/viva/insights/advanced/admin/manage-settings-copilot-dashboard |

### How Compass differs (OUR POSITIONING, not sourced)

| Dimension | Copilot metrics | AI-Engineering-Coach | SEI platforms (DX, LinearB, Jellyfish, Swarmia, Faros, Flow) | **Compass** |
|---|---|---|---|---|
| Primary user | Admins | Individual engineer | Engineering leaders | **Engineer first; manager second** |
| Signals | AI usage telemetry | Local AI session logs | Delivery + AI adoption + surveys | **AI usage patterns + delivery signals (PR size, review rounds, CI first-pass, tests added, flaky tests)** |
| Output | Charts | Practice scores, rules | Dashboards, benchmarks | **Next-best practice / prompt / agent recommendation, with "why" evidence links** |
| Manager visibility | User-level available | None | Team, often individual drill-down | **k-anonymous aggregates only (k >= 5, default 10); no drill-down** |
| Individual scoring/ranking | Possible via API | Personal scores only | Varies | **None by design** |
| Closes the loop to delivery outcomes | Partly (impact dashboard) | No | Yes, at team level | **Yes, privately per engineer and aggregated per team** |

---

## 4. Business value model inputs

### 4.1 SOURCED inputs

| # | SOURCED FACT | Source |
|---|---|---|
| 43 | US software developers median annual wage $135,980 (May 2025); ~1.7M jobs. | https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm |
| 44 | BLS ECEC (June 2026), management/professional occupations (civilian): $78.85/hour total compensation, benefits 32.6% of total. | https://www.bls.gov/news.release/ecec.t02.htm |
| 45 | BLS ECEC (June 2026), private industry: benefits 30.0% of compensation. | https://www.bls.gov/news.release/ecec.nr0.htm |
| 46 | Stripe Developer Coefficient (2018): developers spend 17.3 hours/week on maintenance (bad code, debugging, refactoring) of a 41.1-hour week; 3.8 hours/week on bad code. | https://stripe.com/files/reports/the-developer-coefficient.pdf |
| 47 | Atlassian 2025: 50% of developers lose 10+ hours/week to organizational inefficiencies. | https://www.atlassian.com/blog/developer/developer-experience-report-2025 |
| 48 | Flaky tests: at least 2.5% of productive developer time in one industrial case. | https://conf.researchr.org/details/icst-2024/icst-2024-industry/1/Cost-of-Flaky-Tests-in-CI-An-Industrial-Case-Study |
| 49 | Meta: review nudges cut average Time In Review 7%. | https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/ |

### 4.2 OUR ASSUMPTIONS and model

- Fully loaded cost per engineer = median wage / (1 - benefits share) = $135,980 / 0.674 = **~$201,750/year**. Excludes equipment, space, and management overhead, so it is conservative.
- Productive hours/year = **1,800** (assumption) -> loaded hourly rate **~$112**.
- Working weeks/year = **46** (assumption).
- Compass annual cost C = **$500,000** (assumption: build, hosting, LLM inference, 1-2 enablement staff). Replace with real numbers.

**Formula (transparent):**

```
Annual value V = N x E x H x W x R
  N = engineers (1,000)
  E = share of engineers who act on Compass recommendations
  H = hours saved per engaged engineer per week (less review wait, rework, flaky-test triage, better AI prompting)
  W = working weeks (46)
  R = loaded hourly rate ($112)
ROI = (V - C) / C
```

| Scenario | E | H (h/week) | Hours/year | V | ROI at C = $500k |
|---|---|---|---|---|---|
| Conservative | 30% | 0.5 | 6,900 | $772,800 | 55% |
| Expected | 50% | 1.5 | 34,500 | $3,864,000 | 673% |
| Optimistic | 70% | 3.0 | 96,600 | $10,819,200 | 2,064% |

Plausibility anchors for H (OUR reasoning): 0.5 h/week is ~1.2% of a 41-hour week, below the 2.5% flaky-test time cost (row 48) alone; 3 h/week is ~7%, well under the Stripe maintenance share (row 46) and the Atlassian lost-time figure (row 47).

Caveats (OUR):
- Time saved is capacity, not cash. Atlassian (row 25) shows AI savings can be absorbed by friction. Report as "capacity hours redeployed" unless finance confirms.
- Quality upside (fewer incidents, lower change fail rate) is excluded, which keeps the model conservative.
- Measure with a pilot: compare team-level aggregates before/after (DORA guidance: same service over time), not individuals.

---

## 5. Responsible AI and governance references

| # | SOURCED FACT | Source |
|---|---|---|
| 50 | NIST AI RMF 1.0 released Jan 26, 2023; core functions Govern, Map, Measure, Manage; Generative AI Profile (NIST AI 600-1) released Jul 26, 2024; Playbook available. | https://www.nist.gov/itl/ai-risk-management-framework ; https://airc.nist.gov/airmf-resources/playbook/ |
| 51 | NIST trustworthy AI characteristics: valid and reliable; safe; secure and resilient; accountable and transparent; explainable and interpretable; privacy-enhanced; fair with harmful bias managed. *(secondary summary)* | https://docs.modulos.ai/frameworks/nist-ai-rmf/trustworthy-ai |
| 52 | ISO/IEC 42001:2023 (published Dec 2023): AI management system standard, Plan-Do-Check-Act, risk-based. | https://www.iso.org/standard/42001 |
| 53 | ISO/IEC 42001 Annex A (39 controls) includes A.5 assessing impacts of AI systems (incl. A.5.3 impact assessment), A.8 information for interested parties (incl. A.8.5 enabling human actions in response to AI outputs), A.9 use of AI systems (incl. A.9.5 human oversight). *(secondary summary)* | https://bastion.tech/learn/iso42001/annex-a-controls |
| 54 | UK ICO: meaningful human review and transparency about logic for worker-monitoring tools. | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/what-do-we-need-to-do-if-we-use-monitoring-tools-that-use-solely-automated-processes/ |

OUR mapping to Compass controls:
- **Explainability (NIST, ISO A.8):** every recommendation shows the triggering signal, the practice, and the evidence link from this file.
- **Human oversight (ISO A.9.5, ICO):** recommendations are advisory; the engineer accepts, dismisses, or snoozes. No automated decisions about people.
- **Privacy-enhanced (NIST):** individual data visible only to that engineer; k-anonymous aggregation for managers; data minimization (metadata, not code or prompt text, leaves the device where possible); retention limits.
- **Impact assessment (ISO A.5):** run a lightweight AI impact assessment before pilot, covering misuse risk (e.g., attempts to de-anonymize or rank).
- **Fairness:** monitor whether recommendation rates differ by team or tenure; DORA and field experiments show effects vary by experience (row 17).

---

## 6. Hackathon demo guidance

SOURCED tips:
- Lead with the problem; show the solution working within about 90 seconds; one end-to-end flow; before/after contrast; pre-fill forms and mock slow calls; be candid about what is real vs not; rehearse and time it. https://blog.jetbrains.com/ai/2026/06/how-to-win-a-hackathon-notes-from-the-judging-table/
- Tell a story from a recognizable problem; name the AI model and how you validated output quality; create one memorable moment; prepare for questions on real vs mocked; keep a recorded backup demo. https://angelhack.com/blog/10-tips-to-help-you-rock-your-next-hackathon-demo/

OUR suggested 5-minute structure:

| Time | Segment | Content |
|---|---|---|
| 0:00-0:40 | Problem | AI is everywhere (DORA 2025: 90% adoption) but stability drops and experts can slow down (DORA 2024 -7.2%; METR 19%). Leaders measure usage, not practice. |
| 0:40-1:00 | Promise | Private coach for engineers; k-anonymous insights for managers; no ranking. |
| 1:00-3:00 | Live demo, engineer view | Persona with large PRs + multi-round reviews + no context file. Compass shows signal -> recommendation -> evidence link -> one-click template (PR split, AGENTS.md starter, spec prompt). Show before/after on a sample PR. |
| 3:00-3:50 | Manager view | Team aggregates only; show a group under k suppressed ("Not enough people to show"). Memorable moment: try to drill into an individual and the system refuses. |
| 3:50-4:30 | Value | ROI table (conservative/expected/optimistic), clearly labeled assumptions. |
| 4:30-5:00 | Trust and next steps | NIST/ISO mapping, what is real vs mocked, pilot plan. Backup recording ready. |

---

## Open gaps to verify before final pitch
- LinearB numeric benchmark tiers (PR size, cycle time) are in the PDF images; extract from https://assets.linearb.io/image/upload/v1731970015/resources/LinearB_2025_Benchmark_Report.pdf.
- Google code review medians (row 7) are from course slides; confirm in the paper PDF.
- DORA AI Capabilities list (row 21) is from a secondary site; confirm at dora.dev.
- Context-file evidence (rows 26-28) is from 2025-2026 preprints with mixed results.
