// Original illustrations for the deck: a navigator-style AI compass, people
// avatars on a guided path, and a team strip. Dark-theme friendly.
// Usage: node scripts/deck_art.js <out dir>
const React = require("react");
const RDS = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const path = require("path");

const OUT = process.argv[2] || ".";
const C = {
  navy: "#0B1B2B", ink: "#071421", card: "#13283D", line: "#2F4A63",
  cyan: "#2EC4B6", cyan2: "#7FD8CF", gold: "#F2B544", gold2: "#C98A1C", gold3: "#FFE3A3",
  coral: "#F0715A", green: "#5DD39E", mist: "#F2F5F8", slate: "#8FA3B3",
};

const icon = (name, color, size, x, y) =>
  RDS.renderToStaticMarkup(React.createElement(fa[name], { color, size }))
    .replace(/ (width|height)="[^"]*"/g, "")
    .replace("<svg ", `<svg x="${x}" y="${y}" width="${size}" height="${size}" `);
const polar = (cx, cy, r, deg) => [cx + r * Math.sin(deg * Math.PI / 180), cy - r * Math.cos(deg * Math.PI / 180)];
const sparkle = (x, y, r, fill) =>
  `<path d="M ${x} ${y - r} Q ${x + r * 0.16} ${y - r * 0.16} ${x + r} ${y} Q ${x + r * 0.16} ${y + r * 0.16} ${x} ${y + r} Q ${x - r * 0.16} ${y + r * 0.16} ${x - r} ${y} Q ${x - r * 0.16} ${y - r * 0.16} ${x} ${y - r} Z" fill="${fill}"/>`;

const DEFS = `
<defs>
  <linearGradient id="goldRim" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="${C.gold3}"/><stop offset="0.45" stop-color="${C.gold}"/>
    <stop offset="0.7" stop-color="${C.gold2}"/><stop offset="1" stop-color="${C.gold3}"/>
  </linearGradient>
  <radialGradient id="face" cx="0.5" cy="0.45" r="0.6">
    <stop offset="0" stop-color="#1B3A55"/><stop offset="1" stop-color="${C.ink}"/>
  </radialGradient>
  <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0.6" stop-color="${C.cyan}" stop-opacity="0.35"/><stop offset="1" stop-color="${C.cyan}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="goldHalo" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="${C.gold}" stop-opacity="0.5"/><stop offset="1" stop-color="${C.gold}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="path" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="${C.slate}" stop-opacity="0.4"/><stop offset="1" stop-color="${C.gold}"/>
  </linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>`;

// ---------- 1. Navigator compass with an AI core ----------
function compass() {
  const S = 1200, cx = 600, cy = 600;
  let g = DEFS;
  g += `<circle cx="${cx}" cy="${cy}" r="595" fill="url(#halo)"/>`;
  g += `<circle cx="${cx}" cy="${cy}" r="540" fill="url(#goldRim)"/>`;
  g += `<circle cx="${cx}" cy="${cy}" r="512" fill="${C.ink}"/>`;
  g += `<circle cx="${cx}" cy="${cy}" r="500" fill="url(#face)"/>`;
  for (let d = 0; d < 360; d += 3) {
    const major = d % 30 === 0;
    const [x1, y1] = polar(cx, cy, 492, d), [x2, y2] = polar(cx, cy, major ? 455 : 474, d);
    g += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${major ? C.gold : C.slate}" stroke-width="${major ? 6 : 2.5}" stroke-linecap="round"/>`;
  }
  g += `<circle cx="${cx}" cy="${cy}" r="440" fill="none" stroke="${C.line}" stroke-width="3"/>`;
  // 16-point compass rose
  const point = (deg, len, wid, light, dark) => {
    const tip = polar(cx, cy, len, deg), l = polar(cx, cy, wid, deg - 90), r = polar(cx, cy, wid, deg + 90);
    return `<polygon points="${tip} ${l} ${cx},${cy}" fill="${light}"/><polygon points="${tip} ${r} ${cx},${cy}" fill="${dark}"/>`;
  };
  for (let d = 11.25; d < 360; d += 22.5) g += point(d, 240, 22, "#2A4A66", "#1E3850");
  for (let d = 45; d < 360; d += 90) g += point(d, 310, 40, C.cyan2, C.cyan);
  for (let d = 0; d < 360; d += 90) g += point(d, 420, 56, d === 0 ? C.gold3 : C.mist, d === 0 ? C.gold : "#C9D4DD");
  // AI core: a small neural network in a glowing disc
  g += `<circle cx="${cx}" cy="${cy}" r="150" fill="${C.cyan}" opacity="0.35" filter="url(#glow)"/>`;
  g += `<circle cx="${cx}" cy="${cy}" r="128" fill="${C.ink}" stroke="${C.gold}" stroke-width="7"/>`;
  const nodes = [[-70, -45], [-70, 0], [-70, 45], [0, -62], [0, -20], [0, 20], [0, 62], [70, -25], [70, 25]];
  const edges = [[0, 3], [0, 4], [1, 4], [1, 5], [2, 5], [2, 6], [0, 5], [2, 4], [3, 7], [4, 7], [5, 8], [6, 8], [4, 8], [5, 7]];
  for (const [a, b] of edges) g += `<line x1="${cx + nodes[a][0]}" y1="${cy + nodes[a][1]}" x2="${cx + nodes[b][0]}" y2="${cy + nodes[b][1]}" stroke="${C.cyan2}" stroke-width="4" opacity="0.75"/>`;
  nodes.forEach(([x, y], i) => { g += `<circle cx="${cx + x}" cy="${cy + y}" r="${i >= 7 ? 15 : 11}" fill="${i >= 7 ? C.gold : C.cyan}"/>`; });
  // N marker on the rim
  g += `<text x="${cx}" y="${cy - 428}" font-family="Georgia, 'DejaVu Serif', serif" font-size="0" fill="none">N</text>`;
  // needle pointing north-east, with glow
  const needle = (n1, n2, s1, s2) =>
    `<g transform="rotate(38 ${cx} ${cy})">` +
    `<polygon points="${cx},${cy - 470} ${cx - 34},${cy - 128} ${cx},${cy - 128}" fill="${n1}"/>` +
    `<polygon points="${cx},${cy - 470} ${cx + 34},${cy - 128} ${cx},${cy - 128}" fill="${n2}"/>` +
    `<polygon points="${cx},${cy + 400} ${cx - 30},${cy + 128} ${cx},${cy + 128}" fill="${s1}"/>` +
    `<polygon points="${cx},${cy + 400} ${cx + 30},${cy + 128} ${cx},${cy + 128}" fill="${s2}"/></g>`;
  g += `<g filter="url(#soft)" opacity="0.8">${needle(C.gold, C.gold, "none", "none")}</g>`;
  g += needle(C.gold3, C.gold, "#3B5B78", "#2A4A66");
  g += sparkle(1040, 140, 40, C.gold) + sparkle(1120, 240, 18, C.cyan2) + sparkle(140, 1050, 22, C.cyan2);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${S}" height="${S}" viewBox="0 0 ${S} ${S}">${g}</svg>`;
}

// ---------- people ----------
// Bust-style avatar inside a circle. hair: "short" | "long" | "bun" | "curly"
let clipId = 0;
function avatar(cx, cy, r, o) {
  const id = "c" + clipId++;
  const s = r / 100;
  let g = `<clipPath id="${id}"><circle cx="${cx}" cy="${cy}" r="${r}"/></clipPath>`;
  g += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${o.bg || C.card}"/>`;
  g += `<g clip-path="url(#${id})"><g transform="translate(${cx} ${cy + r * 0.12}) scale(${s})">`;
  if (o.hair === "long") g += `<path d="M -48 -30 Q -52 -80 0 -82 Q 52 -80 48 -30 L 54 44 Q 0 56 -54 44 Z" fill="${o.hairC}"/>`;
  g += `<path d="M -90 130 Q -90 50 -30 40 L 30 40 Q 90 50 90 130 Z" fill="${o.shirt}"/>`;
  g += `<path d="M -22 40 L 0 66 L 22 40 Z" fill="${C.mist}" opacity="0.9"/>`;
  g += `<rect x="-14" y="8" width="28" height="36" rx="10" fill="${o.skin}"/>`;
  g += `<ellipse cx="0" cy="-24" rx="38" ry="44" fill="${o.skin}"/>`;
  if (o.hair === "short") g += `<path d="M -40 -26 Q -44 -72 0 -72 Q 44 -72 40 -26 Q 30 -52 0 -50 Q -26 -52 -40 -26 Z" fill="${o.hairC}"/>`;
  if (o.hair === "long") g += `<path d="M -40 -20 Q -42 -72 0 -72 Q 42 -72 40 -20 Q 20 -50 -10 -48 Q -30 -42 -40 -20 Z" fill="${o.hairC}"/>`;
  if (o.hair === "bun") g += `<circle cx="0" cy="-76" r="20" fill="${o.hairC}"/><path d="M -40 -26 Q -42 -70 0 -70 Q 42 -70 40 -26 Q 28 -52 0 -52 Q -28 -52 -40 -26 Z" fill="${o.hairC}"/>`;
  if (o.hair === "curly") for (const [x, y] of [[-30, -54], [-12, -66], [10, -66], [28, -54], [-38, -34], [38, -34]]) g += `<circle cx="${x}" cy="${y}" r="17" fill="${o.hairC}"/>`;
  g += `</g></g>`;
  g += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${o.ring || C.line}" stroke-width="${Math.max(4, r * 0.07)}"/>`;
  return g;
}
const PEOPLE = [
  { skin: "#C98E62", hair: "short", hairC: "#2B1D16", shirt: "#2EC4B6" },
  { skin: "#8D5A3B", hair: "curly", hairC: "#1A1210", shirt: "#F2B544" },
  { skin: "#E8C2A0", hair: "long", hairC: "#6B4423", shirt: "#5DD39E" },
  { skin: "#B07A52", hair: "bun", hairC: "#241812", shirt: "#7FD8CF" },
  { skin: "#F0CBA8", hair: "short", hairC: "#A0653A", shirt: "#F0715A" },
];

// ---------- 2. The guided path: tool, prompt, proof ----------
function journey() {
  const W = 1800, H = 700;
  let g = DEFS;
  const P = "M 60 620 C 420 620 520 490 820 460 S 1300 320 1660 200";
  g += `<path d="${P}" fill="none" stroke="${C.gold}" stroke-width="26" stroke-linecap="round" opacity="0.18" filter="url(#soft)"/>`;
  g += `<path d="${P}" fill="none" stroke="url(#path)" stroke-width="10" stroke-linecap="round"/>`;
  const stops = [
    { x: 360, y: 585, p: 0, col: C.cyan, ic: "FaTools" },
    { x: 860, y: 452, p: 1, col: C.gold, ic: "FaCommentDots" },
    { x: 1340, y: 318, p: 2, col: C.green, ic: "FaCheck" },
  ];
  for (const st of stops) {
    const ay = st.y - 195;
    g += `<circle cx="${st.x}" cy="${st.y}" r="32" fill="${st.col}" opacity="0.4" filter="url(#soft)"/>`;
    g += `<circle cx="${st.x}" cy="${st.y}" r="16" fill="${st.col}" stroke="${C.navy}" stroke-width="6"/>`;
    g += `<line x1="${st.x}" y1="${st.y - 20}" x2="${st.x}" y2="${ay + 95}" stroke="${st.col}" stroke-width="4" stroke-dasharray="2 10" stroke-linecap="round"/>`;
    g += avatar(st.x, ay, 90, Object.assign({ ring: st.col }, PEOPLE[st.p]));
    g += `<circle cx="${st.x + 72}" cy="${ay - 66}" r="40" fill="${st.col}" stroke="${C.navy}" stroke-width="8"/>`;
    g += icon(st.ic, C.navy, 40, st.x + 52, ay - 86);
  }
  g += avatar(140, 500, 64, Object.assign({ ring: C.slate }, PEOPLE[3]));
  g += `<circle cx="1660" cy="200" r="130" fill="url(#goldHalo)"/>`;
  g += `<circle cx="1660" cy="200" r="74" fill="url(#goldRim)"/><circle cx="1660" cy="200" r="61" fill="${C.ink}"/>`;
  g += `<g transform="rotate(38 1660 200)"><polygon points="1660,146 1648,200 1672,200" fill="${C.gold}"/><polygon points="1660,254 1648,200 1672,200" fill="${C.slate}"/></g>`;
  g += `<circle cx="1660" cy="200" r="9" fill="${C.gold3}"/>`;
  g += sparkle(1775, 70, 24, C.gold) + sparkle(1555, 80, 14, C.cyan2);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}</svg>`;
}

// ---------- 3. Team strip ----------
function team() {
  const W = 1500, H = 400;
  let g = DEFS;
  g += `<path d="M 120 62 C 500 0 1000 0 1360 52" fill="none" stroke="${C.gold}" stroke-width="9" stroke-linecap="round" stroke-dasharray="1 20"/>`;
  g += `<polygon points="1402,60 1344,26 1348,88" fill="${C.gold}"/>`;
  PEOPLE.forEach((p, i) => { g += avatar(170 + i * 290, 245, i === 2 ? 128 : 108, Object.assign({ ring: i === 2 ? C.gold : C.line }, p)); });
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}</svg>`;
}

// ---------- 4. Avatars for the three view cards ----------
const svg400 = (g) => `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">${g}</svg>`;
const single = (i, ring) => svg400(avatar(200, 200, 186, Object.assign({ ring }, PEOPLE[i])));
const group = (ring) => svg400(
  avatar(105, 140, 92, Object.assign({ ring: C.line }, PEOPLE[1])) +
  avatar(295, 140, 92, Object.assign({ ring: C.line }, PEOPLE[4])) +
  avatar(200, 262, 128, Object.assign({ ring }, PEOPLE[3])));

(async () => {
  const out = (n, s) => sharp(Buffer.from(s)).png().toFile(path.join(OUT, n));
  await out("ai-compass.png", compass());
  await out("journey.png", journey());
  await out("team.png", team());
  await out("person-engineer.png", single(0, C.cyan));
  await out("person-group.png", group(C.gold));
  await out("person-coach.png", single(2, C.green));
  console.log("art written to", OUT);
})();
