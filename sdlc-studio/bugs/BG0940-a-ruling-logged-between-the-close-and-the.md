# BG0940: A ruling logged between the close and the sign changes the filed page, and sign seals it without re-deriving

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_ruling_after_close.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T19:57:15Z

## Summary

decisions.py add --by operator (or persona) appends the ruling to the open run's rulings while the run is closed and not yet signed, so the filed page's Rulings figure re-derives differently; sprint sign checks the tree for changed files but does not re-derive the page before sealing, so it sealed RPT0017 already INVALIDATED (`operator_rulings` signed 1, now 2) and the run had to be reopened and re-filed as RPT0018. Same class as BG0926 (a lane return between close and sign), and LC-016. Also: `sprint_report.py` check reports a fresh signature INVALID ('a signature changes only in a commit') until the seal is committed, which reads as a defect at the moment of signing.

## Steps to Reproduce

1. sprint close files a page. 2. decisions.py add --by operator ... 3. sprint sign seals it. 4. `sprint_report.py` check: INVALIDATED, `operator_rulings` signed 1, now 2.

## Proposed Fix

Do not count a ruling against a run whose page is filed and not reopened (as BG0926 does for late totals), and have sign re-derive the page and refuse to seal one that no longer matches, naming the figure that moved; say in check's output that an uncommitted fresh signature is awaiting its commit. No new gate beyond sign refusing to seal a page that already fails its own check.

## Acceptance Criteria

- [ ] **AC1** Given a run closed with a filed page and not signed, when decisions.py add --by operator logs a ruling, then the run's rulings are unchanged and the filed page still checks VALID, and a ruling logged after a reopen is counted. Fails on: the current code, which counts it and invalidates the page
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_ruling_after_close.py::RulingAfterCloseTests::test_a_ruling_after_the_close_leaves_the_page_valid
- [ ] **AC2** Given a filed page whose run state has moved since the close, when sprint sign runs, then it refuses to seal and names the figure that moved. Fails on: the current sign, which seals a page that already fails its check
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_ruling_after_close.py::RulingAfterCloseTests::test_sign_refuses_a_page_that_no_longer_matches

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
