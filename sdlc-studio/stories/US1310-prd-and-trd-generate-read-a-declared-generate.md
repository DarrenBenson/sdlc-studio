# US1310: PRD and TRD generate read a declared `generate.runtime_inputs` folder of schema dumps, stored-procedure source and trace exports, cite each file used, and state that the skill never connects to a running system

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0737
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-prd.md, .claude/skills/sdlc-studio/reference-trd.md, .claude/skills/sdlc-studio/help/brownfield-runbook.md, tools/tests/test_generate_runtime_inputs.py, changelog.d/US1310.md
> **Epic:** EP0374
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** PRD and TRD generate read a declared `generate.runtime_inputs` folder of schema dumps, stored-procedure source and trace exports, cite each file used, and state that the skill never connects to a running system
**So that** CR0737 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Generate reads runtime exports from one folder and cites them

- **Given** `reference-prd.md`'s and `reference-trd.md`'s generate workflows
- **When** they are read
- **Then** each names `sdlc-studio/runtime-inputs/`, lists what belongs there (schema dumps, stored-procedure source, trace or log exports), and tells the agent to cite each file a requirement was drawn from. Fails on: a workflow that names the folder but asks for no citation, or one workflow without it
- **Verify:** pytest tools/tests/test_generate_runtime_inputs.py::RuntimeInputsTests::test_both_generate_workflows_read_and_cite_the_runtime_inputs_folder

### AC2: The skill never connects to a running system (D0518)

- **Given** the same two workflows and the runbook
- **When** they are read
- **Then** each says the skill reads exports only and never connects to a database or a running service, and the runbook's extraction stage says what to export and that an empty folder means generate works from source alone and says so in the spec. Fails on: any instruction to connect, query or log in to a live system
- **Verify:** pytest tools/tests/test_generate_runtime_inputs.py::RuntimeInputsTests::test_no_page_tells_the_agent_to_connect_to_a_live_system

### AC3: The pages stay within their budgets

- **Given** the changed pages
- **When** `python3 tools/check_budgets.py`, `tools/check_links.py` and `tools/lint-style.sh` are run
- **Then** all pass. Fails on: `reference-prd.md` over its line ceiling
- **Verify:** pytest tools/tests/test_generate_runtime_inputs.py::RuntimeInputsTests::test_the_pages_pass_budget_link_and_style_checks

## Notes

- Groomed to a fixed folder instead of the `generate.runtime_inputs` key CR0737 proposed: generate mode is agent-driven, no script would read the key, and BG0831's test refuses a documented key nothing honours. Config files dropped from Affects.
- `reference-prd.md` is at its ceiling (660 of 660): replace or tighten a line rather than add, and keep the detail in the runbook.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
