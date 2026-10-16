/* Compass loaders helpers. Vanilla JS, no dependencies.
   Usage:
     const stop = Loaders.rotate(el, ["Reading files...", "Checking facts..."]);
     const s = Loaders.steps(listEl); s.next(); s.done(); s.fail("Scanner missing");
     Loaders.stream(el, "Text to reveal"); // returns a Promise
     const busy = Loaders.busy(button, "Building..."); busy.stop();
   Every helper sets role="status" + aria-live so screen readers hear changes. */
(function (root) {
  "use strict";
  const reduced = () => root.matchMedia && root.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const live = (el) => { el.setAttribute("role", "status"); el.setAttribute("aria-live", "polite"); };

  // Rotating status messages. Use only for messages that are true for the whole wait.
  function rotate(el, messages, every) {
    live(el);
    const msg = el.querySelector(".cl-msg") || el;
    let i = 0;
    msg.textContent = messages[0];
    const t = setInterval(() => {
      if (reduced()) { i = (i + 1) % messages.length; msg.textContent = messages[i]; return; }
      msg.classList.add("is-out");
      setTimeout(() => { i = (i + 1) % messages.length; msg.textContent = messages[i]; msg.classList.remove("is-out"); }, 250);
    }, every || 2200);
    return () => clearInterval(t);
  }

  // Step checklist that reflects real progress. Call next() when a step really finishes.
  function steps(list) {
    live(list);
    const items = Array.from(list.querySelectorAll("li"));
    let i = 0;
    const paint = () => items.forEach((li, k) => {
      li.classList.toggle("is-done", k < i);
      li.classList.toggle("is-active", k === i);
    });
    paint();
    return {
      next() { if (i < items.length) { i++; paint(); } },
      done() { i = items.length; paint(); },
      fail(reason) {
        const li = items[i]; if (!li) return;
        li.classList.remove("is-active"); li.dataset.failed = "true";
        li.textContent = li.textContent + (reason ? " (" + reason + ")" : " (failed)");
      },
      get index() { return i; },
    };
  }

  // Reveal text like a streamed answer. Resolves when finished.
  function stream(el, text, cps) {
    live(el);
    el.classList.add("cl-stream"); el.classList.remove("is-done");
    if (reduced()) { el.textContent = text; el.classList.add("is-done"); return Promise.resolve(); }
    const words = text.split(/(\s+)/);
    let n = 0; el.textContent = "";
    const delay = 1000 / (cps || 40);
    return new Promise((resolve) => {
      (function tick() {
        if (n >= words.length) { el.classList.add("is-done"); resolve(); return; }
        el.textContent += words[n++];
        setTimeout(tick, delay * Math.max(1, words[n - 1].length / 2));
      })();
    });
  }

  // Put a button into a busy state with a small spinner, and restore it later.
  function busy(btn, label) {
    const html = btn.innerHTML, disabled = btn.disabled;
    btn.disabled = true; btn.classList.add("cl-btn", "is-busy"); btn.setAttribute("aria-busy", "true");
    btn.innerHTML = '<span class="cl-spinner sm" aria-hidden="true"></span> ' + (label || "Working...");
    return { stop() { btn.innerHTML = html; btn.disabled = disabled; btn.classList.remove("is-busy"); btn.removeAttribute("aria-busy"); } };
  }

  // Only show a loader if the wait is longer than `after` ms, to avoid flicker on fast calls.
  function delayed(show, hide, after) {
    let shown = false;
    const t = setTimeout(() => { shown = true; show(); }, after == null ? 300 : after);
    return () => { clearTimeout(t); if (shown) hide(); };
  }

  root.Loaders = { rotate, steps, stream, busy, delayed };
})(window);
