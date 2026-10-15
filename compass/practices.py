"""Reusable practice catalog.

Each practice names the workflow signals it is associated with improving (AC7),
the evidence behind it (sourced, see docs/research/evidence.md), where engineers
can apply it with the agent kit (Copilot prompt file, Claude/Copilot skill, Devin
playbook) and a conservative, clearly labeled simulation assumption used only for
before/after projections (AC12).
"""

PRACTICES = {
    "pr-slicing": {
        "code": "P1",
        "title": "Slice work into small, single-concern PRs",
        "workflow": "pr_readiness",
        "type": "workflow",
        "summary": "Keep each PR under about 400 changed lines and one concern. Ask the agent to propose slices before coding.",
        "signals": ["pr_size_loc_median", "review_rounds_avg", "pr_cycle_time_hrs"],
        "evidence": [
            {"claim": "Reviews of 200-400 lines find 70-90% of defects; effectiveness drops beyond 400 lines.",
             "source": "SmartBear / Cisco code review study",
             "url": "https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/"},
            {"claim": "Working in small batches amplifies the positive impact of AI adoption.",
             "source": "DORA capabilities: working in small batches",
             "url": "https://dora.dev/capabilities/working-in-small-batches/"},
        ],
        "kit": {"copilot": "agent-kit/.github/prompts/slice-pr.prompt.md",
                "claude": "agent-kit/.claude/skills/pr-slicing/SKILL.md",
                "devin": "agent-kit/devin/playbooks/jira-ticket-to-pr.devin.md"},
        "prompt_id": "pr-slice-plan",
        "simulation": {"pr_size_loc_median": ("cap", 300), "review_rounds_avg": ("mult", 0.65),
                       "pr_cycle_time_hrs": ("mult", 0.6)},
    },
    "pr-readiness-selfcheck": {
        "code": "P2",
        "title": "Run an AI readiness self-check before requesting review",
        "workflow": "pr_readiness",
        "type": "prompt",
        "summary": "Before opening a PR, have the agent check the diff against a readiness checklist (tests, description, risks, no secrets, no debug code) and show build/test evidence.",
        "signals": ["review_rounds_avg", "ci_first_pass_rate", "pr_template_used_rate"],
        "evidence": [
            {"claim": "Lightweight review practices find about as many defects as formal inspection in under 20% of the time.",
             "source": "SmartBear / Cisco code review study",
             "url": "https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/"},
            {"claim": "Over 80% of reviews at Google finish in a single address-and-resend round.",
             "source": "Sadowski et al., Modern Code Review at Google (secondary summary)",
             "url": "https://research.google/pubs/modern-code-review-a-case-study-at-google/"},
        ],
        "kit": {"copilot": "agent-kit/.github/prompts/pr-readiness.prompt.md",
                "claude": "agent-kit/.claude/skills/pr-readiness-selfcheck/SKILL.md",
                "devin": "agent-kit/devin/playbooks/pr-readiness.devin.md"},
        "prompt_id": "pr-readiness-check",
        "simulation": {"review_rounds_avg": ("mult", 0.7), "ci_first_pass_rate": ("add", 0.15),
                       "pr_template_used_rate": ("set", 0.9)},
    },
    "test-first-acceptance": {
        "code": "P3",
        "title": "Derive tests from acceptance criteria first",
        "workflow": "test_creation",
        "type": "prompt",
        "summary": "Give the agent the acceptance criteria and ask for a test plan (happy, negative, boundary) before implementation, then generate tests in your stack's framework with meaningful assertions.",
        "signals": ["tests_added_per_pr", "test_creation_time_min", "tests_first_rate"],
        "evidence": [
            {"claim": "Test-driven teams at Microsoft and IBM cut pre-release defect density 40-90% for 15-35% more initial time.",
             "source": "Nagappan et al., Empirical Software Engineering 2008",
             "url": "https://doi.org/10.1007/s10664-008-9062-z"},
            {"claim": "Ambiguous or incomplete task descriptions reduce LLM first-try correctness by 20-30%.",
             "source": "Larbi et al., 2025",
             "url": "https://arxiv.org/html/2507.20439v1"},
        ],
        "kit": {"copilot": "agent-kit/.github/prompts/test-plan.prompt.md",
                "claude": "agent-kit/.claude/skills/test-creation/SKILL.md",
                "devin": "agent-kit/devin/playbooks/test-creation.devin.md"},
        "prompt_id": "test-plan-from-story",
        "simulation": {"tests_added_per_pr": ("min", 2.5), "test_creation_time_min": ("mult", 0.55),
                       "tests_first_rate": ("set", 0.65)},
    },
    "plan-then-implement": {
        "code": "P4",
        "title": "Plan first, then implement in small steps",
        "workflow": "pr_readiness",
        "type": "agent",
        "summary": "Start agent sessions by asking for a plan (files, steps, risks, tests). Approve it, then implement step by step instead of steering a long chat.",
        "signals": ["chat_turns_avg", "abandoned_session_rate", "plan_first_rate"],
        "evidence": [
            {"claim": "Spec-driven development: agents need unambiguous instructions; intent is the source of truth.",
             "source": "GitHub Spec Kit",
             "url": "https://github.blog/ai-and-ml/github-copilot/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/"},
            {"claim": "Experienced developers were measured 19% slower with AI on familiar code, while believing they were faster.",
             "source": "METR 2025",
             "url": "https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/"},
        ],
        "kit": {"copilot": "agent-kit/.github/prompts/jira-to-plan.prompt.md",
                "claude": "agent-kit/.claude/skills/writing-plans/SKILL.md",
                "devin": "agent-kit/devin/playbooks/jira-ticket-to-pr.devin.md"},
        "prompt_id": "implementation-plan",
        "simulation": {"chat_turns_avg": ("mult", 0.55), "abandoned_session_rate": ("mult", 0.45),
                       "plan_first_rate": ("set", 0.7)},
    },
    "context-pack": {
        "code": "P5",
        "title": "Give agents a short, human-written context pack",
        "workflow": "pr_readiness",
        "type": "agent",
        "summary": "Add AGENTS.md / copilot-instructions.md with build and test commands, conventions and guardrails so every agent session starts with project context.",
        "signals": ["repo_has_instructions", "chat_turns_avg", "ci_first_pass_rate"],
        "evidence": [
            {"claim": "With AGENTS.md present, median agent runtime fell 28.6% with comparable task completion.",
             "source": "Lulla et al., 2026 (preprint)", "url": "https://arxiv.org/abs/2601.20404"},
            {"claim": "Developer-written context files improved agent success about 4%; auto-generated ones did not.",
             "source": "Gloaguen et al., 2026 (preprint)", "url": "https://arxiv.org/html/2602.11988v1"},
        ],
        "kit": {"copilot": "agent-kit/.github/prompts/create-agents-md.prompt.md",
                "claude": "agent-kit/.claude/skills/context-pack/SKILL.md",
                "devin": "agent-kit/devin/knowledge/repo-conventions.md"},
        "prompt_id": "context-pack-agents-md",
        "simulation": {"repo_has_instructions": ("set", 1), "chat_turns_avg": ("mult", 0.8),
                       "ci_first_pass_rate": ("add", 0.05)},
    },
    "verify-before-done": {
        "code": "P6",
        "title": "Make the agent show test evidence before 'done'",
        "workflow": "pr_readiness",
        "type": "workflow",
        "summary": "Require the agent to run build, tests and lint locally and paste the results before you push. No evidence, no push.",
        "signals": ["ci_first_pass_rate", "review_rounds_avg"],
        "evidence": [
            {"claim": "Each 25% increase in AI adoption was associated with an estimated 7.2% drop in delivery stability.",
             "source": "DORA 2024", "url": "https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report"},
        ],
        "kit": {"copilot": "agent-kit/.github/prompts/self-review.prompt.md",
                "claude": "agent-kit/.claude/skills/verification-before-completion/SKILL.md",
                "devin": "agent-kit/devin/playbooks/pr-readiness.devin.md"},
        "prompt_id": "self-review-strict",
        "simulation": {"ci_first_pass_rate": ("add", 0.2), "review_rounds_avg": ("mult", 0.85)},
    },
    "right-tool-for-task": {
        "code": "P7",
        "title": "Route each task to the right tool",
        "workflow": "pr_readiness",
        "type": "agent",
        "summary": "Use Copilot for in-editor changes, Claude Code for multi-file reasoning, Devin for long well-specified async work, a writing assistant for documents and email, and plain tooling (formatter, codemod) for deterministic work.",
        "signals": ["noncode_tasks_in_coding_agent", "large_task_chat_sessions", "devin_sessions"],
        "evidence": [
            {"claim": "Developers lose substantial time to organizational inefficiencies even when AI saves time on coding.",
             "source": "Atlassian Developer Experience Report 2025",
             "url": "https://www.atlassian.com/blog/developer/developer-experience-report-2025"},
        ],
        "kit": {"copilot": "agent-kit/tool-routing-guide.md",
                "claude": "agent-kit/.claude/skills/right-tool-for-task/SKILL.md",
                "devin": "agent-kit/devin/playbooks/modernization-migration.devin.md"},
        "prompt_id": "route-task-to-tool",
        "simulation": {"devin_sessions": ("min", 1), "noncode_tasks_in_coding_agent": ("mult", 0.3),
                       "large_task_chat_sessions": ("mult", 0.3)},
    },
    "flaky-test-hardening": {
        "code": "P8",
        "title": "Harden AI-generated tests against flakiness",
        "workflow": "test_creation",
        "type": "prompt",
        "summary": "Review generated tests for fixed sleeps, shared data and brittle selectors; prefer web-first assertions, isolated fixtures and deterministic waits.",
        "signals": ["flaky_test_rate", "ci_first_pass_rate"],
        "evidence": [
            {"claim": "About 16% of tests at Google show some flakiness and 84% of pass-to-fail transitions involve a flaky test.",
             "source": "Google Testing Blog", "url": "https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html"},
            {"claim": "Flaky tests consumed at least 2.5% of productive developer time in an industrial case study.",
             "source": "Leinen et al., ICST 2024",
             "url": "https://conf.researchr.org/details/icst-2024/icst-2024-industry/1/Cost-of-Flaky-Tests-in-CI-An-Industrial-Case-Study"},
        ],
        "kit": {"copilot": "agent-kit/.github/prompts/fix-flaky-test.prompt.md",
                "claude": "agent-kit/.claude/skills/flaky-test-hardening/SKILL.md",
                "devin": "agent-kit/devin/playbooks/flaky-test-fix.devin.md"},
        "prompt_id": "flaky-test-diagnose",
        "simulation": {"flaky_test_rate": ("mult", 0.35), "ci_first_pass_rate": ("add", 0.08)},
    },
    "starter-path": {
        "code": "L1",
        "title": "30-minute guided starter path",
        "workflow": "pr_readiness",
        "type": "learning",
        "summary": "A short hands-on path: one context pack, one plan-first session, one readiness self-check on a real ticket.",
        "signals": ["copilot_sessions", "claude_sessions"],
        "evidence": [
            {"claim": "In field experiments, less experienced developers adopted AI tools more and gained more.",
             "source": "Cui et al., Microsoft/Accenture field experiments",
             "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4945566"},
        ],
        "kit": {"copilot": "agent-kit/README.md", "claude": "agent-kit/.claude/skills/brainstorming/SKILL.md",
                "devin": "agent-kit/devin/README.md"},
        "prompt_id": "task-brief",
        "simulation": {"copilot_sessions": ("min", 8), "claude_sessions": ("min", 2)},
    },
}

SIGNAL_META = {
    # signal: (label, unit, better)  better = "lower" | "higher"
    "pr_size_loc_median": ("Median PR size", "lines", "lower"),
    "review_rounds_avg": ("Review rounds per PR", "rounds", "lower"),
    "pr_cycle_time_hrs": ("PR cycle time", "hours", "lower"),
    "ci_first_pass_rate": ("CI first-pass rate", "%", "higher"),
    "pr_template_used_rate": ("PR template used", "%", "higher"),
    "tests_added_per_pr": ("Tests added per PR", "tests", "higher"),
    "test_creation_time_min": ("Time to create tests", "minutes", "lower"),
    "tests_first_rate": ("Tests written first", "%", "higher"),
    "chat_turns_avg": ("Chat turns per agent session", "turns", "lower"),
    "abandoned_session_rate": ("Abandoned agent sessions", "%", "lower"),
    "plan_first_rate": ("Sessions started with a plan", "%", "higher"),
    "repo_has_instructions": ("Repo has agent instructions", "yes/no", "higher"),
    "noncode_tasks_in_coding_agent": ("Non-code tasks in coding agent", "per week", "lower"),
    "large_task_chat_sessions": ("Large multi-file tasks done in chat", "per week", "lower"),
    "devin_sessions": ("Devin sessions", "per week", "higher"),
    "flaky_test_rate": ("Flaky test rate", "%", "lower"),
    "ai_assisted_test_share": ("AI-assisted test share", "%", "higher"),
    "copilot_sessions": ("Copilot sessions", "per week", "higher"),
    "claude_sessions": ("Claude Code sessions", "per week", "higher"),
    "agent_mode_share": ("Agent-mode share", "%", "higher"),
}

PERCENT_SIGNALS = {k for k, v in SIGNAL_META.items() if v[1] == "%"}


def fmt(signal: str, value, unit: bool = False) -> str:
    if value is None:
        return "n/a"
    if signal in PERCENT_SIGNALS:
        return f"{round(value * 100)}%"
    if signal == "repo_has_instructions":
        return "yes" if value >= 0.5 else "no"
    if isinstance(value, float):
        txt = f"{round(value)}" if abs(value) >= 100 else f"{value:.1f}"
    else:
        txt = str(value)
    u = SIGNAL_META.get(signal, ("", "", ""))[1]
    return f"{txt} {u}" if unit and u not in ("%", "yes/no") else txt


def apply_effect(signal: str, value: float, effect) -> float:
    op, arg = effect
    if op == "mult":
        out = value * arg
    elif op == "add":
        out = value + arg
    elif op == "set":
        out = arg
    elif op == "cap":
        out = min(value, arg)
    elif op == "min":
        out = max(value, arg)
    else:
        out = value
    if signal in PERCENT_SIGNALS:
        out = max(0.0, min(1.0, out))
    return round(out, 3)
