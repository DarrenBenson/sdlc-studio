# US1153: sprint plan shows each unit's class and flags a unit that touches a higher class than its tag

> **Status:** Ready
> **Delivers:** CR0696
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag.py, changelog.d/US1153.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0307
> **Points:** 2
> **Depends on:** US1152
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** sprint plan shows each unit's class and flags a unit that touches a higher class than its tag
**So that** every release passes the change board on the evidence the run produced, with no separate write-up

## Acceptance Criteria

- **AC1:** Given a map and a batch, when `sprint plan` runs, then the plan lists each unit's class and the second review seat each high-class unit will need.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag.py::PlanShowsClassTests::test_plan_lists_class_per_unit_and_second_seat
- **AC2:** Given a unit tagged standard whose Affects touch a high-class component, when `sprint plan` runs, then it flags the unit, naming the file, the component and both classes, and exits 0 with no per-unit sign-off asked.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag.py::PlanFlagsHigherClassTests::test_flag_names_file_component_and_classes_and_never_refuses
- **AC3:** Given no component map, when `sprint plan` runs, then it prints exactly one line saying every unit is standard, and nothing refuses.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag.py::PlanNoMapTests::test_no_map_prints_one_line

## Notes

- Serves Abena Osei's End goal 1; delivers part of CR0696 (D0476).
- AC1 must fail on: Classes listed only for high units; the second seat not named; the class recomputed differently from the refine-time tag for an unchanged unit.
- AC2 must fail on: No flag when tag and files disagree; a refusal or prompt; a flag when the tag already equals or exceeds the touched class (the positive control).
- AC3 must fail on: The class block printed per unit with no map; zero lines; a non-zero exit.
- Follow the plan-block pattern of the TSD strategy: scripts/sprint.py:6114 `_print_test_strategy` (plan prints it, stores `data['test_strategy']`) with `render_test_strategy` :13209; add a sibling `_print_risk_classes` and `data['risk_classes']` so --write records it in the plan artefact. Print only; no change to the refusal paths in `cmd_plan` (:10759).
- Classifier comes from the first story's `scripts/lib/risk_class.py`; read the story's Risk-class field, else derive from Affects (bugs). Affects parse: reuse the split used at sprint.py ~13197 or `file_finding.declared_affects`.
- Second seat name: the first story's config key `risk.second_seat` (default a seat other than the unit's first reviewer; confirm the seat vocabulary in `persona_resolve.SEATS` and `sprint.review_seats` :3176).
- Plan approval stays one human step; add no per-unit confirmation (D0459).
- `test_sprint.py` already asserts plan output: grep 'test strategy' there to see what a new line might disturb.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run twelve grooming, D0476) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
