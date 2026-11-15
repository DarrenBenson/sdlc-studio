# US1165: A project sets builder and reviewer reasoning effort; the plan stamps it on each unit, the lane brief names it, and a reviewer below its builder is refused without a recorded decision

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0699
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint.md, tools/check_budgets.py, tools/tests/test_check_budgets.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_keys_read.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_config_code_defaults.py, .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py, changelog.d/US1165.md
> **Epic:** EP0311
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** a project sets builder and reviewer reasoning effort; the plan stamps it on each unit, the lane brief names it, and a reviewer below its builder is refused without a recorded decision
**So that** I know what each team's delivery costs per point and can hold it to a monthly budget

## Acceptance Criteria

- **AC1:** Given a project that sets no `routing.effort`, when `sprint.py plan` runs and a lane brief is printed, then each unit's plan row carries `effort: {builder: inherit, reviewer: inherit}` and the brief says to dispatch at the session's own effort, which is today's behaviour.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py::EffortSettingTests::test_the_default_inherits_the_session_effort
- **AC2:** Given `routing.effort: {builder: low, reviewer: medium}`, when `sprint.py plan` runs and `sprint.py lane brief --units <id>` is printed, then the plan row carries both values and the brief names the effort to dispatch the builder at and the effort for its reviewer.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py::EffortSettingTests::test_a_set_effort_reaches_the_plan_and_the_lane_brief
- **AC3:** Given a reviewer effort below its builder's (builder high, reviewer low), when `sprint.py plan` runs, then it refuses naming both values, unless `routing.effort.reviewer_below_builder` names a decision id present in sdlc-studio/decisions.md, in which case it plans and prints that id.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py::EffortSettingTests::test_a_reviewer_below_its_builder_is_refused_without_a_decision
- **AC4:** Given an effort value outside inherit, low, medium, high, xhigh and max, when `sprint.py plan` runs, then it refuses naming the key and the allowed values.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py::EffortSettingTests::test_an_unknown_effort_value_is_refused

## Notes

- Serves Abena Osei's End goal 3; delivers part of CR0699 (D0479).
- AC1 must fail on: a default other than inherit, or a plan row with no effort
- AC2 must fail on: a brief silent on effort when one is set, or the plan reading `routing.enabled` before stamping effort (effort applies with model routing off)
- AC3 must fail on: a lower reviewer effort accepted silently, or a decision id that does not exist accepted
- AC4 must fail on: an unknown value passed through to the brief
- Start from config-defaults.yaml:244-262 (the routing block; `critic_tier: match` at :258 is the model-tier rule this mirrors), sprint.py `_enrich_routing` (:1133-1155, which stamps tier and model per unit only when routing is enabled), `lane_brief_text` (:2770) and cmd_lane (:9393). route.py is read for the critic_tier precedent, not edited; test_route.py stays green.
- Values follow the effort levels an agent spawn takes (low, medium, high, xhigh, max) plus inherit. reference-sprint.md's wave dispatch step tells the orchestrator to pass the brief's value when it spawns the builder and the reviewer.
- reference-config.md is 729 lines against an ALLOWLIST ceiling of 695 (tools/check_budgets.py:74) plus 5%, about 729.75: one added line fails the budgets lane. Document the key in its #routing section and either trim as many lines elsewhere in the page or raise the ceiling with a reason in check_budgets.py and the expected dict in test_check_budgets.py (:236-246). Both files are in Affects so either route lands.
- Headless lanes (`sprint lane run --harness`, lanes.py:629 headless_command) are out of scope: pass effort there only in a later unit, once each CLI's --help is confirmed to take it.
- Stamp effort on the plan rows so the run record's plan snapshot keeps it; story B then reads it from the run record without touching sprint.py.
- The new test carries `# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
