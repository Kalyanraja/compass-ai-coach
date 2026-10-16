# Compass loaders

Fourteen loading and "thinking" states. They are plain CSS plus a 2 KB helper, with no dependencies and no CDN. Open `index.html` in any browser to see them all, toggle dark mode, slow them down and copy the markup.

| Loader | Class | Use it for |
|---|---|---|
| Thinking dots | `.cl-dots` | Short AI waits next to a message or button |
| Shimmer label | `.cl-shimmer` | A quiet "Thinking..." line where the answer will appear |
| Rotating status | `.cl-rotate` + `Loaders.rotate()` | 3 to 15 s waits, with messages that stay true the whole time |
| Compass needle | `.cl-compass` | Brand moment: first load, "finding the right tool" |
| Step checklist | `.cl-steps` + `Loaders.steps()` | Multi-step jobs with **real** progress (local checks, test runs) |
| Skeleton | `.cl-skel` | Results whose layout you already know |
| Progress bar | `.cl-bar`, `.cl-bar.is-determinate` | Panel activity; switch to determinate when you know the % |
| Spinner | `.cl-spinner`, `.cl-spinner.sm` | Buttons and anything under 2 s |
| Breathing orb | `.cl-orb` | An assistant working in the background |
| Typing bubble | `.cl-typing` | Chat replies before the first word |
| Streaming text | `.cl-stream` + `Loaders.stream()` | Revealing an answer with a caret |
| Orbit | `.cl-orbit` | Compact indicator for empty states |
| Working card | `.cl-working` | The one card whose task is running |
| Bars | `.cl-bars` | Listening or streaming activity |
| Busy button | `Loaders.busy(button, label)` | Disable and label the button the user pressed |

## Use

```html
<link rel="stylesheet" href="loaders.css">
<script src="loaders.js"></script>

<div class="cl-dots" role="status"><span></span><span></span><span></span><span class="cl-sr">Thinking</span></div>
```

```js
const hide = Loaders.delayed(() => panel.classList.add("loading"), () => panel.classList.remove("loading"), 300);
const steps = Loaders.steps(document.querySelector(".cl-steps"));
await runSecretScan();  steps.next();
await runPatterns();    steps.next();
hide();
```

## Rules we follow
- **Timing:** under 300 ms show nothing (`Loaders.delayed`). Under 2 s use a spinner or dots. Longer waits say what is happening.
- **Never fake progress:** steps advance only when the work really finishes. Rotating messages must be true for the whole wait.
- **Accessible:** every loader carries `role="status"`, `aria-live` or `aria-busy`, with screen-reader text in `.cl-sr`.
- **Reduced motion:** movement stops and the state text stays visible.
- **Theming:** colors come from Compass variables (`--sea`, `--amber`, `--ink`...), so the loaders match light and dark mode. Override `--cl-accent`, `--cl-accent-2` or `--cl-speed` if you need to.

License: MIT, same as this repository.
