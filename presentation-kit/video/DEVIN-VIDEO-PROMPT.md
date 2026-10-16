# Devin Prompt — Generate the Compass Demo Video

Copy everything in the fenced block below into a Devin session that has the `compass-ai-coach` repository. It produces `presentation-kit/media/compass-demo.mp4` per `presentation-kit/video/VIDEO-SCRIPT.md`.

```text
You are generating the official 2-minute demo video for the Compass hackathon
project. Work only inside this repository. Read AGENTS.md first and follow it.

GOAL
Produce presentation-kit/media/compass-demo.mp4 (1080p, H.264, ≤ 50 MB, ~115 s)
that follows presentation-kit/video/VIDEO-SCRIPT.md scene by scene. This video
is judging evidence (rubric row "Demo and Delivery Readiness"), so accuracy of
every number and label matters more than flashy effects.

ASSETS (all local, no external fetches)
- Intro/outro clip: presentation-kit/media/compass-hero.mp4 (8 s, AI-generated)
- UI screenshots: docs/screenshots/*.png and docs/screenshots/workflow/*.png
- Brand tokens: presentation-kit/README.md (colors, fonts, verdict colors)
- Script, timings, captions: presentation-kit/video/VIDEO-SCRIPT.md

APPROACH
1. Build a static HTML/CSS slide renderer (one file per storyboard scene) that
   renders each scene at 1920×1080 using ONLY local assets and the brand
   tokens. Reuse docs/screenshots directly; do not modify them. Dark
   background #0b1220, text #e6edf7, accent #2dd4bf, warn #fbbf24.
2. Render each scene with headless Chromium to PNG frames (or use Playwright
   if already available in the environment). No npm installs beyond what the
   sandbox already has; plain ffmpeg is enough.
3. Assemble with ffmpeg: cross-fade (xfade, 0.3 s) between scenes, compass-hero
   as scene 1 and as the outro background, burned-in captions as text overlays
   or prerendered into the HTML scenes (preferred), 30 fps, H.264 CRF 20,
   audio track: silent or a generated ambient loop if a tool is available —
   never a copyrighted track.
4. Pan/zoom on screenshots via ffmpeg zoompan (slow, ≤ 10% scale change over
   the clip) or CSS transform animations captured frame-by-frame.

RULES (hard constraints)
- Every statistic on screen must come from VIDEO-SCRIPT.md / repo docs
  (DORA 2025 90%, DORA 2024 −7.2%, METR −19%, 74/74, 25/25, 0 tokens,
  15k vs 454k). Do not invent or round differently.
- Label the capacity-value figures as scenarios with assumptions if shown;
  when in doubt, omit rather than approximate.
- Do not edit source screenshots; scale only.
- No fake UI, no placeholder text left in the final video.
- If headless rendering is unavailable, fall back to pure ffmpeg
  (zoompan + drawtext) and report the fallback.

ACCEPTANCE CHECKLIST (verify before finishing)
- [ ] Duration 105–125 s, 1920×1080, plays in a browser, ≤ 50 MB
- [ ] Scene order matches VIDEO-SCRIPT.md 1–9
- [ ] Captions legible (≥ 28 px equivalent, contrast ≥ 4.5:1)
- [ ] compass-hero.mp4 appears as intro and outro
- [ ] No copyrighted material; no unlabeled claims
- [ ] Output path exactly presentation-kit/media/compass-demo.mp4
- [ ] Run python -m unittest discover -s tests -t . -q to confirm the repo
      still passes (you should not have touched app code)

DELIVERABLES
- presentation-kit/media/compass-demo.mp4
- presentation-kit/video/build/ containing the scene renderer + the exact
  ffmpeg command used (for reproducibility)
- A short summary: what was built, any fallback used, and the checklist above
  with actual results.
```

## Tips for the hand-off

- Give Devin the repo with `develop` checked out — the kit and screenshots are all there.
- If Devin's sandbox lacks ffmpeg or Chromium, it will report the fallback; the pure-ffmpeg path in the prompt still yields a solid video.
- Review the video against the acceptance checklist before submitting; re-run Devin with the specific failed item if anything is off.
