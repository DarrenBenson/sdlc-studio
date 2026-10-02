# BG0915: retro-validate and the gate's unattributed path still hand over their header and prose as known issues

> **Status:** In Progress
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_gap_lines_rest.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T22:49:29Z

## Summary

BG0908 fixed review-coverage only (D0316). `close_known_issues_from` still turns every detail line of a failed close step into a known issue for retro-validate (its explanatory header, sprint.py ~4683) and the gate's unattributed path (its whole output plus prose, sprint.py ~5108), and retro-extract's extract-failed branch (rc not 0) is unpinned.

## Steps to Reproduce

1. A close whose retro fails validation on one field. 2. The page lists the validator's header line as a known issue beside the real failure. 3. Likewise a gate failure nobody is attributed to hands over its whole output.

## Proposed Fix

Have each step hand over only its failures, as BG0894 and BG0908 did, and pin retro-extract's extract-failed branch. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a close whose only gap is one retro-validate failure, when the page is filed, then its known issues hold that failure and not the validator's header line. Fails on: the current code hands over the header too
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_gap_lines_rest.py::CloseGapLinesRestTests::test_retro_validate_hands_over_only_its_failure
  - **Verified:** yes (2026-10-02)
- [ ] **AC2** Given a close whose gate fails on a lane nobody is attributed to, when the page is filed, then its known issues hold that lane's failure line only, not the gate's whole output. Fails on: the current code hands over every output line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_gap_lines_rest.py::CloseGapLinesRestTests::test_unattributed_gate_hands_over_only_its_failure
  - **Verified:** yes (2026-10-02)
- [ ] **AC3** Given retro-extract exits non-zero, when the close runs, then the page carries one known issue naming the extract failure. Fails on: a mutant dropping the rc check, which the current suite does not kill
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_gap_lines_rest.py::CloseGapLinesRestTests::test_extract_failed_is_one_known_issue
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
