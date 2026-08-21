# CR-0552: revert-check mutates the live working tree, so a boundary gate rewrites files underneath anything else reading the repo

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** RUN-01M0JD1W, 2026-08-21: the lane reverted this repository's own `verify_ac.py` while a parallel xdist worker read it, and `inspect.getsource` in an unrelated test returned lines from the base revision.
> **Date:** 2026-08-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`verify_ac.py revert-check` reverts a unit's declared production files IN PLACE, runs the unit's verifiers, and restores from a byte snapshot. The restore is correct - byte and mode exact, in a `finally`, guarded against SIGTERM and SIGINT - but for the duration of the run the live working tree holds the BASE revision of those files. Anything else reading the repository in that window sees code that is not there.

That is tolerable for the per-unit CLI, which an author runs deliberately and waits for. It is not tolerable for the `revert-check` gate lane, which binds at the push and release boundaries and walks the whole batch: at a real push it rewrites a developer's tracked files while an editor, a language server, a watch process or a concurrent suite may be reading them.

## Impact

Anyone running `gate.py --boundary push|release` in a working tree that anything else is reading. Measured rather than hypothesised: inside this repository's own suite the lane rewrote `verify_ac.py` underneath a parallel test worker, and an unrelated source-introspection test failed with a docstring fragment where a function body should have been. The failure was intermittent and cost most of a delivery round to diagnose, because nothing in the symptom pointed at the lane.

The blast radius is wider than the confusion. `tools/repo_writes.py` refuses a commit whose suites modified a tracked file, so a lane that leaves anything behind - after a signal the interpreter cannot handle, a SIGKILL, a full disk mid-restore - turns a review aid into a commit blocker, and it does so on the developer's own source rather than in a sandbox.

## Acceptance Criteria

- [ ] Given the revert-check lane running at a push or release boundary, when it examines a unit, then no tracked file in the live working tree changes at any point during the run - asserted by hashing the tree continuously from a second process, not by inspecting it afterwards, because the defect is a window rather than an end state
- [ ] Given the lane and the per-unit CLI run over the same unit, when both report, then they reach the same verdict for the same reason - one measurement, not two paths that may drift
- [ ] Given a unit whose production file did not exist at the base ref, when the isolated copy is built, then that file is absent from it rather than present-and-empty, so the criterion is measured against the tree the base ref actually held
- [ ] Given the isolated copy, when a verifier runs against it, then it reads the unit's CURRENT test files and the BASE production files, and nothing it writes can reach the real repository
- [ ] Given US0672's criteria, which are written about restoring the live tree, when this lands, then they are re-authored against what the new design actually promises rather than left to pass vacuously on a tree nothing touches

## Recommendation

Give the lane an isolated worktree instead of the live tree. `git worktree add --detach <tmp> <base>` yields the production files as they stood at the base ref; overlay the unit's declared TEST files from the live tree; run the verifiers with that directory as the working root; remove the worktree. That is exactly 'revert production, keep the tests' expressed as a copy rather than as a mutation, and it matches what this repository already does for close previews and for reviewer isolation.

Two things to settle when it is built. The per-unit CLI and the lane must MEASURE THE SAME THING - a review will otherwise ask why one path reverts in place and the other does not, and the honest answer is that they should not differ. And US0672's criteria are written about restoring the live tree; under an isolated worktree there is nothing to restore, so those criteria and their mutants have to be re-authored rather than quietly satisfied. That is the reason this is a CR and not a repair inside RUN-01M0JD1W: D0146 caps the run at two delivery rounds, and re-cutting a delivered unit's criteria mid-round is a redesign.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Raised |
