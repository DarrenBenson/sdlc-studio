# BG1582: Once HEAD moves past the close commit, sprint sign skips the whole-tree check, so an uncommitted edit to a unit's file seals with no later run open

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1582.md, .claude/skills/sdlc-studio/scripts/tests/test_sign_uncommitted_edit_after_close.py
> **Evidence:** US1290 QA round-2 verdict, sdlc-studio/reviews/verdicts/US1290/b9e0f15856ad-b543e9a9.txt; ruling D0524.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T03:20:29Z

## Summary

US1290's repair (run sixteen) implements D0524: once HEAD has moved past the commit that filed the waiting run's record, sign judges the run against that commit, not the working tree. The QA seat's round-2 probe shows the cost: with no later run open, one empty commit after the close is enough for an uncommitted edit to a file the batch declared to seal. D0524's own rationale is that the narrower check applies only where the wider one cannot pass at all, and here the wider one could.

## Steps to Reproduce

Close a run, commit the close, add one empty commit, edit a file a batch unit declares without committing, run sprint sign: it seals.

## Proposed Fix

Keep the committed-close judgement, and also refuse an uncommitted change to a file the waiting batch declared, whatever HEAD is; or apply the committed-close path only when a later run is open or the close tree cannot be read.

## Acceptance Criteria

- [ ] **AC1** Given a run closed and committed, then one empty commit on top and no later run open, and an uncommitted edit to a file a batch unit declares, when `sprint.py sign --report <the run's report> --principal <operator>` runs, then it refuses and names the edited file, and seals nothing. Fails on: sign seals the run with the edit still uncommitted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_uncommitted_edit_after_close.py::SignRefusesUncommittedEditAfterCloseTests

## Impact

A signature can attest a run whose working tree the report no longer describes, the case US0876's tree check exists to refuse.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (qa seat, groom) | Acceptance criteria authored for planning (run twenty-one) |
