# US0910: A bug reaches Fixed without a verification depth tier

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/reference-bug.md, .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/reference-test-best-practices.md, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/help/arguments.md, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer closing a bug fix
**I want** a bug to reach Fixed on green Verify selectors alone, with no depth tier to stamp or derive
**So that** a field that read `functional` on 636 of 637 units stops costing a stamp, a lane and a refusal on every fix

## Acceptance Criteria

- **AC1:** Given a fixture bug with green executable criteria and no `Verification depth` field, when `transition.py set <id> Fixed` runs, then it succeeds; the same bug with a red criterion is still refused, so the verify gate survives
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_a_bug_without_a_depth_reaches_fixed
- **AC2:** Given `verify_ac.py depth` or `verify_ac.py depth-check`, when invoked, then each exits 2 with a message that it is retired and that a unit's Verify selectors are its evidence, and `verify_ac.py --help` lists neither
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_the_depth_verbs_are_retired
- **AC3:** Given `artifact.py close <id> --depth <value>`, when invoked, then it exits 2 naming the retired flag, and `artifact.py close <id>` without it still closes a green fixture story
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_close_depth_is_retired_and_close_still_works
- **AC4:** Given the standard gate, then it runs no `derived-depth` lane, so a hand-edited `Verification depth` line no longer fails `gate.py`; a reopen writes no depth retraction, and `quality.depth_parity_gate` has no reader
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_no_depth_lane_retraction_or_parity_knob
- **AC5:** Given the bug template and `docgen.py surface` rerun in the same commit, then the template carries no `Verification depth` field, reference-scripts-surface.md names neither `verify_ac.py depth` nor `verify_ac.py depth-check`, and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_the_surface_names_no_retired_verb
- **AC6:** Given every criterion whose stamped Verify selector names a test this story deletes (DerivedDepthTests, DepthTierGateTests, DerivedDepthLaneTests and the reopen retraction tests; at least those on US0675, US0676), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
