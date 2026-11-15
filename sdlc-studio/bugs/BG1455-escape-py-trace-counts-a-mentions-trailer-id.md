# BG1455: escape.py trace counts a Mentions: trailer id as a unit the release shipped, so a commit that only names a unit puts it among the suspects

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/escape.py, .claude/skills/sdlc-studio/scripts/tests/test_escape_trace_units.py, changelog.d/BG1455.md
> **Evidence:** Run thirteen (RUN-01M7EYR3) review of US1158, qa-seat-US1158-r1, verdict sdlc-studio/reviews/verdicts/US1158/231a64965fb7-5c9a341f.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run thirteen orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T08:01:36Z

## Summary

`release_units` (scripts/escape.py:60, regex :32) counts every US or BG id anywhere in a commit message as shipped, `Mentions:` trailers included. In this repository's convention a Mentions id is one the commit names without owning any of its files (`engagement_floor.py`:119-124), and 110 of the last 400 commits carry one, so trace proposes units the release never changed. The same review found three documented behaviours untested: the latest APPROVE rather than the latest row (escape.py:75), the exclusion of the bug's own id (:110), and the refusal for a bug with no Affects (:107-109).

## Steps to Reproduce

Tag a release over one commit whose subject names D0001 and whose Mentions trailer names US0005, then run `escape.py trace` on a bug shipped in it: US0005 is proposed.

## Proposed Fix

Count the units a commit owns (its subject ids and Refs trailers), not its Mentions trailers; pin the three documented behaviours.

## Acceptance Criteria

- [ ] **AC1** Given a release whose only commit names a unit in a Mentions trailer, when trace runs, then that unit is not proposed. Fails on: it proposed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace_units.py::EscapeTraceUnitsTests
- [ ] **AC2** Given each of the three documented behaviours mutated, when the trace tests run, then each fails. Fails on: any surviving.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run thirteen orchestrator) | Filed |
