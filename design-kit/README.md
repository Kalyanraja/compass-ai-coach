# Compass design kit

Everything for the "look and feel" work in one place, and as one zip: [`downloads/compass-design-kit.zip`](../downloads/compass-design-kit.zip).

| Folder | What is inside |
|---|---|
| `loaders/` | **14 original loading and "thinking" animations.** Plain CSS and JS, offline, light and dark, reduced-motion safe. Open `loaders/index.html` to try them. |
| `tools/` | The seven design tools (Scrolltide, Navbar Gallery, 3D Icons, Framer, Rive, Spline, Untitled UI): what each one is, official links, licenses checked on 2026-10-16, and where each fits. `tools.json` has the same data for scripts. |
| `screenshots/` | The loader gallery in light and dark mode, and the compass loader inside the app. |
| `prompts/` | Copy-paste prompts for Copilot, Claude Code or Devin: add the loaders to Compass, review the "thinking" UX, and one prompt per tool. |

## Quick start
1. Open `loaders/index.html` in a browser. Click **Code** on any loader to copy it.
2. The Compass app already uses them: a top loading bar, a spinning compass on busy buttons, and compass loaders for pages, local checks, fix verification and Jira. To use them in more places, paste prompt 1 from `prompts/PROMPTS.md` into Copilot Chat (agent mode) or Claude Code.
3. Read `tools/TOOLS.md` before using any of the online tools at work.

## Why the third-party tools are links, not files
- Scrolltide is a paid library, and Navbar Gallery shows other companies' designs. Copying either into a public repository would break their terms.
- Framer, Rive and Spline are hosted apps. There is nothing to download until you build something in them.
- 3dicons (CC0) and the Untitled UI React components (MIT) are free to reuse. They are large, so download only what you need from the official links.
- The Compass app must stay offline with no runtime dependencies, so anything added to `web/` must be vendored and reviewed.

## Rebuild the zip
```bash
python scripts/build_design_kit.py
```

License for the files in this folder: MIT, same as the repository.
