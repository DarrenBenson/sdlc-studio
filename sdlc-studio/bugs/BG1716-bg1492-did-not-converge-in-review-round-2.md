# BG1716: BG1492 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .githooks/pre-commit, tools/tests/test_precommit_unrecorded_verdict.py, changelog.d/BG1492.md
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T23:12:16Z

## Summary

BG1492 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The type-change branch of the staged-verdict filter is unpinned, the same class as round one's rename finding. Dropping `T` from `--diff-filter=ACMRT` (critic.py:5944) leaves `StagedVerdictTests` and `UnrecordedVerdictLaneTests` green (6 passed). Re-tested alone through `critic.py show --unrecorded-staged` in a fixture: a committed verdict replaced by a symlink and staged (`git diff --cached --name-status` prints `T`) is refused by HEAD (exit 1) and passed by the mutant (exit 0). So a staged verdict whose bytes no recorded row cites would commit with the suite still green, the AC1 Fails-on case. A type-changed case in the AC1 test pins it; RULINGS: Round one's finding "The rename branch of the staged-verdict filter is unpinned" is CLOSED. Dropping `R` now fails the AC1 test at test\_critic.py:4426, and a mutant that judges the moved file under its old name fails it at line 4427. Verify dry-run passes 3 of 3, and the author's 4 recorded mutants replay killed. Claim inventory of the repair: the AC1 test docstring's added mutant and the commit message's BG1492 paragraph are TRUE by execution. The repair changes no code, hook or changelog of this unit. Mutant notes: `R` dropped with `--no-renames` added is equivalent, since the moved file is then staged as `A` and still refused. `C` is unreachable under git's default rename detection and not judged. The suites over test\_critic.py, test\_critic\_self\_check\_kept\_list.py, test\_critic\_self\_check\_record.py, test\_precommit\_unrecorded\_verdict.py and test\_lean\_commit\_lanes.py pass in a detached worktree (268 passed). Re-ran: my first worktree was written into by another reviewer's mutation run from 22:54 to 22:55 UTC, so I discarded every run taken there and re-ran the baseline, the `R`, `T` and old-name mutants and the type-change probe in a fresh worktree confirmed clean at 23:08 UTC. This verdict rests only on those runs.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1492 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1492 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The type-change branch of the staged-verdict filter is unpinned, the same class as round one's rename finding. Dropping `T` from `--diff-filter=ACMRT` (critic.py:5944) leaves `StagedVerdictTests` and `UnrecordedVerdictLaneTests` green (6 passed). Re-tested alone through `critic.py show --unrecorded-staged` in a fixture: a committed verdict replaced by a symlink and staged (`git diff --cached --name-status` prints `T`) is refused by HEAD (exit 1) and passed by the mutant (exit 0). So a staged verdict whose bytes no recorded row cites would commit with the suite still green, the AC1 Fails-on case. A type-changed case in the AC1 test pins it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1492 AC1 still passes: Given a verdict file staged under sdlc-studio/reviews/verdicts/ that no recorded review row cites, when the staged-verdict check in `critic.py` runs, then it exits non-zero and names the file and the `critic.py record` command that would bind it. Fails on: a verdict still being written passing as a record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StagedVerdictTests::test_a_staged_verdict_no_recorded_row_cites_is_refused_by_name
- [ ] **AC3** BG1492 AC2 still passes: Given a staged verdict file whose bytes a recorded review row cites, when the same check runs, then it exits 0 and prints no refusal. Fails on: the check refusing the verdicts an accept legitimately commits, or passing a file edited after its row was recorded.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StagedVerdictTests::test_a_staged_verdict_its_recorded_row_cites_passes
- [ ] **AC4** BG1492 AC3 still passes: Given a clone with the hooks enabled and an unrecorded verdict file swept in by a git add of the records, when the commit runs, then pre-commit refuses it on a lane that `.githooks/pre-commit --list` prints, and nothing is committed. Fails on: the check existing in `critic.py` with no hook lane calling it.
  - **Verify:** pytest tools/tests/test_precommit_unrecorded_verdict.py::UnrecordedVerdictLaneTests::test_a_commit_holding_an_unrecorded_verdict_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
