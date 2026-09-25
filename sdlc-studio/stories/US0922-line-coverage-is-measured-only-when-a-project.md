# US0922: Line coverage is measured only when a project opts in

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py, changelog.d/US0922.md, .claude/skills/sdlc-studio/reference-config.md, sdlc-studio/stories/US0816-the-fixed-and-done-gates-refuse-a-unit.md
> **Epic:** EP0263
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer closing a story
**I want** coverage to stay off unless the project turns it on, and `block` to judge every unit with no date cutoff when it does
**So that** a close pays for coverage only in a project that asked for it, and an opted-in project gets a plain rule

## Acceptance Criteria

- **AC1:** Given a project that does not set `review.line_coverage`, with an open run (or `--base <ref>`), when a fixture story with an added line no criterion executes is moved to Done, then it succeeds with no coverage collected and no coverage line printed. Fails on: HEAD's shipped default `report`, which collects coverage and prints the uncovered line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py::CoverageOptInTests::test_coverage_is_off_by_default
- **AC2:** Given `review.line_coverage: block` and a leftover `review.line_coverage_after` dated after the story's Created date, when the same story is moved to Done, then it is refused naming the uncovered file and line. Fails on: HEAD's cutoff, which exempts a unit created before it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py::CoverageOptInTests::test_block_still_refuses_with_no_date_cutoff
- **AC3:** Given config-defaults.yaml, then it sets `line_coverage: off`, carries no `line_coverage_after`, and no shipped script reads `review.line_coverage_after`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py::CoverageOptInTests::test_the_cutoff_key_is_retired
- **AC4:** Given the criteria whose stamped Verify selector names a test this story deletes (`CoverageGateTests::test_units_created_before_the_cutoff_are_exempt` and `CoverageGateTests::test_the_shipped_default_is_report`): US0816 (2), then each is retired in the D0259 pattern (`Verify: manual - retired by US0922: <why>`, `Verified: manual (<date>) - retired, superseded by US0922`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_coverage_opt_in.py::CoverageOptInTests::test_no_stamp_names_a_deleted_test

## Notes

- `LineCoverageTests` has no cutoff test, so US0815 retires nothing here.
- Lands after US0910, which shares `CoverageGateTests`.
- `verify_ac.py`, `test_verify_ac.py`, `help/verify.md`, `help/test-automation.md` and `help/test-spec.md` left Affects: none of them names the key.
- - Line numbers re-measured at 013a46d0: `line_coverage: report` at config-defaults.yaml 70 and `line_coverage_after: null` at 77; readers `transition.line_coverage_mode` 744 and `line_coverage_cutoff` 763; `CoverageGateTests` at `test_transition.py` 2939, with the two retiring nodes at 3174 and 3222.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 2 points held; AC1 needs an open run or `--base` so coverage would run at HEAD; AC2 carries a leftover cutoff dated after the story; AC4 names the two CoverageGateTests nodes (US0816); Affects drops verify_ac.py, test_verify_ac.py and three help pages, and adds the changelog fragment |
| 2026-09-25 | sdlc-studio v6 planning | Sprint 5 (engineering seat): line numbers refreshed against 013a46d0; premises stand |
