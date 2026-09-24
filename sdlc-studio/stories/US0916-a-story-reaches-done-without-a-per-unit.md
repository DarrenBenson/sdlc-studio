# US0916: A story reaches Done without a per-unit reviewer-of-record sign-off

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer closing a story
**I want** a story with green criteria and an independent delivery APPROVE to reach Done, with no evidence row or sign-off row demanded per unit
**So that** the one review decides a unit, and the operator's single signature at the end of the run replaces a rubber-stamp row per unit

## Acceptance Criteria

- **AC1:** Given a fixture project setting `review.two_role_after: 1` and a story past it with green criteria and an independent delivery APPROVE but no sign-off or evidence row, when `transition.py set <id> Done` runs, then it succeeds
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_done_needs_no_signoff
- **AC2:** Given that Done story, when `conformance.py check` runs, then it reports critiqued met and names neither `adversarial-pass evidence` nor `reviewer-of-record sign-off`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_conformance_names_no_two_role_half
- **AC3:** Given the same story with no delivery verdict, when it is moved to Done, then it is still refused naming the missing independent APPROVE, so the review bar survives
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_done_still_needs_an_independent_approve
- **AC4:** Given a batch of stories past the old cutoff, when `sprint.py plan` reports the batch's reachable end state, then it is Done, not capped at Review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_the_plan_reaches_done
- **AC5:** Given config-defaults.yaml, then it carries no `review.two_role_after` and no shipped script reads it; a Definition of Done line tagged `[check: review.two-role]` is reported by `validate.py` as a retired tag naming `migrate`, never refused as an unknown id
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_the_two_role_key_and_tag_are_retired
- **AC6:** Given every criterion whose stamped Verify selector names a test this story deletes (TwoRoleCutoffOnUlidIdsTests, CritiquedHalvesTests and the transition two-role gate tests; at least those on US0373), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
