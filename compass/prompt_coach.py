"""Prompt coach: turn a Jira story (or any task text) into the next-best prompt and agent.

Flow (three interactions or fewer):
  1. analyze(text)            -> task type, what's present/missing, up to 3 questions,
                                  recommended tool with reasons, anti-pattern warnings
  2. build(text, answers, tool) -> a ready-to-paste prompt for Copilot, Claude Code or Devin
  3. copy / open the matching agent-kit file

Privacy: text is processed in memory for the request and never stored or logged.
It never reaches the manager or leader views. A sensitive-data scan warns the
engineer before anything is pasted into an AI tool.

Deterministic by default (no model, no API key). An optional approved LLM can be
plugged in through compass/llm.py; nothing depends on it.
"""

from __future__ import annotations

import csv
import io
import json
import re
from functools import lru_cache

from . import config

TASK_TYPES = {
    "trivial_deterministic": {
        "label": "Deterministic chore (formatting, lint, simple rename)",
        "keywords": [r"\bformat(ting)?\b", r"\blint\b", r"\bindent", r"\bsort imports\b", r"\brename (a |the )?variable",
                     r"\bwhitespace\b", r"\bprettier\b", r"\beslint --fix\b", r"\bcode style\b"],
    },
    "docs_communication": {
        "label": "Writing or communication (email, status, summary)",
        "keywords": [r"\bemail\b", r"\bstatus update\b", r"\bslide", r"\bpresentation\b", r"\bmeeting notes?\b",
                     r"\brelease notes\b", r"\bsummari[sz]e\b", r"\bstakeholders?\b", r"\bbullet points\b", r"\bsummar(y|ize) (for|to) (leadership|stakeholders|the team)\b",
                     r"\brewrite (this|the) (text|message|paragraph)\b", r"\bnewsletter\b"],
    },
    "test_creation": {
        "label": "Test creation",
        "keywords": [r"\btests?\b", r"\bunit test", r"\bcoverage\b", r"\bplaywright\b", r"\be2e\b", r"\bend[- ]to[- ]end tests?\b",
                     r"\bregression (suite|tests?)\b", r"\bautomat(e|ion) (the )?test", r"\bjunit\b", r"\bxunit\b", r"\bpytest\b",
                     r"\bjest\b", r"\btest cases?\b"],
    },
    "bug_fix": {
        "label": "Bug investigation and fix",
        "keywords": [r"\bbug\b", r"\bdefect\b", r"\bfail(s|ing|ed|ure)?\b", r"\berror\b", r"exception\b", r"\bbroken\b",
                     r"\bincident\b", r"\b500\b", r"null ?pointer", r"\bnot working\b", r"\bcrash", r"\btimeout\b",
                     r"\bregress(ion|ed)\b", r"\bfix\b", r"\bduplicat", r"\bincorrect\b", r"\bwrong\b"],
    },
    "refactor_modernization": {
        "label": "Refactor, upgrade or migration",
        "keywords": [r"\brefactor", r"\bmigrat(e|ion)\b", r"\bupgrade\b", r"\bmoderni[sz]", r"\bdeprecat", r"\bjava (17|21)\b",
                     r"\.net ?(6|8|9)\b", r"\bspring boot 3\b", r"\bacross (all|every|the) (services|repos|modules)",
                     r"\btech(nical)? debt\b", r"\bdependenc(y|ies)\b", r"\bbump\b"],
    },
    "pr_readiness": {
        "label": "Pull request readiness or review",
        "keywords": [r"\bpull request\b", r"\bPR\b", r"\bcode review\b", r"\bready for review\b", r"\breview (my|this|the) (change|diff|code)",
                     r"\bmerge\b"],
    },
    "data_sql": {
        "label": "Data / SQL",
        "keywords": [r"\bsql\b", r"\bstored proc", r"\bquery\b", r"\btable\b", r"\betl\b", r"\bt-sql\b", r"\bindex(es)?\b",
                     r"\bschema\b", r"\bdatabase\b"],
    },
    "exploration": {
        "label": "Understand or explore code",
        "keywords": [r"\bexplain\b", r"\bhow does\b", r"\bwhere is\b", r"\bunderstand\b", r"\bonboard", r"\bwalk me through\b",
                     r"\bwhat does .* do\b"],
    },
    "feature_api": {
        "label": "Feature or API change",
        "keywords": [r"\bendpoint\b", r"\bapi\b", r"\brest\b", r"\bimplement\b", r"\bbuild\b", r"\badd (a |an )?(new )?(feature|field|screen|page|button|endpoint)",
                     r"\bcreate (a |an )?(new )?(service|endpoint|component|screen)", r"\bas a .* i want\b", r"\buser story\b",
                     r"\bfeature\b", r"\bcontroller\b", r"\bui\b"],
    },
}

# What a strong brief contains, per task type. Each check has a detector, a
# question to ask when missing, why it matters (that explanation is the coaching),
# and a priority (lower = asked first).
COMMON_CHECKS = [
    ("goal", "Clear goal", r"\b(as a|i want|so that|goal|need to|should|must|implement|add|create|fix|build|write)\b",
     "In one sentence, what should be true when this is done?", "A one-line goal stops the agent from solving a different problem.", 1),
    ("acceptance", "Acceptance criteria", r"(acceptance criteria|\bAC\d|\bgiven\b.*\bwhen\b.*\bthen\b|\bshould (return|show|display|reject|allow)|\bexpected\b)",
     "What are the acceptance criteria (Given / When / Then, or a short bullet list)?",
     "Acceptance criteria give the agent and the reviewer a testable definition of done; ambiguous specs cut first-try correctness 20-30%.", 2),
    ("scope", "Scope / files", r"(\.(java|cs|py|ts|tsx|js|sql|yaml|yml)\b|\bmodule\b|\bservice\b|\bclass\b|\bcomponent\b|\bpackage\b|\brepo\b|\bfolder\b|\bcontroller\b)",
     "Which module, service or files are in scope (and anything explicitly out of scope)?",
     "Naming the area keeps the agent from editing unrelated code and keeps the PR small.", 4),
    ("constraints", "Constraints", r"(must not|do not|don't|without|keep|backward compatib|no breaking|constraint|only change|limit)",
     "Any constraints (no breaking changes, keep public signatures, performance limits, libraries to use or avoid)?",
     "Constraints prevent 'technically correct but unusable' output.", 5),
    ("verification", "Verification", r"(\btest(s|ed|ing)?\b|\bverify\b|\bevidence\b|\bci\b|\bbuild passes\b|\bcoverage\b)",
     "How should the result be verified (which tests to add or run)?",
     "Asking for test evidence up front is the cheapest way to raise CI first-pass rate.", 6),
]

TYPE_CHECKS = {
    "feature_api": [
        ("io", "Inputs and outputs", r"(request|response|payload|field|schema|json|parameter|returns?|input|output)",
         "What are the inputs and outputs (fields, required vs optional, response shape)?",
         "Without a contract the agent invents one, and the PR fails review on interface details.", 3),
        ("errors", "Error handling", r"(error|4\d\d|5\d\d|invalid|validation|reject|exception|fallback)",
         "How should errors and invalid input be handled (status codes, messages)?",
         "Error paths are where most review comments land for new endpoints.", 3),
        ("security", "Auth / permissions", r"(auth|role|permission|token|entitle|access control|scope)",
         "Who is allowed to call or see this (roles, permissions)?",
         "Authorization rules are rarely guessable and are costly to retrofit.", 3),
    ],
    "bug_fix": [
        ("expected_actual", "Expected vs actual", r"(expected|actual|should .* but|instead of)",
         "What happened, and what should have happened?", "Expected behavior is the definition of a successful fix.", 2),
        ("repro", "Reproduction", r"(steps|reproduc|repro|when i|to reproduce|happens when)",
         "How can it be reproduced with synthetic or approved test data?",
         "A failing reproduction lets the agent prove the fix instead of guessing.", 2),
        ("env_change", "Environment / recent change", r"(uat|prod|qa|staging|dev env|environment|version|since|after (the )?(deploy|release|upgrade)|changed)",
         "Where does it fail (environment, version) and what changed since it last worked?",
         "Recent changes are the fastest route to root cause.", 3),
    ],
    "test_creation": [
        ("behaviour", "Behavior under test", r"(acceptance criteria|given|when|then|should|expected|behaviou?r)",
         "Which behavior must the tests prove (link the acceptance criteria)?",
         "Tests derived from acceptance criteria catch real defects; tests derived from code only mirror it.", 2),
        ("negative", "Negative and edge cases", r"(invalid|negative|error|edge|boundary|empty|null|unauthori[sz]ed|timeout)",
         "Which failure and edge cases matter (invalid input, empty, unauthorized, timeouts)?",
         "Happy-path-only tests are the most common weakness in AI-generated suites.", 3),
        ("data", "Test data and fixtures", r"(fixture|test data|mock|stub|seed|factory|test account)",
         "What test data or fixtures should be used (no production data or real credentials)?",
         "Isolated fixtures prevent flaky, order-dependent tests.", 3),
    ],
    "refactor_modernization": [
        ("behaviour_kept", "Behavior preserved", r"(no behaviou?r change|same behaviou?r|characteri[sz]ation|backward compatib|regression)",
         "Must behavior stay identical? Are there characterization tests to protect it?",
         "Refactors without a safety net are the riskiest AI-assisted changes.", 2),
        ("increments", "Increments / rollback", r"(increment|phase|step|batch|rollback|feature flag|one (module|service) at a time)",
         "Can it be done in increments (one module or service per PR) with a rollback path?",
         "Small batches amplify the benefit of AI and keep reviews effective.", 3),
    ],
    "data_sql": [
        ("schema", "Schema / tables", r"(table|column|schema|view|proc)",
         "Which tables, columns or procedures are involved?", "Names prevent the agent from inventing schema.", 2),
        ("volume", "Volume / performance", r"(rows|volume|million|performance|index|execution plan|latency)",
         "What data volume and performance target apply?", "Query shape depends heavily on volume.", 3),
    ],
    "docs_communication": [
        ("audience", "Audience and tone", r"(audience|leadership|team|customer|tone|formal|casual|stakeholder)",
         "Who is the audience and what tone or length do you need?", "Audience drives every wording choice.", 2),
    ],
}

TOOLS = {  # labels shown to users
    "copilot": {"label": "GitHub Copilot (VS Code)", "mode": "Agent mode with a prompt file"},
    "claude": {"label": "Claude Code (VS Code)", "mode": "Start in plan mode"},
    "devin": {"label": "Devin (web)", "mode": "Session with an attached playbook"},
    "writing": {"label": "Microsoft 365 Copilot (if enabled)", "mode": "Optional writing assistant, only if your company provides it"},
    "no_ai": {"label": "No AI needed", "mode": "Use the formatter, linter, IDE refactoring or a codemod"},
}

KIT_FOR_TYPE = {
    "feature_api": {"copilot": ".github/prompts/jira-to-plan.prompt.md", "claude": ".claude/skills/ticket-to-plan/SKILL.md",
                    "devin": "devin/playbooks/jira-ticket-to-pr.devin.md"},
    "bug_fix": {"copilot": ".github/prompts/debug-investigation.prompt.md", "claude": ".claude/skills/systematic-debugging/SKILL.md",
                "devin": "devin/playbooks/bug-investigation.devin.md"},
    "test_creation": {"copilot": ".github/prompts/test-plan.prompt.md", "claude": ".claude/skills/test-creation/SKILL.md",
                      "devin": "devin/playbooks/test-creation.devin.md"},
    "refactor_modernization": {"copilot": ".github/prompts/refactor-safely.prompt.md", "claude": ".claude/skills/writing-plans/SKILL.md",
                               "devin": "devin/playbooks/modernization-migration.devin.md"},
    "pr_readiness": {"copilot": ".github/prompts/pr-readiness.prompt.md", "claude": ".claude/skills/pr-readiness-selfcheck/SKILL.md",
                     "devin": "devin/playbooks/pr-readiness.devin.md"},
    "data_sql": {"copilot": ".github/prompts/sql-review.prompt.md", "claude": ".claude/skills/test-driven-development/SKILL.md",
                 "devin": "devin/playbooks/jira-ticket-to-pr.devin.md"},
    "exploration": {"copilot": ".github/prompts/explain-code.prompt.md", "claude": ".claude/skills/brainstorming/SKILL.md",
                    "devin": "devin/README.md"},
    "docs_communication": {"copilot": "tool-routing-guide.md", "claude": "tool-routing-guide.md", "writing": "tool-routing-guide.md"},
    "trivial_deterministic": {"no_ai": "tool-routing-guide.md"},
}

SENSITIVE = [
    ("password or secret", r"(password|passwd|pwd|secret|api[_-]?key|token)\s*[:=]\s*\S+"),
    ("private key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("email address", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    ("possible SSN", r"\b\d{3}-\d{2}-\d{4}\b"),
    ("possible card number", r"\b(?:\d[ -]?){13,16}\b"),
    ("connection string", r"(Server|Data Source)=[^;]+;.*(Password|Pwd)="),
    ("bearer token", r"\bBearer\s+[A-Za-z0-9\-._~+/]{20,}"),
]

BROAD = r"\b(across (all|every|the)|all (services|repos|modules|endpoints)|repo[- ]wide|every (service|module|file)|\d{2,} (files|services|modules))\b"
MULTI_FILE = r"\b(multiple|several|many) (files|modules|services|classes)\b|\bend[- ]to[- ]end\b|\barchitecture\b|\bdesign\b|\binvestigat"


@lru_cache(maxsize=1)
def anti_patterns() -> dict:
    try:
        with open(config.ANTI_PATTERNS_JSON, encoding="utf-8") as fh:
            data = json.load(fh)
        return {a["id"]: a for a in data}
    except (OSError, ValueError):
        return {}


@lru_cache(maxsize=1)
def prompt_library() -> list:
    try:
        with open(config.PROMPTS_JSON, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return []


def classify(text: str) -> list[dict]:
    t = text.lower()
    first = t.strip().split("\n", 1)[0] if t.strip() else ""
    scores = []
    for tid, spec in TASK_TYPES.items():
        hits = [k for k in spec["keywords"] if re.search(k, t, re.I)]
        # Words in the title / summary line count double.
        title_hits = [k for k in spec["keywords"] if re.search(k, first, re.I)]
        if hits:
            scores.append({"type": tid, "label": spec["label"], "score": len(hits) + len(title_hits)})
    # Tie-breaks: a story that is mainly about tests or a bug outranks generic feature words.
    priority = ["trivial_deterministic", "docs_communication", "refactor_modernization", "test_creation", "bug_fix",
                "pr_readiness", "data_sql", "exploration", "feature_api"]
    scores.sort(key=lambda s: (-s["score"], priority.index(s["type"])))
    if not scores:
        scores = [{"type": "feature_api", "label": TASK_TYPES["feature_api"]["label"], "score": 0}]
    return scores


def _checks_for(task_type: str):
    if task_type in ("docs_communication", "trivial_deterministic"):
        return [c for c in COMMON_CHECKS if c[0] in ("goal", "scope")] + TYPE_CHECKS.get(task_type, [])
    if task_type == "exploration":
        return [c for c in COMMON_CHECKS if c[0] in ("goal", "scope")]
    return COMMON_CHECKS + TYPE_CHECKS.get(task_type, [])


def assess(text: str, task_type: str) -> tuple[list, list]:
    present, missing = [], []
    first = text.strip().split("\n", 1)[0] if text.strip() else ""
    for cid, label, rx, question, why, prio in _checks_for(task_type):
        item = {"id": cid, "label": label, "question": question, "why": why, "priority": prio}
        ok = bool(re.search(rx, text, re.I | re.S))
        if cid == "goal" and len(first.split()) >= 4:
            ok = True  # a descriptive summary line states the goal
        (present if ok else missing).append(item)
    missing.sort(key=lambda c: c["priority"])
    return present, missing


def detect_anti_patterns(text: str, task_type: str, missing_ids: set) -> list[dict]:
    ap = anti_patterns()
    found = []

    def add(aid, note):
        a = ap.get(aid, {"id": aid, "name": aid.replace("-", " ").title(), "fix": ""})
        found.append({"id": aid, "name": a.get("name"), "note": note, "fix": a.get("fix", "")})

    words = len(text.split())
    if words < 12:
        add("lazy-prompt", f"Only {words} words; the agent will have to guess intent, files and scope.")
    if "acceptance" in missing_ids and task_type not in ("docs_communication", "trivial_deterministic", "exploration"):
        add("no-constraints" if "constraints" in missing_ids else "tests-after-or-never",
            "No acceptance criteria or constraints, so there is no testable definition of done.")
    verbs = len(re.findall(r"\b(and|also|plus|then)\b", text, re.I))
    if words > 120 and verbs > 10:
        add("mega-pr-request", "Many asks in one request; split into a plan and small steps.")
    if task_type == "trivial_deterministic":
        add("ai-for-deterministic-work", "A formatter, linter or IDE refactor does this faster and deterministically.")
    if re.search(r"(as a .* i want|acceptance criteria|story points|sprint)", text, re.I) and not re.search(
            r"\b(please|implement|write|create|fix|plan|generate)\b", text, re.I):
        add("ticket-as-instructions", "The ticket is pasted as-is; add what you want the agent to do with it.")
    if "verification" in missing_ids and task_type not in ("docs_communication", "trivial_deterministic", "exploration"):
        add("trust-without-evidence", "No verification step; ask the agent to run tests and show results.")
    return found


def scan_sensitive(text: str) -> list[str]:
    return [label for label, rx in SENSITIVE if re.search(rx, text, re.I)]


def route(text: str, task_type: str, complexity: str = "medium") -> dict:
    t = text.lower()
    broad = bool(re.search(BROAD, t))
    multi = bool(re.search(MULTI_FILE, t)) or complexity == "high"
    reasons, alts = [], []
    if task_type == "trivial_deterministic":
        tool = "no_ai"
        reasons = ["The change is deterministic; the project formatter, linter or IDE refactoring is faster, free and exact.",
                   "Save AI for work that needs reasoning."]
    elif task_type == "docs_communication":
        tool, alts = "copilot", ["claude", "writing"]
        reasons = ["Office work (documents, emails, summaries): GitHub Copilot and Claude Code in VS Code are approved for it.",
                   "Give the audience, tone and length, and keep facts unchanged.",
                   "Microsoft 365 Copilot is an alternative only if your company provides it."]
    elif task_type == "refactor_modernization" and broad:
        tool, alts = "devin", ["claude"]
        reasons = ["Repo-wide, repetitive and well specified: suits an asynchronous agent that works through it and opens a PR.",
                   "Attach the modernization or dependency-upgrade playbook so steps and forbidden actions are explicit.",
                   "Prerequisite: the repository must already be connected in Devin; otherwise use Claude Code."]
    elif task_type in ("bug_fix", "refactor_modernization", "exploration") or (task_type == "feature_api" and multi):
        tool, alts = "claude", ["copilot"]
        reasons = ["Needs reading across several files and reasoning about cause or design before editing.",
                   "Plan mode produces a reviewable plan before any change (human review point).",
                   "Can run the project's tests in the terminal to show evidence."]
        if task_type == "exploration":
            alts = ["copilot", "devin"]
            reasons.append("Devin Ask is an alternative if the repo is indexed there.")
    else:
        tool, alts = "copilot", ["claude"]
        reasons = ["Scoped change in files you already have open; fastest feedback loop in the editor.",
                   "The matching prompt file gives a consistent structure (/" +
                   {"test_creation": "test-plan", "pr_readiness": "pr-readiness", "data_sql": "sql-review"}.get(task_type, "jira-to-plan") + ").",
                   "Agent mode can run the tests and show results."]
    kit = KIT_FOR_TYPE.get(task_type, {})
    return {"tool": tool, "label": TOOLS[tool]["label"], "mode": TOOLS[tool]["mode"], "reasons": reasons,
            "alternatives": [{"tool": a, "label": TOOLS[a]["label"]} for a in alts],
            "kit_file": ("agent-kit/" + kit[tool]) if tool in kit else None,
            "kit_files": {k: "agent-kit/" + v for k, v in kit.items()}}


def related_prompts(task_type: str, tool: str, limit: int = 3) -> list[dict]:
    wf = {"feature_api": ["planning"], "bug_fix": ["debugging"], "test_creation": ["test_creation"],
          "refactor_modernization": ["refactoring", "modernization"], "pr_readiness": ["pr_readiness", "review"],
          "data_sql": ["data_sql"], "docs_communication": ["docs"], "exploration": ["docs", "planning"],
          "trivial_deterministic": ["refactoring"]}.get(task_type, [])
    lib = [p for p in prompt_library() if p.get("workflow") in wf]
    tool_key = {"copilot": "copilot", "claude": "claude_code", "devin": "devin", "writing": "m365", "no_ai": "no_ai"}[tool]
    lib.sort(key=lambda p: 0 if str(p.get("best_tool", "")).startswith(tool_key) else 1)
    return [{"id": p["id"], "title": p["title"], "when_to_use": p.get("when_to_use"), "template": p.get("template"),
             "best_tool": p.get("best_tool")} for p in lib[:limit]]


def analyze(text: str, complexity: str = "medium", task_type: str | None = None) -> dict:
    text = (text or "").strip()
    types = classify(text)
    tt = task_type or types[0]["type"]
    present, missing = assess(text, tt)
    ap = detect_anti_patterns(text, tt, {m["id"] for m in missing})
    r = route(text, tt, complexity)
    total = len(present) + len(missing)
    return {
        "task_type": tt,
        "task_label": TASK_TYPES[tt]["label"],
        "candidates": types[:3],
        "checklist": {"present": present, "missing": missing, "covered": len(present), "total": total},
        "questions": missing[:3],
        "anti_patterns": ap,
        "sensitive_data_warnings": scan_sensitive(text),
        "recommendation": r,
        "related_prompts": related_prompts(tt, r["tool"]),
        "privacy": "Processed in memory only. Not stored, not logged, never shown to managers.",
    }


def _bullets(text: str) -> list[str]:
    lines = [ln.strip(" -*\t") for ln in re.split(r"[\r\n]+", text) if ln.strip()]
    return lines


def build(text: str, answers: dict | None = None, tool: str | None = None, complexity: str = "medium",
          task_type: str | None = None, stack: str | None = None) -> dict:
    """Produce a ready-to-paste prompt for the chosen tool."""
    answers = {k: v.strip() for k, v in (answers or {}).items() if v and v.strip()}
    a = analyze(text, complexity, task_type)
    tt = a["task_type"]
    tool = tool or a["recommendation"]["tool"]
    title = _bullets(text)[0][:140] if text.strip() else "Task"
    labels = {c["id"]: c["label"] for c in a["checklist"]["present"] + a["checklist"]["missing"]}
    open_q = [q["question"] for q in a["checklist"]["missing"] if q["id"] not in answers]
    extra = "\n".join(f"- {labels.get(k, k)}: {v}" for k, v in answers.items())
    test_cmd = {"java": "mvn -q verify", "dotnet": "dotnet test", "typescript": "npm test", "python": "pytest -q",
                "playwright": "npx playwright test"}.get(stack or "", "the project's test command")
    source = text.strip()

    if tool == "no_ai":
        prompt = ("No prompt needed. Run the project's formatter or linter (for example `prettier --write`, `dotnet format`, "
                  "`black .`, `mvn spotless:apply`) or use the IDE's rename/refactor. Commit the result as its own small PR.")
    elif tool == "writing" or (tool in ("copilot", "claude") and tt == "docs_communication"):
        prompt = (f"Rewrite the following for {answers.get('audience', 'the intended audience')}. Keep it concise, plain and "
                  f"specific. Keep all facts unchanged and flag anything unclear instead of guessing.\n\nText:\n{source}\n"
                  "\nDo not include confidential data, customer data or credentials.")
    elif tool == "devin":
        prompt = (
            "## Overview\n"
            f"{title}\n\n"
            "## Source ticket\n"
            f"{source}\n"
            + (f"\n## Clarifications\n{extra}\n" if extra else "")
            + "\n## Procedure\n"
            "1. Read AGENTS.md and the repo's contributing/test docs first.\n"
            "2. Explore the relevant code and post a short plan (files, steps, risks) before changing anything; wait for approval.\n"
            "3. Implement in small, reviewable commits; one concern per PR (under ~400 changed lines).\n"
            f"4. Add or update tests for every behavior change; run {test_cmd} and lint.\n"
            "5. Open a draft PR with a description, test evidence and a risk/rollback note.\n\n"
            "## Specifications\n"
            "- All acceptance criteria above are covered by tests.\n- Build, tests and lint pass; results pasted in the PR.\n\n"
            "## Forbidden actions\n- Do not push to main or merge.\n- Do not change unrelated files or public interfaces not listed.\n"
            "- Do not use production data, real credentials or customer information.\n\n"
            "## Required from user\n" + ("\n".join(f"- {q}" for q in open_q) if open_q else "- Nothing further.")
            + "\n\nTip: attach the matching playbook from the agent kit (for example !jira-ticket-to-pr)."
        )
    else:
        header = ("Use the ticket-to-plan skill. Start in plan mode and do not edit files until I approve the plan.\n\n"
                  if tool == "claude" else
                  "Follow .github/copilot-instructions.md and AGENTS.md. First reply with a plan only; wait for my OK before editing.\n\n")
        if tt == "test_creation":
            header = (("Use the test-creation skill. " if tool == "claude" else "Use the /test-plan approach. ")
                      + "First list the test cases (happy, negative, boundary) mapped to each acceptance criterion and wait for my OK.\n\n")
        if tt == "bug_fix":
            header = (("Use the systematic-debugging skill. " if tool == "claude" else "")
                      + "Investigate first: do not change code until you have a reproduction and a root-cause hypothesis backed by evidence.\n\n")
        prompt = (
            header
            + f"## Goal\n{title}\n\n"
            + f"## Ticket\n{source}\n\n"
            + (f"## Clarifications\n{extra}\n\n" if extra else "")
            + "## Constraints\n- Keep the change small and focused (one concern, under ~400 changed lines).\n"
            "- Follow existing patterns in the codebase; do not change public interfaces unless listed above.\n"
            "- Never include secrets, credentials, personal or production data.\n\n"
            + "## Steps\n1. List the files you will touch and why.\n2. Propose the plan and tests; wait for approval.\n"
            "3. Implement step by step.\n"
            + f"4. Run {test_cmd} and lint; paste the summary lines as evidence.\n\n"
            + "## Output\n- Summary of changes\n- Test evidence\n- Risks and follow-ups\n"
            + ("\n## Open questions (ask me, do not assume)\n" + "\n".join(f"- {q}" for q in open_q) if open_q else "")
        )
    return {"tool": tool, "tool_label": TOOLS[tool]["label"], "task_type": tt, "prompt": prompt,
            "open_questions": open_q, "kit_file": a["recommendation"]["kit_files"].get(tool),
            "human_review": "Review the agent's plan and the final diff before merging. Compass never applies changes for you.",
            "privacy": a["privacy"]}


def parse_jira_csv(csv_text: str) -> list[dict]:
    """Parse a Jira CSV export (no API needed). Recognizes common column names."""
    reader = csv.DictReader(io.StringIO(csv_text))
    out = []
    for row in reader:
        norm = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
        key = norm.get("issue key") or norm.get("key") or ""
        summary = norm.get("summary") or ""
        desc = norm.get("description") or ""
        ac = norm.get("acceptance criteria") or norm.get("custom field (acceptance criteria)") or ""
        itype = norm.get("issue type") or ""
        text = summary + ("\n" + desc if desc else "") + ("\nAcceptance criteria:\n" + ac if ac else "")
        if summary:
            out.append({"key": key, "summary": summary, "issue_type": itype, "text": text})
    return out[:200]
