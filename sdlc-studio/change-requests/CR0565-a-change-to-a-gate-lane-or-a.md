# CR-0565: A change to a gate lane or a hook cannot reach Fixed without a recorded self-run on the repository

> **Status:** In Progress
> **Decomposed-into:** EP0248
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** RUN-01M1WPNV delivery, 2026-09-07: BG0646 (two REJECTs r1) and BG0649 (three REJECTs r1, two r2) - every rejection was a check a seat did in minutes that the author had not: run the shipped lane on this repository, measure a number written into prose, write a mutant for a branch the fixture never reached. Analysis recorded in the run's retro.
> **Date:** 2026-09-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0649's new boundary lane was green on its fixture and red on this repository (an absolute PYTHONPATH where the hook exports a relative one); it would have refused every push from this clone. Nothing demanded that a lane be run where the hook runs it before review. A unit whose Affects touches gate.py's lane registry, a `.githooks/` file or `tools/skill-tests.sh` must carry a recorded run of the affected lane or hook on the repository itself (`gate.py --boundary push --only <lane>` or the hook's dry run), with its verdict and wall clock, before `transition set Fixed` accepts it; the record is what AGENTS.md's 'exercise every claim through the shipped entry point' rule has lacked a gate for (CR0520's area).

## Impact

A gate-lane change that refuses every push from the clone that ships it (BG0649 r1) cannot reach Fixed; the pre-push hook's self-consistency is proved once at delivery rather than by the first pusher.

## Acceptance Criteria

- [ ] Given a unit whose Affects names a gate lane file and no recorded self-run, when it is transitioned to Fixed, then the transition refuses naming the lane and the command that records a run; with a run recorded green it passes - the control.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Raised |
| 2026-09-21 | audit ruling | still wanted, correctly in progress. No self-run requirement exists anywhere: nothing in `transition.py` reads a unit's `Affects` for gate-lane, `.githooks/` or `tools/skill-tests.sh` membership. The specific BG0649 defect that motivated it was repaired in gate.py; the general gate it motivated was not. Its single child US0817 is Ready - groomed, through three goal-review rounds, expanded 3 to 8 points, and explicitly deferred from RUN-01M1WPNV's batch, so its state is a recorded choice rather than neglect. It is also one of the four 8-pointers US0854 decomposes in this run. |
