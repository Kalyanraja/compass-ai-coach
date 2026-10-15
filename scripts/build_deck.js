// Builds docs/presentation/Compass-Hackathon.pptx
// Usage: node scripts/build_deck.js <image dir> <output.pptx> [apply_theme.js path]
// Image dir holds cropped screenshots (from docs/screenshots) and icon PNGs.
const pptxgen = require("pptxgenjs");
const path = require("path");

const IMG = process.argv[2];
const OUT = process.argv[3] || "Compass-Hackathon.pptx";
const THEME_JS = process.argv[4];
const img = (n) => path.join(IMG, n);

const THEME = {
  name: "Compass",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "102A35", lt1: "FFFFFF", dk2: "1D5C63", lt2: "EEF4F3",
    accent1: "1D6E6B", accent2: "C77D1E", accent3: "B8432F", accent4: "2E7D4F",
    accent5: "5E7279", accent6: "A9CFC9", hlink: "1D6E6B", folHlink: "5E7279",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.title = "Compass: Right tool. Sharp prompt. Proven result.";
pres.author = "Compass team";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "DARK_TITLE",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.3, w: 5.2, h: 1.2, fontSize: 48, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 2.65, w: 5.2, h: 1.9, fontSize: 16, color: C.accent6, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "DARK_CLOSE",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.7, w: 5.2, h: 1.5, fontSize: 36, bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 2.4, w: 5.2, h: 1.3, fontSize: 15, color: C.accent6, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.lt1 },
  margin: [0.3, 0.5, 0.45, 0.5],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.28, w: 9.0, h: 0.7, fontSize: 28, bold: true, color: C.text1, fontFace: THEME.headFontFace, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "Compass  |  Right tool. Sharp prompt. Proven result.  |  synthetic data only", options: { x: 0.5, y: 5.22, w: 7, h: 0.25, fontSize: 9, color: C.accent5, margin: 0 } } },
  ],
  slideNumber: { x: 9.0, y: 5.22, w: 0.5, h: 0.25, fontSize: 9, color: C.accent5, align: "right" },
});

// ---------- helpers ----------
const shadow = () => ({ type: "outer", color: "1A3640", opacity: 0.14, blur: 6, offset: 2, angle: 90 });
function card(s, x, y, w, h, opts = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: opts.fill || C.background2 },
    line: opts.line ? { color: opts.line, width: 1 } : { type: "none" },
    shadow: opts.noShadow ? undefined : shadow(), objectName: opts.name,
  });
}
function iconCircle(s, x, y, d, icon, fill) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill || C.accent1 }, line: { type: "none" } });
  const p = d * 0.26;
  s.addImage({ path: img(icon + "-w.png"), x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p });
}
function text(s, t, o) { s.addText(t, Object.assign({ isTextBox: true, margin: 0, valign: "top" }, o)); }
function bullets(s, items, o) {
  const runs = items.map((it, i) => {
    const r = typeof it === "string" ? { text: it, options: {} } : it;
    r.options = Object.assign({ bullet: { indent: 14 }, paraSpaceAfter: 6, breakLine: i < items.length - 1 }, r.options);
    return r;
  });
  s.addText(runs, Object.assign({ isTextBox: true, margin: 0, valign: "top", fontSize: 14, color: C.text1 }, o));
}
function shot(s, file, x, y, w, pxW, pxH) {
  const h = w * pxH / pxW;
  s.addShape(pres.shapes.RECTANGLE, { x: x - 0.03, y: y - 0.03, w: w + 0.06, h: h + 0.06, fill: { color: C.background1 }, line: { color: HEX.accent6, width: 1 }, shadow: shadow() });
  s.addImage({ path: img(file), x, y, w, h });
  return h;
}
function chip(s, label, x, y, w, color) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.3, rectRadius: 0.15, fill: { color }, line: { type: "none" } });
  text(s, label, { x, y, w, h: 0.3, fontSize: 11, bold: true, color: C.background1, align: "center", valign: "middle" });
}
function content(section, title) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  return s;
}

// ================= 1. Title =================
pres.addSection({ title: "Opening" });
let s = pres.addSlide({ masterName: "DARK_TITLE", sectionTitle: "Opening" });
s.addText("Compass", { placeholder: "title" });
s.addText([
  { text: "Right tool. Sharp prompt. Proven result.", options: { fontSize: 22, bold: true, color: C.background1, breakLine: true } },
  { text: " ", options: { fontSize: 8, breakLine: true } },
  { text: "Private GenAI coaching that guides every engineer the right way", options: { breakLine: true } },
  { text: "AI Engineering Enablement Coach  |  Hackathon submission", options: { fontSize: 12, breakLine: true } },
  { text: "Synthetic data only. Runs on a laptop. No API keys.", options: { fontSize: 12 } },
], { placeholder: "body" });
s.addImage({ path: img("ai-compass.png"), x: 5.95, y: 0.95, w: 3.7, h: 3.7 });
s.addNotes("Compass coaches how engineers use AI, privately, and gives managers only aggregated, suppressed insights. Everything in this deck runs on synthetic data.");

// ================= 2. Problem =================
pres.addSection({ title: "Problem and solution" });
s = content("Problem and solution", "AI adoption is up; delivery outcomes are not");
const stats = [
  ["-7.2%", "estimated change in delivery stability for each 25% increase in AI adoption", "DORA 2024", C.accent3],
  ["19%", "longer task time for experienced open-source developers using AI tools", "METR, July 2025 (16 developers, 246 tasks)", C.accent3],
  ["39%", "of developers report little or no trust in AI-generated code", "DORA 2024", C.accent2],
];
stats.forEach(([n, l, src, col], i) => {
  const x = 0.5 + i * 3.1;
  card(s, x, 1.2, 2.8, 2.35, { name: "stat-" + i });
  text(s, n, { x: x + 0.25, y: 1.35, w: 2.3, h: 0.85, fontSize: 48, bold: true, color: col, fontFace: THEME.headFontFace, valign: "middle" });
  text(s, l, { x: x + 0.25, y: 2.25, w: 2.3, h: 0.85, fontSize: 13, color: C.text1 });
  text(s, src, { x: x + 0.25, y: 3.12, w: 2.3, h: 0.3, fontSize: 10, italic: true, color: C.accent5 });
});
card(s, 0.5, 3.85, 9.0, 1.05, { fill: C.text1, noShadow: true });
iconCircle(s, 0.75, 4.1, 0.55, "chart", C.accent1);
text(s, [
  { text: "Usage dashboards count seats and prompts. ", options: { bold: true } },
  { text: "They can't tell an engineer what to change next, and they tempt managers to rank people." },
], { x: 1.5, y: 3.95, w: 7.8, h: 0.85, fontSize: 15, color: C.background1, valign: "middle" });
s.addNotes("Sources: dora.dev and cloud.google.com DORA 2024 announcement; metr.org July 2025 study. Full list in docs/research/evidence.md.");

// ================= 2b. Tagline explained =================
s = content("Problem and solution", "How Compass guides every engineer the right way");
s.addImage({ path: img("journey.png"), x: 1.6, y: 0.98, w: 6.8, h: 6.8 * 680 / 1800 });
const beats = [
  ["Right tool", C.accent1, "Approval and data rules first, then fit: Copilot, Claude Code, Devin, or no AI at all."],
  ["Sharp prompt", C.accent2, "A reviewed work package: confirmed facts, up to 3 answers, decisive files in full."],
  ["Proven result", C.accent4, "Tests, scans and reproduction evidence. A missing check is never a pass."],
];
beats.forEach(([h, col, d], i) => {
  const x = 0.5 + i * 3.1;
  card(s, x, 3.68, 2.8, 1.38, { name: "beat-" + i });
  text(s, h, { x: x + 0.2, y: 3.8, w: 2.4, h: 0.35, fontSize: 16, bold: true, color: col, fontFace: THEME.headFontFace });
  text(s, d, { x: x + 0.2, y: 4.17, w: 2.4, h: 0.82, fontSize: 12, color: C.text1 });
});
s.addNotes("The whole product in one line. Every engineer is pointed to the approved tool, gets a complete prompt package, and only gets a pass when there is evidence.");

// ================= 3. What Compass is =================
s = content("Problem and solution", "Compass coaches how AI is used, not how much");
const pillars = [
  ["user", "Engineer (private)", ["Next best actions: observation, action, why, outcome to watch", "Tailored to role, stack and project complexity", "Dismiss and feedback stay private"]],
  ["users", "Manager and leader", ["Gaps shared by at least 5 engineers, with an enablement action", "Suppression plus differencing protection", "No path to any individual"]],
  ["route", "Workflow coach", ["Goal, facts, questions, tool, package, evidence, lesson", "Feature or API, UAT defect, meaningful tests", "Works with Copilot, Claude Code and Devin as they are"]],
];
pillars.forEach(([ic, h, b], i) => {
  const x = 0.5 + i * 3.1;
  card(s, x, 1.2, 2.8, 3.35, { name: "pillar-" + i });
  iconCircle(s, x + 0.25, 1.4, 0.6, ic);
  text(s, h, { x: x + 0.25, y: 2.1, w: 2.35, h: 0.4, fontSize: 15, bold: true, color: C.text1, fontFace: THEME.headFontFace });
  bullets(s, b, { x: x + 0.25, y: 2.55, w: 2.35, h: 1.9, fontSize: 12 });
});
text(s, "No scoring, ranking or labeling of people. Python standard library only. Works offline.", { x: 0.5, y: 4.7, w: 9.0, h: 0.35, fontSize: 14, italic: true, color: C.text2 });

// ================= 4. Architecture map =================
pres.addSection({ title: "How it works" });
s = content("How it works", "Architecture map");
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.45, y: 1.08, w: 7.25, h: 4.02, rectRadius: 0.06, fill: { color: C.background2 }, line: { color: HEX.accent6, width: 1, dashType: "dash" } });
text(s, "Engineer laptop, bound to 127.0.0.1", { x: 0.6, y: 1.13, w: 4, h: 0.25, fontSize: 10, bold: true, color: C.text2 });
const box = (t, x, y, w, h, fill, color) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.05, fill: { color: fill }, line: { type: "none" } });
  text(s, t, { x: x + 0.06, y, w: w - 0.12, h, fontSize: 10, color: color || C.text1, align: "center", valign: "middle" });
};
const colHead = (t, x, w) => text(s, t, { x, y: 1.4, w, h: 0.25, fontSize: 10, bold: true, color: C.accent5, align: "center" });
// inputs
colHead("INPUTS", 0.6, 1.7);
box("Synthetic signals\n(usage + PR/CI metadata)", 0.6, 1.7, 1.7, 0.6, C.background1);
box("Project folder\n(read-only)", 0.6, 2.42, 1.7, 0.6, C.background1);
box("Story, defect\nor Jira key", 0.6, 3.14, 1.7, 0.6, C.background1);
s.addShape(pres.shapes.CAN, { x: 0.6, y: 3.95, w: 0.8, h: 0.95, fill: { color: C.accent5 }, line: { type: "none" } });
text(s, "signals.db\nread-only", { x: 0.6, y: 4.15, w: 0.8, h: 0.7, fontSize: 9, color: C.background1, align: "center", valign: "middle" });
s.addShape(pres.shapes.CAN, { x: 1.5, y: 3.95, w: 0.8, h: 0.95, fill: { color: C.accent2 }, line: { type: "none" } });
text(s, "private.db\nengineer only", { x: 1.5, y: 4.15, w: 0.8, h: 0.7, fontSize: 9, color: C.background1, align: "center", valign: "middle" });
// services
colHead("SERVICES (compass/)", 2.65, 2.55);
const svc = ["Recommendation engine: rules + persona", "Aggregator: k = 5, no ids", "Workflow coach: facts, 3 questions, tool policy", "Context budgeter + package: redaction, fencing", "Evidence + safe runner: no shell, approvals"];
svc.forEach((t, i) => box(t, 2.65, 1.7 + i * 0.66, 2.55, 0.56, C.accent1, C.background1));
// UI
colHead("VIEWS (web/)", 5.55, 1.95);
["Engineer view\n(private)", "Manager and leader\n(aggregated)", "Enablement\n(eval, audit)", "Workflow coach\n(7 steps)"].forEach((t, i) => box(t, 5.55, 1.7 + i * 0.83, 1.95, 0.7, C.background1));
// arrows between columns
const arrow = (x1, y1, x2, y2, o = {}) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001, flipH: x2 < x1, flipV: y2 < y1, line: { color: o.color || HEX.dk2, width: 1.5, endArrowType: "triangle", dashType: o.dash } });
[2.0, 2.72, 3.44].forEach((y) => arrow(2.3, y, 2.65, y));
[2.0, 2.66, 3.32, 3.98, 4.64].forEach((y) => arrow(5.2, y, 5.55, y));
// external
text(s, "OUTSIDE THE LAPTOP", { x: 7.9, y: 1.4, w: 1.7, h: 0.25, fontSize: 10, bold: true, color: C.accent5, align: "center" });
box("Jira (optional)\nread-only GET,\ntoken never stored", 7.9, 1.7, 1.7, 0.95, C.text1, C.background1);
arrow(7.9, 2.17, 7.7, 2.17, {});
text(s, "\u2192 user copies the reviewed package", { x: 7.9, y: 2.95, w: 1.7, h: 0.4, fontSize: 9, italic: true, color: C.text2 });
text(s, "\u2190 diffs and reports imported as evidence", { x: 7.9, y: 3.35, w: 1.7, h: 0.4, fontSize: 9, italic: true, color: C.accent2 });
box("Copilot\nClaude Code\nDevin", 7.9, 3.85, 1.7, 1.05, C.text1, C.background1);
arrow(7.5, 4.3, 7.9, 4.3, {});
arrow(7.9, 4.6, 7.5, 4.6, { dash: "dash", color: HEX.accent2 });
s.addNotes("Two physically separate stores. The aggregator opens signals.db read-only and never touches private.db. The project folder is read-only; fixes are verified on temporary copies. Nothing leaves the laptop unless the user copies it, or enables Jira.");

// ================= 5. Journey =================
s = content("How it works", "One journey: seven steps, at most three questions");
const steps = [
  ["Goal", "Story, defect or Jira key"], ["Facts", "Detected, inferred, confirmed or unknown, with file:line"],
  ["Questions", "Up to 3, each says why"], ["Tool", "Policy first, then fit; \"no AI\" allowed"],
  ["Package", "Lean 4k, Balanced 8k, Deep 16k"], ["Evidence", "Local checks, approved runs, imports"],
  ["Result", "Verdict per criterion, next action, lesson"],
];
s.addShape(pres.shapes.LINE, { x: 0.95, y: 1.48, w: 8.1, h: 0, line: { color: HEX.accent6, width: 2 } });
steps.forEach(([h, d], i) => {
  const cx = 0.5 + i * 1.3 + 0.45;
  s.addShape(pres.shapes.OVAL, { x: cx - 0.28, y: 1.2, w: 0.56, h: 0.56, fill: { color: i === 6 ? C.accent2 : C.accent1 }, line: { color: C.background1, width: 2 } });
  text(s, String(i + 1), { x: cx - 0.28, y: 1.2, w: 0.56, h: 0.56, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle" });
  text(s, h, { x: cx - 0.6, y: 1.86, w: 1.2, h: 0.3, fontSize: 13, bold: true, color: C.text1, align: "center" });
  text(s, d, { x: cx - 0.6, y: 2.16, w: 1.2, h: 0.9, fontSize: 10, color: C.accent5, align: "center" });
});
const wfs = [
  ["route", "Feature or API", "Catches missing requirements against your API standard"],
  ["bug", "UAT defect", "No fix is accepted without a reproduction test"],
  ["vial", "Meaningful tests", "Proves tests fail when the behavior is broken"],
  ["shield", "Shared security stage", "Secrets, risky patterns, ASVS chapter references"],
];
wfs.forEach(([ic, h, d], i) => {
  const x = 0.5 + i * 2.3;
  card(s, x, 3.3, 2.1, 1.45, { name: "wf-" + i, fill: i === 3 ? C.background1 : C.background2, line: i === 3 ? HEX.accent6 : undefined });
  iconCircle(s, x + 0.15, 3.45, 0.42, ic, i === 3 ? C.text2 : C.accent1);
  text(s, h, { x: x + 0.65, y: 3.45, w: 1.4, h: 0.42, fontSize: 12, bold: true, color: C.text1, valign: "middle" });
  text(s, d, { x: x + 0.15, y: 3.95, w: 1.85, h: 0.75, fontSize: 11, color: C.text1 });
});
text(s, "Planned, not shown as working: PR review, docs and onboarding, release and config.", { x: 0.5, y: 4.85, w: 9, h: 0.28, fontSize: 10, italic: true, color: C.accent5 });

// ================= 6. Demo 1 =================
pres.addSection({ title: "Demos" });
s = content("Demos", "Demo 1: a missing API requirement, caught early");
bullets(s, [
  { text: "Story ORD-12: add an endpoint to cancel an order.", options: { bold: true } },
  "Compass finds the project's API standard and asks whether the operation needs X-Correlation-Id (standards/api-standard.md:10).",
  "It also asks who may call it and which errors it returns.",
  "The built-in OpenAPI check reports 1 passed, 3 failed, 1 not checked.",
], { x: 0.5, y: 1.2, w: 3.8, h: 2.9, fontSize: 13 });
chip(s, "Not accepted yet", 0.5, 4.15, 1.8, C.accent3);
text(s, "Agents fill missing requirements with guesses; those guesses are what fail review.", { x: 0.5, y: 4.55, w: 3.8, h: 0.55, fontSize: 11, italic: true, color: C.text2 });
shot(s, "api7.png", 4.6, 1.2, 4.9, 855, 570);
s.addNotes("Click the demo sample 'Catch a missing API requirement'. Show the source link on the correlation-id fact, then jump to the result: three failed criteria, each with a next action.");

// ================= 7. Demo 2 =================
s = content("Demos", "Demo 2: no reproduction, no acceptance");
chip(s, "Fix without a test", 0.5, 1.12, 2.0, C.accent3);
chip(s, "Fix with a regression test", 5.1, 1.12, 2.6, C.accent4);
shot(s, "def7.png", 0.5, 1.55, 4.4, 855, 580);
shot(s, "def7b.png", 5.1, 1.55, 4.4, 855, 480);
text(s, "Both fixes make the suite pass. Only the second proves the defect was reproduced: its test fails before the fix and passes after, checked on temporary copies.", { x: 5.1, y: 4.15, w: 4.4, h: 0.85, fontSize: 12, color: C.text1 });
s.addNotes("LOGIN-7 defect. Import fixes/fix-no-repro.diff, verify: Not accepted, no reproduction evidence. Import fixes/fix-with-repro.diff: Accepted with evidence. The project folder is never modified.");

// ================= 8. Demo 3 =================
s = content("Demos", "Demo 3: tests that actually detect a seeded defect");
bullets(s, [
  { text: "Synthetic defect SD-1 seeded at login_service/auth.py:35.", options: { bold: true } },
  "With approval, Compass runs the tests on a temporary copy: one test fails because of the defect.",
  "Tests that pass on broken code (existence or type checks only) are flagged.",
  "The built-in secrets check finds the synthetic credential in settings.ini.",
], { x: 0.5, y: 1.2, w: 3.8, h: 2.9, fontSize: 13 });
chip(s, "Defect detected, suite flagged", 0.5, 4.15, 2.7, C.accent2);
text(s, "A test that passes on broken code proves nothing.", { x: 0.5, y: 4.55, w: 3.8, h: 0.5, fontSize: 11, italic: true, color: C.text2 });
shot(s, "tests7.png", 4.6, 1.2, 4.9, 855, 480);

// ================= 9. Context budgeter =================
pres.addSection({ title: "Evidence" });
s = content("Evidence", "Right-sized context, nothing silently dropped");
text(s, "~3.3%", { x: 0.5, y: 1.15, w: 3.8, h: 1.0, fontSize: 60, bold: true, color: C.accent1, fontFace: THEME.headFontFace, valign: "middle" });
text(s, "Deep package vs pasting the whole 386-file repository: 15,145 vs 454,230 estimated tokens.", { x: 0.5, y: 2.2, w: 3.8, h: 0.7, fontSize: 13, color: C.text1 });
[["Lean ~4k", C.accent5], ["Balanced ~8k", C.text2], ["Deep ~16k", C.accent1]].forEach(([l, c], i) => chip(s, l, 0.5 + i * 1.3, 3.05, 1.2, c));
text(s, "Lean and Balanced report an overflow for that task instead of dropping a file the task names.", { x: 0.5, y: 3.5, w: 3.8, h: 0.65, fontSize: 12, color: C.text1 });
s.addChart(pres.charts.BAR, [{ name: "Estimated tokens", labels: ["Deep package", "Whole-repo paste"], values: [15145, 454230] }], {
  x: 4.6, y: 1.15, w: 4.9, h: 3.0, barDir: "bar",
  chartColors: [HEX.accent1, HEX.accent5], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0",
  dataLabelColor: HEX.dk1, dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt",
  showTitle: true, title: "Estimated tokens (characters / 4)", titleFontSize: 12, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
  catAxisLabelColor: HEX.accent5, valAxisLabelColor: HEX.accent5, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
  catAxisLabelFontSize: 11, valAxisLabelFontSize: 9, valAxisLabelFormatCode: "#,##0", valAxisMaxVal: 520000, valAxisMinVal: 0,
  valGridLine: { color: "DCE6E4", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false,
});
text(s, "Estimates, not Copilot, Claude or Devin billing. On the tiny fixtures the package is slightly larger than the project (3,716 vs 2,977) because it adds goal, facts, questions and criteria.", { x: 0.5, y: 4.4, w: 9.0, h: 0.6, fontSize: 10, italic: true, color: C.accent5 });

// ================= 10. Honest evidence =================
s = content("Evidence", "Honest evidence: a missing tool is never a pass");
const sts = [
  ["passed", C.accent4, "The check ran and found nothing"],
  ["failed", C.accent3, "Finding with file:line and the next step"],
  ["not checked", C.accent5, "Tool missing or not approved"],
  ["blocked", C.text1, "Report malformed or run refused"],
];
sts.forEach(([l, c, d], i) => {
  chip(s, l, 0.5, 1.25 + i * 0.6, 1.35, c);
  text(s, d, { x: 2.0, y: 1.25 + i * 0.6, w: 2.3, h: 0.3, fontSize: 12, color: C.text1, valign: "middle" });
});
card(s, 0.5, 3.75, 3.8, 1.05, { name: "scanners" });
text(s, [
  { text: "Real scanners verified through the approval flow", options: { bold: true, breakLine: true } },
  { text: "gitleaks 8.30.1, Semgrep 1.181.0 (metrics off, local rules), Spectral 6.17.0, plus JUnit and unittest reports." },
], { x: 0.65, y: 3.85, w: 3.5, h: 1.05, fontSize: 11, color: C.text1 });
shot(s, "tests6.png", 4.6, 1.2, 4.9, 855, 515);

// ================= 11. Privacy =================
pres.addSection({ title: "Trust" });
s = content("Trust", "Privacy is designed in, not configured later");
const priv = [
  ["db", "Two separate stores", "signals.db for aggregation (read-only); private.db for the engineer"],
  ["users", "k = 5 suppression", "Teams under 5 show nothing; differencing blocked in totals"],
  ["ban", "No ranking, anywhere", "A compliance check fails the build if scores or rankings appear"],
  ["eye", "Private by default", "Dismiss, feedback and history: engineer-only, deletable"],
  ["filter", "Data minimization", "Metadata only: no code, prompt text or free text stored"],
];
priv.forEach(([ic, h, d], i) => {
  const y = 1.15 + i * 0.78;
  iconCircle(s, 0.5, y + 0.05, 0.48, ic);
  text(s, h, { x: 1.15, y, w: 3.7, h: 0.3, fontSize: 13, bold: true, color: C.text1 });
  text(s, d, { x: 1.15, y: y + 0.3, w: 3.7, h: 0.4, fontSize: 11, color: C.accent5 });
});
shot(s, "supp.png", 5.1, 1.3, 4.4, 1240, 500);
text(s, "A manager of a team below the threshold sees no data at all.", { x: 5.1, y: 3.2, w: 4.4, h: 0.3, fontSize: 11, italic: true, color: C.text2 });

// ================= 12. Security =================
s = content("Trust", "Security guardrails for running on real projects");
const sec = [
  ["terminal", "No shell, ever", "Named command templates, validated arguments, minimal environment, timeouts"],
  ["fingerprint", "Pinned, approved scanners", "Approved once and pinned by SHA-256; a changed binary is refused"],
  ["folder", "Read-only project", "Allowed folders only; no traversal, symlinks or credential files"],
  ["shield", "Untrusted text stays data", "Prompt-injection phrases flagged and fenced; secrets redacted on export"],
  ["network", "Localhost only", "127.0.0.1 with Host, Origin and JSON checks against other websites"],
  ["key", "Jira read-only", "One pinned https host; the token is never written to disk"],
];
sec.forEach(([ic, h, d], i) => {
  const x = 0.5 + (i % 2) * 4.6, y = 1.15 + Math.floor(i / 2) * 1.27;
  card(s, x, y, 4.4, 1.07, { name: "sec-" + i });
  iconCircle(s, x + 0.2, y + 0.25, 0.55, ic);
  text(s, h, { x: x + 0.95, y: y + 0.13, w: 3.3, h: 0.3, fontSize: 13, bold: true, color: C.text1 });
  text(s, d, { x: x + 0.95, y: y + 0.45, w: 3.3, h: 0.55, fontSize: 11, color: C.text1 });
});

// ================= 13. Quality =================
s = content("Evidence", "Quality, measured and repeatable");
const q = [["74 / 74", "automated tests pass"], ["25 / 25", "seeded scenarios pass (target 80%)"], ["16 / 16", "prompt-routing stories"], ["37 / 37", "personas get complete recommendations"]];
q.forEach(([n, l], i) => {
  const x = 0.5 + i * 2.3;
  card(s, x, 1.2, 2.1, 1.9, { name: "q-" + i });
  text(s, n, { x: x + 0.15, y: 1.35, w: 1.8, h: 0.8, fontSize: 32, bold: true, color: C.accent1, fontFace: THEME.headFontFace, align: "center", valign: "middle" });
  text(s, l, { x: x + 0.15, y: 2.2, w: 1.8, h: 0.75, fontSize: 12, color: C.text1, align: "center" });
});
card(s, 0.5, 3.35, 9.0, 1.3, { fill: C.background1, line: HEX.accent6, noShadow: true });
iconCircle(s, 0.75, 3.6, 0.5, "check", C.accent4);
bullets(s, [
  "Every scenario must be relevant, complete, explainable, actionable and persona-specific to pass.",
  "The team wrote the scenarios, so 100% is a regression baseline, not held-out accuracy.",
  "CI runs on Windows and Linux with Python 3.9 and 3.12. Reports: reports/eval-report.md, docs/measurements.md.",
], { x: 1.45, y: 3.5, w: 7.9, h: 1.4, fontSize: 12 });

// ================= 14. Rubric =================
pres.addSection({ title: "Close" });
s = content("Close", "How Compass maps to the scoring guide");
const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text1 } } });
const rows = [
  [hdr("Area"), hdr("Weight"), hdr("What we show")],
  ["Problem fit and innovation", "30%", "All 14 acceptance criteria tested; coaches how AI is used, not how much; three live demos"],
  ["Business impact", "25%", "No new licenses or infrastructure; drops into any repo; pilot plan with success criteria"],
  ["Tech excellence and AI", "20%", "Context budgeter (~3.3% of a whole-repo paste); 25/25 eval; 74 tests; real scanner evidence"],
  ["Demo and delivery", "15%", "One-click start; 5-minute demo script; architecture, setup, user guide, security docs"],
  ["NFRs and governance", "10%", "Localhost, no shell, pinned tools, k = 5, audit of role, path and status only"],
];
s.addTable(rows, {
  x: 0.5, y: 1.15, w: 9.0, colW: [2.3, 0.9, 5.8], fontSize: 12, color: C.text1,
  border: { type: "solid", pt: 0.5, color: HEX.accent6 }, fill: { color: C.background1 },
  rowH: [0.4, 0.62, 0.62, 0.62, 0.62, 0.62], valign: "middle", margin: 0.08,
});

// ================= 15. Roadmap and hand-off =================
s = content("Close", "Next: pilot, scale, and an independent check");
text(s, "ROADMAP", { x: 0.5, y: 1.1, w: 4.3, h: 0.3, fontSize: 11, bold: true, color: C.accent5 });
const road = [
  ["Now", "MVP: private coaching, aggregated insights, workflow coach, agent kit"],
  ["Pilot, 4-6 weeks", "2-3 volunteer teams, authorized metadata only, SSO, k reviewed (consider 10)"],
  ["Scale", "VS Code extension shell, more workflows, central agent-kit repository"],
];
s.addShape(pres.shapes.LINE, { x: 0.74, y: 1.6, w: 0, h: 2.9, line: { color: HEX.accent6, width: 2 } });
road.forEach(([h, d], i) => {
  const y = 1.5 + i * 1.15;
  s.addShape(pres.shapes.OVAL, { x: 0.6, y, w: 0.28, h: 0.28, fill: { color: i === 0 ? C.accent2 : C.accent1 }, line: { color: C.background1, width: 2 } });
  text(s, h, { x: 1.05, y: y - 0.03, w: 3.7, h: 0.3, fontSize: 13, bold: true, color: C.text1 });
  text(s, d, { x: 1.05, y: y + 0.28, w: 3.7, h: 0.7, fontSize: 11, color: C.text1 });
});
text(s, "HAND-OFF FOR VERIFICATION", { x: 5.1, y: 1.1, w: 4.4, h: 0.3, fontSize: 11, bold: true, color: C.accent5 });
const ho = [
  ["1", "Devin", "Independent Linux run; installs scanners from the approved artifact repository"],
  ["2", "GitHub Copilot", "Windows run-through, sample-data mapping, deck and submission text"],
  ["3", "Claude Code", "Code and security review, final pre-submission check"],
];
ho.forEach(([n, h, d], i) => {
  const y = 1.45 + i * 1.15;
  card(s, 5.1, y, 4.4, 0.98, { name: "ho-" + i });
  s.addShape(pres.shapes.OVAL, { x: 5.25, y: y + 0.22, w: 0.5, h: 0.5, fill: { color: C.accent1 }, line: { type: "none" } });
  text(s, n, { x: 5.25, y: y + 0.22, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle" });
  text(s, h, { x: 5.95, y: y + 0.1, w: 3.4, h: 0.3, fontSize: 13, bold: true, color: C.text1 });
  text(s, d, { x: 5.95, y: y + 0.4, w: 3.4, h: 0.55, fontSize: 11, color: C.text1 });
});
s.addNotes("Hand-off instructions live in docs/handoff/. None of the assistants needs MCP servers or API keys.");

// ================= 16. Closing =================
s = pres.addSlide({ masterName: "DARK_CLOSE", sectionTitle: "Close" });
s.addText("Points the way. Never points fingers.", { placeholder: "title" });
s.addText([
  { text: "Right tool. Sharp prompt. Proven result.", options: { bold: true, color: C.background1, breakLine: true } },
  { text: "Double-click Start-Coach.bat, or run python -m compass", options: { breakLine: true } },
  { text: "github.com/Kalyanraja/compass-ai-coach  |  MIT licensed", options: { fontSize: 12 } },
], { placeholder: "body" });
s.addImage({ path: img("team.png"), x: 0.6, y: 3.85, w: 4.6, h: 4.6 * 420 / 1400 });
s.addImage({ path: img("ai-compass.png"), x: 5.95, y: 0.95, w: 3.7, h: 3.7 });

(async () => {
  await pres.writeFile({ fileName: OUT });
  if (THEME_JS) { const { applyTheme } = require(THEME_JS); await applyTheme(OUT, THEME); }
  console.log("wrote", OUT);
})();
