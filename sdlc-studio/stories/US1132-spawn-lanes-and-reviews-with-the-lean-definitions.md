# US1132: Spawn lanes and reviews with the lean definitions and carry the builder traps in the lane brief

> **Status:** Done
> **Delivers:** CR0674
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-epic.md, .claude/skills/sdlc-studio/lessons/ (new LL files for the builder traps), .claude/skills/sdlc-studio/lessons/_index.md, .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, changelog.d/US1132.md, sdlc-studio/lessons.jsonl
> **Epic:** EP0300
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Spawn lanes and reviews with the lean definitions and carry the builder traps in the lane brief
**So that** every spawned agent stops paying for tools it never calls, a run needs no hand-written builder brief, and an agent that starts heavy is flagged

## Acceptance Criteria

- **AC1:** Given every spawn site the references name (`reference-epic.md`'s wave example, `reference-agent-prompt-template.md`, `reference-sprint.md`'s wave step), then a builder is spawned as `sdlc-builder` and a reviewer as `sdlc-reviewer`, with `general-purpose` named as the fallback for a harness with no agent config (Codex CLI; Copilot CLI and OpenCode keep their own). Fails on: any `subagent_type="general-purpose"` left as the primary at a spawn site.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::SpawnSiteTests::test_every_spawn_site_names_the_lean_definition
  - **Verified:** yes (2026-11-06)
- **AC2:** Given `reference-sprint.md`'s wave step, then it launches a parallel wave's first agent alone and the rest after it has started, so they start on a warm shared prefix. Fails on: the step or the `reference-epic.md` example still launching every agent of a wave in one message.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::SpawnSiteTests::test_the_wave_launches_its_first_agent_first
  - **Verified:** yes (2026-11-06)
- **AC3:** Given the durable traps from run six's builder brief and run seven's builder notes filed as lessons, when `sprint plan --export-lanes` writes a builder unit's lane brief, then its lessons block carries each trap's rule. Fails on: the traps written into a reference file the lane brief does not read, or filed under a phase the lane brief's digest does not select.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::SpawnSiteTests::test_the_lane_brief_carries_the_builder_traps
  - **Verified:** yes (2026-11-06)
- **AC4:** Given a subagent transcript whose first call's context exceeds `cost.agent_start_budget` (a new key in `config-defaults.yaml`, documented in `reference-config.md`), when `sprint.py cost --anatomy` renders, then that agent is flagged with its start and the budget, and one under it is not. Fails on: the flag comparing the largest call instead of the first, or the key read from nowhere.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_a_subagent_over_its_start_budget_is_flagged
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria and Verify checks authored |
| 2026-11-06 | Claude Opus 5.5 | Affects widened mid-build: a lane brief reads its lessons from `sdlc-studio/lessons.jsonl`, not the cross-project `lessons/` registry, so AC3's builder traps must be recorded there (grouped to fit the per-phase cap) |
