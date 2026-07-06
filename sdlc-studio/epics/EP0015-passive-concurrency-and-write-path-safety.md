# EP0015: Passive concurrency and write-path safety

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new

## Summary

The write-path safety floor for a team-based tool: atomic index/cascade writes
(write-temp-then-rename) and an advisory allocation lock so the ledger stays passively safe
under concurrent writes when orchestration fails. Complements EP0012 - ULIDs remove the
id-allocation race, but index and epic-cascade writes still need atomicity, and this covers
the pre-ULID scheme too. Groups CR0183 (passive concurrency safety). Pairs with EP0012 in the
v4 foundation tranche; explicitly not a scheduler.

## Story Breakdown

- [x] [US0069: Atomic index and cascade writes with an advisory allocation lock](../stories/US0069-atomic-index-and-cascade-writes-with-an-advisory.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
