# Data dictionary

All data is synthetic, generated deterministically by `compass/synth.py` (seed 20261015). CSV copies are in `data/synthetic/` (`python -m compass export-data`). There are no names, emails, free-text fields, source code or prompt content.

## signals.db

### teams
| Column | Type | Description |
|---|---|---|
| team_id | text | Pseudonymous team id, for example `T-ATLAS` |
| name, domain | text | Synthetic labels |
| stack | text | `java`, `dotnet`, `typescript`, `python` |
| project_complexity | text | `low`, `medium`, `high` |
| source | text | Always `synthetic:org_metadata` |

### engineers
| Column | Type | Description |
|---|---|---|
| engineer_id | text | Pseudonymous id, for example `E-ATL-01` |
| codename | text | Synthetic display name, for example `Falcon` |
| team_id | text | Team |
| seniority | text | `junior`, `mid`, `senior`, `lead`, `sdet` |
| role, stack, stack_label, project_complexity, primary_workflows | text | Persona context used to tailor advice |

### usage_weekly (GenAI usage metadata, one row per engineer-week)
| Column | Meaning |
|---|---|
| record_id | `U-<engineer>-W<week>`, cited as evidence |
| copilot_sessions, claude_sessions, devin_sessions | Sessions per week per tool |
| agent_mode_share | Share of sessions in agent mode |
| suggestion_accept_rate | Completion acceptance rate |
| chat_turns_avg | Average turns per agent/chat session |
| abandoned_session_rate | Share of sessions ended without a kept change |
| noncode_tasks_in_coding_agent | Writing tasks (emails, docs) done in a coding agent per week |
| large_task_chat_sessions | Repo-wide tasks driven turn by turn in chat per week |
| repo_has_instructions | 1 if the main repo has AGENTS.md or copilot-instructions.md |

### delivery_weekly (SCM/CI metadata, one row per engineer-week)
| Column | Meaning |
|---|---|
| record_id | `D-<engineer>-W<week>` |
| prs_opened | PRs opened |
| pr_size_loc_median | Median changed lines per PR |
| pr_cycle_time_hrs | Open to merge, hours |
| review_rounds_avg | Address-and-resend rounds per PR |
| ci_first_pass_rate | Share of pushes passing CI first time |
| tests_added_per_pr | Test cases added per PR |
| test_creation_time_min | Minutes spent writing tests per PR |
| flaky_test_rate | Share of test runs with a flaky result |
| ai_assisted_test_share | Share of new tests drafted with AI |
| pr_template_used_rate | Share of PRs using the template or readiness checklist |
| plan_first_rate | Share of agent sessions started with a plan |
| tests_first_rate | Share of changes where tests were written first |

### seed_labels
Ground truth for evaluation only (`engineer_id`, `patterns`). The engine never reads it.

## private.db (engineer-owned)

| Table | Columns | Notes |
|---|---|---|
| feedback | engineer_id, rec_key, action (`useful`, `not_useful`, `dismissed`, `restored`, `tried`), reason (fixed list), created_at | No free text. Deletable by the engineer. |
| coaching_history | engineer_id, rec_key, shown_at | Deletable by the engineer. |

## Seeded patterns

`large_prs`, `low_ci_pass`, `long_sessions`, `few_tests`, `no_context`, `wrong_tool`, `flaky_ai_tests`, `low_adoption`, `modernization_in_chat`, `healthy`, and two adopter patterns (`adopter_pr`, `adopter_tests`) that show the problem in weeks 1-4 and the improved practice in weeks 5-8. These provide the before/after demonstration from data.

## Mapping the organizers' sample data

When the organizers' sample file is available, map its columns to the fields above in `compass/synth.py` or add a loader that writes the same tables. Any extra column must pass `compass/compliance.py` (allow-list, no PII, no free text).
