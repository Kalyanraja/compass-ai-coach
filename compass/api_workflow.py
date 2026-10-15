"""API routes for the workflow coach, setup/settings, catalog, scanners and Jira.

Registered into compass.server.ROUTES on import.
"""

from __future__ import annotations

import json
import sys

from . import config, jira_client, settings
from .server import ApiError, route
from .workflow import cache, coach, journey, runner
from .workflow.workspace import WorkspaceError

WF_ROLES = ("engineer", "enablement", "manager", "leader")


def _owner(ctx):
    return f"{ctx['role']}:{ctx['sub']}"


def _wrap(fn, *a, **k):
    try:
        return fn(*a, **k)
    except (journey.JourneyError, WorkspaceError, KeyError, ValueError, runner.RunError) as e:
        raise ApiError(400, str(e).strip("'\""))


# ------------------------------------------------------------------ setup / settings (local user)

@route("GET", "/api/setup")
def get_setup(ctx, q, body):
    s = settings.public_view()
    return {"settings": s, "questions": SETUP_QUESTIONS, "python": sys.version.split()[0]}


SETUP_QUESTIONS = [
    {"id": "approved_tools", "text": "Which AI tools are you approved to use?",
     "options": [["copilot", "GitHub Copilot in VS Code"], ["claude", "Claude Code in VS Code"], ["devin", "Devin (web)"],
                 ["writing", "Microsoft 365 Copilot (only if your company provides it)"]]},
    {"id": "tools_see_internal_code", "text": "Which of them may see internal source code?"},
    {"id": "allowed_roots", "text": "Which project folders may Compass read? (Compass never reads outside these.)"},
    {"id": "jira", "text": "How do you want to bring in Jira work? Off (paste or CSV import), Jira Cloud, or Jira Data Center."},
    {"id": "scanners", "text": "Which local scanners are installed and approved? (gitleaks, Semgrep, Spectral are optional.)"},
    {"id": "allow_test_execution", "text": "May Compass offer to run your project's tests when you approve each run?"},
    {"id": "context_budget", "text": "Default work-package size: Lean (~4k), Balanced (~8k) or Deep (~16k) estimated tokens?"},
    {"id": "cache_enabled", "text": "Allow a local cache of project facts? (Off by default; invalidated on any change.)"},
]


@route("POST", "/api/setup")
def post_setup(ctx, q, body):
    allowed = {"approved_tools", "tools_see_internal_code", "allowed_roots", "default_project", "default_data_class",
               "context_budget", "cache_enabled", "allow_test_execution", "jira", "setup_complete"}
    upd = {k: v for k, v in (body or {}).items() if k in allowed}
    if "context_budget" in upd and upd["context_budget"] not in ("lean", "balanced", "deep"):
        raise ApiError(400, "invalid budget")
    if "default_data_class" in upd and upd["default_data_class"] not in ("synthetic", "internal", "restricted"):
        raise ApiError(400, "invalid data class")
    if "jira" in upd and upd["jira"].get("mode", "off") not in ("off", "cloud", "datacenter"):
        raise ApiError(400, "invalid Jira mode")
    try:
        s = settings.save(upd)
    except ValueError as e:
        raise ApiError(400, str(e))
    if "cache_enabled" in upd and not upd["cache_enabled"]:
        cache.clear()
    return {"settings": settings.public_view(s)}


@route("POST", "/api/scanners/discover")
def scanners_discover(ctx, q, body):
    name = body.get("name")
    path = body.get("path") or None
    try:
        return runner.discover(name, path)
    except runner.RunError as e:
        raise ApiError(400, str(e))


@route("POST", "/api/scanners/approve")
def scanners_approve(ctx, q, body):
    name = body.get("name")
    d = runner.discover(name, body.get("path") or None)
    if not d.get("found"):
        raise ApiError(400, f"{name} was not found at that path")
    rec = {"path": d["path"], "version": d["version"], "sha256": d["sha256"], "approved": bool(body.get("approve", True))}
    s = settings.load()
    sc = dict(s["scanners"])
    sc[name] = rec
    settings.save({"scanners": sc})
    return {"scanner": rec, "note": "Approved for this machine. Compass re-checks the SHA-256 before every run."}


@route("GET", "/api/doctor")
def doctor(ctx, q, body):
    from .doctor import report
    return report()


# ------------------------------------------------------------------ catalog

@route("GET", "/api/catalog/tools")
def catalog_tools(ctx, q, body):
    return json.loads((config.ROOT / "catalog" / "tools.json").read_text(encoding="utf-8"))


@route("GET", "/api/catalog/capabilities")
def catalog_caps(ctx, q, body):
    return coach.catalog()


@route("GET", "/api/wf/packs")
def wf_packs(ctx, q, body):
    return {"packs": coach.pack_list()}


# ------------------------------------------------------------------ journey

@route("GET", "/api/wf/projects", roles=WF_ROLES)
def wf_projects(ctx, q, body):
    s = settings.load()
    return {"projects": journey.projects(s["allowed_roots"]), "default": s["default_project"], "allowed_roots": s["allowed_roots"]}


@route("POST", "/api/wf/start", roles=WF_ROLES)
def wf_start(ctx, q, body):
    return _wrap(journey.start, _owner(ctx), body.get("goal", ""), body.get("project", ""), body.get("workflow") or None,
                 body.get("source", "manual"))


@route("GET", "/api/wf/state", roles=WF_ROLES)
def wf_state(ctx, q, body):
    return _wrap(journey.state, (q.get("id") or [""])[0], _owner(ctx))


@route("POST", "/api/wf/workflow", roles=WF_ROLES)
def wf_workflow(ctx, q, body):
    return _wrap(journey.set_workflow, body.get("id", ""), _owner(ctx), body.get("workflow", ""))


@route("POST", "/api/wf/fact", roles=WF_ROLES)
def wf_fact(ctx, q, body):
    return _wrap(journey.confirm_fact, body.get("id", ""), _owner(ctx), body.get("fact", ""), body.get("value"))


@route("POST", "/api/wf/answer", roles=WF_ROLES)
def wf_answer(ctx, q, body):
    return _wrap(journey.answer, body.get("id", ""), _owner(ctx), body.get("answers") or {}, body.get("skip") or [])


@route("POST", "/api/wf/tool", roles=WF_ROLES)
def wf_tool(ctx, q, body):
    return _wrap(journey.recommend, body.get("id", ""), _owner(ctx), body.get("data_class"), body.get("complexity"),
                 body.get("large_scope"), bool(body.get("deterministic")), body.get("choose"))


@route("POST", "/api/wf/package", roles=WF_ROLES)
def wf_package(ctx, q, body):
    return _wrap(journey.build_package, body.get("id", ""), _owner(ctx), body.get("budget"), body.get("include"), body.get("exclude"))


@route("POST", "/api/wf/checks", roles=WF_ROLES)
def wf_checks(ctx, q, body):
    approve = bool(body.get("approve_tests")) and settings.load().get("allow_test_execution")
    if body.get("approve_tests") and not approve:
        raise ApiError(400, "Test execution is turned off in Settings. Turn it on, or import a report instead.")
    return _wrap(journey.run_checks, body.get("id", ""), _owner(ctx), approve)


@route("POST", "/api/wf/import", roles=WF_ROLES)
def wf_import(ctx, q, body):
    return _wrap(journey.import_report, body.get("id", ""), _owner(ctx), body.get("kind", ""), body.get("text", ""),
                 body.get("label", "imported"))


@route("POST", "/api/wf/verify-fix", roles=WF_ROLES)
def wf_verify(ctx, q, body):
    approve = bool(body.get("approve_tests")) and settings.load().get("allow_test_execution")
    if not approve:
        raise ApiError(400, "Verifying a fix runs your tests on temporary copies. Turn on test execution in Settings and approve this run.")
    return _wrap(journey.verify_fix, body.get("id", ""), _owner(ctx), body.get("diff", ""), approve)


@route("GET", "/api/wf/file", roles=WF_ROLES)
def wf_file(ctx, q, body):
    return _wrap(journey.read_file, (q.get("id") or [""])[0], _owner(ctx), (q.get("path") or [""])[0])


@route("POST", "/api/wf/delete", roles=WF_ROLES)
def wf_delete(ctx, q, body):
    return {"deleted": journey.delete(body.get("id", ""), _owner(ctx))}


@route("POST", "/api/wf/cancel", roles=WF_ROLES)
def wf_cancel(ctx, q, body):
    return {"cancelled": runner.cancel(str(body.get("run_id", "")))}


# ------------------------------------------------------------------ jira

@route("GET", "/api/jira/status", roles=WF_ROLES)
def jira_status(ctx, q, body):
    return jira_client.status()


@route("POST", "/api/jira/issue", roles=WF_ROLES)
def jira_issue(ctx, q, body):
    try:
        return jira_client.fetch_issue(body.get("key", ""), body.get("token") or None)
    except jira_client.JiraError as e:
        raise ApiError(400, str(e))


@route("POST", "/api/jira/search", roles=WF_ROLES)
def jira_search(ctx, q, body):
    try:
        return {"issues": jira_client.search(body.get("jql") or None, body.get("token") or None)}
    except jira_client.JiraError as e:
        raise ApiError(400, str(e))


SAMPLES = [
    {"id": "demo-api", "title": "Catch a missing API requirement", "project": "java-orders-api", "doc": "docs/stories/ORD-12.md",
     "workflow": "feature-api"},
    {"id": "demo-defect", "title": "Reject a fix without reproduction evidence", "project": "py-login-service",
     "doc": "docs/uat-defect-LOGIN-7.md", "workflow": "uat-defect"},
    {"id": "demo-tests", "title": "Show a test catching a seeded defect", "project": "py-login-service",
     "doc": "docs/stories/LOGIN-3.md", "workflow": "test-creation"},
]


@route("GET", "/api/wf/samples", roles=WF_ROLES)
def wf_samples(ctx, q, body):
    out = []
    base = (config.ROOT / "examples").resolve()
    for s in SAMPLES:
        p = base / s["project"] / s["doc"]
        if p.is_file():
            out.append(s | {"project_path": str(base / s["project"]), "text": p.read_text(encoding="utf-8")[:8000],
                            "label": "SYNTHETIC sample"})
    return {"samples": out}
