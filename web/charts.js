/* Tiny dependency-free SVG charts (works offline). */
(function (root) {
  "use strict";
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  function fmt(v, pct) {
    if (v === null || v === undefined) return "";
    if (pct) return Math.round(v * 100) + "%";
    return Math.abs(v) >= 100 ? Math.round(v) : Math.round(v * 10) / 10;
  }

  // series: [{points:[{week,value}], cls:'actual'|'proj'}]
  function line(series, opts) {
    opts = opts || {};
    var W = opts.width || 520, H = opts.height || 200, P = { l: 44, r: 14, t: 14, b: 28 };
    var pts = [];
    series.forEach(function (s) { s.points.forEach(function (p) { if (p.value !== null) pts.push(p); }); });
    if (!pts.length) return '<p class="muted small">Not enough data to chart.</p>';
    var xs = pts.map(function (p) { return p.week; }), ys = pts.map(function (p) { return p.value; });
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
    var y0 = Math.min(0, Math.min.apply(null, ys)), y1 = Math.max.apply(null, ys) * 1.12 || 1;
    var sx = function (x) { return P.l + (x - x0) / Math.max(1, x1 - x0) * (W - P.l - P.r); };
    var sy = function (y) { return H - P.b - (y - y0) / Math.max(1e-9, y1 - y0) * (H - P.t - P.b); };
    var out = ['<svg class="chart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + esc(opts.label || "chart") + '">'];
    for (var i = 0; i <= 3; i++) {
      var yv = y0 + (y1 - y0) * i / 3, yy = sy(yv);
      out.push('<line class="axis" x1="' + P.l + '" x2="' + (W - P.r) + '" y1="' + yy + '" y2="' + yy + '"/>');
      out.push('<text x="' + (P.l - 6) + '" y="' + (yy + 4) + '" text-anchor="end">' + fmt(yv, opts.pct) + '</text>');
    }
    for (var w = x0; w <= x1; w++) {
      out.push('<text x="' + sx(w) + '" y="' + (H - 8) + '" text-anchor="middle">W' + w + '</text>');
    }
    if (opts.divider) {
      var dx = sx(opts.divider);
      out.push('<line class="axis" stroke-dasharray="3 3" x1="' + dx + '" x2="' + dx + '" y1="' + P.t + '" y2="' + (H - P.b) + '"/>');
    }
    series.forEach(function (s) {
      var p = s.points.filter(function (q) { return q.value !== null; });
      if (!p.length) return;
      var d = p.map(function (q, j) { return (j ? "L" : "M") + sx(q.week).toFixed(1) + " " + sy(q.value).toFixed(1); }).join(" ");
      out.push('<path class="' + (s.cls || "actual") + '" d="' + d + '"/>');
      p.forEach(function (q) {
        out.push('<circle class="' + (s.cls === "proj" ? "pdot" : "dot") + '" r="3" cx="' + sx(q.week).toFixed(1) + '" cy="' + sy(q.value).toFixed(1) + '"><title>W' + q.week + ": " + fmt(q.value, opts.pct) + '</title></circle>');
      });
    });
    out.push("</svg>");
    return out.join("");
  }

  // items: [{label, share (0..1) or null when suppressed, display}]
  function bars(items, opts) {
    opts = opts || {};
    var W = opts.width || 520, rowH = 38, H = items.length * rowH + 8, L = 120;
    var out = ['<svg class="chart bars" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + esc(opts.label || "bar chart") + '">'];
    items.forEach(function (it, i) {
      var y = 4 + i * rowH, w = it.share == null ? 10 : (W - L - 150) * it.share;
      out.push('<text x="0" y="' + (y + 20) + '">' + esc(it.label) + '</text>');
      out.push('<rect class="bar' + (it.share == null ? " sup" : "") + '" x="' + L + '" y="' + (y + 6) + '" width="' + Math.max(2, w).toFixed(1) + '" height="18" rx="3"/>');
      out.push('<text x="' + (L + Math.max(2, w) + 8) + '" y="' + (y + 20) + '">' + esc(it.display) + '</text>');
    });
    out.push("</svg>");
    return out.join("");
  }

  root.Charts = { line: line, bars: bars, esc: esc };
})(window);
