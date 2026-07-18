# BG0191: handoff is generated before the apply-signoff cascade, so delivered units are reported as remaining

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional (unit tests over the rewrite, the worklist, the preserved history and the batch scoping; four mutants executed and killed)
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py
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
| 2026-07-18 | sdlc-studio | Fixed: new `handoff.refresh` re-renders the EXISTING handoff in place (same id, same index row, same retro link) and the apply-signoff tail calls it after the cascade, scoped to the run's own batch. The scoping is load-bearing and was initially untested: `build` defaults to whichever run is open, so an unscoped refresh rewrites a closed run's handoff with the next sprint's batch - which is exactly what a hand-run smoke test did to HO-0007 during this fix |
