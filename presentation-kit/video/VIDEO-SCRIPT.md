# Demo Video Script — "Compass in 2 minutes"

Target: 110–120 seconds, 16:9, 1080p. Serves as the "Demo Video / Live Demo" evidence for rubric row 4 and as the live-demo fallback. Voiceover: calm, precise, one claim per sentence. Music: understated ambient, licensed or generated — no copyrighted tracks. All screen footage comes from `docs/screenshots/` — no staged or fake UI.

## Storyboard

| # | Time | Visual | Voiceover / caption |
|---|---|---|---|
| 1 | 0:00–0:08 | `media/compass-hero.mp4` — compass needle settles north | "Every engineer has AI tools. Almost none have guidance." Title card: **Compass** — private workflow coaching for GenAI adoption. |
| 2 | 0:08–0:22 | Fade to dark stat card: 90% adoption (DORA 2025) → −7.2% stability per +25% adoption (DORA 2024) → −19% speed for experienced devs (METR 2025) | "Adoption is near universal — and delivery stability fell as adoption rose. Usage dashboards show who clicked what. Nothing says what to do next." |
| 3 | 0:22–0:32 | `docs/screenshots/2-coach.png` with slow pan | "Compass is a coach that runs on your machine — no API keys, no cloud, no new licenses. It gives each engineer one evidence-backed next step, privately." |
| 4 | 0:32–0:50 | `docs/screenshots/workflow/api-2-facts.png` → `api-3-questions.png` → `api-5-package.png` (ken-burns pans, 6s each) | "The workflow coach guides the whole loop: project facts with file:line sources, the questions the story forgot to answer, the right tool — even when the answer is no AI — and a work package sized to your budget." |
| 5 | 0:50–1:10 | `docs/screenshots/workflow/api-6-evidence.png` → `api-7-result.png`; verdict colors emphasized | "Then it checks the work: local scans, tests on temporary copies, imported evidence. This fix is rejected — no reproduction. This one is accepted with evidence." |
| 6 | 1:10–1:30 | `docs/screenshots/6-suppressed.png` → `5-manager.png` | "Managers see only patterns shared by five or more engineers — differencing protection, no drill-down, no ranking. Enablement, not evaluation." |
| 7 | 1:30–1:45 | Stat card: 74/74 tests · 25/25 eval · 0 tokens at the core · 15k vs 454k context | "Measured, not promised: seventy-four passing tests, a deterministic core that uses zero tokens, and work packages ninety-seven percent smaller than pasting the repo." |
| 8 | 1:45–1:55 | `docs/screenshots/9-trust.png` | "Private by architecture. Guardrails by test. NIST AI RMF mapped." |
| 9 | 1:55–2:05 | Closing card: "Give every engineer a coach — not a scorecard." `Start-Coach.bat` / `python -m compass` + repo URL over compass-hero outro frame | "Double-click to run. MIT license. The compass is yours." |

## Production notes

- Captions: burned-in, bottom third, system sans, white on 60% dark scrim.
- Transitions: 300 ms cross-fades only; no spins or zoom-blasts.
- Verdict colors from the brand: teal `#2dd4bf` = accepted, amber `#fbbf24` = not accepted yet.
- Export: H.264, 1080p, ~8–12 Mbps, loudness −16 LUFS, under 50 MB for upload.
