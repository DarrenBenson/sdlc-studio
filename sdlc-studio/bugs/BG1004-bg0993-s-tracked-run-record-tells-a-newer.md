# BG1004: BG0993's tracked run record tells a newer copy by reopen count alone, so two reopens made at once overwrite each other; and the close preview's no-write guard is unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_record_versioned_writes.py, changelog.d/BG1004.md, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** BG0993 QA round 4 APPROVE, 2026-10-09, kept verbatim on BG0993 (the ledger refuses a round past the cap, BG1003).
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T00:18:19Z

## Summary

BG0993's approved repair decides which of two checkouts' copies of a run is newer by comparing reopen counts (`run_state.supersedes`, `_file_awaiting_record`). Two reopens made concurrently in different checkouts have the same count, so the second re-close files its copy over the first's: the committed record's reopen entry then names only the later reopen, and the other checkout's reopen survives only in git history and its own `.local`. The signature chain still checks VALID. Separately, the guard that keeps `close --dry-run` from taking a newer record up has no test. Both are non-blocking findings of BG0993's QA round 4. The count is a proxy for a version; four review rounds each found a further interleaving it could not distinguish.

## Steps to Reproduce

A closes and commits. B signs, reopens, re-closes and commits. A reopens before pulling, pulls and re-closes: A's copy is filed over B's record, and B's reopen entry is gone from the head record.

## Proposed Fix

Give the tracked record a version that every write (close, sign, stop) checks and bumps, with this checkout's copy remembering the version it last read or wrote: a writer whose base version is older than the record's is refused and named (both moved: a conflict), and a reader whose copy is older takes the record up. Pin the concurrent-reopen sequence and the preview guard.

## Acceptance Criteria

- [ ] **AC1** Two re-closes of one run from checkouts that each reopened it at the same count never silently overwrite each other: the second is refused, naming the record and the other reopen
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_versioned_writes.py -k concurrent_reopens_conflict
- [ ] **AC2** `close --dry-run` against a newer record writes nothing, pinned by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_versioned_writes.py -k preview_takes_nothing_up

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
