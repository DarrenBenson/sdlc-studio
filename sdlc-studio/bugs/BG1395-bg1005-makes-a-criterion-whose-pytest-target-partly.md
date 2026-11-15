# BG1395: BG1005 makes a criterion whose pytest target partly skips on the running machine read red, including Done criteria the release gate re-runs, and the count is not measured

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py, .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py, changelog.d/BG1395.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane verify builder, BG1005
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:10:53Z

## Summary

`verify_ac` now fails any criterion whose pytest target partly skips (`verify_ac.py` around line 463). Done criteria that skip on the release machine will read red at the gate; how many is not measured.

## Steps to Reproduce

Run `verify_ac` over Done stories and count partial skips.

## Proposed Fix

Measure before the next release; allow an explicit skip allowance if needed.

## Acceptance Criteria

- [ ] **AC1** Given two stories, one whose pytest Verify target passes with one test skipped and one whose target fails outright, when `verify_ac.py run` covers both, then each story's summary line and the total line report the partial skip as its own count (for example `partly_skipped=1`) beside `fail=2`, and name the partly-skipped criterion.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py::PartialSkipReleaseGateCountTests::test_the_summary_counts_partial_skips_apart_from_other_failures
- [ ] **AC2** Given a target whose every selected test is skipped and a target that runs clean with no skip, when the same run covers them, then neither adds to the partial-skip count, and the all-skipped target keeps its own vacuous verdict.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py::PartialSkipReleaseGateCountTests::test_an_all_skipped_or_clean_target_is_not_counted

## Notes

- AC1 must fail on: a partial skip counted only inside fail, so the release gate cannot say how many of its reds are partial skips
- AC2 must fail on: the all-skipped case counted as a partial skip
- Still true at HEAD: `_pytest_partial_skips` (verify_ac.py:476-492) fails the criterion at :823-830, and the summaries (:3644, :4690-4697) carry no partial-skip count. No commit since 62ef7fad touches it.
- The filed AC ('Fails on: no measurement') could not be a test. The count on the gate host is a measurement: the orchestrator runs tools/verify-corpus.sh on the gate host before run fifteen's cut and records the partial-skip count in docs/known-issues.md. The summary count is what lets it read that number.
- The proposed 'skip allowance' is not taken: it would reopen what BG1005 closed.
- Builds second in the verify lane, after BG1396 (same function, same test files).
- End goal 1 (the release gate's reds are counted by cause).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed for run fourteen: criteria with Verify lines, notes |
