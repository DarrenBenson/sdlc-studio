# BG0581: the goal-review brief states a reachable end state without knowing the rung, so it promises Review for a design rung that ends at Ready

> **Status:** Fixed
> **Severity:** Medium
> **Verification depth:** functional [[derived: criteria 4; plan rows 5; executed 5; killed 5; survived 0; not-run 0; entry point 0 of 4 criteria through the shipped CLI, 4 in-process | fp 05a1630bbd39 ]] (four criteria over `reachable_end_state`, each with its own mutant executed and killed: the rung ignored, the cap dropped, the story-only filter deleted, and the terminal returned unresolved. The type axis needed the fourth: the first three left a bug batch reported at `Done` on the build rung and `Ready` on a design one, and neither state is in a bug's vocabulary at all)
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

- [ ] **AC1** Given a batch and a rung, when the reachable end state is derived, then it reports THAT RUNG's terminal for that batch's types - `design` and `plan` reach Ready for a story, and `triage` reaches Triaged for an issue - rather than the build rung's, which describes work the rung never set out to do
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RungTerminalAndProductTests::test_the_end_state_is_the_rungs_own_terminal
  - **Verified:** yes (2026-08-25)
- [ ] **AC2** Given the `done` rung and a story past the two-role cutoff, when the state is derived, then it is Review exactly as today - the paired control, proving the rung was made visible rather than the build case broken
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RungTerminalAndProductTests::test_the_build_rung_still_reports_its_own_terminal
  - **Verified:** yes (2026-08-25)
- [ ] **AC3** Given a batch of BUGS on the build rung, when the state is derived, then it is the bug's own terminal and never `Review`, and the report names NO unit as reached by the gate and gives no reason - the two-role gate is story-and-Done only, so a bug batch is capped by nothing here
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RungTerminalAndProductTests::test_a_bug_batch_is_not_capped_by_a_story_only_gate
  - **Verified:** yes (2026-08-25)
- [ ] **AC4** Given a batch whose type cannot hold the rung's terminal, when the state is derived, then it is said in THAT TYPE's vocabulary - a bug reaches `Fixed` on the build rung and is not moved at all by a design one - and never borrows `Ready`, `Triaged`, `Done` or `Review` from the story vocabulary the rung terminals are written in
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RungTerminalAndProductTests::test_a_rung_terminal_is_said_in_the_batchs_own_vocabulary
  - **Verified:** yes (2026-08-25)

## Impact

The brief is what an independent seat reads before judging a plan, and `reviews/LATEST.md` is what a fresh session reads first. A brief promising Review for a run that correctly ends at Ready makes the close look short of its own goal when it is not, and invites a reviewer to demand sign-off the rung does not owe. It is the same class as a lane that reports a state it did not measure.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, drop the `rung` lookup from `reachable_end_state` and return the build rung's terminal | Given a batch and a rung, when the reachable end state is derived, then it reports THAT RUNG's terminal for that batch's types - `design` and `plan` reach Ready for a story, and `triage` reaches Triaged for an issue - rather than the build rung's, which describes work the rung never set out to do |
| AC2 | in `sprint.py`, return the uncapped terminal from `reachable_end_state` for every batch | Given the `done` rung and a story past the two-role cutoff, when the state is derived, then it is Review exactly as today - the paired control, proving the rung was made visible rather than the build case broken |
| AC3 | in `sprint.py`, delete the story-only filter from `reachable_end_state`'s cap loop | Given a batch of BUGS on the build rung, when the state is derived, then it is the bug's own terminal and never `Review`, and the report names NO unit as reached by the gate and gives no reason - the two-role gate is story-and-Done only, so a bug batch is capped by nothing here |
| AC4 | in `sprint.py`, return `terminal` unresolved from `_terminal_in_type_vocab`, so the rung's terminal is reported whatever the batch is made of | Given a batch whose type cannot hold the rung's terminal, when the state is derived, then it is said in THAT TYPE's vocabulary - a bug reaches `Fixed` on the build rung and is not moved at all by a design one - and never borrows `Ready`, `Triaged`, `Done` or `Review` from the story vocabulary the rung terminals are written in |
| AC4 | in `sprint.py`, drop the `COMPLETING_RUNGS` gate from `reachable_end_state`'s cap loop, so the story-and-Done cap is computed on every rung and written over the resolved answer | Given a batch whose type cannot hold the rung's terminal, when the state is derived, then it is said in THAT TYPE's vocabulary - a bug reaches `Fixed` on the build rung and is not moved at all by a design one - and never borrows `Ready`, `Triaged`, `Done` or `Review` from the story vocabulary the rung terminals are written in |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Groomed: acceptance criteria authored so the unit is plannable |
| 2026-08-25 | sdlc-studio | AC4 added on review: the rung axis was fixed and the TYPE axis left standing, so a bug batch was still reported at a story state |
