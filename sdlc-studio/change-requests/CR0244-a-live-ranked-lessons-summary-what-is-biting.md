# CR-0244: A live, ranked lessons summary: what is biting us most, right now

> **Status:** Complete
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 D6
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P1
> **Type:** feature

## Summary

A flat append-only log is what grew until an infrastructure project had to evict its 750-line ops-lessons.md from auto-memory. Make the summary a live instrument: ranked by recurrence (LL0008 has bitten 3x across 3 repos - it should have been top of the list before anyone touched install.sh), recency, and structural-fix demotion (once a guard makes the class impossible, the lesson stops shouting). The Review-by horizon already exists and is unused for ranking. Regenerated and never trusted, as the summary gate already does.

## Impact

Anyone who reads the summary to decide what to worry about. Changes the summary from a flat log into a ranked instrument, so ordering shifts as classes recur, decay, or get a structural guard. A flat log is what grew until an infrastructure project had to evict its 750-line lessons doc from memory entirely.

**Effort:** M

## Acceptance Criteria

- [ ] The summary is ranked, not flat: recurrence, recency and structural-fix demotion decide the
      order, and the top of the list is what is biting now.
- [ ] A lesson whose class has recurred across repos ranks above a one-off of the same age.
- [ ] A lesson with a shipped structural guard is demoted, not deleted - the history stays, the
      shouting stops.
- [ ] The summary is recomputed from the artefacts and compared, never trusted (LL0001), and a
      stale summary still fails the gate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
