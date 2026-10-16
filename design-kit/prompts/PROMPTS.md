# Prompts

Copy-paste prompts for GitHub Copilot Chat (agent mode), Claude Code or Devin. None of them needs MCP servers or API keys. Each one asks for a plan first and keeps the Compass rules: no new runtime dependencies in `web/`, no CDNs, tests must pass.

---

## 1. Add the loaders to the Compass app (start here)

```text
You are working in the Compass repository. Read AGENTS.md first and follow it.

Goal: give every wait in the web UI a simple, honest loading state using the loader kit in design-kit/loaders/.

Steps:
1. Copy design-kit/loaders/loaders.css to web/loaders.css and design-kit/loaders/loaders.js to web/loaders.js. Link them from web/index.html (local files only, no CDN).
2. Use them in web/app.js and web/workflow.js:
   - Any fetch that can take longer than 300 ms: wrap with Loaders.delayed so fast calls show nothing.
   - Buttons that start work ("Check my task", "Write my prompt", "Build work package", "Run local checks", "Verify fix", "Fetch from Jira"): Loaders.busy(button, "<verb>ing...") and stop it in finally.
   - "Run local checks": show a .cl-steps list with one item per check that will actually run. Advance it only when the server says that check finished. If the API returns all results at once, show the spinner plus a rotating status instead and do NOT fake per-step progress.
   - Jira fetch: .cl-rotate with "Contacting Jira...", "Reading the issue...".
   - Result panels and coaching cards while loading: .cl-skel placeholders that match the final layout.
   - First load of the app: .cl-compass for at most one second, then content.
3. Every loader keeps role="status" or aria-busy and screen-reader text. Reduced motion must stop the animation and keep the text.
4. On error, replace the loader with a clear message and a retry button. Never leave a spinner running.

Constraints: vanilla JS, no new packages, no layout shift bigger than the skeleton, keep all strings in plain language.
Show me a plan first and wait for my OK. After the change, run:
python -m unittest discover -s tests -t . -v
python -m compass eval
and paste the output. Add a short note to docs/user-guide.md only if user-visible behavior changed.
```

## 2. "Thinking" UX review

```text
Review every place in web/ where the user waits for something (network calls, scans, test runs, Jira).
For each one, give: the trigger, the typical duration (estimate from the code and label it an estimate), the current feedback, and the loader from design-kit/loaders/README.md that fits best.
Flag any fake progress, any spinner without a timeout or error state, and any wait over 2 s that does not say what is happening.
Output a table, then the three most valuable fixes. Do not change code yet.
```

---

## 3. Scroll storytelling (our own take on the Scrolltide style)

```text
Build a single-page marketing site for "Compass: Right tool. Sharp prompt. Proven result." as one self-contained HTML file (no frameworks, no CDN).
Sections, revealed as the user scrolls:
1. Hero: big title and tagline, with a compass needle that swings to north-east as you scroll.
2. "Right tool": three tool cards slide in.
3. "Sharp prompt": a work package builds up line by line.
4. "Proven result": a checklist ticks green.
5. Privacy promise: "Points the way. Never points fingers."
Use CSS scroll-driven animations (animation-timeline: view()) with an IntersectionObserver fallback for browsers that lack them. Respect prefers-reduced-motion: show the final state with no motion.
Colors: navy #0B1B2B, gold #F2B544, teal #2EC4B6, text #F2F5F8. Make it work at 375 px wide with no horizontal scroll.
Plan first, then build.
```

## 4. Navbar (inspired by Navbar Gallery, not copied)

```text
I looked at navbar patterns on Navbar Gallery for ideas. Do not copy any specific site.
Redesign the top navigation in web/index.html and web/styles.css:
- sticky; condenses on scroll
- clear active-page indicator
- keyboard focus styles
- works at 375 px with a menu button
- keeps the privacy marker and "Signed in as" area
Vanilla CSS and JS only. Keep the existing routes. Show before and after screenshots from Playwright if available, and run the tests.
```

## 5. 3D icons (3dicons, CC0)

```text
I will download a few CC0 icons from 3dicons.co (for example: compass, shield, check, chat, tools, lock) as PNG.
Write a small Python script, scripts/optimize_icons.py, that:
- resizes each PNG to 256 px
- converts it to WebP
- writes it to docs/assets/icons/
- prints the byte savings
Use only the standard library plus Pillow, and run it as a separate dev step, not inside the app.
Then use the icons in docs/presentation and README.md only, not in the offline app. Add a line to NOTICE crediting "3dicons by Vijay Verma (CC0)" even though attribution is optional.
```

## 6. Framer landing page

```text
Write the content for a one-page Framer site about Compass, ready to paste section by section:
hero (title, tagline, one sentence, primary button "See the 5-minute demo"), a problem section with the three sourced stats from docs/research/evidence.md (keep their sources), how-it-works in 3 steps, the three demos, privacy and security, an FAQ with 5 questions, and a footer.
Give each section a suggested Framer layout (stack direction, gap, breakpoints) and one subtle animation (appear, scroll transform or hover).
Synthetic data and generic wording only: no company names.
```

## 7. Rive interactive loader

```text
Design a Rive state machine for a Compass loader, to be built in the Rive editor:
States: idle, thinking (needle searches), found (needle locks to north-east with a gold pulse), error (needle shakes, turns coral).
Inputs: boolean isThinking, trigger found, trigger error.
Give me the artboard size, the layers and the timeline for each animation.
Then write web/rive-loader.js that loads compass.riv with the Rive web runtime, ONLY if the runtime file is vendored locally (no CDN) and pinned by SHA-256 in a comment. Fall back to the CSS .cl-compass loader if the file or runtime is missing.
Do not add it to the app until I confirm the runtime is approved.
```

## 8. Spline 3D compass scene

```text
Describe a Spline scene for the Compass landing page and deck:
- a 3D brass compass on a navy background
- a 16-point rose
- a needle that rotates toward the cursor (mouse follow, limited to 40 degrees)
- a soft teal glow from a small neural-network core in the center
List objects, materials, lights, camera, and the "Mouse Hover / Look At" events to add.
Export plan: use a poster image fallback, lazy-load the scene only on the landing page, and never inside the offline Compass app. Show the embed code with @splinetool/runtime and a static PNG fallback for reduced motion.
```

## 9. Untitled UI patterns for Compass

```text
Using Untitled UI's public docs and open-source React components (MIT) as a reference, without copying their code into this vanilla-JS repo:
1. Propose a spacing scale, a type scale and radius tokens for web/styles.css that match Untitled UI's level of polish while keeping Compass's colors.
2. Restyle buttons (primary, secondary, tertiary, destructive), inputs, badges and cards with these tokens.
3. Keep focus rings accessible (3:1 contrast) and dark mode working.
Show a token table first, then the CSS diff. Run the tests and attach Playwright screenshots of the Workflow coach page in light and dark mode.
```
