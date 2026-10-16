# How to Generate the Best PPT for Compass

Guidelines that produced the 16-slide deck in `docs/presentation/compass-pitch/`. Follow them for any revision or new deck — they are tuned to the official scoring rubric (`rubric/scoring-rubric.jpg`).

## 1. Design backwards from the rubric

The rubric is the contract. Before opening a slide tool, write one line per rubric row saying which slide(s) prove it:

| Weight | Rubric row | Deck evidence |
|---|---|---|
| 30% | Problem fit, innovation & user value | Problem severity data · current vs future state · competitive table · engineer journey · use-case demos |
| 25% | Business impact & implementation potential | Transparent value model with labeled assumptions · ROI scenarios · pilot path · LOB reusability |
| 20% | Technology excellence + AI | Test/eval results · architecture diagram · responsible-AI guardrails · token efficiency · prompt strategy |
| 15% | Demo & delivery readiness | Working demo instructions · demo video · repo documentation set (README, setup, deployment, assumptions, limitations) |
| 10% | NFRs & operational governance | Scalability, security/compliance, reliability, performance, operational + adoption readiness |

Include one explicit "rubric mapping" slide so judges do not have to hunt. Full traceability: `docs/rubric-mapping.md`.

## 2. Narrative arc (emotion curve)

Unease → hope → belief → urge:

1. **Pain** — big sourced numbers, one claim per page. Hook: "Adoption was never the bottleneck — guidance is."
2. **Gap** — why the current alternative (usage dashboards) fails, including the privacy trap.
3. **Solution** — what Compass is, in one sentence a tired engineer would repeat.
4. **Proof** — real screenshots, measured results, honest labels ("the team wrote the evals").
5. **Action** — how to run it, what the ask is, what happens after the hackathon.

One idea per slide; a slide is a billboard, not a document. If it needs more than ~40 words of body text, split it.

## 3. Evidence rules (never break these)

- **Never fabricate** a metric, citation, customer, or benchmark. Missing material is labeled "assumption" or "to be supplied".
- **Label estimates** (ESTIMATE) vs measured facts, exactly as the repo does in `docs/measurements.md`.
- **Cite sources** for every external number with a footnote and a link (DORA 2024/2025, METR 2025, etc.).
- **Use real screenshots** from `docs/screenshots/` — they are dark-themed and blend with the deck. No stock photos of smiling teams.
- Screenshots with hairline borders; never stretch them.

## 4. Visual system

- 16:9, dark navigator theme (tokens in `../README.md`).
- Hierarchy from **type size contrast and hairline rules** — no card walls, no rounded-rectangle stacking, no multi-color badge confetti.
- Big display numbers (48–72pt) for the stats judges remember; body 12–14pt; sources 10–11pt.
- 2–5 recurring motifs only: compass icon, hairline separators, teal accent, the "accepted / not accepted" verdict color language (teal = accepted, amber = not accepted yet).
- Tables: thin horizontal rules only, no heavy frames, no zebra striping. Highlight only the Compass column.
- Diagrams: numbered loops for journeys, layered bands for architecture. Sources in `../diagrams/` (Mermaid).

## 5. Slide roster that worked (16 slides)

Cover → Problem → Gap → Current vs Future → Solution → Competitive → Journey loop → 3 Demos → Measured evidence → Architecture → Responsible AI → Rubric mapping → Business impact → NFRs → Roadmap → Closing/Ask.

## 6. Delivery checklist

- [ ] 10-minute version rehearsed; 5-minute cut identified (drop Demos + NFR slides)
- [ ] Every number on a slide has a source or an "assumption" label
- [ ] Demo path rehearsed twice from a clean clone; demo video ready as fallback (`../video/`)
- [ ] Rubric mapping slide included; judges can find each artifact from the repo link
- [ ] Q&A prep: token cost (0 at the core), privacy (k≥5, differencing), why deterministic not LLM, pilot measurement plan
- [ ] Export PPTX from the Kimi slides editor; commit source `.pptd` + `pages/` to the repo

## 7. Anti-patterns to avoid

- Walls of bullet points; reading slides verbatim; jargon without a number.
- "AI-powered" claims with no measured output quality.
- Vanity metrics (tokens used, prompts sent) presented as value.
- Individual-level people analytics — contradicts the product's core principle and the SPACE guidance cited in the deck.
