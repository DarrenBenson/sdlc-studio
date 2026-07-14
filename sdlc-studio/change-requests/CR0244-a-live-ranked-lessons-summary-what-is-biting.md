# CR-0244: A live, ranked lessons summary: what is biting us most, right now

> **Status:** Proposed
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 D6
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P1
> **Type:** feature

## Summary

A flat append-only log is what grew until an infrastructure project had to evict its 750-line ops-lessons.md from auto-memory. Make the summary a live instrument: ranked by recurrence (LL0008 has bitten 3x across 3 repos - it should have been top of the list before anyone touched install.sh), recency, and structural-fix demotion (once a guard makes the class impossible, the lesson stops shouting). The Review-by horizon already exists and is unused for ranking. Regenerated and never trusted, as the summary gate already does.

## Impact

{{who this affects and what breaks}}

**Effort:** {{S|M|L}}

## Acceptance Criteria

- [ ] The summary is ranked, not flat: recurrence, recency and structural-fix demotion order it. Verify: python3 .claude/skills/sdlc-studio/scripts/lessons.py summary --dry-run
- [ ] A lesson whose class has recurred across repos ranks above a one-off of the same age. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k rank
- [ ] A lesson with a shipped structural guard is demoted, not deleted - the history stays, the shouting stops. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k demote
- [ ] The summary is recomputed and compared, never trusted, and the gate still fails on staleness. Verify: python3 .claude/skills/sdlc-studio/scripts/gate.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
