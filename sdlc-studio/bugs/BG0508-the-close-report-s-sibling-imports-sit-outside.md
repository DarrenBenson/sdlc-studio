# BG0508: the close report's sibling imports sit outside its advisory try, so an ImportError escapes after the run is already stamped closed

> **Status:** Fixed
> **Verification depth:** functional (executed: critic made unimportable via a meta-path blocker - _tell_the_operator raised before and returns having printed its report after)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Found by the independent boundary review of BG0502 (RUN-01KZ3V4D) and forced by execution: an ImportError propagates out of main() AFTER the deferred artefacts are on disk and close_run has stamped closed-outstanding, and re-running is then refused with 'this run's close already completed'. Present identically on all three emission sites and unchanged in the BG0502 diff, so pre-existing.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_tell_the_operator` wraps its body in a bare `except Exception` on the stated principle that the close outranks its own report - a missing report must never lose a completed ceremony. But the two deferred sibling imports (`critic`, `sprint_report`) sit ABOVE that try, so an ImportError is not caught by the guard written to catch exactly this.

The consequence is worst on the route BG0502 has just taught to report: the exception escapes after the filings are written and the run is stamped, so the ceremony is complete on disk while the command exits non-zero, and the natural response - run the close again - is refused because the close already completed.

## Steps to Reproduce

Make `import sprint_report` fail (shadow it on the path, or remove read permission), then drive `sprint.py close --file-and-close --retro RETROxxxx` to the point of the report. The artefacts are filed, run-state reads `closed-outstanding`, and the ImportError propagates out of `main`. Re-running prints 'file-and-close REFUSED: this run's close already completed'.

## Acceptance Criteria

- [x] **AC1** Given a sibling module the close report imports is unavailable, when `_tell_the_operator` runs, then it returns rather than raising - the close outranks its own report, and a completed ceremony must never be lost to a missing import.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k the_close_report_survives_an_unimportable_sibling

## Proposed Fix

Move both imports inside the try, so the advisory guard covers the failure mode it was written for. Pin it with a test that patches the import to raise and asserts the close still exits zero with the advisory on stderr - the existing advisory test patches `close_report` itself, which is inside the try and therefore cannot see this.

## Impact

Anyone whose close hits an import failure: the ceremony completes, the command reports failure, and the documented remedy is refused. The guard that would have made this advisory is one line too low.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in sprint.py `_tell_the_operator`, move the deferred critic and sprint_report imports back above the try | Given a sibling module the close report imports is unavailable, when `_tell_the_operator` runs, then it returns rather than raising - the close outranks its own report, and a completed ceremony must never be lost to a missing import. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
