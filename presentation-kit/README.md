# Compass Presentation Kit

Everything needed to pitch Compass: the scoring rubric, the pitch deck source, PPT generation guidelines, reusable diagrams, a demo-video script, and a ready-to-paste prompt for Devin to produce the demo video.

## Contents

| Path | What it is |
|---|---|
| `rubric/scoring-rubric.jpg` | The official hackathon scoring rubric (reference photo) |
| `PPT-GUIDELINES.md` | How to generate the best possible PPT for this project (structure, design rules, rubric mapping, delivery checklist) |
| `diagrams/` | Mermaid sources for the four key diagrams (GitHub renders these natively) |
| `video/VIDEO-SCRIPT.md` | Shot-by-shot script and storyboard for the 2-minute demo video |
| `video/DEVIN-VIDEO-PROMPT.md` | Copy-paste prompt to hand Devin so it generates the video end-to-end |
| `media/compass-hero.mp4` | 8-second AI-generated compass intro clip (dark navigator theme) |

## The deck

The 16-slide pitch deck lives in `docs/presentation/compass-pitch/` (kimi-slides `.pptd` source + rendered pages). Export to PPTX from the Kimi slides editor. Slide 12 maps every deck page to the rubric row it satisfies.

## Brand tokens (use everywhere)

```
--ink-950:#070b14  --ink-900:#0b1220  --ink-800:#101a2e  --ink-700:#16233c
--line:rgba(148,184,255,.14)
--brand:#2dd4bf  --brand-2:#22d3ee  --accent:#8b5cf6
--text:#e6edf7  --dim:#93a4c3
--ok:#34d399  --warn:#fbbf24  --err:#f87171
font: system sans-serif stack
mood: dark "navigator", hairline separators, no card walls, big honest numbers
```
