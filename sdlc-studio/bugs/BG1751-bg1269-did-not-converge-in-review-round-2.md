# BG1751: BG1269 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-delivery.md, changelog.d/BG1269.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T05:16:20Z

## Summary

BG1269 was rejected at round 2, the review cap, by agent-ae6aa6dce0ac8e256 (engineering), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the diff ships "a shared prose page merges cleanly" as the reason a shared page is advisory, and by execution the case it names conflicts: two branches that each append a section to the end of one `.md` page do not rebase cleanly ("append: rebase CONFLICT" in a throwaway repository, while an edit in another section of the page rebases clean). `lane land` replays a lane with a plain `git rebase` (lib/lanes.py:403 and 487, no union merge, no `.gitattributes`), aborts on that conflict and refuses the landing. So two units this plan now places in parallel lanes because they share only a page they both append to will have the second landing refused, while the plan told the operator it would merge cleanly. The claim is the unit's own and absent at the base (`git grep 'merges cleanly' 74903e754` finds no match in the skill). It is printed by `sprint plan` (sprint.py:4821, " - prose only, advisory: a shared page merges cleanly") and written in the worklist header (sprint.py:2960), the `PROSE_SUFFIXES` and `_full_partition` comments (sprint.py:2460, 2804), the `_render_clusters` docstring (sprint.py:4809), reference-delivery.md:19 and 48 and reference-sprint.md:307. AC3 asks only that the share be reported as advisory and leave the partition unchanged, so the repair is the wording: say the page joins no lane and that two units editing one place in it meet a text conflict at `lane land`'s rebase, which names the file to resolve. The behaviour stays as it is. No open bug covers it [LC-018]; RULINGS: Judged across both rounds (c1aa3b055 and 0bcd03956) in a detached worktree at 0bcd03956. verify\_ac BG1269 passes 3/3, and test\_sprint.py::SharedFileClusterTests and ::LanePartitionTests pass (10 passed). The rest of the claim inventory holds: a pair sharing a code file is named on its own line, a wave is warned only over a code file, test files still couple, a cluster holding a code file is never labelled prose only, and `.MD` reads as prose. The bug's own Summary carries the premise ("Prose files most units append to merge cleanly"), and the builder followed it, but the shipped text is what an operator reads at plan time, and the rebase shows it false for the append case it describes. The author's seven mutants replay killed. My mutation pass on the partition code went no further, because the blocking finding is a claim settled by the rebase probe.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1269 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1269 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the diff ships "a shared prose page merges cleanly" as the reason a shared page is advisory, and by execution the case it names conflicts: two branches that each append a section to the end of one `.md` page do not rebase cleanly ("append: rebase CONFLICT" in a throwaway repository, while an edit in another section of the page rebases clean). `lane land` replays a lane with a plain `git rebase` (lib/lanes.py:403 and 487, no union merge, no `.gitattributes`), aborts on that conflict and refuses the landing. So two units this plan now places in parallel lanes because they share only a page they both append to will have the second landing refused, while the plan told the operator it would merge cleanly. The claim is the unit's own and absent at the base (`git grep 'merges cleanly' 74903e754` finds no match in the skill). It is printed by `sprint plan` (sprint.py:4821, " - prose only, advisory: a shared page merges cleanly") and written in the worklist header (sprint.py:2960), the `PROSE_SUFFIXES` and `_full_partition` comments (sprint.py:2460, 2804), the `_render_clusters` docstring (sprint.py:4809), reference-delivery.md:19 and 48 and reference-sprint.md:307. AC3 asks only that the share be reported as advisory and leave the partition unchanged, so the repair is the wording: say the page joins no lane and that two units editing one place in it meet a text conflict at `lane land`'s rebase, which names the file to resolve. The behaviour stays as it is. No open bug covers it [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1269 AC1 still passes: Given a batch whose units all declare one reference doc and two of which also declare one code file, when `sprint.py plan` prints its shared-file report, then a line of its own names that pair and the code file they share. Fails on: the code file listed only inside the batch-wide cluster.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SharedFileClusterTests::test_a_pair_sharing_a_code_file_is_named_on_its_own_line
  - **Verified:** yes (2026-11-25)
- [ ] **AC3** BG1269 AC2 still passes: Given the same batch, when the lane partition is computed, then the two units sharing the code file sit in one lane or in strictly sequential waves. Fails on: both units placed in parallel lanes of one wave.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LanePartitionTests::test_units_sharing_a_code_file_are_never_parallel
  - **Verified:** yes (2026-11-25)
- [ ] **AC4** BG1269 AC3 still passes: Given units that share only a prose file, when the batch is planned, then the share is reported as advisory and the partition is unchanged. Fails on: a shared reference doc forcing the units sequential.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SharedFileClusterTests::test_a_shared_prose_file_stays_advisory
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
