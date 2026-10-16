# Seven design tools: what they are and how to use them safely

These are the seven tools from a short design-tools video. Most of them are websites or apps, not downloadable packs. This kit therefore gives you, for each one:
- what it is
- the official link
- the license or pricing found on 2026-10-16
- how it fits Compass
- how to use it without MCP servers or API keys

The **loaders** in `../loaders/` are original and bundled in full.

> Before using any online tool for work, check that it is approved for your organization. Only put synthetic or public content into it, never internal code or data. Compass itself must stay dependency-free and offline: no CDNs and no runtime packages in `web/`.

| # | Tool | What it is | Official link | License / price (checked 2026-10-16) | Bundled here? |
|---|---|---|---|---|---|
| 1 | **Scrolltide** | Paid library of "cinematic" website templates and copy-paste AI build prompts (scroll animation, 3D, shaders) aimed at Claude, Cursor and v0, with Next.js output | https://www.scrolltide.co/ | Paid: $39/month, $144/year or $299 lifetime; covers "personal & client use"; some free templates | **No.** Their prompts are paid content. `../prompts/PROMPTS.md` has our own scroll-storytelling prompt instead |
| 2 | **Navbar Gallery** | Curated collection of navigation bar designs from real websites, for inspiration | https://www.navbar.gallery/ | Listed as free on a showcase site; the designs belong to the sites they come from | **No.** Use it for ideas only. `../prompts/PROMPTS.md` has a navbar prompt |
| 3 | **3D Icons (3dicons)** | Open-source set of 3D icons made in Blender, by Vijay Verma | https://3dicons.co/ | **CC0** (public domain): commercial use, editing and redistribution allowed | Not included (large PNG/Blender files). Download only the icons you need from the site |
| 4 | **Framer** | No-code website builder for responsive, animated sites, with hosting | https://www.framer.com/ | Free and paid plans (pricing not re-checked) | No (hosted app). Good for a public landing page for Compass, not for the app itself |
| 5 | **Rive** | Editor and runtime for interactive vector animations with state machines (hover, click, loading states) | https://rive.app/ | Editor: free and paid plans. Web runtime (`rive-app/rive-wasm`): **MIT** | No. If approved, export a `.riv` file and load it with the runtime: see the prompt |
| 6 | **Spline** | 3D design tool for web scenes and objects, exported as embed, code or self-hosted | https://spline.design/ | Free and paid plans. The `@splinetool/runtime` npm package shows no open-source license, so Spline's terms apply | No. Use for a hero visual or the deck only. Too heavy for Compass's offline app |
| 7 | **Untitled UI** | UI kit and design system. The free React version is built on Tailwind CSS and React Aria | https://www.untitledui.com/ (React: https://github.com/untitleduico/react) | Open-source React components: **MIT**. PRO components and Figma PRO are licensed separately | No. Compass uses vanilla JS. Use it for spacing, type and color ideas, or in a React project |

## How each one fits Compass

- **Loading and "thinking" states:** use `../loaders/`. They match Compass's colors, work offline and respect reduced motion. This is the part you can ship today.
- **Brand visuals (deck, landing page, demo video):** Spline (3D compass scene), 3dicons (CC0 icons), Framer (one-page site).
- **Micro-interactions:** Rive, only if approved and if the runtime file can be vendored locally.
- **UI polish ideas:** Untitled UI (component patterns) and Navbar Gallery (top navigation ideas).
- **Scroll storytelling for a marketing page:** a Scrolltide-style effect, built from our own prompt.

## Sources
- Scrolltide home and pricing: https://www.scrolltide.co/ , https://www.scrolltide.co/why-scrolltide
- Navbar Gallery listing: https://uiuxshowcase.com/resources/navbar-gallery-find-the-best-navigation-bar-examples/
- 3dicons license (CC0): https://old.3dicons.co/about , https://smashingmagazine.com/2022/05/3dicons-open-source-library-case-study-download/
- Untitled UI React (MIT): https://github.com/untitleduico/react
- Rive web runtime (MIT): https://github.com/rive-app/rive-wasm , docs https://rive.app/docs/runtimes/web/
- Spline runtime: https://npmjs.com/package/@splinetool/runtime , export docs https://docs.spline.design/exporting-your-scene/web/exporting-as-code.md
