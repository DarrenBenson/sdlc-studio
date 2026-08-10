# BG0567: the upgrading-project baseline compares against this tree minus one branch, not against the base ref, so a regression the epic introduced elsewhere sits on both sides and is invisible

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** Round-3 delivery review of RUN-01KZM49Y, 2026-08-10. US0663 AC2 originally demanded a baseline captured from the base ref before the epic's branch existed. `_capture_with_softening_disabled` clones the CURRENT skill tree and disables one branch, so every other change the epic made is present on both sides of the comparison. The seat also noted the baseline fixture holds 0 retros while the case under test holds 3, so it is not literally the same fixture either. The criterion was narrowed to describe what is built rather than left overstating it.
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A counterfactual baseline is only as good as what it holds constant. Disabling one branch in the current tree answers `did THIS branch change the behaviour`, which is a real question and the one the test now claims to ask. It does not answer `is an upgrading project's behaviour what it was before this epic`, which is what the unit promises a consuming project.

The difference matters for exactly the population the promise is about. An established project upgrading to v5 gets whatever this epic did to the transition ladder, not merely whatever the softening branch did. A change elsewhere in the epic - to the advisory, to the gate ordering, to a message - is invisible to a comparison that carries it on both sides.

The stronger form is buildable: capture the baseline by checking the base ref out into a throwaway worktree and running the same fixture against it. It costs a worktree per assertion, which is why it was not built under time pressure, and that is a reason to file it rather than to claim it.

## Steps to Reproduce

1. Read `_capture_with_softening_disabled` in `test_transition.py`: it clones the current skill tree and rewrites one branch. 2. Introduce any other behaviour change in the same epic - a changed message on the transition path, say. 3. The upgrading-project test still passes, because the change is present in both the baseline and the observed run.

## Proposed Fix

Capture from the BASE REF: `git worktree add` a throwaway checkout of the run's base ref, run the same fixture against its `transition.py`, and compare. Use one fixture shape for both sides so the comparison is like for like - the current baseline holds 0 retros against the observed 3. Pin it by introducing a deliberate unrelated change on the epic's side and asserting the comparison notices, which the present form does not.

## Acceptance Criteria

- [ ] **AC1** The upgrading-project baseline is captured from the run's base ref in a throwaway worktree, not from the current tree with a branch disabled
- [ ] **AC2** Both sides run the SAME fixture shape, so a difference in the fixture cannot be read as a difference in behaviour
- [ ] **AC3** A deliberate unrelated change on the epic's side makes the comparison fail, proving it can see more than the one branch it disables

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Filed |
