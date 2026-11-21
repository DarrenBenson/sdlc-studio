# BG1693: BG1470 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1470.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T19:37:45Z

## Summary

BG1470 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the `_loose` docstring (lanes.py:278-279) and the copy test's (test\_lane\_land.py:520-521) give the reason only a work-tree rename's source is named: a copy's source "is listed on its own wherever it changed". Execution shows that is false where the source is deleted in the work tree. With `status.renames=copies`, `src/b.py` deleted and two identical copies added with `git add -N`, `git status --porcelain=v1 -z` prints a status line for `src/c1.py` whose index column is blank and whose work-tree column is C, and one for `src/c2.py` whose index column is blank and whose work-tree column is R, each followed by `src/b.py` as its source, and `src/b.py` has no entry of its own. `sprint.py lane land` still refuses with exit 2, naming `src/b.py (unstaged), src/c1.py (unstaged), src/c2.py (unstaged)`, because the rename entry names the source. So the code is right and the sentence is wrong. The same false reason is in the commit message and in the author's answer for the surviving mutant, though the mutant is still equivalent [LC-018]; BLOCKING: [new] the non-UTF-8 test's docstring (test\_lane\_land.py:431-432) says "the refusal names it as the filesystem spells it". Through `sprint.py lane land`, the raw stderr of the refusal reads `src/stray-\udcff.py (untracked)`. That is Python's surrogate escape written out with backslashreplace, while the filesystem holds the byte 0xff and git spells the name `"src/stray-\377.py"`. The test's own pattern (`\S+`) accepts any spelling, so nothing pins the sentence [LC-018]; RULINGS: Round 2, the review cap, judged on c70b799e (lanes.py, test\_lane\_land.py, changelog.d/BG1470.md). The verify\_ac dry run passes 3/3\\\; all 36 tests in test\_lane\_land.py pass in a clone. Each round-1 finding: (1) the work-tree rename misread by `_loose` is CLOSED. My two scenarios, run again through `lane land`, now give `src/b.py (unstaged), src/b3.py (unstaged)` and `CHANGES.txt (unstaged), docs.txt (unstaged), src/stray.py (untracked)`, both exit 2 with no hook run. These also come out right: a source starting with R (README moved to README.md, beside an untracked Rstray.py), a staged rename followed by a work-tree rename, a staged rename whose source is re-created untracked, a plain mv and a work-tree copy. My mutants are killed: skipping the source only on the index column, not naming the source, and naming it untracked. (2) The unpinned several-worktree preflight check is CLOSED: dropping it fails the new test on 2 != 1 with both hand-ins copied. (3) The unpinned `os.fsdecode` is CLOSED: a strict decode is killed. (4) The unpinned unstaged deletion is CLOSED: narrowing to `tree == "M"` is killed. (5) The missing space in `story = self.wt` is CLOSED. Naming a staged rename's source too is killed by `test_a_staged_rename_is_no_leftover`. The surviving mutant that names a copy's source from the copy entry is equivalent: in every state I probed, the source is named elsewhere, by its own entry or as a rename's source. Claim inventory for the repair: the changelog's added sentences are TRUE by CLI (every worktree of several, the first and the second\\\; the unstaged deletion\\\; a moved file named under both paths, with or without `add -N`\\\; the non-UTF-8 name). The commit message is TRUE except for the copy-source reason. The `_loose` docstring is TRUE except for that same sentence. The two ruff RUF100 hits the new tests add follow the file's existing `noqa: SLF001` convention, and no hook runs ruff.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1470 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1470 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the `_loose` docstring (lanes.py:278-279) and the copy test's (test\_lane\_land.py:520-521) give the reason only a work-tree rename's source is named: a copy's source "is listed on its own wherever it changed". Execution shows that is false where the source is deleted in the work tree. With `status.renames=copies`, `src/b.py` deleted and two identical copies added with `git add -N`, `git status --porcelain=v1 -z` prints a status line for `src/c1.py` whose index column is blank and whose work-tree column is C, and one for `src/c2.py` whose index column is blank and whose work-tree column is R, each followed by `src/b.py` as its source, and `src/b.py` has no entry of its own. `sprint.py lane land` still refuses with exit 2, naming `src/b.py (unstaged), src/c1.py (unstaged), src/c2.py (unstaged)`, because the rename entry names the source. So the code is right and the sentence is wrong. The same false reason is in the commit message and in the author's answer for the surviving mutant, though the mutant is still equivalent [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: BLOCKING: [new] the non-UTF-8 test's docstring (test\_lane\_land.py:431-432) says "the refusal names it as the filesystem spells it". Through `sprint.py lane land`, the raw stderr of the refusal reads `src/stray-\udcff.py (untracked)`. That is Python's surrogate escape written out with backslashreplace, while the filesystem holds the byte 0xff and git spells the name `"src/stray-\377.py"`. The test's own pattern (`\S+`) accepts any spelling, so nothing pins the sentence [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1470 AC1 still passes: Given a lane worktree whose builder recorded a self-check, leaving sdlc-studio/reviews/author-self-checks.md modified and unstaged beside a staged change, when `sprint.py lane land` runs, then it restores that file before the commit, the lane commits, rebases and fast-forwards in one pass, and the self-check is recorded on the root. Fails on: the rebase refused over unstaged changes after the hooks have already run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_self_check_ledger_left_unstaged_does_not_stop_the_land
- [ ] **AC4** BG1470 AC2 still passes: Given a worktree holding any other unstaged or untracked file outside the hand-in path, when `sprint.py lane land` runs, then it refuses before the commit, naming the file, and no commit is made and no hook runs. Fails on: the hooks running first and the refusal coming only at the rebase, or the leftover file silently discarded.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_leftover_file_is_refused_before_the_hooks_run
- [ ] **AC5** BG1470 AC3 still passes: Given a worktree holding only its staged change, the hand-in files and the unstaged verify edit to the unit's own artefact, when `sprint.py lane land` runs, then it lands as before. Fails on: the new check refusing a clean lane, the hand-in, or the edit the land already discards.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_clean_lane_still_lands

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
