# US0916: A story reaches Done without a per-unit reviewer-of-record sign-off

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_dor_dod.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py, changelog.d/US0916.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, AGENTS.md, sdlc-studio/bugs/BG0318-two-role-review-gate-silently-stands-down-for.md, sdlc-studio/bugs/BG0354-three-more-places-still-enumerate-the-v2-four.md, sdlc-studio/bugs/BG0417-transition-done-never-checks-the-two-role-rule.md, sdlc-studio/bugs/BG0581-the-goal-review-brief-states-a-reachable-end.md, sdlc-studio/stories/US0373-decompose-critiqued-into-its-named-halves-in-the.md, sdlc-studio/stories/US0626-an-unfinished-batch-unit-holds-the-close-through.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer closing a story
**I want** a story with green criteria and an independent delivery APPROVE to reach Done, with no evidence row or sign-off row demanded per unit
**So that** the one review decides a unit, and the operator's single signature at the end of the run replaces a rubber-stamp row per unit

## Acceptance Criteria

- **AC1:** Given a fixture project setting `review.two_role_after: 1` and a story past it with green criteria and an independent delivery APPROVE but no sign-off or evidence row, when `transition.py set <id> Done` runs, then it succeeds. Fails on: HEAD's `_two_role_gate` refusing the missing halves
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_done_needs_no_signoff
- **AC2:** Given that Done story, when `conformance.py check` runs, then it reports critiqued met and names neither `adversarial-pass evidence` nor `reviewer-of-record sign-off`; the same story with no delivery verdict reads critiqued unmet, naming the missing independent APPROVE, so the review bar survives in the lane. Fails on: HEAD naming the two-role halves, and on a deletion that removes the APPROVE bar with them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_conformance_names_no_two_role_half
- **AC3:** Given a fixture setting `review.two_role_after: 1` and a batch of stories past it, when `sprint.py plan` reports the batch's reachable end state, then it is Done, not capped at Review. Fails on: HEAD's `sprint.reachable_end_state`, which caps a past-cutoff batch at Review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_the_plan_reaches_done
- **AC4:** Given config-defaults.yaml, then it carries no `review.two_role_after` and no shipped script reads it; a Definition of Done line tagged `[check: review.two-role]` is reported by `validate.py` as a retired tag naming `migrate`, never refused as an unknown id, and the retired id is read from one registry in `sdlc_md` (for example `RETIRED_CHECK_IDS`, beside `DOR_DOD_CHECK_IDS`). Fails on: deleting the id from `DOR_DOD_CHECK_IDS` alone, which makes `validate.py` refuse every consuming DoD that still carries the tag
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_the_two_role_key_and_tag_are_retired
- **AC5:** Given the criteria whose stamped Verify selector names a test this story deletes (TwoRoleCutoffOnUlidIdsTests, CritiquedHalvesTests, TwoRoleCritiquedTests and the transition two-role gate tests in TheVerbEnforcesTheBarItWritesTests): BG0318 (4), BG0417 (4) and US0373 (4), then each is retired in the D0259 pattern (`Verify: manual - retired by US0916: <why>`, `Verified: manual (<date>) - retired, superseded by US0916`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py::TwoRoleGoneTests::test_no_stamp_names_a_deleted_test

## Notes

- Measured: at default config `transition.py set <id> Done` does not refuse a story with no verdict. Only `conformance.py check` objects. Making the verb refuse would be a new blocking check under LC-008, so the review bar stays in conformance and at `sprint sign`. The old AC3 rested on that false premise; its surviving half is the control in AC2.
- AC4 builds the shared retired-check-id mechanism: US0935 adds `repair.mutation-evidence` to it, and US0925 reads the same registry.
- Lands before US0917 and US0935.
- The shared prose edit to `reference-workflow-personas.md` moved to US0924.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 5 points held; the old AC3 replaced (the verb never refused a missing verdict) and folded into AC2 as the conformance control; the plan criterion sets `review.two_role_after: 1` so it fails at HEAD; AC4 builds the retired-check-id registry; stamps named (12 criteria); Affects adds test_dor_dod.py, test_config.py, reference-config.md and the changelog fragment, and moves reference-workflow-personas.md to US0924 |
