# US1245: The shipped instruction templates and SKILL.md take the accepted cuts and reach projects on project upgrade

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0700
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/skills/sdlc-studio/templates/agents/sdlc-reviewer.md, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/templates/personas/amigos/engineering.md, .claude/skills/sdlc-studio/templates/personas/amigos/product.md, .claude/skills/sdlc-studio/templates/personas/amigos/qa.md, .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py, .claude/agents/sdlc-builder.md, .claude/agents/sdlc-reviewer.md, changelog.d/US1245.md
> **Epic:** EP0342
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The shipped instruction templates and SKILL.md take the accepted cuts and reach projects on project upgrade
**So that** CR0700 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The shipped files take the accepted cuts and keep the kept text

- **Given** CR0700's audit rows citing `templates/agent-instructions.md`, `templates/agents/`, SKILL.md and the shipped amigo seat cards
- **When** each cited file is read at HEAD
- **Then** the quoted text of every `changed` or `removed` row is gone, the quoted text of every `kept` row is still there, no file is larger than the audit recorded and their total is smaller. Fails on: an accepted cut not made, a kept rule cut, or a file grown by the rewrite
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::ShippedAuditCutsTests::test_accepted_cuts_are_made_and_no_file_grows

### AC2: The template keeps its gates and this repository's agent definitions match

- **Given** the cut template and agent definitions
- **When** the template's gate list is read, and `.claude/agents/` is compared with `templates/agents/`
- **Then** every rule sentence in the template's non-negotiable gates survives within the 5,000 character cap, and each of this repository's agent definitions is byte for byte the shipped one. Fails on: a gate's rule sentence cut or reworded, or a shipped definition changed while this repository's copy is left behind
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_the_template_fits_and_keeps_its_gates

### AC3: An initialised project receives the cut files

- **Given** a throwaway project with no AGENTS.md and no agent definitions
- **When** `init.py run` seeds it, and `project_upgrade.py` is then run on a project whose AGENTS.md still carries a removed passage
- **Then** the seeded AGENTS.md and agent definitions carry none of the removed text and pass the instruction hygiene check, and the upgrade names the stale AGENTS.md as owing a refresh from the template without rewriting it. Fails on: a seeded file still carrying the removed text, or an upgrade that reports a stale file clean or overwrites a project's own sections
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::ShippedAuditCutsTests::test_init_seeds_the_cut_files_and_upgrade_names_a_stale_one

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
