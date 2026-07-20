# BG0223: file-and-close refuses a budget-spent or stopped run with a false already-closed message

> **Status:** Fixed
> **Severity:** Medium
> **Verification depth:** functional (both mid-flight outcomes and both completed outcomes covered; 4 mutants killed over the FileAndCloseTests class - restoring the over-broad guard, removing the completed-close refusal, removing the duplication guard, and narrowing it to goal-reached only. The first mutation pass reported 3 survivors and was WRONG: the -k filter did not match two of the three new test names, so they never ran. The tests were sound; the harness was not)
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The re-run guard added at the round-1 repair gates on the bare outcome string: any terminal outcome refuses with 'this run is already closed ... re-running would duplicate the filing'. A run stamped budget-spent or stopped mid-flight - `loop_guard`'s own recommended flow, and runs the close path documents as routinely completing their ceremony afterwards - has filed nothing, so the message is false on both counts and the bounded exit is unavailable to one of its natural customers. Fails closed (no duplication, no waiver, the fix path remains), so it survived round 2 as non-blocking. Found by the independent reviewer at the RUN-01KXZQF0 close.

## Steps to Reproduce

1. Open a run and let it stop mid-flight (outcome budget-spent or stopped). 2. Leave administrative close blockers in place. 3. sprint close --retro RETROxxxx --file-and-close. 4. rc 2 with 'already closed ... would duplicate the filing' although nothing was ever filed.

## Proposed Fix

Gate the refusal on what it actually protects: refuse on existing `deferred_blockers` (the duplication) and on a COMPLETED close (goal-reached / closed-outstanding), not on the bare terminal-outcome string; or keep the refusal and state the true reason (re-closing would overwrite the recorded budget-spent fact) so the operator is not told a filing exists that does not.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
