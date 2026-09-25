# US0910: Verification depth is no longer derived, and the gate runs no depth lane

> **Status:** In Progress
> **Depends on:** US0934 - both retire stamps in US0675 and US0676, so they land apart (EP0263 readiness)
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py, changelog.d/US0910.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, sdlc-studio/stories/US0675-every-count-in-verification-depth-is-read-from.md, sdlc-studio/stories/US0676-the-derived-half-of-verification-depth-is-delimited.md
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer committing and closing units
**I want** `verify_ac.py depth` and `depth-check` gone and no `derived-depth` lane in the gate
**So that** a field that read `functional` on 636 of 637 units stops costing a derivation on every close and a blocking lane on every commit

## Acceptance Criteria

- **AC1:** Given `verify_ac.py depth` or `verify_ac.py depth-check`, when invoked, then each exits 2 with a message that it is retired and that a unit's Verify selectors are its evidence, and `verify_ac.py --help` lists neither. Fails on: deleting the parsers so argparse exits 2 with an unhelpful usage error instead of the retirement message
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_the_depth_verbs_are_retired
- **AC2:** Given a fixture story whose `Verification depth` line was hand-edited inside its derived half, when `gate.py --root <fixture>` runs the standard gate, then it passes, and `derived-depth` is in neither `DEFAULT_CHECKS` nor `BLOCKING_ON_ERROR`. Fails on: dropping the lane from `DEFAULT_CHECKS` while `_derived_depth` still runs from `BLOCKING_ON_ERROR`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_the_gate_runs_no_derived_depth_lane
- **AC3:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names neither `verify_ac.py depth` nor `verify_ac.py depth-check`, and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_the_surface_names_no_retired_verb
- **AC4:** Given the criteria whose stamped Verify selector names a test this story deletes (DerivedDepthTests and DerivedDepthLaneTests): US0675 (5) and US0676 (9), then each is retired in the D0259 pattern (`Verify: manual - retired by US0910: <why>`, `Verified: manual (<date>) - retired, superseded by US0910`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node. `CriteriaSectionTests` (BG0648) is edited, not deleted, and keeps its test names so its stamps survive
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth.py::DepthGoneTests::test_no_stamp_names_a_deleted_test

## Notes

- Split from the original US0910 (5 points). This half takes the old AC2, the lane half of AC4 and the surface half of AC5. The bug depth gate, parity, retraction, both `--depth` flags and the template moved to US0934.
- Engineering call: BG0650's selector (`tools/tests/test_known_issues.py::DepthFieldCountsTests`) is left alone. That test reads historic depth fields and this story does not delete it.
- Engineering call: the prose docs the original story listed (reference-bug.md, reference-schema.md, reference-test-best-practices.md, reference-scripts-create.md, SKILL.md, help/arguments.md, help/verify.md) moved to US0924. No criterion of either half reads them.
- Lands before US0922, which shares `CoverageGateTests`. Must not share a wave with US0934.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: split 5 -> 3 + 5 (US0934 takes the bug depth gate, parity, retraction and both `--depth` flags); retitled to the derived-depth verbs and lane; keeps the old AC2, the lane half of AC4 and the surface half of AC5; stamps measured at US0675 (5) and US0676 (9); Affects narrowed to verify_ac.py, gate.py and their tests plus the surface and changelog fragment |
