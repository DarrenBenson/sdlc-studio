# US1129: Cut AGENTS.md to 7,000 chars and gate the always-loaded files by size

> **Status:** Done
> **Delivers:** CR0677
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** AGENTS.md, CONTRIBUTING.md, .claude/skills/sdlc-studio/SKILL.md, tools/check_budgets.py, .githooks/pre-commit, tools/tests/test_check_budgets.py, tools/tests/test_agents_md_budget.py (new), changelog.d/US1129.md
> **Epic:** EP0300
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Cut AGENTS.md to 7,000 chars and gate the always-loaded files by size
**So that** every call of every session in this repository re-reads at least 3,200 fewer tokens of instructions, and the file cannot grow back unnoticed

## Acceptance Criteria

- **AC1:** Given the cut `AGENTS.md`, then it is at most 7,000 chars (from 15,786; at the measured 2.73 chars a token that is at least 3,200 tokens off every call, the CR's before-and-after bar), keeps the four start-here steps, the refusals table and one paragraph per non-negotiable rule, and each block it moves to `CONTRIBUTING.md` is linked from the line that names its subject. Fails on: a budget constant above 7,000, or a cut that drops a start-here step or leaves a moved block unlinked.
  - **Verify:** pytest tools/tests/test_agents_md_budget.py::AgentsMdBudgetTests::test_agents_md_fits_its_budget_and_keeps_its_spine
  - **Verified:** yes (2026-11-06)
- **AC2:** Given the cut, then every sentence a test or corpus Verify line reads survives, the test files themselves unedited: `fetch` (US0099), `forward-port.sh`, `forward-port.sh --check` and `forward-port.pin` (US0200, `test_forward_port.py`), `sprint sign` with no `reviewer of record` or `persona_resolve.py panel` (US0926), the `## What will refuse you` table naming `pre-push` and `gate_timing.py estimate --suite boundary-push` in a `| pre-push hook |` row with no fixed figure, ahead of the `**Enable the hooks` paragraph, `three tracked hooks`, `git push --no-verify` and `.githooks/pre-push` each in their own backticks (`test_pre_push_hook.py`, `test_push_first_estimate.py`), the `## Non-negotiable rules` paragraph led by `The push gate is the full-suite check.` (`test_agents_md_full_suite_rule.py`, `test_agentic_lessons_full_suite.py`), the exercise-every-claim paragraph naming `critic.py self-check record` and `review.author_self_check` (`test_author_self_check_repo.py`), `## Soft dependencies` with `coverage` (backticked) 7.10 or later within 2,000 chars of it (`test_lint_workflow_coverage.py`), and the `--list` pointers with no backticked lane key (`test_lean_commit_lanes.py`); those ten modules and the three Verify lines pass. Fails on: dropping the forward-porting or soft-dependency text the CR calls operator-only, or editing a pinning test to pass.
  - **Verify:** pytest tools/tests/test_agents_md_budget.py::AgentsMdBudgetTests::test_every_pinned_phrase_survives
  - **Verified:** yes (2026-11-06)
- **AC3:** Given an `AGENTS.md` one char over its budget, when `tools/check_budgets.py` runs (the pre-commit `budgets` lane), then it exits non-zero naming the file, its size and the budget, and at the budget it passes; the lane's stated rule in `.githooks/pre-commit` names the always-loaded files. Fails on: the check never reading `AGENTS.md`, or reading it in lines.
  - **Verify:** pytest tools/tests/test_check_budgets.py::AlwaysLoadedBudgetTests::test_agents_md_over_budget_is_refused_naming_its_size
  - **Verified:** yes (2026-11-06)
- **AC4:** Given a `SKILL.md` over its declared token estimate, or one whose `description` exceeds 600 chars, then `check_budgets.py` refuses naming the estimate or the length; the shipped description (984 chars today) is cut to at most 600 keeping its `NOT for:` clause and every test that reads it passes. Fails on: the SKILL.md check still counting lines only, or a description cap above 600.
  - **Verify:** pytest tools/tests/test_check_budgets.py::AlwaysLoadedBudgetTests::test_skill_md_token_and_description_budgets_refuse
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria and Verify checks authored |
