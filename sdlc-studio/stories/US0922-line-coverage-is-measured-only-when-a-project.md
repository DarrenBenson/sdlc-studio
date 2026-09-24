# US0922: Line coverage is measured only when a project opts in

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/help/test-automation.md, .claude/skills/sdlc-studio/help/test-spec.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py
> **Epic:** EP0263
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer closing a story
**I want** coverage to stay off unless the project turns it on, and `block` to judge every unit with no date cutoff when it does
**So that** a close pays for coverage only in a project that asked for it, and an opted-in project gets a plain rule

## Acceptance Criteria

- **AC1:** Given a project that does not set `review.line_coverage`, when a fixture story with an added line no criterion executes is moved to Done, then it succeeds with no coverage collected and no coverage line printed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py::CoverageOptInTests::test_coverage_is_off_by_default
- **AC2:** Given `review.line_coverage: block`, when the same story is moved to Done, then it is refused naming the uncovered file and line, whatever the story's Created date
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py::CoverageOptInTests::test_block_still_refuses_with_no_date_cutoff
- **AC3:** Given config-defaults.yaml, then it sets `line_coverage: off`, carries no `line_coverage_after`, and no shipped script reads `review.line_coverage_after`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py::CoverageOptInTests::test_the_cutoff_key_is_retired
- **AC4:** Given every criterion whose stamped Verify selector names a test this story deletes (the `line_coverage_after` cutoff tests in LineCoverageTests and CoverageGateTests; at least those on US0815, US0816), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py::CoverageOptInTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
