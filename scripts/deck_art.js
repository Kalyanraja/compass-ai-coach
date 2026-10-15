// Generates the original illustrations used by the deck (an AI compass and a
// "people on the path" strip). Usage: node scripts/deck_art.js <out dir>
const React = require("react");
const RDS = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const path = require("path");

const OUT = process.argv[2] || ".";
const C = { dark: "#102A35", teal: "#1D6E6B", teal2: "#2E8B87", deep: "#1D5C63", mint: "#A9CFC9", face: "#F4F8F7", amber: "#C77D1E", amber2: "#E9A23B", slate: "#5E7279", red: "#B8432F", green: "#2E7D4F" };

const icon = (name, color, size, x, y) => {
  const svg = RDS.renderToStaticMarkup(React.createElement(fa[name], { color, size }));
  return svg.replace(/ (width|height)="[^"]*"/g, "").replace("<svg ", `<svg x="${x}" y="${y}" width="${size}" height="${size}" `);
};
const sparkle = (x, y, r, fill) =>
  `<path d="M ${x} ${y - r} Q ${x + r * 0.18} ${y - r * 0.18} ${x + r} ${y} Q ${x + r * 0.18} ${y + r * 0.18} ${x} ${y + r} Q ${x - r * 0.18} ${y + r * 0.18} ${x - r} ${y} Q ${x - r * 0.18} ${y - r * 0.18} ${x} ${y - r} Z" fill="${fill}"/>`;

// ---------- 1. AI compass ----------
function compass() {
  const S = 1200, cx = 600, cy = 600;
  let g = "";
  // bezel and rim
  g += `<circle cx="${cx}" cy="${cy}" r="585" fill="${C.deep}"/>`;
  g += `<circle cx="${cx}" cy="${cy}" r="560" fill="none" stroke="${C.amber}" stroke-width="10"/>`;
  g += `<circle cx="${cx}" cy="${cy}" r="530" fill="${C.face}"/>`;
  // circuit traces (the "AI" in the dial), drawn between the cardinal points
  const traces = [];
  for (let k = 0; k < 8; k++) {
    const a = (k * 45 + 22.5) * Math.PI / 180;
    const r1 = 150, r2 = 290, r3 = 360;
    const p1 = [cx + r1 * Math.sin(a), cy - r1 * Math.cos(a)];
    const p2 = [cx + r2 * Math.sin(a), cy - r2 * Math.cos(a)];
    const b = a + (k % 2 ? 0.16 : -0.16);
    const p3 = [cx + r3 * Math.sin(b), cy - r3 * Math.cos(b)];
    traces.push(`<polyline points="${p1.join(",")} ${p2.join(",")} ${p3.join(",")}" fill="none" stroke="${C.mint}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>`);
    traces.push(`<circle cx="${p3[0]}" cy="${p3[1]}" r="17" fill="${C.face}" stroke="${C.teal2}" stroke-width="8"/>`);
    traces.push(`<circle cx="${p2[0]}" cy="${p2[1]}" r="9" fill="${C.teal2}"/>`);
  }
  g += traces.join("");
  g += `<circle cx="${cx}" cy="${cy}" r="150" fill="none" stroke="${C.mint}" stroke-width="6" stroke-dasharray="4 18" stroke-linecap="round"/>`;
  // ticks
  for (let d = 0; d < 360; d += 5) {
    const major = d % 45 === 0, mid = d % 15 === 0;
    const r0 = 525, r1 = major ? 470 : mid ? 488 : 502;
    const a = d * Math.PI / 180;
    g += `<line x1="${cx + r0 * Math.sin(a)}" y1="${cy - r0 * Math.cos(a)}" x2="${cx + r1 * Math.sin(a)}" y2="${cy - r1 * Math.cos(a)}" stroke="${C.dark}" stroke-width="${major ? 9 : 4}" stroke-linecap="round"/>`;
  }
  // cardinal letters
  const letters = [["N", 0, C.amber], ["E", 90, C.dark], ["S", 180, C.dark], ["W", 270, C.dark]];
  for (const [t, d, col] of letters) {
    const a = d * Math.PI / 180, r = 412;
    g += `<text x="${cx + r * Math.sin(a)}" y="${cy - r * Math.cos(a) + 34}" font-family="Georgia, 'DejaVu Serif', serif" font-size="96" font-weight="700" fill="${col}" text-anchor="middle">${t}</text>`;
  }
  // needle, tilted toward north-east: "the right way"
  const needle =
    `<g transform="rotate(32 ${cx} ${cy})">` +
    `<polygon points="${cx},${cy - 400} ${cx - 62},${cy} ${cx},${cy}" fill="${C.amber2}"/>` +
    `<polygon points="${cx},${cy - 400} ${cx + 62},${cy} ${cx},${cy}" fill="${C.amber}"/>` +
    `<polygon points="${cx},${cy + 330} ${cx - 62},${cy} ${cx},${cy}" fill="${C.teal2}"/>` +
    `<polygon points="${cx},${cy + 330} ${cx + 62},${cy} ${cx},${cy}" fill="${C.teal}"/>` +
    `</g>`;
  g += `<g opacity="0.18" transform="translate(10 14)">${needle.replace(/fill="#[0-9A-Fa-f]+"/g, 'fill="#102A35"')}</g>`;
  g += needle;
  // hub with an AI sparkle
  g += `<circle cx="${cx}" cy="${cy}" r="70" fill="${C.dark}" stroke="${C.face}" stroke-width="10"/>`;
  g += sparkle(cx, cy, 44, "#FFFFFF");
  // little sparkles outside the dial
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${S}" height="${S}" viewBox="0 0 ${S} ${S}">${g}</svg>`;
}

// ---------- 2. People on the path ----------
function person(x, y, s, body, skin) {
  return `<g transform="translate(${x} ${y}) scale(${s})">` +
    `<path d="M -62 170 Q -62 70 0 70 Q 62 70 62 170 Z" fill="${body}"/>` +
    `<circle cx="0" cy="18" r="40" fill="${skin}"/>` +
    `</g>`;
}
function journey() {
  const W = 1800, H = 680;
  let g = '<g transform="translate(0 55)">';
  // ground path, rising to the right
  g += `<path d="M 40 560 C 420 560 560 470 900 450 S 1420 330 1640 250" fill="none" stroke="${C.mint}" stroke-width="16" stroke-linecap="round" stroke-dasharray="2 34"/>`;
  // three stops: tool, prompt, proof
  const stops = [
    { x: 340, y: 545, body: C.teal, skin: "#C98E62", badge: C.teal, ic: "FaTools", label: "Right tool" },
    { x: 820, y: 455, body: C.amber, skin: "#8D5A3B", badge: C.amber, ic: "FaCommentDots", label: "Sharp prompt" },
    { x: 1300, y: 355, body: C.deep, skin: "#E2B48C", badge: C.green, ic: "FaCheck", label: "Proven result" },
  ];
  for (const st of stops) {
    const by = st.y - 300;
    g += `<line x1="${st.x}" y1="${by + 70}" x2="${st.x}" y2="${st.y - 175}" stroke="${C.mint}" stroke-width="6" stroke-dasharray="3 12" stroke-linecap="round"/>`;
    g += `<circle cx="${st.x}" cy="${by}" r="70" fill="${st.badge}"/>`;
    g += `<circle cx="${st.x}" cy="${by}" r="70" fill="none" stroke="#FFFFFF" stroke-width="8"/>`;
    g += icon(st.ic, "#FFFFFF", 66, st.x - 33, by - 33);
    g += person(st.x, st.y - 165, 1.0, st.body, st.skin);
  }
  // a fourth person starting out, smaller, at the left
  g += person(110, 410, 0.8, C.slate, "#B07A52");
  // destination: a small compass at the top right
  g += `<circle cx="1650" cy="200" r="100" fill="${C.deep}"/><circle cx="1650" cy="200" r="80" fill="${C.face}"/>`;
  g += `<g transform="rotate(32 1650 200)"><polygon points="1650,130 1630,200 1670,200" fill="${C.amber}"/><polygon points="1650,265 1630,200 1670,200" fill="${C.teal}"/></g>`;
  g += `<circle cx="1650" cy="200" r="14" fill="${C.dark}"/>`;
  g += sparkle(1770, 80, 26, C.amber2) + sparkle(1530, 70, 16, C.mint);
  g += "</g>";
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}</svg>`;
}

// ---------- 3. Team (for the closing slide) ----------
function team() {
  const W = 1400, H = 420;
  let g = "";
  const cols = [[C.slate, "#B07A52"], [C.teal, "#C98E62"], [C.amber, "#8D5A3B"], [C.mint, "#E2B48C"], [C.teal2, "#9C6B48"]];
  cols.forEach(([b, s], i) => {
    const x = 220 + i * 240, big = i === 2;
    g += person(x, big ? 150 : 175, big ? 1.25 : 1.05, b, s);
  });
  // a shared direction arrow above the group
  g += `<path d="M 200 90 C 500 20 900 20 1180 70" fill="none" stroke="${C.amber2}" stroke-width="12" stroke-linecap="round"/>`;
  g += `<polygon points="1215,80 1160,40 1165,100" fill="${C.amber2}"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}</svg>`;
}

(async () => {
  await sharp(Buffer.from(compass())).png().toFile(path.join(OUT, "ai-compass.png"));
  await sharp(Buffer.from(journey())).png().toFile(path.join(OUT, "journey.png"));
  await sharp(Buffer.from(team())).png().toFile(path.join(OUT, "team.png"));
  console.log("art written to", OUT);
})();
