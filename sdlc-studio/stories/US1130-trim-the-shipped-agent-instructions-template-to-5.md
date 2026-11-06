# US1130: Trim the shipped agent-instructions template to 5,000 chars and name the start context a delivery session pays

> **Status:** Ready
> **Delivers:** CR0677
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py (new), changelog.d/US1130.md
> **Epic:** EP0300
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Trim the shipped agent-instructions template to 5,000 chars and name the start context a delivery session pays
**So that** every consuming-project session starts about 2,000 tokens smaller while keeping its only always-loaded statement of its gates, and an operator can see what a session's start costs

## Acceptance Criteria

- **AC1:** Given `templates/agent-instructions.md`, then it is at most 5,000 chars (from 10,893), keeps its `## Operating doctrine` and `## Non-negotiable gates` sections with the gate list and commands, and points at `reference-doctrine.md` for the text it moves. Fails on: a size cap above 5,000, or a cut that drops a gate from the list.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_the_template_fits_and_keeps_its_gates
- **AC2:** Given the trimmed template, then the lines tests read survive: the `agent-instructions.md#operating-doctrine` anchor (`test_status.py`), the trunk-integration rule stated on one line with its commit clause, its `pr-required` opt-in and the words push `main` (`test_trunk_integration.py`), the CR-sizing claim (`test_lean_cr_filing.py`), and `test_init.py`, `test_validate.py`, `test_lean_guided_stage_confirm.py`, `test_lean_migrate_config.py` and `tools/tests/test_check_neutrality.py` pass unedited; a project initialised from it passes `validate`. Fails on: the trunk rule line or the doctrine heading cut.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_an_initialised_project_s_agents_md_still_validates
- **AC3:** Given `reference-sprint.md#cost-anatomy`, then it recommends a project `.claude/settings.json` that disables the plugins and connectors a delivery session does not use, and says claude.ai connectors may not be switchable per project. Fails on: the recommendation absent or stated as already enforced.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_reference_sprint_recommends_the_settings_file
- **AC4:** Given a session transcript whose first main-thread call carries a known input and cache, when `sprint.py cost --anatomy` renders, then its header names the main thread's start context as that first call's input plus cache. Fails on: the header omitting it, or reading the largest call's context instead of the first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_the_main_thread_start_context_is_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria and Verify checks authored |
