# US1034: critic.py seats adds a second, different seat to a high-risk unit

> **Status:** Draft
> **Delivers:** CR0622
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-scripts-review.md, AGENTS.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_second_seat.py, changelog.d/US1034.md
> **Epic:** EP0284
> **Points:** 3
> **Depends on:** US1029, US1032, US1033
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose riskiest units touch production runtime or alerting
**I want** `critic.py seats` to name a second seat from a different role for a high-risk unit, and say what made it high risk
**So that** the minority of units that can page someone or break a running system get a second lens, at the cost of one more review on those units only

## Acceptance Criteria

- **AC1:** Given an 8-point story and a 3-point story, when `critic.py seats` runs on each, then the 8-point story is given a second seat different from its first, citing its Points against `review.second_seat.points`, and the 3-point story only one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_second_seat.py::SecondSeatTests::test_an_eight_point_unit_gets_a_second_different_seat
- **AC2:** Given three 3-point stories whose `Affects production runtime:` field reads true, false and the unfilled `{{affects_production_runtime}}` placeholder, when `critic.py seats` runs on each, then only the first is given a second seat, citing the field
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_second_seat.py::SecondSeatTests::test_only_a_true_runtime_field_adds_a_second_seat
- **AC3:** Given a project `review.second_seat.paths` glob matching one of a 3-point story's Affects files, when `critic.py seats` runs, then it names a second seat citing that glob and file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_second_seat.py::SecondSeatTests::test_a_high_risk_path_gets_a_second_seat

## Notes

- Release: later (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the points trigger is dropped, or a second seat is added to every unit
- AC2 must fail on: the trigger fires on the field's presence rather than its value, so false and the placeholder add a seat; or the field is read under another name and never fires
- AC3 must fail on: only the shipped second_seat settings are read, never the project override
- Second seat: the next mapped seat that differs from the first, else the type's default when different, else the first of engineering, qa, product that differs and has a card. With none resolvable the output says so and names one seat; it never invents a seat. For a high-risk unit the 'one seat reviews the unit' line becomes the two seats and the reason.
- Config: `review.second_seat: {points: 8, paths: []}` in config-defaults.yaml. At d327d5d0, 42 of 2,005 stories and bugs here carry 8 or more points (about 2%).
- The runtime field has no tooled writer: `artifact.py new --type story` omits it, `--template full` writes the placeholder, and the 16 of 993 stories here that carry it all say false. Until something writes it, the configured-path trigger is the practical one. If the operator follows the panel and drops the field, AC2 is struck and the story is 2 points.
- AGENTS.md and reference-sprint.md say 'one independent reviewer per unit'; amended to 'and a second seat of a different role on a high-risk unit' only if the operator rules CR0622 in.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
