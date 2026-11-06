# US1131: Ship sdlc-builder and sdlc-reviewer agent definitions and draft them into each project's .claude/agents

> **Status:** Done
> **Delivers:** CR0674
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md (new), .claude/skills/sdlc-studio/templates/agents/sdlc-reviewer.md (new), .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/help/init.md, .claude/skills/sdlc-studio/templates/personas/amigos/engineering.md, .claude/skills/sdlc-studio/templates/personas/amigos/product.md, .claude/skills/sdlc-studio/templates/personas/amigos/qa.md, .claude/agents/sdlc-builder.md (new), .claude/agents/sdlc-reviewer.md (new), .claude/skills/sdlc-studio/scripts/tests/test_init.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py (new), changelog.d/US1131.md
> **Epic:** EP0300
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Ship sdlc-builder and sdlc-reviewer agent definitions and draft them into each project's .claude/agents
**So that** a lane or review agent in any project starts about 12k tokens smaller and still has every tool it uses

## Acceptance Criteria

- **AC1:** Given `templates/agents/sdlc-builder.md` and `sdlc-reviewer.md`, then each has a name, a description and a `tools` line of exactly Bash, Read, Edit, Write and Monitor, with no Skill, Agent, WebFetch, WebSearch or MCP tool. Fails on: the `tools` line omitted (which grants every tool), or Write or Monitor dropped (reviewers write verdict files).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::AgentDefinitionTests::test_each_definition_restricts_its_tools
  - **Verified:** yes (2026-11-06)
- **AC2:** Given a consuming-project fixture outside this repository, when `init.py`'s agents stage runs, then `.claude/agents/sdlc-builder.md` and `sdlc-reviewer.md` are drafted from the installed templates; a re-run leaves a definition the project edited untouched and names it skipped; on a project that already has `AGENTS.md`, the stage still drafts the missing definitions; `help/init.md` says so. Fails on: `AGENT_FILES` not listing them, the parent directory not created, or an edited copy overwritten without `force`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::AgentDefinitionStageTests::test_the_agents_stage_drafts_the_definitions_into_a_project
  - **Verified:** yes (2026-11-06)
- **AC3:** Given each definition and each amigo seat's review render, then it carries the hand-back contract: run every command in the foreground or wait for it; hand back in at most three lines (unit, outcome, hand-in path); no progress message unless blocked. Fails on: the contract missing from either definition or any one seat.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::AgentDefinitionTests::test_the_hand_back_contract_is_carried
  - **Verified:** yes (2026-11-06)
- **AC4:** Given this repository's `.claude/agents/`, then its two definitions are byte-identical to the shipped templates. Fails on: a hand-edited repository copy drifting from the template a consuming project receives.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::AgentDefinitionTests::test_this_repository_s_copies_match_the_templates
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria and Verify checks authored |
