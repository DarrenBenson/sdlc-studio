# BG0191: handoff is generated before the apply-signoff cascade, so delivered units are reported as remaining

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

HO-0006 lists US0236/US0237/US0238/US0247/US0248 as remaining with 'needs human judgement', but all five reached Done at that same close via 'sprint close --apply-signoff'. The handoff snapshot is taken before the terminal cascade runs, so the run's own delivered work is misreported as outstanding and the generated handoff-worklist.txt would re-plan finished stories. Same close-tail family as BG0190.

## Steps to Reproduce

1. Run a sprint to close with units in Review. 2. Close it with 'sprint close --apply-signoff --principal <you>', which transitions those units to Done. 3. Read the emitted handoff HO-xxxx and .local/handoff-worklist.txt. 4. Observe the just-Done units listed under 'Remaining', and 'sprint plan' advertising them as pickup work on the next run.

## Proposed Fix

Emit the handoff after the apply-signoff terminal cascade completes, or re-read each unit's status at handoff-render time rather than reusing the pre-cascade run-state snapshot.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
