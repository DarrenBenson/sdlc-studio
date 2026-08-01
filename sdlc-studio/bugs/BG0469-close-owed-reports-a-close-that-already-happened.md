# BG0469: close_owed reports a close that already happened: a unit raised and Fixed inside a run never joins that run's recorded batch

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

**Id collision, recorded not hidden.** Commit `edb9fdf0` (2026-07-31, "a census threshold that
failed as a surprise, not a signal") carries the subject `fix(BG0469)` but filed no BG0469
artefact, so `next_id` correctly saw the id as free and allocated it to THIS finding. Two
unrelated pieces of work therefore answer to BG0469: that commit's census-ratchet change, and
this bug. `git log -S BG0469` will mislead. Nothing is renumbered, because no tool renumbers an
artefact and hand-editing `_index.md` is forbidden here. The commit's work is unfiled ad-hoc
delivery of the same class as BG0467 and BG0468 - see the inherited-debt note on RETRO0086.

## Summary

12 of the 14 units `close_owed` flagged as owing a close had been delivered inside RUN-01KYPZ1G or RUN-01KYTKA1 and were simply absent from the retro Batch line. A finding filed against an open run becomes a tracked unit but is never added to the run's batch, so the close records fewer units than the run delivered and `close_owed` then demands a close for work whose close already ran. The batch should accrete a unit raised in-batch that reaches terminal before the close, or `close_owed` should attribute by the run window it already reads.

## Steps to Reproduce

1. python3 .claude/skills/sdlc-studio/scripts/`close_owed.py` detect
2. Observe 14 units reported as owing a close.
3. For BG0424-BG0428 and BG0451, read 'Raised-in-batch: 2026-07-29T15:35:33Z' - inside RUN-01KYPZ1G's 2026-07-29T13:02:54Z to 2026-07-30T22:48:16Z window, recorded in .local/run-archive/RUN-01KYPZ1G.json.
4. For BG0456/BG0458/BG0461/BG0464/BG0465, git log --diff-filter=A shows first commits inside RUN-01KYTKA1's window; RETRO0086's own prose names them as its review repairs.
5. Neither retro's Batch line contains any of them, so the detector is right that no retro accounts for them and wrong that a close is owed.

## Proposed Fix

Accrete into `run_state.batch` when a finding filed with a run open reaches terminal before that run closes, so the close counts what the run delivered; or have `close_owed` attribute a terminal unit to the run whose recorded window contains its Raised-in-batch stamp before declaring a close owed. Either way the operator must not be hand-correcting Batch lines against git timestamps.

## Acceptance Criteria

- [ ] The behaviour described is corrected: 12 of the 14 units `close_owed` flagged as owing a close had been delivered inside RUN-01KYPZ1G or RUN-01KYTKA1 and were simply absent from the retro Batch...
- [ ] The proposed fix lands, pinned by a test: Accrete into `run_state.batch` when a finding filed with a run open reaches terminal before that run closes, so the close counts what the run delivered; or...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | sdlc-studio | Filed |
