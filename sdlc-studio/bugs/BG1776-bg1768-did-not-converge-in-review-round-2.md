# BG1776: BG1768 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py, changelog.d/BG1768.md, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Created:** 2026-11-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-27T13:02:38Z

## Summary

BG1768 was rejected at round 2, the review cap, by agent-add468292e4378640 (qa), so it was carried as a known issue rather than reviewed again. Filed at Low rather than the carry's default Medium: the release bar (`review.blocking_priority`) bars Medium, and Low is the most severe level it allows. The findings still open: BLOCKING: [new] the fragment's new index claim is false for `--since` without `--files`: changelog.d/BG1768.md says of `mutation.py run --since REF` that "the index is never rewritten, even when a staged file's cached stat data is stale", but with no `--files` the surface comes from `select_files`, whose `git diff --name-only REF` (mutation.py:1692) refreshes a stale index and writes it. Measured on the AC1 fixture after its own `_stale`: `mutation.py run --since main --test <the unit's command> --format json --dry-run` takes the copy route over calc.py and test\_calc.py, exits 1, and leaves `.git/index` with new bytes and a new mtime, while the same run with `--files pkg/calc.py` leaves both unchanged. `git --no-optional-locks diff --name-only main` rewrites a stale index too, and `git diff --cached` and `git ls-files` do not. The rewrite itself predates the unit (the base refuses the same run and rewrites the index the same way, and the call dates from a30eecb22), so only the sentence is new, and `--since main` with no `--files` is the form the bug's summary says builders were asked to run. Say it of `--files` or of the copy itself, or stop the surface selection refreshing the index [LC-018]; RULINGS: "the AC1 test cannot fail when the copy route writes the real index" CLOSED: `_stale` ages every file's stat data, the test asserts the index's bytes and mtime are unchanged beside a control, and the round-one mutant (status without `--no-optional-locks`) now fails test\_a\_staged\_target\_is\_mutated\_in\_a\_private\_copy\_of\_the\_index at line 136 for that reason. "the copy route's baseline-red remedy names the wrong tree" CLOSED: INDEX\_COPY\_RED (mutation.py:1396) replaces it only for a failed baseline over a copy, the error and in-place remedies keep theirs, test\_a\_red\_staged\_suite\_names\_the\_copy\_not\_the\_working\_tree reproduces the round-one probe, and dropping the override (mutation.py:1295) turns it red. "the copy route's `since` is unpinned" CLOSED: the round-one mutant, `"HEAD"` for `since` in `run_in_index_copy`, now fails test\_the\_copy\_measures\_the\_diff\_against\_since\_not\_head with "4 != 2". "a test command that names the repository by absolute path" CLOSED as answered by documentation: the page and the fragment now state it, and test\_an\_absolute\_test\_path\_runs\_the\_working\_tree\_not\_the\_copy measures it. Remark: round one's commit f7cb9a8b1 fails test\_confinement.py here (1 failed, 42 passed) because it moved the report write out of run\_gate, a suite my round-one pass did not run. The repair restores the write site and test\_confinement passes. The undeclared docs/known-issues.md and docs/release-notes-v6.5.0.md come from the paperwork commit e1db512e2, which names many units, not from BG1768's code commits, so its Affects is not wrong. Claim inventory for the repair: the page's absolute-path sentence (line count held at 859), the run\_gate docstring on `tree` and `report_as`, INDEX\_COPY\_RED, the commit message's test\_confinement account, and the fragment's other sentences (the diff is against REF not HEAD, a red baseline names the copy and asks for staging, no mutant touches the working tree) are TRUE by execution. Checks: 468 tests across the unit's module, test\_mutation, test\_mutation\_runner, test\_critic, test\_confinement, test\_lean\_mutation\_opt\_in, test\_lean\_no\_mutation\_gates and tools/tests/test\_doc\_claims pass at 4a4f7fc2a, verify\_ac run --id BG1768 --dry-run gives 4 of 4, and lint-style reports nothing on the changed files.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1768 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1768 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the fragment's new index claim is false for `--since` without `--files`: changelog.d/BG1768.md says of `mutation.py run --since REF` that "the index is never rewritten, even when a staged file's cached stat data is stale", but with no `--files` the surface comes from `select_files`, whose `git diff --name-only REF` (mutation.py:1692) refreshes a stale index and writes it. Measured on the AC1 fixture after its own `_stale`: `mutation.py run --since main --test <the unit's command> --format json --dry-run` takes the copy route over calc.py and test\_calc.py, exits 1, and leaves `.git/index` with new bytes and a new mtime, while the same run with `--files pkg/calc.py` leaves both unchanged. `git --no-optional-locks diff --name-only main` rewrites a stale index too, and `git diff --cached` and `git ls-files` do not. The rewrite itself predates the unit (the base refuses the same run and rewrites the index the same way, and the call dates from a30eecb22), so only the sentence is new, and `--since main` with no `--files` is the form the bug's summary says builders were asked to run. Say it of `--files` or of the copy itself, or stop the surface selection refreshing the index [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1768 AC1 still passes: a staged target is mutated in a private copy of the index under --since
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py::StagedSinceTests::test_a_staged_target_is_mutated_in_a_private_copy_of_the_index
- [ ] **AC3** BG1768 AC2 still passes: unstaged and untracked work is still refused, and the refusal names the staged route
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py::StagedSinceTests::test_unstaged_and_untracked_work_is_still_refused_naming_the_staged_route
- [ ] **AC4** BG1768 AC3 still passes: the JSON report states the run was isolated and names repository paths
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py::StagedSinceTests::test_the_report_states_isolation_and_names_repository_paths
- [ ] **AC5** BG1768 AC4 still passes: the review reference states the staged route at no cost in lines
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py::StagedSinceTests::test_the_review_reference_states_the_staged_route

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Filed |
