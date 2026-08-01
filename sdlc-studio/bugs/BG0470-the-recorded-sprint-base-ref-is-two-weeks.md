# BG0470: The recorded sprint base ref is two weeks stale, so any pre-existing/regression classification computed from it is wrong

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sdlc-studio/.local/sprint-base-ref.txt` holds 5f864bf1, dated 2026-07-17. RUN-01KYX375 opened on 2026-07-31T22:04:33Z, and the commit immediately before its first delivery is edb9fdf0 (2026-07-31T21:29). The file was not rewritten when the run opened.

This is inert today because nothing reads it for classification. It stops being inert the moment CR0512 lands: that change decides REGRESSION / NEW / PRE-EXISTING by diffing a unit against the run's base ref, and blocks only on the first two. A base ref two weeks early folds a fortnight of other people's commits into 'this unit's diff', so unrelated work is classified NEW and blocks the review - the precise failure the policy exists to end, reintroduced through its own input.

It fails in the more damaging direction too: a defect genuinely introduced by the unit but also present somewhere in that fortnight can read as PRE-EXISTING and be waved through.

## Steps to Reproduce

1. cat sdlc-studio/.local/sprint-base-ref.txt -> 5f864bf17c773a9265878fa9c8672bbd04b53a7f
2. git log --format='%h %aI' -1 5f864bf1 -> 2026-07-17T00:01:01+01:00
3. Read `started_at` from the run state for RUN-01KYX375 -> 2026-07-31T22:04:33Z
4. git log --format='%h %aI' -1 10b6fd54^ -> edb9fdf0 2026-07-31T21:29:20+01:00, the true base
5. The gap is 14 days of unrelated commits that any diff against the recorded ref would attribute to this run's units.

## Proposed Fix

Stamp the base ref when `sprint plan --write` opens the run, from HEAD at that moment, and record it on the run state rather than in a loose file nothing owns. A consumer of the ref should refuse when the ref predates the run's own `started_at`, because a base ref older than the run it describes cannot be that run's base - fail loud rather than classify against it.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `sdlc-studio/.local/sprint-base-ref.txt` holds 5f864bf1, dated 2026-07-17.
- [ ] The proposed fix lands, pinned by a test: Stamp the base ref when `sprint plan --write` opens the run, from HEAD at that moment, and record it on the run state rather than in a loose file nothing owns.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Filed |
