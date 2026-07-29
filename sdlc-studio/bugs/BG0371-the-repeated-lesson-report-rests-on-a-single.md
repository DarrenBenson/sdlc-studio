# BG0371: The repeated-lesson report rests on a single unpinned call, so a lesson violated twice can report once

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0521 reports at close a lesson violated again after being carried, naming the unit that violated it. The report is produced by one call whose result is not pinned or accumulated, so the count reflects that call's view rather than the run's history, and US0522's proposal path - which acts on repeated violation - inherits whatever that single view saw.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review. The violation record is read once at close; a violation recorded earlier in the run by a different process is not merged in, so two violations of one lesson can present as one.

## Proposed Fix

Accumulate violations against the run rather than sampling them at close, and have the close read the accumulated record. Pin the read so the report and US0522's proposal act on the same data.

## Acceptance Criteria

### AC1: the report and the proposals act on one pinned read

- **Given** a violation recorded between the report and the proposal path
- **When** the close reports repeats
- **Then** a caller that reads once and passes the same list to both gets one answer, rather than the report naming a count the proposal never saw
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RepeatReadIsPinnedTests::test_the_report_and_the_proposals_read_the_same_counts
- **Verified:** yes (2026-07-29)

### AC2: an unpinned read is still the run's accumulated history

- **Given** further violations appended to the record
- **When** the close reports repeats
- **Then** the count grows with them, because the violations file is append-only and a count is the run's history rather than one call's view
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RepeatReadIsPinnedTests::test_an_unpinned_call_still_reads_the_accumulated_record
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
| 2026-07-29 | Claude Opus 5 | Half the premise did not reproduce and is recorded as such: violations are appended to a JSONL and `repeats` reads all of them, so a count IS the run's history and not one call's view. The half that did reproduce is the one the finding's own Proposed Fix named last - the report and the proposal path each took their own read, so a violation landing between them answered one question two ways. Both now accept a pinned `found`, and the close reads once. |
