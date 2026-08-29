# CR-0562: no shipped command ticks a delivered unit's acceptance criteria, so the close's tick-verification row can only be satisfied by hand-editing the artefact

> **Status:** Proposed
> **Priority:** Medium
> **Type:** enhancement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Date:** 2026-08-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The close's `tick-verification` row checks that ticked criteria are supported by the run's diff, and it is COMPULSORY - the close refuses until it is answered or waived. But nothing ticks them. `transition.py` ticks a STORY's line in its parent epic's Story Breakdown and writes each criterion's `Verified: yes (date)` stamp, and stops there; the `- [ ]` box on the criterion itself is never touched for a bug. So the row reads `no ticked criteria found` on a batch of bugs however complete the work is, and the only way to answer it is to hand-edit ten artefacts - which the doctrine's own no-hand-rolling rule forbids, and which LL0027 says is the weakest available fix.

## Impact

Every close of a bug batch hits it. The row is compulsory, so the choice is a hand-edit across every unit or a waiver, and both are worse than the check: the hand-edit is the class of work this project files bugs about, and the waiver retires the one row that audits an author's completion claim against the diff. This close ticked 58 criteria across ten units by hand to answer it.

## Acceptance Criteria

- [ ] `transition.py set <id> Fixed` ticks a criterion's box in the same write that stamps it `Verified: yes` - the two are one assertion, and splitting them is what leaves one unwritten
- [ ] A criterion the transition does NOT verify keeps its empty box, so the close's tick-verification row still has something to catch: a tick nobody earned
- [ ] A close over a batch of bugs answers `tick-verification` without any artefact being hand-edited

## Steps to Reproduce

1. Deliver a batch of bugs to Fixed with executed mutants and `Verified: yes` on every criterion.
2. Run `sprint.py report --id RETROxxxx`.
3. The `tick-verification` row reads `NOT RUN - no ticked criteria found`, and `close` refuses.
4. `grep -c '^- \[x\]'` on any of the units returns 0, though every criterion is evidenced.

## Proposed Fix

Have `transition.py set <id> Fixed` tick a criterion at the moment it writes that criterion's `Verified: yes` stamp - the two assertions are the same assertion, and splitting them is what leaves one of them unwritten. The tick is the author's claim and the close's row is what audits it against the diff, so the pair only works when something makes the claim. Alternatively `verify_ac.py stamps` could gain a `--tick` verb; the transition is the better home, because it is the command that already decides the criterion passed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-28 | sdlc-studio | Raised |
