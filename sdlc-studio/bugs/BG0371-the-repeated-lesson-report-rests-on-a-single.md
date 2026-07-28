# BG0371: The repeated-lesson report rests on a single unpinned call, so a lesson violated twice can report once

> **Status:** Open
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

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
