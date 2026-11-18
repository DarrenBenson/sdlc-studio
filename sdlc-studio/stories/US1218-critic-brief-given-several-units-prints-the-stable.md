# US1218: Critic brief given several units prints the stable blocks once and each unit's scope, criteria and diff apart

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0680
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_several_units.py
> **Epic:** EP0332
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Critic brief given several units prints the stable blocks once and each unit's scope, criteria and diff apart
**So that** CR0680 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Several units share one set of stable blocks

- **Given** two units ready for review by the same seat
- **When** `critic.py brief --unit <a> --unit <b> --seat qa` is run
- **Then** the seat charter, the standing practices, the lessons and the return contract are each printed once, and each unit's scope, acceptance criteria and UNIT DIFF are printed under that unit's own heading. Fails on: two whole briefs printed one after the other, or one unit's diff under the other's heading
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_several_units.py::BriefSeveralUnitsTests::test_the_stable_blocks_print_once_and_each_unit_apart

### AC2: Each unit keeps its own verdict file and its verdict records

- **Given** the same two units, briefed together
- **When** the brief is read, and a verdict for each unit is recorded with the command the brief prints for it
- **Then** the brief names a separate verdict file path and record command for each unit, at that unit's own tier, and both verdicts are recorded against the brief. Fails on: one verdict path for both units, or the second unit's record refused because the fingerprint is another brief's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_several_units.py::BriefSeveralUnitsTests::test_each_unit_has_its_own_verdict_path_and_records

### AC3: One refused unit refuses the whole brief, and one unit prints as before

- **Given** a project that blocks a brief without a recorded self-check, one unit with a current self-check and one without
- **When** `critic.py brief` is run for both together, and then for the first alone
- **Then** the joint brief is refused naming the unit without a self-check and prints no part of the other; the single brief is byte-identical to the one printed before this change. Fails on: a joint brief that silently leaves a unit out, or a changed single-unit brief
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_several_units.py::BriefSeveralUnitsTests::test_a_refused_unit_refuses_the_brief_and_one_unit_is_unchanged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
