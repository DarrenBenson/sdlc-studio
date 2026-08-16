# BG0581: the goal-review brief states a reachable end state without knowing the rung, so it promises Review for a design rung that ends at Ready

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Adversarial goal review of the SC0005 grooming batch, 2026-08-16, before the run opened. Verified independently at sprint.py:3090 (no rung parameter) and sprint.py:5474 (the design rung's stated terminal).
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-14T01:30:38Z

## Summary

`reachable_end_state(repo_root, batch)` takes the root and the batch and nothing else. The rung a batch will be planned at is not an input, so the brief prints one answer for every rung. Planned at `--goal design` the same batch ends at Ready by the shipped stamp's own words - `anchor_status_block` at sprint.py:5474 says design-rung units 'correctly end at Ready with RED acceptance criteria' - while the brief handed to the seats says 'Reachable end state: Review'. The two disagree about the same run, and the brief is the artefact the reviewing seats read first.

## Steps to Reproduce

1. Build a worklist of ungroomed units. 2. `sprint.py goal-review brief --goal '<any>' --brief-worklist <file>` - it prints `Reachable end state: Review - derived from the cutoff and the story Definition of Done the conformance gate itself reads`. 3. `sprint.py plan --worklist <file> --goal design` - the design rung ACCEPTS the batch and its terminal is Ready. Measured 2026-08-16 on a 12-unit grooming batch; an adversarial goal review caught the contradiction before the run opened.

## Proposed Fix

Take the rung. `reachable_end_state` should accept the goal/rung the brief is being written for and derive the terminal from it, exactly as `sprint plan` already does when it decides whether to accept an ungroomed batch. Where the rung is genuinely unknown the honest answer is to say so rather than to print the delivery rung's terminal as though it were the only one - an unanswered question stated as an answer is the shape this repository files hardest against.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `reachable_end_state(repo_root, batch)` takes the root and the batch and nothing else.

## Impact

The brief is what an independent seat reads before judging a plan, and `reviews/LATEST.md` is what a fresh session reads first. A brief promising Review for a run that correctly ends at Ready makes the close look short of its own goal when it is not, and invites a reviewer to demand sign-off the rung does not owe. It is the same class as a lane that reports a state it did not measure.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
