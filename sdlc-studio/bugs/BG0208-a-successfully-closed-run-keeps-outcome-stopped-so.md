# BG0208: a successfully closed run keeps outcome=stopped, so a goal-reached sprint reads as abandoned in the archive

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

RUN-01KXVYGR completed its full close chain - all six gates PASS, goal verdict achieved, 28 units signed off to Done, 7 epics derived terminal, handoff at 32 delivered / 0 remaining, velocity row written - and the run state still reads outcome=stopped. The outcome was set earlier in the run and nothing in close or apply-signoff updates it on success. Because run state is archived per cycle, the permanent record of a sprint that reached its goal says it was stopped. Every consumer of the archive (sprint report, velocity, boundary regeneration, the close-owed detector) reads that field, so a successful run is indistinguishable from an abandoned one after the fact. This is the same class as BG0188 and the plan --write outcome=running defect: the outcome field is written on the failure paths and forgotten on the success path.

## Steps to Reproduce

1. Run a sprint to a stop, so outcome=stopped is recorded. 2. Complete the close: sprint close --retro RETROxxxx --apply-signoff --principal NAME with a recorded critic verdict. 3. Observe every close step reports ok and all units reach Done. 4. Read outcome from sdlc-studio/.local/run-state.json - still stopped.

## Proposed Fix

Set the outcome from the recorded goal verdict at the end of a successful close, the same place the velocity row is written: achieved maps to goal-reached, partial and missed to their own values. Assert it in the close chain's own test so the success path is covered rather than only the refusal paths.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
