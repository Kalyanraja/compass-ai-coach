/* Compass web client. Vanilla JS, no build step, no external requests. */
(function () {
  "use strict";
  var esc = Charts.esc;
  var state = { token: null, role: null, display: null, coaching: null, analysis: null, coachText: "", jira: [] };

  // ---------------------------------------------------------------- session storage (best effort)
  try {
    var saved = JSON.parse(sessionStorage.getItem("compass.session") || "null");
    if (saved) { state.token = saved.token; state.role = saved.role; state.display = saved.display; }
  } catch (e) { /* storage unavailable: session lives in memory */ }
  function persist() {
    try { sessionStorage.setItem("compass.session", JSON.stringify({ token: state.token, role: state.role, display: state.display })); } catch (e) {}
  }

  // ---------------------------------------------------------------- api
  function api(method, path, body) {
    var headers = { "Content-Type": "application/json" };
    if (state.token) headers.Authorization = "Bearer " + state.token;
    return fetch(path, { method: method, headers: headers, body: body ? JSON.stringify(body) : undefined })
      .then(function (r) {
        return r.json().then(function (j) {
          if (r.status === 401) { signOut(true); }
          if (!r.ok) throw new Error(j.error || ("Request failed (" + r.status + ")"));
          return j;
        });
      });
  }

  // ---------------------------------------------------------------- helpers
  var $main = document.getElementById("main");
  function view(html) { $main.innerHTML = html; $main.focus({ preventScroll: true }); window.scrollTo(0, 0); }
  function toast(msg) {
    var t = document.getElementById("toast"); t.textContent = msg; t.classList.add("show");
    clearTimeout(toast._t); toast._t = setTimeout(function () { t.classList.remove("show"); }, 2200);
  }
  function fail(e) { view('<div class="panel"><h2>Something went wrong</h2><p>' + esc(e.message) + '</p><p><a href="#/">Return to sign-in</a></p></div>'); }
  function lockIcon() { return '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="2"/></svg>'; }
  function privacyBar(text, sub) { return '<div class="privacy">' + lockIcon() + '<div>' + esc(text) + (sub ? '<div class="muted small">' + esc(sub) + '</div>' : '') + '</div></div>'; }
  function toolName(id) { return { copilot: "GitHub Copilot", claude: "Claude Code", devin: "Devin", writing: "Writing assistant", no_ai: "No AI needed" }[id] || id; }
  function copy(text) {
    if (navigator.clipboard && window.isSecureContext !== false) {
      navigator.clipboard.writeText(text).then(function () { toast("Copied to clipboard"); }, fallback);
    } else { fallback(); }
    function fallback() {
      var ta = document.createElement("textarea"); ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); toast("Copied to clipboard"); } catch (e) { toast("Select the text and copy it manually"); }
      document.body.removeChild(ta);
    }
  }
  function openModal(title, html) {
    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-body").innerHTML = html;
    document.getElementById("modal").hidden = false;
    document.querySelector("#modal [data-close]").focus();
  }
  function closeModal() { document.getElementById("modal").hidden = true; }

  // ---------------------------------------------------------------- nav
  var NAV = {
    engineer: [["#/coach", "My coaching"], ["#/workflow", "Workflow coach"], ["#/practices", "Practices"], ["#/mydata", "My data"], ["#/catalog", "Tool catalog"], ["#/setup", "Setup"], ["#/trust", "How it works"]],
    manager: [["#/team", "Team insights"], ["#/workflow", "Workflow coach"], ["#/practices", "Practices"], ["#/trust", "How it works"]],
    leader: [["#/org", "Portfolio insights"], ["#/practices", "Practices"], ["#/catalog", "Tool catalog"], ["#/trust", "How it works"]],
    enablement: [["#/enable", "Enablement"], ["#/workflow", "Workflow coach"], ["#/catalog", "Tool catalog"], ["#/practices", "Practices"], ["#/setup", "Setup"], ["#/trust", "How it works"]]
  };
  function renderNav() {
    var links = state.role ? NAV[state.role] : [["#/setup", "Setup"], ["#/catalog", "Tool catalog"], ["#/trust", "How it works"]];
    var cur = (location.hash || "#/").split("?")[0];
    document.getElementById("nav").innerHTML = links.map(function (l) {
      return '<a href="' + l[0] + '"' + (cur === l[0] ? ' aria-current="page"' : "") + ">" + esc(l[1]) + "</a>";
    }).join("");
    document.getElementById("who").innerHTML = state.role
      ? '<span>Signed in as <strong>' + esc(state.display) + '</strong></span><button class="btn ghost small" data-action="signout">Switch role</button>'
      : '<span class="small">Demo with synthetic data</span>';
  }
  function signOut(silent) {
    state.token = state.role = state.display = null; state.coaching = null; persist();
    if (!silent) location.hash = "#/";
  }

  // ---------------------------------------------------------------- sign-in
  function signInView() {
    api("GET", "/api/demo/personas").then(function (d) {
      var byTeam = {};
      d.engineers.forEach(function (e) { (byTeam[e.team_name] = byTeam[e.team_name] || []).push(e); });
      var featured = d.engineers.filter(function (e) { return d.featured.indexOf(e.engineer_id) >= 0; });
      function card(e, f) {
        return '<button class="persona' + (f ? " featured" : "") + '" data-action="login" data-role="engineer" data-subject="' + esc(e.engineer_id) + '">' +
          '<strong>' + esc(e.codename) + '</strong><div class="small muted">' + esc(e.role) + '</div><div class="small">' + esc(e.stack_label) + ' &middot; ' + esc(e.team_name) + '</div></button>';
      }
      view(
        '<section class="hero"><div><h1>Get more from the AI tools you already have</h1>' +
        '<p class="lead">Compass reads workflow signals, suggests one next step at a time, and writes the prompt for the right tool. Your coaching stays private. Leaders only see team patterns.</p>' +
        privacyBar("Enablement, not evaluation", "No scores, rankings or labels for people. Recommendations, feedback and history are visible only to the engineer.") +
        '</div>' + rose() + '</section>' +
        '<div id="setup-banner"></div><h2>Choose how you sign in</h2><p class="muted small">Demo sign-in with synthetic personas. A real deployment uses your enterprise single sign-on.</p>' +
        '<div class="choices">' +
        '<button class="choice" data-action="show-engineers"><h3>Engineer</h3><p class="small muted">Private coaching, prompt coach and practice library.</p></button>' +
        '<div class="choice"><h3>Engineering manager</h3><p class="small muted">Team patterns and enablement opportunities, never individuals.</p><select aria-label="Choose team" id="mgr-team">' +
        d.teams.map(function (t) { return '<option value="' + esc(t.team_id) + '">' + esc(t.name) + ' (' + esc(t.domain) + ')</option>'; }).join("") +
        '</select><div style="margin-top:.6rem"><button class="btn small" data-action="login-manager">Open team view</button></div></div>' +
        '<button class="choice" data-action="login" data-role="leader"><h3>Engineering leader</h3><p class="small muted">Portfolio-level adoption patterns and reusable practices.</p></button>' +
        '<button class="choice" data-action="login" data-role="enablement"><h3>AI enablement team</h3><p class="small muted">Practice catalog, quality evaluation, compliance and access audit.</p></button>' +
        '</div>' +
        '<section id="engineers" hidden style="margin-top:2rem"><h2>Pick an engineer persona</h2>' +
        '<p class="muted small">Suggested for the demo:</p><div class="persona-list">' + featured.map(function (e) { return card(e, true); }).join("") + '</div>' +
        '<div class="stack" style="margin-top:1rem">' + Object.keys(byTeam).sort().map(function (t) {
          return '<details class="team"><summary>' + esc(t) + ' (' + byTeam[t].length + ' personas)</summary><div class="persona-list">' + byTeam[t].map(function (e) { return card(e); }).join("") + "</div></details>";
        }).join("") + '</div></section>'
      );
      setupBanner();
    }).catch(fail);
  }
  function rose() {
    return '<svg class="rose" viewBox="0 0 200 200" aria-hidden="true">' +
      '<circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-opacity=".25" stroke-width="1.5"/>' +
      '<circle cx="100" cy="100" r="70" fill="none" stroke="currentColor" stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="2 5"/>' +
      '<path d="M100 14 L112 100 L100 186 L88 100Z" fill="currentColor" fill-opacity=".9"/>' +
      '<path d="M14 100 L100 88 L186 100 L100 112Z" fill="currentColor" fill-opacity=".35"/>' +
      '<path d="M100 14 L112 100 L100 100Z" fill="var(--amber)"/>' +
      '<text x="100" y="10" text-anchor="middle" font-size="11" fill="currentColor">Observe</text>' +
      '<text x="196" y="104" text-anchor="end" font-size="11" fill="currentColor">Act</text>' +
      '<text x="100" y="199" text-anchor="middle" font-size="11" fill="currentColor">Explain</text>' +
      '<text x="4" y="104" font-size="11" fill="currentColor">Measure</text></svg>';
  }
  function setupBanner() {
    api("GET", "/api/setup").then(function (d) {
      var el = document.getElementById("setup-banner");
      if (el && !d.settings.setup_complete) {
        el.innerHTML = '<div class="warn" style="margin-bottom:1rem"><strong>First run:</strong> answer 8 quick setup questions (about 2 minutes): which AI tools you may use, which project folders Compass may read, Jira, and local scanners. <a href="#/setup">Open setup</a></div>';
      }
    }).catch(function () {});
  }
  function login(role, subject) {
    api("POST", "/api/session", { role: role, subject: subject }).then(function (s) {
      state.token = s.token; state.role = s.role; state.display = s.display; persist();
      if (state.pendingDeepLink && (NEED[state.pendingDeepLink.split("?")[0]] || []).indexOf(role) >= 0) {
        var dl = state.pendingDeepLink; state.pendingDeepLink = null; location.hash = dl;
      } else { location.hash = NAV[role][0][0]; }
    }).catch(function (e) { toast(e.message); });
  }

  // ---------------------------------------------------------------- engineer: coaching
  function coachView() {
    api("GET", "/api/me/coaching").then(function (d) {
      state.coaching = d;
      var p = d.profile;
      var html = '<div class="spread"><div class="profile"><div class="avatar" aria-hidden="true">' + esc(p.codename[0]) + '</div><div>' +
        '<h1 style="margin:0">' + esc(p.codename) + '</h1><div class="facts"><span class="tag plain">' + esc(p.role) + '</span><span class="tag plain">' + esc(p.stack_label) +
        '</span><span class="tag plain">' + esc(p.project_complexity) + ' complexity</span><span class="tag plain">' + esc(p.team_name) + '</span></div></div></div>' +
        privacyBar("Only you can see this page", "Managers see team-level patterns only. Dismissals and feedback never leave your view.") + '</div>';
      if (d.progress.length) {
        html += '<section style="margin-top:1.25rem" class="stack">' + d.progress.map(function (g) {
          return '<div class="panel progress"><h3>Progress you made: ' + esc(g.practice_title) + '</h3><p>' + esc(g.text) +
            ' The pattern that triggered this recommendation in weeks 1-4 no longer appears.</p></div>';
        }).join("") + '</section>';
      }
      html += '<h2 style="margin-top:1.5rem">Your next best actions</h2><p class="muted small">Based on weeks ' + d.window_weeks[0] + '-' + d.window_weeks[1] +
        ' of synthetic workflow signals. Optional coaching: try what helps, dismiss what does not.</p><div class="stack" id="recs">' +
        (d.recommendations.length ? d.recommendations.map(recCard).join("") : '<div class="panel empty">No open recommendations. Restore a dismissed one below or explore the practice library.</div>') + '</div>';
      if (d.dismissed.length) {
        html += '<details class="panel" style="margin-top:1rem"><summary><strong>Dismissed (' + d.dismissed.length + ')</strong> <span class="muted small">only you see these</span></summary><div class="stack" style="margin-top:.75rem">' +
          d.dismissed.map(function (r) { return '<div class="spread"><span>' + esc(r.practice_title) + '</span><button class="btn ghost small" data-action="fb" data-key="' + esc(r.rec_key) + '" data-act="restored">Restore</button></div>'; }).join("") + '</div></details>';
      }
      html += '<h2 style="margin-top:1.75rem">Your signals over 8 weeks</h2><div class="grid3" id="trend"></div>';
      view(html);
      loadTrend();
    }).catch(fail);
  }

  function recCard(r) {
    var o = r.outcome_to_monitor;
    var kit = r.kit || {};
    return '<article class="rec" id="rec-' + esc(r.rec_key) + '">' +
      '<div class="rec-head spread"><div><div class="row small"><span class="tag">' + esc(r.practice_code) + '</span><span class="tag plain">' + esc(r.action_type) + ' action</span><span class="tag plain">' + esc(r.workflow.replace("_", " ")) + '</span>' +
      (r.my_feedback ? '<span class="tag amber">you marked: ' + esc(r.my_feedback.replace("_", " ")) + '</span>' : '') + '</div>' +
      '<h3 style="margin-top:.4rem">' + esc(r.practice_title) + '</h3></div>' +
      '<div class="tool-pill" title="Recommended tool">Use: ' + esc(r.recommended_tool.label) + '</div></div>' +
      '<div class="bearing">' +
      '<div><h4><span class="n">1</span>Observation</h4><p>' + esc(r.observation) + '</p></div>' +
      '<div class="action"><h4><span class="n">2</span>Suggested action</h4><p>' + esc(r.suggested_action) + '</p></div>' +
      '<div><h4><span class="n">3</span>Why</h4><p>' + esc(r.rationale) + '</p></div>' +
      '<div><h4><span class="n">4</span>Outcome to watch</h4><p>' + esc(o.text) + '</p></div></div>' +
      '<details class="rec-more"><summary>Evidence, sources and agent-kit files</summary>' +
      '<p class="small muted">Traceability: this recommendation was derived from these synthetic records.</p><div class="table-wrap"><table><thead><tr><th>Record</th><th>Week</th>' +
      Object.keys((r.evidence_records[0] || { values: {} }).values).map(function (k) { return "<th>" + esc(k) + "</th>"; }).join("") + '</tr></thead><tbody>' +
      r.evidence_records.map(function (e) { return '<tr><td class="mono">' + esc(e.record_id) + '</td><td>' + e.week + '</td>' + Object.keys(e.values).map(function (k) { return "<td>" + esc(e.values[k]) + "</td>"; }).join("") + "</tr>"; }).join("") +
      '</tbody></table></div><h4 style="margin-top:.75rem">Sources</h4><ul class="small">' + r.sources.map(function (s) { return '<li>' + esc(s.claim) + ' <a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.source) + '</a></li>'; }).join("") + '</ul>' +
      '<h4>Apply it with the agent kit</h4><div class="row">' + Object.keys(kit).map(function (k) { return '<button class="btn ghost small" data-action="kit" data-path="' + esc(kit[k]) + '">' + esc(toolName(k)) + ' file</button>'; }).join("") + '</div></details>' +
      '<div class="rec-foot"><div class="row">' +
      '<button class="btn small" data-action="simulate" data-practice="' + esc(r.practice_id) + '">Show before and after</button>' +
      '<button class="btn ghost small" data-action="fb" data-key="' + esc(r.rec_key) + '" data-act="tried">I tried this</button>' +
      '<button class="btn ghost small" data-action="fb" data-key="' + esc(r.rec_key) + '" data-act="useful" aria-pressed="' + (r.my_feedback === "useful") + '">Useful</button>' +
      '<button class="btn ghost small" data-action="fb" data-key="' + esc(r.rec_key) + '" data-act="not_useful" aria-pressed="' + (r.my_feedback === "not_useful") + '">Not useful</button></div>' +
      '<div class="row"><label class="small muted" for="why-' + esc(r.rec_key) + '" style="margin:0;font-weight:400">Dismiss because</label><select id="why-' + esc(r.rec_key) + '" style="width:auto"><option value="not_relevant">Not relevant</option><option value="already_doing">Already doing it</option><option value="not_now">Not now</option><option value="wrong_context">Wrong for my context</option><option value="too_generic">Too generic</option></select>' +
      '<button class="btn ghost small" data-action="dismiss" data-key="' + esc(r.rec_key) + '">Dismiss</button></div></div>' +
      '<div class="sim" id="sim-' + esc(r.rec_key) + '"></div></article>';
  }

  function loadTrend() {
    api("GET", "/api/me/trend").then(function (t) {
      var el = document.getElementById("trend"); if (!el) return;
      el.innerHTML = Object.keys(t.series).map(function (k) {
        var s = t.series[k], pct = /rate/.test(k);
        return '<div class="panel"><h3>' + esc(s.label) + '</h3><p class="small muted">' + (s.direction === "lower" ? "Lower is better" : "Higher is better") + '</p>' +
          Charts.line([{ points: s.points, cls: "actual" }], { width: 320, height: 170, pct: pct, label: s.label }) + "</div>";
      }).join("");
    });
  }

  function simulate(practice, key) {
    var box = document.getElementById("sim-" + key);
    if (box.innerHTML) { box.innerHTML = ""; return; }
    api("GET", "/api/me/simulate?practice=" + encodeURIComponent(practice)).then(function (s) {
      box.innerHTML = '<div style="padding:1rem 1.25rem;border-top:1px solid var(--line)"><h3>Before and after: ' + esc(s.practice_title) + '</h3><p class="small muted">' + esc(s.label) + '</p><div class="grid2">' +
        Object.keys(s.series).map(function (k) {
          var x = s.series[k], pct = /rate|share/.test(k);
          return '<div><h4>' + esc(x.label) + '</h4><div class="compare"><div><div class="small muted">Now (W5-8)</div><div class="v">' + esc(x.before_display) + '</div></div><div><div class="small muted">Simulated</div><div class="v after">' + esc(x.after_display) + '</div></div></div>' +
            Charts.line([{ points: x.actual, cls: "actual" }, { points: [x.actual[x.actual.length - 1]].concat(x.projected), cls: "proj" }], { width: 420, height: 190, pct: pct, divider: 8, label: x.label }) + "</div>";
        }).join("") + '</div><div class="legend"><span><i></i>Synthetic actuals</span><span><i class="p"></i>Simulated with practice</span></div></div>';
    }).catch(function (e) { toast(e.message); });
  }

  function feedback(key, act, reason) {
    api("POST", "/api/me/feedback", { rec_key: key, action: act, reason: reason || null }).then(function () {
      toast({ dismissed: "Dismissed. Only you can see this.", restored: "Restored", useful: "Saved privately: useful", not_useful: "Saved privately: not useful", tried: "Nice. Watch the outcome signal over 2 weeks." }[act]);
      coachView();
    }).catch(function (e) { toast(e.message); });
  }

  // ---------------------------------------------------------------- my data
  function myDataView() {
    api("GET", "/api/me/history").then(function (h) {
      view('<h1>My data</h1>' + privacyBar("Everything on this page is visible only to you", "Stored in a separate private store that the manager and leader views never read.") +
        '<div class="grid2" style="margin-top:1rem"><div class="panel"><h2>My feedback</h2>' +
        (h.feedback.length ? '<table><thead><tr><th>Recommendation</th><th>Action</th><th>Reason</th><th>When (UTC)</th></tr></thead><tbody>' + h.feedback.map(function (f) { return "<tr><td>" + esc(f.rec_key) + "</td><td>" + esc(f.action) + "</td><td>" + esc(f.reason || "") + "</td><td>" + esc(f.created_at) + "</td></tr>"; }).join("") + "</tbody></table>" : '<p class="muted">No feedback yet.</p>') +
        '</div><div class="panel"><h2>Coaching history</h2>' +
        (h.shown.length ? '<table><thead><tr><th>Recommendation</th><th>Times shown</th><th>Last shown</th></tr></thead><tbody>' + h.shown.map(function (s) { return "<tr><td>" + esc(s.rec_key) + "</td><td>" + s.times_shown + "</td><td>" + esc(s.last_shown) + "</td></tr>"; }).join("") + "</tbody></table>" : '<p class="muted">Nothing yet.</p>') +
        '</div></div><div class="panel" style="margin-top:1rem"><h2>Delete my coaching data</h2><p>Removes your feedback, dismissals and coaching history. Your recommendations are recalculated from synthetic signals next time.</p><button class="btn" data-action="forget">Delete my coaching data</button></div>');
    }).catch(fail);
  }

  // ---------------------------------------------------------------- prompt coach
  function promptView() {
    view('<p class="small"><a href="#/workflow">Back to the Workflow coach</a></p><h1>Quick prompt coach</h1><p class="lead">For tasks outside the three guided workflows (documents, emails, refactors, SQL, exploration). Paste a Jira story or describe the task. Compass checks what is missing, picks the right tool, and writes the prompt. Three steps.</p>' +
      '<div class="steps" id="steps"><span class="on">1. Paste the task</span><span>2. Answer up to 3 questions</span><span>3. Copy the prompt</span></div>' +
      privacyBar("Your text is processed in memory and never stored", "It is not logged and never appears in any manager or leader view. Remove secrets and customer data before using any AI tool.") +
      '<div class="grid2" style="margin-top:1rem;align-items:start"><div class="panel stack"><div><label for="coach-text">Story or task</label><textarea id="coach-text" placeholder="Example: Build REST API to create a service request. As a portal user I want to submit a request...">' + esc(state.coachText) + '</textarea></div>' +
      '<div class="row"><button class="btn" data-action="analyze">Check my task</button><button class="btn ghost" data-action="sample-jira">Load sample Jira stories</button>' +
      '<label class="btn ghost" style="margin:0">Import Jira CSV<input type="file" id="jira-file" accept=".csv,text/csv" hidden></label></div>' +
      '<p class="small muted">No Jira API needed: in Jira, export issues as CSV and import the file here.</p><div id="jira-list"></div></div>' +
      '<div id="coach-out" class="stack"><div class="panel empty">Your analysis appears here.</div></div></div>');
    document.getElementById("jira-file").addEventListener("change", function (ev) {
      var f = ev.target.files[0]; if (!f) return;
      var rd = new FileReader();
      rd.onload = function () { api("POST", "/api/coach/jira-csv", { csv: rd.result }).then(function (d) { showJira(d.issues); }).catch(function (e) { toast(e.message); }); };
      rd.readAsText(f);
    });
    if (state.jira.length) showJira(state.jira);
  }
  function showJira(issues) {
    state.jira = issues;
    var el = document.getElementById("jira-list");
    el.innerHTML = issues.length ? '<label>Pick a story</label><div class="stack">' + issues.map(function (i, n) {
      return '<button class="persona" data-action="pick-jira" data-i="' + n + '"><strong>' + esc(i.key) + '</strong> <span class="small muted">' + esc(i.issue_type) + '</span><div class="small">' + esc(i.summary) + "</div></button>";
    }).join("") + "</div>" : '<p class="muted">No issues found in that file.</p>';
  }
  function analyze() {
    var text = document.getElementById("coach-text").value;
    state.coachText = text;
    api("POST", "/api/coach/analyze", { text: text }).then(function (a) {
      state.analysis = a;
      setStep(2);
      var r = a.recommendation;
      var out = '<div class="panel"><div class="spread"><div><div class="small muted">Task type</div><h2>' + esc(a.task_label) + '</h2></div><div class="small muted">' + a.checklist.covered + ' of ' + a.checklist.total + ' brief elements present</div></div>' +
        '<ul class="check-list small">' + a.checklist.present.map(function (c) { return '<li class="yes">' + esc(c.label) + "</li>"; }).join("") + a.checklist.missing.map(function (c) { return '<li class="no">' + esc(c.label) + ' <span class="muted">missing</span></li>'; }).join("") + "</ul></div>";
      if (a.sensitive_data_warnings.length) out += '<div class="warn"><strong>Remove before sending to any AI tool:</strong> ' + esc(a.sensitive_data_warnings.join(", ")) + "</div>";
      if (a.anti_patterns.length) out += '<div class="panel"><h3>Coaching notes</h3><ul class="small">' + a.anti_patterns.map(function (x) { return "<li><strong>" + esc(x.name) + ":</strong> " + esc(x.note) + (x.fix ? ' <span class="muted">Fix: ' + esc(x.fix) + "</span>" : "") + "</li>"; }).join("") + "</ul></div>";
      out += '<div class="panel"><h3>Recommended: ' + esc(r.label) + '</h3><p class="small muted">' + esc(r.mode) + '</p><ul class="small">' + r.reasons.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" +
        '<div class="tool-options">' + [{ tool: r.tool, label: r.label }].concat(r.alternatives).map(function (t, i) {
          return '<label class="tool-opt"><input type="radio" name="tool" value="' + esc(t.tool) + '"' + (i === 0 ? " checked" : "") + "> " + esc(t.label) + (i === 0 ? ' <span class="tag">recommended</span>' : "") + "</label>";
        }).join("") + "</div></div>";
      if (a.questions.length) {
        out += '<div class="panel stack"><h3>Answer what you can (optional)</h3>' + a.questions.map(function (q) {
          return '<div><label for="q-' + esc(q.id) + '">' + esc(q.question) + '</label><input type="text" id="q-' + esc(q.id) + '" data-q="' + esc(q.id) + '"><div class="small muted">' + esc(q.why) + "</div></div>";
        }).join("") + "</div>";
      }
      out += '<div class="row"><button class="btn" data-action="build">Write my prompt</button></div><div id="built"></div>';
      document.getElementById("coach-out").innerHTML = out;
    }).catch(function (e) { toast(e.message); });
  }
  function setStep(n) {
    var s = document.querySelectorAll("#steps span");
    for (var i = 0; i < s.length; i++) s[i].classList.toggle("on", i === n - 1);
  }
  function build() {
    var answers = {};
    document.querySelectorAll("[data-q]").forEach(function (el) { if (el.value.trim()) answers[el.getAttribute("data-q")] = el.value; });
    var t = document.querySelector('input[name="tool"]:checked');
    api("POST", "/api/coach/build", { text: state.coachText, answers: answers, tool: t ? t.value : null, task_type: state.analysis && state.analysis.task_type }).then(function (b) {
      setStep(3);
      state.lastPrompt = b.prompt;
      document.getElementById("built").innerHTML = '<div class="panel stack"><div class="spread"><h3>Prompt for ' + esc(b.tool_label) + '</h3><div class="row"><button class="btn" data-action="copy-prompt">Copy prompt</button>' +
        (b.kit_file ? '<button class="btn ghost" data-action="kit" data-path="agent-kit/' + esc(b.kit_file.replace(/^agent-kit\//, "")) + '">Open matching kit file</button>' : "") + '</div></div><pre class="prompt">' + esc(b.prompt) + '</pre>' +
        '<p class="small muted">' + esc(b.human_review) + "</p></div>";
    }).catch(function (e) { toast(e.message); });
  }

  // ---------------------------------------------------------------- practices
  function practicesView() {
    var calls = [api("GET", "/api/practices")];
    if (state.role !== "engineer") calls.push(api("GET", "/api/practices/discovery"));
    Promise.all(calls).then(function (res) {
      var d = res[0], disc = res[1];
      var html = '<h1>Practice library</h1><p class="lead">Reusable prompt, agent and workflow practices. Each one names the workflow signals it improves and links to ready-to-use files for Copilot, Claude Code and Devin.</p>';
      if (disc) html += discoveryPanel(disc.practices);
      html += '<div class="grid2" style="margin-top:1rem">' + d.practices.map(function (p) {
        return '<article class="panel stack"><div class="row"><span class="tag">' + esc(p.code) + '</span><span class="tag plain">' + esc(p.type) + '</span><span class="tag plain">' + esc(p.workflow.replace("_", " ")) + '</span></div><h3>' + esc(p.title) + '</h3><p class="small">' + esc(p.summary) + '</p>' +
          '<p class="small"><strong>Improves:</strong> ' + esc(p.signal_labels.join(", ")) + '</p><div class="row">' + Object.keys(p.kit).map(function (k) { return '<button class="btn ghost small" data-action="kit" data-path="' + esc(p.kit[k]) + '">' + esc(toolName(k)) + "</button>"; }).join("") + "</div></article>";
      }).join("") + "</div>";
      view(html);
    }).catch(fail);
  }
  function discoveryPanel(list) {
    return '<div class="panel" style="margin-top:1rem"><h2>Practices discovered in the data</h2><p class="small muted">Org-level comparison of engineer-weeks with and without each practice. Association in synthetic data, not causation.</p><div class="table-wrap"><table><thead><tr><th>Practice</th><th>Adoption signal</th><th>Outcome signal</th><th>With practice</th><th>Without</th><th>Pearson r</th></tr></thead><tbody>' +
      list.map(function (p) { return "<tr><td>" + esc(p.practice_code + " " + p.practice_title) + "</td><td>" + esc(p.adoption_signal) + "</td><td>" + esc(p.outcome_signal) + "</td><td><strong>" + esc(p.median_with_practice) + "</strong></td><td>" + esc(p.median_without_practice) + "</td><td>" + esc(p.pearson_r) + "</td></tr>"; }).join("") + "</tbody></table></div></div>";
  }

  // ---------------------------------------------------------------- manager / leader
  function insightsBody(d, title) {
    if (d.suppressed) {
      return '<div class="panel suppressed"><div class="k-stamp" style="margin:0 auto 1rem">k&nbsp;&ge;&nbsp;' + esc(d.k_threshold || 5) + '</div><h2>' + esc(title) + ' is below the privacy threshold</h2><p style="margin:0 auto">' + esc(d.reason) + '</p></div>';
    }
    var ad = Object.keys(d.adoption).map(function (k) { var a = d.adoption[k]; return { label: k, share: a.suppressed ? null : a.share, display: a.display }; });
    var html = '<div class="grid2" style="margin-top:1rem"><div class="panel"><h2>Tool adoption</h2><p class="small muted">Share of engineers who used each tool in the last 4 weeks.</p>' + Charts.bars(ad, { label: "Tool adoption" }) + '</div>' +
      '<div class="panel"><h2>Team medians</h2><div class="table-wrap"><table><tbody>' + Object.keys(d.medians).map(function (k) { var m = d.medians[k]; return "<tr><td>" + esc(m.label) + '</td><td><strong>' + esc(m.display) + '</strong></td><td class="small muted">' + (m.direction === "lower" ? "lower is better" : "higher is better") + "</td></tr>"; }).join("") + "</tbody></table></div></div></div>";
    html += '<h2 style="margin-top:1.5rem">Common workflow gaps and enablement opportunities</h2><p class="small muted">' + esc(d.privacy_note) + "</p>";
    html += d.workflow_gaps.length ? '<div class="stack">' + d.workflow_gaps.map(function (g) {
      return '<article class="panel gap"><div class="spread"><div><div class="row small"><span class="tag">' + esc(g.practice_code) + '</span><span class="tag plain">' + esc(g.engineers_affected) + '</span></div><h3 style="margin-top:.4rem">' + esc(g.practice_title) + '</h3></div>' +
        '<div class="compare"><div><div class="small muted">' + esc(g.signal_label) + ' (affected group median)</div><div class="v">' + esc(g.group_median) + '</div></div>' + (g.projected_if_adopted ? '<div><div class="small muted">Simulated with practice</div><div class="v after">' + esc(g.projected_if_adopted) + "</div></div>" : "") + '</div></div>' +
        '<p><strong>Pattern:</strong> ' + esc(g.pattern) + '</p><p><strong>Opportunity:</strong> ' + esc(g.enablement_opportunity) + '</p><div class="row">' + Object.keys(g.kit).map(function (k) { return '<button class="btn ghost small" data-action="kit" data-path="' + esc(g.kit[k]) + '">' + esc(toolName(k)) + " file</button>"; }).join("") + "</div></article>";
    }).join("") + "</div>" : '<div class="panel empty">No pattern is shared by enough engineers to show safely.</div>';
    if (d.patterns_below_threshold) html += '<p class="small muted" style="margin-top:.75rem">' + d.patterns_below_threshold + ' other pattern(s) affect fewer than ' + d.k_threshold + ' engineers and are hidden to protect privacy.</p>';
    html += '<h2 style="margin-top:1.5rem">Weekly team trends</h2><div class="grid3">' + Object.keys(d.trend).map(function (k) {
      var t = d.trend[k]; return '<div class="panel"><h3>' + esc(t.label) + "</h3>" + Charts.line([{ points: t.points, cls: "actual" }], { width: 320, height: 170, pct: /rate/.test(k), label: t.label }) + "</div>";
    }).join("") + "</div>";
    return html;
  }
  function teamView() {
    api("GET", "/api/team/insights").then(function (d) {
      view('<div class="spread"><div><h1>' + esc(d.team.name) + '</h1><p class="lead">' + esc(d.team.domain) + ' &middot; ' + esc(d.group_size) + '</p></div>' +
        '<div class="row"><div class="k-stamp">k&nbsp;&ge;&nbsp;' + esc(d.k_threshold || 5) + '</div>' + privacyBar("Team-level view", "No individual recommendations, prompts, history, dismissals or feedback. No drill-down to people.") + '</div></div>' +
        insightsBody(d, d.team.name) +
        '<div class="panel" style="margin-top:1.5rem"><h2>Try to see an individual</h2><p class="small muted">There is no link to people in this view. This button calls the private coaching endpoint directly with your manager session, so you can see the server refuse it.</p>' +
        '<button class="btn ghost" data-action="probe">Request an engineer\'s private coaching</button><div id="probe-out" style="margin-top:.75rem"></div></div>');
    }).catch(fail);
  }
  function orgView() {
    api("GET", "/api/org/insights").then(function (d) {
      var teams = '<div class="panel" style="margin-top:1rem"><h2>Teams</h2><p class="small muted">Listed alphabetically. Teams are not ranked or compared.' + (d.teams_excluded_for_privacy ? " " + d.teams_excluded_for_privacy + " small team(s) are excluded from portfolio totals so their data cannot be inferred by subtraction." : "") + '</p><div class="table-wrap"><table><thead><tr><th>Team</th><th>Size</th><th>Top enablement opportunities</th></tr></thead><tbody>' +
        d.teams.map(function (t) { return "<tr><td>" + esc(t.team.name) + '<div class="small muted">' + esc(t.team.domain) + "</div></td><td>" + esc(t.group_size) + "</td><td>" + (t.suppressed ? '<span class="tag plain">Below privacy threshold</span>' : esc(t.top_opportunities.join("; ") || "None above threshold")) + "</td></tr>"; }).join("") + "</tbody></table></div></div>";
      view('<div class="spread"><div><h1>Portfolio insights</h1><p class="lead">How AI tools are being used across teams, which practices help, and where enablement would pay off.</p></div><div class="k-stamp" title="Minimum group size before anything is shown">k&nbsp;&ge;&nbsp;' + esc(d.k_threshold) + '</div></div>' +
        teams + discoveryPanel(d.practice_discovery) + insightsBody(d, "Portfolio"));
    }).catch(fail);
  }

  // ---------------------------------------------------------------- enablement
  function enableView() {
    Promise.all([api("GET", "/api/trust/eval"), api("GET", "/api/trust/compliance"), api("GET", "/api/audit")]).then(function (r) {
      var ev = r[0], co = r[1], au = r[2];
      view('<h1>AI enablement workspace</h1><p class="lead">Evidence that recommendations are good and that privacy holds. Nothing here identifies an engineer.</p>' +
        evalPanel(ev) + compliancePanel(co) +
        '<div class="panel" style="margin-top:1rem"><h2>Access audit</h2><p class="small muted">' + esc(au.note) + ' Blocked attempts show as 401/403.</p><div class="table-wrap" style="max-height:360px;overflow:auto"><table><thead><tr><th>Time (UTC)</th><th>Role</th><th>Request</th><th>Status</th></tr></thead><tbody>' +
        au.entries.slice(0, 120).map(function (e) { return "<tr><td>" + esc(e.ts) + "</td><td>" + esc(e.role) + '</td><td class="mono">' + esc(e.method + " " + e.path) + '</td><td class="passfail ' + (e.status < 400 ? "ok" : "no") + '">' + e.status + "</td></tr>"; }).join("") + "</tbody></table></div></div>");
    }).catch(fail);
  }
  function evalPanel(ev) {
    var s = ev.summary;
    return '<div class="panel" style="margin-top:1rem"><div class="spread"><div><h2>Recommendation quality</h2><p class="small muted">Seeded synthetic scenarios graded on relevance, completeness, explainability, actionability and persona fit. Target 80%.</p></div><div class="stat passfail ' + (s.meets_target ? "ok" : "no") + '">' + s.passed + "/" + s.total + " (" + Math.round(s.pass_rate * 100) + "%)</div></div>" +
      '<div class="grid3"><div><div class="small muted">Context awareness pairs</div><div class="stat">' + ev.context_awareness.summary.passed + "/" + ev.context_awareness.summary.total + '</div></div><div><div class="small muted">Seeded personas</div><div class="stat">' + ev.seeded_personas.summary.passed + "/" + ev.seeded_personas.summary.total + '</div></div><div><div class="small muted">Prompt coach routing</div><div class="stat">' + ev.prompt_coach.summary.passed + "/" + ev.prompt_coach.summary.total + "</div></div></div>" +
      '<details style="margin-top:.75rem"><summary>Scenario results</summary><div class="table-wrap"><table><thead><tr><th>Scenario</th><th>Workflow</th><th>Fired</th><th>Result</th></tr></thead><tbody>' + ev.scenarios.map(function (x) { return "<tr><td>" + esc(x.id + " " + x.title) + "</td><td>" + esc(x.workflow) + '</td><td class="mono small">' + esc(x.fired.join(", ")) + '</td><td class="passfail ' + (x.passed ? "ok" : "no") + '">' + (x.passed ? "PASS" : "FAIL") + "</td></tr>"; }).join("") + "</tbody></table></div></details></div>";
  }
  function compliancePanel(co) {
    return '<div class="panel" style="margin-top:1rem"><div class="spread"><h2>Data minimization and no-ranking checks</h2><div class="stat passfail ' + (co.passed ? "ok" : "no") + '">' + (co.passed ? "All passed" : "Failures") + '</div></div><table><tbody>' +
      co.checks.map(function (c) { return '<tr><td class="passfail ' + (c.passed ? "ok" : "no") + '">' + (c.passed ? "PASS" : "FAIL") + "</td><td>" + esc(c.title) + '</td><td class="small muted">' + esc(Array.isArray(c.detail) ? c.detail.join(", ") : c.detail) + "</td></tr>"; }).join("") + "</tbody></table></div>";
  }

  // ---------------------------------------------------------------- trust / how it works
  function trustView() {
    Promise.all([api("GET", "/api/trust/boundaries"), api("GET", "/api/trust/compliance"), api("GET", "/api/trust/eval")]).then(function (r) {
      var b = r[0];
      view('<h1>How Compass works</h1><p class="lead">Two experiences, one synthetic dataset, and a privacy boundary you can inspect.</p>' + architecture() +
        '<div class="grid2" style="margin-top:1rem"><div class="panel"><h2>Privacy threshold in action</h2><p class="small muted">Minimum group size k = ' + b.k + '. Teams smaller than k show nothing; patterns shared by fewer than k engineers are hidden.</p><table><thead><tr><th>Team</th><th>Size</th><th>Patterns shown</th><th>Hidden</th></tr></thead><tbody>' +
        b.teams.map(function (t) { return "<tr><td>" + esc(t.team) + "</td><td>" + esc(t.group_size) + "</td><td>" + (t.suppressed ? '<span class="tag plain">Suppressed</span>' : t.patterns_shown) + "</td><td>" + (t.patterns_below_threshold == null ? "all" : t.patterns_below_threshold) + "</td></tr>"; }).join("") +
        '</tbody></table></div><div class="panel"><h2>Who can call what</h2><div class="table-wrap" style="max-height:330px;overflow:auto"><table><thead><tr><th>Endpoint</th><th>Roles</th></tr></thead><tbody>' +
        b.access_matrix.map(function (m) { return '<tr><td class="mono small">' + esc(m.endpoint) + "</td><td>" + esc(m.roles.join(", ")) + "</td></tr>"; }).join("") + '</tbody></table></div><p class="small muted">Aggregation reads: ' + esc(b.aggregation_reads) + "</p></div></div>" +
        evalPanel(r[2]) + compliancePanel(r[1]));
    }).catch(fail);
  }
  function architecture() {
    return '<div class="panel" style="margin-top:1rem"><h2>Architecture</h2><svg class="chart" viewBox="0 0 920 380" role="img" aria-label="Architecture diagram">' +
      '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--muted)"/></marker></defs>' +
      box(20, 20, 170, 64, "Synthetic signals", "usage + PR/CI metadata") + box(250, 20, 190, 64, "signals.db", "read-only, traceable ids") +
      box(500, 20, 190, 64, "Recommendation engine", "rules + persona context") + box(740, 20, 160, 64, "Engineer view", "private", true) +
      box(740, 104, 160, 50, "private.db", "feedback, history", true) +
      box(500, 196, 190, 64, "Aggregator", "k >= 5, no ids, no private.db") + box(740, 196, 160, 64, "Manager / leader", "team patterns only") +
      box(20, 296, 170, 64, "Jira story or task", "pasted or CSV export") + box(250, 296, 190, 64, "Prompt coach", "in memory, never stored") +
      box(500, 296, 190, 64, "Tool router", "Copilot / Claude / Devin") + box(740, 296, 160, 64, "Agent kit files", "prompts, skills, playbooks") +
      arrow(190, 52, 250, 52) + arrow(440, 52, 500, 52) + arrow(690, 52, 740, 52) + arrow(820, 84, 820, 104) + arrow(740, 129, 690, 70) +
      arrow(440, 70, 500, 220) + arrow(690, 228, 740, 228) +
      arrow(190, 328, 250, 328) + arrow(440, 328, 500, 328) + arrow(690, 328, 740, 328) +
      '<line x1="20" y1="176" x2="900" y2="176" stroke="var(--private)" stroke-width="1.5" stroke-dasharray="6 4"/>' +
      '<text x="900" y="170" text-anchor="end" font-size="12" fill="var(--private)">Privacy boundary: private.db is never read below this line</text>' +
      '<text x="595" y="284" text-anchor="middle" font-size="11">Human review before any change is applied</text>' +
      "</svg></div>";
    function box(x, y, w, h, t, s, priv) {
      return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="8" fill="' + (priv ? "var(--private-wash)" : "var(--sea-wash)") + '" stroke="' + (priv ? "var(--private)" : "var(--sea)") + '"/>' +
        '<text x="' + (x + w / 2) + '" y="' + (y + h / 2 - 4) + '" text-anchor="middle" font-size="13" font-weight="600" style="fill:var(--ink)">' + t + '</text>' +
        '<text x="' + (x + w / 2) + '" y="' + (y + h / 2 + 14) + '" text-anchor="middle" font-size="11">' + s + "</text>";
    }
    function arrow(x1, y1, x2, y2) { return '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#ar)" style="color:var(--muted)"/>'; }
  }

  // ---------------------------------------------------------------- kit viewer
  function showKit(path) {
    api("GET", "/api/kit?path=" + encodeURIComponent(path)).then(function (k) {
      state.kitText = k.content;
      openModal(path.replace("agent-kit/", ""), '<p class="small muted">Copy this file into your repo (or run install-kit from the agent kit). Works without MCP servers or API keys.</p><div class="row" style="margin-bottom:.75rem"><button class="btn small" data-action="copy-kit">Copy file contents</button></div><pre class="prompt">' + esc(k.content) + "</pre>");
    }).catch(function (e) { toast(e.message); });
  }

  // ---------------------------------------------------------------- events
  document.addEventListener("click", function (ev) {
    var t = ev.target.closest("[data-action], [data-close]");
    if (!t) { if (ev.target.id === "modal") closeModal(); return; }
    if (t.hasAttribute("data-close")) return closeModal();
    var a = t.getAttribute("data-action");
    if (a === "login") login(t.getAttribute("data-role"), t.getAttribute("data-subject"));
    else if (a === "login-manager") login("manager", document.getElementById("mgr-team").value);
    else if (a === "show-engineers") { var s = document.getElementById("engineers"); s.hidden = false; s.scrollIntoView({ behavior: "smooth" }); }
    else if (a === "signout") signOut();
    else if (a === "fb") feedback(t.getAttribute("data-key"), t.getAttribute("data-act"));
    else if (a === "dismiss") { var k = t.getAttribute("data-key"); feedback(k, "dismissed", document.getElementById("why-" + k).value); }
    else if (a === "simulate") simulate(t.getAttribute("data-practice"), t.closest(".rec").id.replace("rec-", ""));
    else if (a === "kit") showKit(t.getAttribute("data-path"));
    else if (a === "copy-kit") copy(state.kitText || "");
    else if (a === "analyze") analyze();
    else if (a === "build") build();
    else if (a === "copy-prompt") copy(state.lastPrompt || "");
    else if (a === "sample-jira") api("GET", "/api/coach/sample-jira").then(function (d) { showJira(d.issues); });
    else if (a === "pick-jira") { var i = state.jira[+t.getAttribute("data-i")]; document.getElementById("coach-text").value = i.text; analyze(); }
    else if (a === "probe") api("GET", "/api/me/coaching").then(function () {
        document.getElementById("probe-out").innerHTML = '<div class="warn">Unexpected: access was allowed.</div>';
      }).catch(function (e) {
        document.getElementById("probe-out").innerHTML = privacyBar("Refused by the server: " + e.message, "Recorded in the access audit as a 403. Individual coaching is reachable only by the engineer it belongs to.");
      });
    else if (a === "forget") api("POST", "/api/me/forget", {}).then(function () { toast("Your coaching data was deleted"); myDataView(); });
  });
  document.addEventListener("keydown", function (ev) { if (ev.key === "Escape") closeModal(); });

  // ---------------------------------------------------------------- router
  var ROUTES_ = {
    "#/": signInView, "#/coach": coachView, "#/prompt": promptView, "#/practices": practicesView, "#/mydata": myDataView,
    "#/team": teamView, "#/org": orgView, "#/enable": enableView, "#/trust": trustView
  };
  var NEED = { "#/coach": ["engineer"], "#/mydata": ["engineer"], "#/team": ["manager"], "#/org": ["leader"], "#/enable": ["enablement"],
    "#/prompt": ["engineer", "manager", "enablement", "leader"], "#/practices": ["engineer", "manager", "leader", "enablement"] };
  window.Compass = { api: api, esc: esc, view: view, toast: toast, copy: copy, openModal: openModal, closeModal: closeModal,
    privacyBar: privacyBar, state: state, toolName: toolName };
  var EXTRA = window.CompassRoutes || {};
  Object.keys(EXTRA).forEach(function (k) { ROUTES_[k] = EXTRA[k].view; if (EXTRA[k].roles) NEED[k] = EXTRA[k].roles; });
  function router() {
    var full = location.hash || "#/";
    var h = full.split("?")[0], query = {};
    (full.split("?")[1] || "").split("&").forEach(function (kv) { if (kv) { var p = kv.split("="); query[decodeURIComponent(p[0])] = decodeURIComponent((p[1] || "").replace(/\+/g, " ")); } });
    if (!ROUTES_[h]) h = "#/";
    if (NEED[h] && NEED[h].indexOf(state.role) < 0) {
      if (!state.role && Object.keys(query).length) { state.pendingDeepLink = full; }
      h = state.role ? NAV[state.role][0][0] : "#/";
    }
    if (h === "#/" && state.role) { h = state.pendingDeepLink ? state.pendingDeepLink.split("?")[0] : NAV[state.role][0][0]; }
    if (full.split("?")[0] !== h) { location.hash = h; return; }
    renderNav();
    ROUTES_[h](query);
  }
  window.addEventListener("hashchange", router);
  router();
})();
