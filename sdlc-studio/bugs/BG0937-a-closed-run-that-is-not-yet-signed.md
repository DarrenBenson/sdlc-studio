# BG0937: A closed run that is not yet signed cannot be reopened, so work added before the sign cannot record its cost

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_reopen_closed_unsigned.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, CHANGELOG.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T15:43:32Z

## Summary

sprint close leaves the outcome running until sprint sign, and `reopen_run` (lib/`run_state.py` ~1673) refuses any run whose outcome is running as 'already open'. Since BG0926, a filed page also refuses every late total. So work added between the close and the sign (D0334's units) can neither reopen the run nor record its cost. Found at the v6.1 close (D0326).

## Steps to Reproduce

1. sprint close files a page (outcome stays running). 2. sprint reopen --reason x: refused, already open. 3. lane return --tokens: records nothing (page filed).

## Proposed Fix

Let `reopen_run` accept a run whose page is filed and not signed (outcome running, `_page_filed` true), recording the page it breaks as for a sealed run; a run with no page filed stays 'already open'. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a run closed with a filed page and not signed, when sprint reopen runs with a reason, then the run is reopened recording the page it breaks, a later lane return --tokens records, and the next close files a new page; a run with no page filed is still refused as already open. Fails on: the current reopen, which refuses the closed unsigned run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_reopen_closed_unsigned.py::ReopenClosedUnsignedTests::test_a_closed_unsigned_run_reopens
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
| 2026-10-03 | engineering seat | Affects corrected to the files a248836d changed (review finding) |
