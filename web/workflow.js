/* Workflow coach, Setup and Tool catalog views. Loaded before app.js; uses window.Compass helpers at call time. */
(function () {
  "use strict";
  function C() { return window.Compass; }
  function esc(s) { return Charts.esc(s == null ? "" : s); }
  var W = { j: null, step: 1, pkg: null, rec: null, samples: [], query: {}, jira: null, setup: null, incl: [], excl: [] };

  var STEPS = [
    [1, "Goal", "What do you want to achieve?"],
    [2, "Project facts", "What Compass found, with sources"],
    [3, "Questions", "Up to 3 missing details at a time"],
    [4, "Tool", "Approved tool for this task"],
    [5, "Work package", "Reviewed handoff, sized to a budget"],
    [6, "Evidence", "Local checks and imported results"],
    [7, "Result and lesson", "Verdict, next action, one lesson"]
  ];

  function pill(status) {
    var cls = { passed: "ok", failed: "no", "not-checked": "", blocked: "", detected: "ok", inferred: "", confirmed: "ok", unknown: "" }[status];
    var label = { "not-checked": "not checked" }[status] || status;
    return '<span class="tag ' + (cls === "ok" ? "" : cls === "no" ? "amber" : "plain") + '">' + esc(label) + "</span>";
  }
  function src(f) {
    if (!f.source || !f.source.line) return "";
    return ' <button class="linkbtn mono small" data-wf="open-file" data-path="' + esc(f.source.path) + '" data-line="' + f.source.line + '">' + esc(f.source.path + ":" + f.source.line) + "</button>";
  }

  // ------------------------------------------------------------------ main view
  function workflowView(query) {
    W.query = query || {};
    var html = '<div class="spread"><div><h1>Workflow coach</h1><p class="lead">Goal, project facts, missing questions, the right approved tool, a reviewed work package, evidence, and one lesson. Runs locally with no API keys.</p></div>' +
      '<div class="row"><a class="btn ghost small" href="#/prompt">Quick prompt for other tasks</a></div></div>' +
      C().privacyBar("Session-only and local", "Project files are read only from folders you allow in Setup. Nothing is stored after this session, and nothing is sent to any assistant: you copy the work package yourself.") +
      '<div class="wf-grid"><nav class="wf-steps" aria-label="Steps" id="wf-steps"></nav><section id="wf-body" class="stack"></section></div>';
    C().view(html);
    renderSteps();
    if (W.j && !W.query.project && !W.query.jira) { goStep(W.step); } else { W.j = null; W.pkg = null; W.rec = null; goStep(1); }
  }

  function renderSteps() {
    var el = document.getElementById("wf-steps");
    if (!el) return;
    el.innerHTML = '<ol class="wf-steplist">' + STEPS.map(function (s) {
      var enabled = s[0] === 1 || W.j;
      return '<li><button class="wf-step' + (W.step === s[0] ? " on" : "") + '" data-wf="go" data-step="' + s[0] + '"' + (enabled ? "" : " disabled") +
        '><span class="n">' + s[0] + '</span><span><strong>' + esc(s[1]) + '</strong><span class="small muted">' + esc(s[2]) + "</span></span></button></li>";
    }).join("") + "</ol>" + (W.j ? '<p class="small muted" style="margin-top:.75rem">Project: <strong>' + esc(W.j.project_name) + '</strong><br>Workflow: ' + esc(W.j.workflow.title) + ' v' + esc(W.j.workflow.version) + '</p><button class="btn ghost small" data-wf="reset">Start a new task</button>' : "");
  }

  function goStep(n) {
    W.step = n;
    renderSteps();
    var body = document.getElementById("wf-body");
    if (!body) return;
    ({ 1: stepGoal, 2: stepFacts, 3: stepQuestions, 4: stepTool, 5: stepPackage, 6: stepEvidence, 7: stepResult })[n](body);
    window.scrollTo(0, 0);
  }

  function nextBtn(n, label) { return '<div class="row"><button class="btn" data-wf="go" data-step="' + n + '">' + esc(label || "Continue") + "</button></div>"; }

  // ------------------------------------------------------------------ 1 goal
  function stepGoal(body) {
    body.innerHTML = '<div class="panel stack"><h2>1. What do you want to achieve?</h2>' +
      '<div><p class="small muted">Try a demo (synthetic projects):</p><div class="row" id="wf-samples"></div></div><hr>' +
      '<div class="grid2"><div><label for="wf-project">Project folder</label><select id="wf-project"></select><p class="small muted">Only folders you allowed in <a href="#/setup">Setup</a> appear here.</p></div>' +
      '<div><label>Bring in the task</label><div class="row"><input type="text" id="wf-jira-key" placeholder="Jira key, e.g. ABC-123" style="max-width:200px"><button class="btn ghost small" data-wf="jira-fetch">Fetch from Jira</button><button class="btn ghost small" data-wf="jira-mine">My open issues</button></div><p class="small muted" id="wf-jira-status"></p><div id="wf-jira-list"></div></div></div>' +
      '<div><label for="wf-goal">Goal, story or defect</label><textarea id="wf-goal" placeholder="Paste the story or describe the task. Remove customer data and secrets."></textarea></div>' +
      '<div><label>Workflow</label><div class="tool-options" id="wf-kinds"></div><p class="small muted" id="wf-guess"></p></div>' +
      '<div class="row"><button class="btn" data-wf="start">Start</button></div></div>';
    var api = C().api;
    api("GET", "/api/wf/projects").then(function (d) {
      var sel = document.getElementById("wf-project");
      sel.innerHTML = d.projects.map(function (p) { return '<option value="' + esc(p.path) + '">' + esc(p.name) + "</option>"; }).join("");
      var want = W.query.project || d.default;
      if (want) {
        var match = d.projects.filter(function (p) { return p.path === want || p.name.split("/").pop() === want; })[0];
        if (match) sel.value = match.path; else if (W.query.project) C().toast("That folder is not in your allowed folders. Add it in Setup.");
      }
    });
    api("GET", "/api/wf/packs").then(function (d) {
      document.getElementById("wf-kinds").innerHTML = d.packs.filter(function (p) { return p.kind !== "shared-stage"; }).map(function (p) {
        var working = p.status === "working";
        return '<label class="tool-opt' + (working ? "" : " disabled") + '"><input type="radio" name="wf-kind" value="' + esc(p.id) + '"' + (working ? "" : " disabled") + '> <span><strong>' + esc(p.title) + "</strong>" +
          (working ? "" : ' <span class="tag plain">coming later</span>') + '<br><span class="small muted">' + esc(p.summary) + "</span></span></label>";
      }).join("") + '<label class="tool-opt"><input type="radio" name="wf-kind" value="auto" checked> <span><strong>Detect for me</strong><br><span class="small muted">Compass picks from the three guided workflows.</span></span></label>';
    });
    api("GET", "/api/wf/samples").then(function (d) {
      W.samples = d.samples;
      document.getElementById("wf-samples").innerHTML = d.samples.map(function (s, i) {
        return '<button class="btn ghost small" data-wf="sample" data-i="' + i + '">' + esc(s.title) + "</button>";
      }).join("");
    });
    api("GET", "/api/jira/status").then(function (s) {
      W.jira = s;
      document.getElementById("wf-jira-status").textContent = s.ready ? ("Jira connected to " + s.base_url + (s.token_present ? "" : " (no token in " + s.token_env + "; you can enter one for this session)")) :
        "Jira is off. Turn it on in Setup, paste the story, or use the Quick prompt page to import a Jira CSV export.";
      if (W.query.jira) { document.getElementById("wf-jira-key").value = W.query.jira; if (s.ready) jiraFetch(); }
    });
    document.getElementById("wf-goal").addEventListener("input", guess);
  }
  var guessTimer;
  function guess() {
    clearTimeout(guessTimer);
    guessTimer = setTimeout(function () {
      var t = document.getElementById("wf-goal").value.toLowerCase();
      var kw = { "feature-api": ["endpoint", "api", "implement", "feature", "story", "as a ", "request"], "uat-defect": ["defect", "bug", "fail", "uat", "wrong", "error", "cannot"], "test-creation": ["test", "coverage", "playwright", "junit", "automation"] };
      var best = Object.keys(kw).map(function (k) { return [k, kw[k].filter(function (w) { return t.indexOf(w) >= 0; }).length]; }).sort(function (a, b) { return b[1] - a[1]; })[0];
      var g = document.getElementById("wf-guess");
      if (g) g.textContent = best[1] ? "Looks like: " + { "feature-api": "Build or change a feature / API", "uat-defect": "Investigate a UAT defect", "test-creation": "Create meaningful tests" }[best[0]] : "";
    }, 250);
  }
  function jiraToken() {
    if (W.jira && W.jira.token_present) return null;
    var t = window.prompt ? null : null; // never use browser dialogs
    var el = document.getElementById("wf-jira-token");
    return el ? el.value : null;
  }
  function jiraFetch() {
    var key = document.getElementById("wf-jira-key").value.trim();
    if (W.jira && W.jira.ready && !W.jira.token_present && !document.getElementById("wf-jira-token")) {
      document.getElementById("wf-jira-list").innerHTML = '<label for="wf-jira-token">Jira token for this session only (not saved)</label><input type="text" id="wf-jira-token" autocomplete="off"><p class="small muted">Prefer setting the ' + esc(W.jira.token_env) + ' environment variable before starting Compass.</p>';
      return;
    }
    C().api("POST", "/api/jira/issue", { key: key, token: jiraToken() }).then(function (i) {
      document.getElementById("wf-goal").value = i.key + ": " + i.text;
      document.getElementById("wf-jira-list").innerHTML = '<p class="small">Fetched <strong>' + esc(i.key) + "</strong> (" + esc(i.issue_type) + ", " + esc(i.status) + "). Review the text below; it is not stored.</p>";
      guess();
    }).catch(function (e) { C().toast(e.message); });
  }

  function start() {
    var kind = (document.querySelector('input[name="wf-kind"]:checked') || {}).value;
    C().api("POST", "/api/wf/start", { goal: document.getElementById("wf-goal").value, project: document.getElementById("wf-project").value,
      workflow: kind === "auto" ? null : kind, source: document.getElementById("wf-jira-key").value ? "jira" : "manual" }).then(function (j) {
      W.j = j; W.pkg = null; W.rec = null; W.incl = []; W.excl = []; goStep(2);
    }).catch(function (e) { C().toast(e.message); });
  }

  // ------------------------------------------------------------------ 2 facts
  function factRow(f, editable) {
    var v = Array.isArray(f.value) ? f.value.slice(0, 4).join(", ") + (f.value.length > 4 ? " ..." : "") : f.value;
    return "<tr><td>" + esc(f.label) + "</td><td>" + (v ? esc(v) : '<span class="muted">' + esc(f.note || "not found") + "</span>") + src(f) + "</td><td>" + pill(f.status) + "</td><td>" +
      (!editable ? "" : f.status === "detected" ? '<button class="btn ghost small" data-wf="confirm" data-fact="' + esc(f.id) + '">Confirm</button>' :
        '<div class="row"><input type="text" data-fact-input="' + esc(f.id) + '" value="' + esc(Array.isArray(f.value) ? "" : (f.value || "")) + '" placeholder="' + (f.status === "unknown" ? "type it if you know it" : "") + '" style="max-width:220px"><button class="btn ghost small" data-wf="confirm" data-fact="' + esc(f.id) + '">' + (f.status === "unknown" ? "Set" : "Confirm") + "</button></div>") + "</td></tr>";
  }
  function stepFacts(body) {
    var j = W.j;
    var html = '<div class="panel stack"><div class="spread"><h2>2. Project facts</h2><span class="small muted">' + j.file_count + " readable files" + (j.cache && j.cache !== "off" ? " &middot; cache " + esc(j.cache) : "") + "</span></div>";
    if (!j.supported_stack) {
      var note = (j.facts.unknown.filter(function (f) { return f.id === "stack"; })[0] || {}).note;
      html += '<div class="warn">' + esc(note || "Automatic framework detection is unavailable for this project.") + "</div>";
    }
    html += '<p class="small muted">Detected means found in a file (click the source to see it). Inferred means a convention Compass assumed: confirm it. Unknown means not found: Compass will not guess.</p>' +
      '<div class="table-wrap"><table><thead><tr><th>Fact</th><th>Value and source</th><th>Status</th><th>Confirm or correct</th></tr></thead><tbody>' +
      j.facts.detected.map(function (f) { return factRow(f, true); }).join("") + j.facts.confirmed.map(function (f) { return factRow(f, false); }).join("") +
      j.facts.unknown.map(function (f) { return factRow(f, true); }).join("") + "</tbody></table></div>" + nextBtn(3, "Continue to questions") + "</div>";
    body.innerHTML = html;
  }

  // ------------------------------------------------------------------ 3 questions
  function stepQuestions(body) {
    var q = W.j.questions;
    var html = '<div class="panel stack"><h2>3. Missing details</h2>';
    if (!q.questions.length) {
      html += '<p>No open questions. Everything this workflow needs is either known or answered.</p>';
    } else {
      html += '<p class="small muted">Answer what you can. Each question says why it matters. ' + (q.remaining ? q.remaining + " more will follow." : "") + "</p>" +
        q.questions.map(function (x) {
          return '<div class="stack" style="gap:.25rem"><label for="q-' + esc(x.id) + '">' + esc(x.text) + "</label>" +
            '<div class="row"><input type="text" id="q-' + esc(x.id) + '" data-wf-q="' + esc(x.id) + '" value="' + esc(x.suggested || "") + '"><button class="btn ghost small" data-wf="skip" data-q="' + esc(x.id) + '">Skip</button></div>' +
            '<div class="small muted">' + esc(x.why) + (x.source ? ' (from ' + esc(x.source.path + ":" + x.source.line) + ")" : "") + "</div></div>";
        }).join("") + '<div class="row"><button class="btn" data-wf="answer">Save answers</button></div>';
    }
    var a = W.j.answers;
    if (Object.keys(a).length) html += '<h3>Your answers</h3><ul class="small">' + Object.keys(a).map(function (k) { return "<li><strong>" + esc(k) + ":</strong> " + esc(a[k]) + "</li>"; }).join("") + "</ul>";
    html += nextBtn(4, q.questions.length ? "Continue with open questions" : "Continue to tool") + "</div>";
    body.innerHTML = html;
  }

  // ------------------------------------------------------------------ 4 tool
  function stepTool(body) {
    var j = W.j;
    body.innerHTML = '<div class="panel stack"><h2>4. Approved tool for this task</h2>' +
      '<p class="small muted">Compass applies your approval and data rules first, then capability and task fit. You can override within policy.</p>' +
      '<div class="grid3"><div><label for="t-data">What data is involved?</label><select id="t-data"><option value="synthetic">Synthetic or public only</option><option value="internal">Internal code and docs, no customer data</option><option value="restricted">Customer, personal or secret data</option></select></div>' +
      '<div><label for="t-cx">Complexity</label><select id="t-cx"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></div>' +
      '<div><label>Shape</label><label class="small" style="font-weight:400"><input type="checkbox" id="t-large"> Repo-wide or many services</label><label class="small" style="font-weight:400"><input type="checkbox" id="t-det"> Pure formatting / lint / chore</label></div></div>' +
      '<div class="row"><button class="btn" data-wf="recommend">Recommend a tool</button></div><div id="t-out"></div></div>';
    document.getElementById("t-data").value = j.data_class; document.getElementById("t-cx").value = j.complexity;
    document.getElementById("t-large").checked = j.large_scope;
    if (W.rec) renderRec();
  }
  function recommend(choose) {
    C().api("POST", "/api/wf/tool", { id: W.j.id, data_class: document.getElementById("t-data").value, complexity: document.getElementById("t-cx").value,
      large_scope: document.getElementById("t-large").checked, deterministic: document.getElementById("t-det").checked, choose: choose || null }).then(function (r) {
      W.rec = r; W.j.tool = r.chosen; W.j.data_class = document.getElementById("t-data").value; renderRec();
    }).catch(function (e) { C().toast(e.message); });
  }
  function renderRec() {
    var r = W.rec;
    document.getElementById("t-out").innerHTML = '<div class="panel" style="margin-top:.75rem"><h3>' + (r.tool ? "Recommended: " + esc(r.label) : "No approved tool fits") + '</h3><ul class="small">' + r.reasons.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" +
      '<div class="tool-options">' + r.options.map(function (o) {
        return '<label class="tool-opt' + (o.allowed ? "" : " disabled") + '"><input type="radio" name="t-choice" value="' + esc(o.id) + '"' + (o.id === r.chosen ? " checked" : "") + (o.allowed ? "" : " disabled") + '> <span><strong>' + esc(o.label) + "</strong>" + (o.id === r.tool ? ' <span class="tag">recommended</span>' : "") +
          (o.allowed ? '<br><span class="small muted">' + esc(o.handoff) + "</span>" : '<br><span class="small muted">Not allowed: ' + esc(o.blocked_reason) + "</span>") + "</span></label>";
      }).join("") + '</div><div class="row" style="margin-top:.75rem"><button class="btn ghost" data-wf="choose">Use the selected tool</button><button class="btn" data-wf="go" data-step="5">Continue to work package</button></div>' +
      (r.override ? '<p class="small muted">You chose a different tool than recommended. That is fine within policy.</p>' : "") + "</div>";
  }

  // ------------------------------------------------------------------ 5 package
  function stepPackage(body) {
    body.innerHTML = '<div class="panel stack"><h2>5. Work package</h2><p class="small muted">A compact, reviewed handoff. Decisive files (spec, standard, failing test) are always included in full. Sizes are estimates, not billing.</p>' +
      '<div class="row"><span>Budget:</span>' + [["lean", "Lean ~4k"], ["balanced", "Balanced ~8k"], ["deep", "Deep ~16k"]].map(function (b) {
        return '<label class="small" style="font-weight:400"><input type="radio" name="p-budget" value="' + b[0] + '"' + ((W.pkg ? W.pkg.budget : W.j.budget) === b[0] ? " checked" : "") + "> " + b[1] + "</label>";
      }).join("") + '<button class="btn" data-wf="package">Build work package</button></div><div id="p-out"></div></div>';
    if (W.pkg) renderPkg();
  }
  function buildPkg() {
    var b = (document.querySelector('input[name="p-budget"]:checked') || {}).value || "balanced";
    C().api("POST", "/api/wf/package", { id: W.j.id, budget: b, include: W.incl, exclude: W.excl }).then(function (p) { W.pkg = p; renderPkg(); }).catch(function (e) { C().toast(e.message); });
  }
  function renderPkg() {
    var p = W.pkg, c = p.comparison;
    var html = '<div class="grid3" style="margin-top:.75rem"><div><div class="small muted">This package</div><div class="stat">~' + p.size.est_tokens.toLocaleString() + '</div><div class="small muted">' + p.size.bytes.toLocaleString() + ' bytes</div></div>' +
      '<div><div class="small muted">Pasting the whole project</div><div class="stat">~' + c.whole_project_paste.tokens.toLocaleString() + '</div><div class="small muted">' + c.whole_project_paste.bytes.toLocaleString() + " bytes, " + c.whole_project_paste.files + ' files</div></div>' +
      '<div><div class="small muted">Budget</div><div class="stat">' + esc(p.budget) + '</div><div class="small muted">' + esc(p.size.count_method) + "</div></div></div>";
    if (p.overflow) html += '<div class="warn"><strong>Required context does not fit.</strong> ' + esc(p.overflow.message) + "</div>";
    if (p.redactions.length) html += '<div class="warn"><strong>' + p.redactions.length + " value(s) redacted before export:</strong> " + esc(p.redactions.map(function (r) { return r.type + (r.line ? " (line " + r.line + ")" : ""); }).join(", ")) + ". The regex check has limits; review the text yourself.</div>";
    if (p.injection_warnings.length) html += '<div class="warn"><strong>Instruction-like text found in project content.</strong> It is fenced as untrusted data in the package: ' + esc(p.injection_warnings.map(function (w) { return w.path + ":" + w.line; }).join(", ")) + "</div>";
    html += '<details><summary><strong>Included (' + p.context.items.length + ") and not included (" + p.context.excluded.length + ')</strong></summary><div class="table-wrap"><table><thead><tr><th>File</th><th>Mode</th><th>Lines</th><th>~Tokens</th><th>Why</th></tr></thead><tbody>' +
      p.context.items.map(function (i) { return '<tr><td class="mono small">' + esc(i.path) + "</td><td>" + esc(i.mode) + (i.required ? ' <span class="tag">required</span>' : "") + "</td><td>" + esc(i.lines) + "</td><td>" + i.tokens + "</td><td>" + esc(i.reason) + ' <button class="linkbtn small" data-wf="pkg-exclude" data-path="' + esc(i.path) + '">remove</button></td></tr>'; }).join("") +
      p.context.excluded.slice(0, 30).map(function (i) { return '<tr><td class="mono small muted">' + esc(i.path) + '</td><td class="muted">not included</td><td></td><td>' + (i.tokens || "") + "</td><td>" + esc(i.reason) + "</td></tr>"; }).join("") + "</tbody></table></div><div class=\"row\" style=\"margin-top:.5rem\"><input type=\"text\" id=\"p-add\" placeholder=\"Add a file by relative path\" style=\"max-width:360px\"><button class=\"btn ghost small\" data-wf=\"pkg-include\">Add file</button>" + (W.excl.length ? '<span class=\"small muted\">Removed by you: ' + esc(W.excl.join(", ")) + ' <button class=\"linkbtn small\" data-wf=\"pkg-reset\">undo</button></span>' : "") + "</div></details>" +
      '<p class="small"><strong>' + esc(p.notice) + '</strong></p><pre class="prompt" id="p-text">' + esc(p.text) + "</pre>" +
      '<label class="small" style="font-weight:400"><input type="checkbox" id="p-reviewed"> I reviewed this text and it contains no customer data or secrets.</label>' +
      '<div class="row"><button class="btn" data-wf="copy-pkg"' + (p.exportable ? "" : " disabled") + '>Copy work package</button><button class="btn ghost" data-wf="download-pkg"' + (p.exportable ? "" : " disabled") + '>Download .md</button><button class="btn ghost" data-wf="go" data-step="6">Continue to evidence</button></div>';
    document.getElementById("p-out").innerHTML = html;
  }
  function reviewed() {
    if (!document.getElementById("p-reviewed").checked) { C().toast("Tick the review box first"); return false; }
    return true;
  }

  // ------------------------------------------------------------------ 6 evidence
  function stepEvidence(body) {
    var j = W.j, defect = j.workflow.id === "uat-defect";
    var html = '<div class="panel stack"><h2>6. Evidence</h2><p class="small muted">Static checks never run your code. Tests run only when you approve each run. Missing tools show as "not checked", never as passing.</p>' +
      '<div class="row"><button class="btn" data-wf="checks">Run local checks</button><label class="small" style="font-weight:400"><input type="checkbox" id="e-tests"> Also run the project\'s tests (executes project code; only for code you trust)</label></div>';
    if (defect) {
      html += '<div class="panel stack"><h3>Verify a fix</h3><p class="small muted">Paste the fix as a unified diff. Compass runs your tests on temporary copies: once with only the diff\'s test changes (to reproduce) and once with the full fix. Your files are never changed.</p>' +
        '<div class="row" id="e-sample-diffs"></div><textarea id="e-diff" placeholder="--- a/...&#10;+++ b/..."></textarea>' +
        '<div class="row"><button class="btn" data-wf="verify">Verify this fix (runs tests on copies)</button><button class="btn ghost" data-wf="import-diff-only">Import diff only, without running</button></div></div>';
    }
    html += '<details class="panel"><summary><strong>Import a report instead</strong></summary><div class="stack" style="margin-top:.5rem"><div class="grid2"><div><label for="e-kind">Report type</label><select id="e-kind"><option value="junit">JUnit XML (Maven, Gradle, pytest, jest-junit)</option><option value="unittest">Python unittest output (-v)</option><option value="gitleaks">gitleaks JSON</option><option value="semgrep">Semgrep JSON</option><option value="spectral">Spectral JSON</option><option value="diff">Unified diff</option></select></div>' +
      '<div><label for="e-label">This run is</label><select id="e-label"><option value="imported">the latest result</option><option value="before">before the fix</option><option value="after">after the fix</option></select></div></div>' +
      '<input type="file" id="e-file"><textarea id="e-text" placeholder="Or paste the report here"></textarea><div class="row"><button class="btn ghost" data-wf="import">Import</button></div></div></details>' +
      '<div id="e-checks"></div>' + nextBtn(7, "See result and lesson") + "</div>";
    body.innerHTML = html;
    renderChecks();
    if (defect && /py-login-service/.test(j.project)) {
      document.getElementById("e-sample-diffs").innerHTML = '<span class="small muted">Synthetic sample fixes:</span><button class="btn ghost small" data-wf="load-diff" data-path="fixes/fix-no-repro.diff">Fix without a test</button><button class="btn ghost small" data-wf="load-diff" data-path="fixes/fix-with-repro.diff">Fix with a regression test</button>';
    }
    document.getElementById("e-file").addEventListener("change", function (ev) {
      var f = ev.target.files[0]; if (!f) return; var rd = new FileReader();
      rd.onload = function () { document.getElementById("e-text").value = rd.result; }; rd.readAsText(f);
    });
  }
  function renderChecks() {
    var el = document.getElementById("e-checks"); if (!el) return;
    var checks = W.j.checks || [];
    if (!checks.length) { el.innerHTML = '<div class="empty">No evidence yet.</div>'; return; }
    el.innerHTML = '<div class="table-wrap"><table><thead><tr><th>Check</th><th>Tool</th><th>Status</th><th>Findings</th><th>Coverage and detail</th></tr></thead><tbody>' +
      checks.map(function (c) {
        return "<tr><td>" + esc(c.title) + '</td><td class="small">' + esc(c.tool) + (c.tool_version ? " " + esc(c.tool_version) : "") + "</td><td>" + pill(c.status) + "</td><td>" +
          (c.findings.length ? "<details><summary>" + c.findings.length + "</summary><ul class=\"small\">" + c.findings.map(function (f) {
            return "<li>" + (f.location && f.location.path ? '<button class="linkbtn mono" data-wf="open-file" data-path="' + esc(f.location.path) + '" data-line="' + (f.location.line || 1) + '">' + esc(f.location.path + (f.location.line ? ":" + f.location.line : "")) + "</button> " : "") +
              esc(f.rule) + ' <span class="tag plain">' + esc(f.claim_state) + "</span><br>" + esc(f.evidence) + '<br><span class="muted">' + esc(f.next_action) + "</span></li>";
          }).join("") + "</ul></details>" : "0") + '</td><td class="small muted">' + esc(c.detail || c.coverage || "") + "</td></tr>";
      }).join("") + "</tbody></table></div>";
  }

  // ------------------------------------------------------------------ 7 result
  function stepResult(body) {
    var v = W.j.verdict;
    body.innerHTML = '<div class="panel stack"><h2>7. Result and lesson</h2><div class="spread"><div class="stat passfail ' + (/^Accepted/.test(v.overall) ? "ok" : /^Not accepted/.test(v.overall) ? "no" : "") + '">' + esc(v.overall) + "</div>" +
      '<div class="small muted">' + v.counts.passed + " passed &middot; " + v.counts.failed + " failed &middot; " + v.counts["not-checked"] + ' not checked</div></div>' +
      '<div class="table-wrap"><table><thead><tr><th>Acceptance criterion</th><th>Status</th><th>Evidence</th></tr></thead><tbody>' + v.acceptance.map(function (r) {
        return "<tr><td><strong>" + esc(r.id) + "</strong> " + esc(r.text) + "</td><td>" + pill(r.status) + '</td><td class="small">' + esc(r.evidence) + (r.next_action ? '<br><span class="muted">Next: ' + esc(r.next_action) + "</span>" : "") + "</td></tr>";
      }).join("") + "</tbody></table></div>" +
      '<div class="panel" style="border-left:4px solid var(--sea)"><h3>Next action</h3><p>' + esc(v.next_action) + "</p></div>" +
      '<div class="panel" style="border-left:4px solid var(--amber)"><h3>One lesson to keep</h3><p>' + esc(v.lesson) + "</p>" +
      (v.exercise ? '<details><summary>Try it yourself</summary><p>' + esc(v.exercise.prompt) + '</p><p class="small muted">Hint: ' + esc(v.exercise.answer_hint) + "</p></details>" : "") + "</div>" +
      '<p class="small muted">' + esc(v.honesty) + '</p><div class="row"><button class="btn ghost" data-wf="reset">Start a new task</button><button class="btn ghost" data-wf="delete">Delete this journey now</button></div></div>';
  }

  function refresh(next) {
    C().api("GET", "/api/wf/state?id=" + W.j.id).then(function (j) { W.j = j; if (next) goStep(next); else goStep(W.step); });
  }

  // ------------------------------------------------------------------ setup
  function setupView() {
    C().api("GET", "/api/setup").then(function (d) {
      W.setup = d.settings; var s = d.settings, q = d.questions;
      var tools = q[0].options;
      var html = '<h1>Setup</h1><p class="lead">Eight questions so Compass fits your environment. Saved on this computer in var/settings.json. No secrets are saved.</p><div class="stack">' +
        '<div class="panel"><h2>1. ' + esc(q[0].text) + '</h2><div class="tool-options">' + tools.map(function (t) { return '<label class="tool-opt"><input type="checkbox" data-s-tool="' + t[0] + '"' + (s.approved_tools[t[0]] ? " checked" : "") + "> " + esc(t[1]) + "</label>"; }).join("") + "</div></div>" +
        '<div class="panel"><h2>2. ' + esc(q[1].text) + '</h2><div class="tool-options">' + tools.map(function (t) { return '<label class="tool-opt"><input type="checkbox" data-s-code="' + t[0] + '"' + (s.tools_see_internal_code[t[0]] ? " checked" : "") + "> " + esc(t[1]) + "</label>"; }).join("") + "</div></div>" +
        '<div class="panel"><h2>3. ' + esc(q[2].text) + '</h2><label for="s-roots">One absolute folder per line</label><textarea id="s-roots">' + esc(s.allowed_roots.join("\n")) + '</textarea><label for="s-default">Default project folder</label><input type="text" id="s-default" value="' + esc(s.default_project) + '"><p class="small muted">Whole drives and your home folder are refused. Credential folders (.ssh, .aws) are never read.</p></div>' +
        '<div class="panel"><h2>4. ' + esc(q[3].text) + '</h2><div class="grid2"><div><label for="s-jmode">Mode</label><select id="s-jmode"><option value="off">Off (paste or CSV import)</option><option value="cloud">Jira Cloud</option><option value="datacenter">Jira Data Center / Server</option></select></div>' +
        '<div><label for="s-jurl">Base URL (https)</label><input type="text" id="s-jurl" value="' + esc(s.jira.base_url) + '" placeholder="https://jira.example.com"></div>' +
        '<div><label for="s-jemail">Account email (Cloud only)</label><input type="text" id="s-jemail" value="' + esc(s.jira.email) + '"></div>' +
        '<div><label for="s-jac">Acceptance-criteria field (optional)</label><input type="text" id="s-jac" value="' + esc(s.jira.acceptance_field) + '" placeholder="customfield_12345"></div>' +
        '<div><label for="s-jenv">Token environment variable</label><input type="text" id="s-jenv" value="' + esc(s.jira.token_env) + '"><p class="small muted">Token present now: ' + (s.jira.token_present ? "yes" : "no") + '. The token is never saved by Compass.</p></div>' +
        '<div><label class="small" style="font-weight:400"><input type="checkbox" id="s-japproved"' + (s.jira.approved ? " checked" : "") + '> My organization allows read-only API access to this Jira.</label></div></div></div>' +
        '<div class="panel"><h2>5. ' + esc(q[4].text) + '</h2><p class="small muted">Compass records each binary\'s path, version and SHA-256 when you approve it, and refuses to run it if the file changes. Install tools only through your approved process.</p><div class="stack">' +
        ["gitleaks", "semgrep", "spectral"].map(function (n) {
          var r = s.scanners[n] || {};
          return '<div class="row"><strong style="min-width:90px">' + n + '</strong><input type="text" data-s-scan="' + n + '" value="' + esc(r.path || "") + '" placeholder="path to ' + n + ' (or leave empty to search PATH)" style="max-width:420px"><button class="btn ghost small" data-wf="scan-find" data-name="' + n + '">Find</button><button class="btn ghost small" data-wf="scan-approve" data-name="' + n + '">Approve</button><span class="small muted" id="scan-' + n + '">' + (r.approved ? "approved: " + esc(r.version) : "not approved") + "</span></div>";
        }).join("") + "</div></div>" +
        '<div class="panel"><h2>6. ' + esc(q[5].text) + '</h2><label class="small" style="font-weight:400"><input type="checkbox" id="s-tests"' + (s.allow_test_execution ? " checked" : "") + "> Yes, offer it. I will still approve each run.</label></div>" +
        '<div class="panel"><h2>7. ' + esc(q[6].text) + '</h2><select id="s-budget"><option value="lean">Lean (~4,000)</option><option value="balanced">Balanced (~8,000)</option><option value="deep">Deep (~16,000)</option></select><label for="s-dclass" style="margin-top:.5rem">Default data class</label><select id="s-dclass"><option value="synthetic">Synthetic or public only</option><option value="internal">Internal, no customer data</option><option value="restricted">Customer, personal or secret data</option></select></div>' +
        '<div class="panel"><h2>8. ' + esc(q[7].text) + '</h2><label class="small" style="font-weight:400"><input type="checkbox" id="s-cache"' + (s.cache_enabled ? " checked" : "") + "> Allow the cache (clears when turned off)</label></div>" +
        '<div class="row"><button class="btn" data-wf="save-setup">Save setup</button><button class="btn ghost" data-wf="doctor">Run a setup check</button></div><pre class="prompt" id="s-doctor" hidden></pre></div>';
      C().view(html);
      document.getElementById("s-jmode").value = s.jira.mode; document.getElementById("s-budget").value = s.context_budget; document.getElementById("s-dclass").value = s.default_data_class;
    }).catch(function (e) { C().toast(e.message); });
  }
  function saveSetup() {
    var at = {}, code = {};
    document.querySelectorAll("[data-s-tool]").forEach(function (el) { at[el.getAttribute("data-s-tool")] = el.checked; });
    document.querySelectorAll("[data-s-code]").forEach(function (el) { code[el.getAttribute("data-s-code")] = el.checked; });
    var body = { approved_tools: Object.assign({ no_ai: true }, at), tools_see_internal_code: code,
      allowed_roots: document.getElementById("s-roots").value.split("\n").map(function (x) { return x.trim(); }).filter(Boolean),
      default_project: document.getElementById("s-default").value.trim(),
      jira: { mode: document.getElementById("s-jmode").value, base_url: document.getElementById("s-jurl").value.trim(), email: document.getElementById("s-jemail").value.trim(),
        acceptance_field: document.getElementById("s-jac").value.trim(), token_env: document.getElementById("s-jenv").value.trim() || "COMPASS_JIRA_TOKEN", approved: document.getElementById("s-japproved").checked },
      allow_test_execution: document.getElementById("s-tests").checked, context_budget: document.getElementById("s-budget").value,
      default_data_class: document.getElementById("s-dclass").value, cache_enabled: document.getElementById("s-cache").checked, setup_complete: true };
    C().api("POST", "/api/setup", body).then(function () { C().toast("Setup saved"); }).catch(function (e) { C().toast(e.message); });
  }

  // ------------------------------------------------------------------ catalog
  function catalogView() {
    Promise.all([C().api("GET", "/api/catalog/tools"), C().api("GET", "/api/catalog/capabilities")]).then(function (r) {
      var reg = r[0], caps = r[1];
      var cats = ["all", "workflow", "security", "context", "testing", "host-model"];
      var html = '<h1>Tool catalog</h1><p class="lead">The assistants you may hand work to, and the open-source tools Compass reviewed. Everything in the reviewed list starts inactive until approved through your enterprise process.</p>' +
        '<div class="panel"><h2>Approved assistants (editable in Setup)</h2><div class="table-wrap"><table><thead><tr><th>Tool</th><th>Approved</th><th>Allowed data</th><th>Good for</th><th>Limits</th></tr></thead><tbody>' +
        caps.tools.map(function (t) { return "<tr><td><strong>" + esc(t.label) + "</strong></td><td>" + (t.approved ? "yes" : "no") + "</td><td>" + esc(t.allowed_data.join(", ")) + '</td><td class="small">' + esc(t.capabilities.join(", ").replace(/-/g, " ")) + '</td><td class="small muted">' + esc(t.limits.join("; ")) + "</td></tr>"; }).join("") +
        '</tbody></table></div></div><div class="panel" style="margin-top:1rem"><div class="spread"><h2>Reviewed open-source candidates (' + reg.tools.length + ')</h2><select id="cat-filter" style="width:auto">' + cats.map(function (c) { return '<option value="' + c + '">' + c + "</option>"; }).join("") + '</select></div><p class="small muted">' + esc(reg.note) + ' Revisions and licenses were checked on ' + esc(reg.generated) + '.</p><div class="table-wrap"><table id="cat-table"><thead><tr><th>Tool</th><th>Category</th><th>Status</th><th>License</th><th>Revision</th><th>Proposed use</th><th>Notes</th></tr></thead><tbody>' +
        reg.tools.map(function (t) {
          return '<tr data-cat="' + esc(t.category) + '"><td><a href="' + esc(t.repository_url) + '" target="_blank" rel="noopener">' + esc(t.name) + "</a></td><td>" + esc(t.category) + "</td><td>" + esc(t.integration_status.replace(/-/g, " ")) + '<br><span class="tag plain">inactive</span></td><td class="small">' + esc(t.license.code_spdx || t.license.rules_or_content_license || "") +
            '</td><td class="mono small">' + esc((t.reviewed_revision.latest_release_tag || "") + " " + (t.reviewed_revision.commit || "").slice(0, 10)) + '</td><td class="small">' + esc(t.proposed_use) + '</td><td class="small muted">' + esc(t.review_notes) + "</td></tr>";
        }).join("") + "</tbody></table></div></div>";
      C().view(html);
      document.getElementById("cat-filter").addEventListener("change", function (ev) {
        var v = ev.target.value;
        document.querySelectorAll("#cat-table tbody tr").forEach(function (tr) { tr.hidden = v !== "all" && tr.getAttribute("data-cat") !== v; });
      });
    }).catch(function (e) { C().toast(e.message); });
  }

  // ------------------------------------------------------------------ events
  document.addEventListener("click", function (ev) {
    var t = ev.target.closest("[data-wf]");
    if (!t) return;
    var a = t.getAttribute("data-wf"), api = C().api;
    if (a === "go") goStep(+t.getAttribute("data-step"));
    else if (a === "reset") { W.j = null; W.pkg = null; W.rec = null; W.query = {}; W.incl = []; W.excl = []; goStep(1); }
    else if (a === "start") start();
    else if (a === "sample") {
      var s = W.samples[+t.getAttribute("data-i")];
      document.getElementById("wf-goal").value = s.text;
      var sel = document.getElementById("wf-project"); sel.value = s.project_path;
      var r = document.querySelector('input[name="wf-kind"][value="' + s.workflow + '"]'); if (r) r.checked = true;
      guess(); C().toast("Loaded synthetic sample: " + s.title);
    }
    else if (a === "jira-fetch") jiraFetch();
    else if (a === "jira-mine") api("POST", "/api/jira/search", { token: jiraToken() }).then(function (d) {
      document.getElementById("wf-jira-list").innerHTML = d.issues.length ? d.issues.map(function (i) { return '<button class="persona" data-wf="jira-pick" data-key="' + esc(i.key) + '"><strong>' + esc(i.key) + "</strong> " + esc(i.summary) + "</button>"; }).join("") : '<p class="small muted">No matching issues.</p>';
    }).catch(function (e) { C().toast(e.message); });
    else if (a === "jira-pick") { document.getElementById("wf-jira-key").value = t.getAttribute("data-key"); jiraFetch(); }
    else if (a === "confirm") {
      var f = t.getAttribute("data-fact"), inp = document.querySelector('[data-fact-input="' + f + '"]');
      api("POST", "/api/wf/fact", { id: W.j.id, fact: f, value: inp ? inp.value : null }).then(function (j) { W.j = j; goStep(2); }).catch(function (e) { C().toast(e.message); });
    }
    else if (a === "answer" || a === "skip") {
      var ans = {}; document.querySelectorAll("[data-wf-q]").forEach(function (el) { if (el.value.trim() && a === "answer") ans[el.getAttribute("data-wf-q")] = el.value; });
      api("POST", "/api/wf/answer", { id: W.j.id, answers: ans, skip: a === "skip" ? [t.getAttribute("data-q")] : [] }).then(function (j) { W.j = j; goStep(3); }).catch(function (e) { C().toast(e.message); });
    }
    else if (a === "recommend") recommend();
    else if (a === "choose") { var c = document.querySelector('input[name="t-choice"]:checked'); if (c) recommend(c.value); }
    else if (a === "package") buildPkg();
    else if (a === "pkg-exclude") { var px = t.getAttribute("data-path"); if (W.excl.indexOf(px) < 0) W.excl.push(px); W.incl = W.incl.filter(function (x) { return x !== px; }); buildPkg(); }
    else if (a === "pkg-include") { var pi = document.getElementById("p-add").value.trim(); if (pi) { W.incl.push(pi); W.excl = W.excl.filter(function (x) { return x !== pi; }); buildPkg(); } }
    else if (a === "pkg-reset") { W.excl = []; buildPkg(); }
    else if (a === "copy-pkg") { if (reviewed()) C().copy(W.pkg.text); }
    else if (a === "download-pkg") {
      if (!reviewed()) return;
      var blob = new Blob([W.pkg.text], { type: "text/markdown" }), url = URL.createObjectURL(blob), link = document.createElement("a");
      link.href = url; link.download = "work-package-" + W.j.workflow.id + ".md"; document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url);
    }
    else if (a === "checks") api("POST", "/api/wf/checks", { id: W.j.id, approve_tests: document.getElementById("e-tests").checked }).then(function (j) { W.j = j; renderChecks(); C().toast("Checks finished"); }).catch(function (e) { C().toast(e.message); });
    else if (a === "import") {
      api("POST", "/api/wf/import", { id: W.j.id, kind: document.getElementById("e-kind").value, label: document.getElementById("e-label").value, text: document.getElementById("e-text").value })
        .then(function (j) { W.j = j; renderChecks(); C().toast("Imported"); }).catch(function (e) { C().toast(e.message); });
    }
    else if (a === "load-diff") api("GET", "/api/wf/file?id=" + W.j.id + "&path=" + encodeURIComponent(t.getAttribute("data-path"))).then(function (f) { document.getElementById("e-diff").value = f.lines.join("\n") + "\n"; });
    else if (a === "verify") api("POST", "/api/wf/verify-fix", { id: W.j.id, diff: document.getElementById("e-diff").value, approve_tests: true }).then(function (j) { W.j = j; renderChecks(); C().toast("Fix verified on temporary copies"); }).catch(function (e) { C().toast(e.message); });
    else if (a === "import-diff-only") api("POST", "/api/wf/import", { id: W.j.id, kind: "diff", text: document.getElementById("e-diff").value }).then(function (j) { W.j = j; renderChecks(); C().toast("Diff imported without running tests"); }).catch(function (e) { C().toast(e.message); });
    else if (a === "delete") api("POST", "/api/wf/delete", { id: W.j.id }).then(function () { W.j = null; W.pkg = null; goStep(1); C().toast("Journey deleted"); });
    else if (a === "open-file") {
      var path = t.getAttribute("data-path"), line = +t.getAttribute("data-line");
      api("GET", "/api/wf/file?id=" + W.j.id + "&path=" + encodeURIComponent(path)).then(function (f) {
        C().openModal(path, '<pre class="prompt">' + f.lines.map(function (l, i) { return '<span class="' + (i + 1 === line ? "hl" : "") + '">' + String(i + 1).padStart(4, " ") + "  " + esc(l) + "</span>"; }).join("\n") + "</pre>");
        var h = document.querySelector("#modal .hl"); if (h) h.scrollIntoView({ block: "center" });
      }).catch(function (e) { C().toast(e.message); });
    }
    else if (a === "save-setup") saveSetup();
    else if (a === "doctor") api("GET", "/api/doctor").then(function (d) { var el = document.getElementById("s-doctor"); el.hidden = false; el.textContent = JSON.stringify(d, null, 2); });
    else if (a === "scan-find" || a === "scan-approve") {
      var n = t.getAttribute("data-name"), p = document.querySelector('[data-s-scan="' + n + '"]').value.trim();
      api("POST", a === "scan-find" ? "/api/scanners/discover" : "/api/scanners/approve", { name: n, path: p || null, approve: true }).then(function (d) {
        var r = d.scanner || d;
        document.getElementById("scan-" + n).textContent = r.found === false ? "not found" : ((a === "scan-approve" ? "approved: " : "found: ") + (r.version || "") + " sha256 " + (r.sha256 || "").slice(0, 12));
        if (r.path) document.querySelector('[data-s-scan="' + n + '"]').value = r.path;
      }).catch(function (e) { C().toast(e.message); });
    }
  });

  window.CompassRoutes = {
    "#/workflow": { view: workflowView, roles: ["engineer", "enablement", "manager", "leader"] },
    "#/setup": { view: setupView },
    "#/catalog": { view: catalogView }
  };
})();
