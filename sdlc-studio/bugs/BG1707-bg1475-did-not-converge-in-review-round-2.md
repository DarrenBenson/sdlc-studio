# BG1707: BG1475 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py, changelog.d/BG1475.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T15:05:36Z

## Summary

BG1475 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [regression] in a project kept in a folder of its repository, a file whose content last changed in a conflict-resolving merge still reads the earlier parent's time, because git names a merge's combined-diff path from the repository top and ignores `--relative` (`review_prep.py:80`), so the walk's `line in tracked` check (`review_prep.py:86`) never matches the merge's line: raw git 2.56.0 in the fixture prints the merge's path as `proj/one/sdlc-studio/bugs/BG0001-b.md` and every ordinary commit's as `sdlc-studio/bugs/BG0001-b.md`, and `staleness` over that fixture (t1, side t2, main t3, conflicted merge t4 2026-04-01, `last_reviewed` 2026-03-15) reads 2026-04-01 with `needs_review` True at the base ref and 2026-03-01 with `needs_review` False at HEAD, so a review older than the file's last change reads as current, the direction that matters\; this is round one's merge finding surviving in the layout the repair itself declares supported, the changelog's "a merge whose artefact differs from each parent's ... still counts as its last change, and a project kept in a folder of its repository still reads its commit times" (`changelog.d/BG1475.md:9-11`) over-claims the two together, and no test combines `test_a_conflict_resolved_in_a_merge_reads_the_merge_time` with `test_a_project_below_the_repository_root_reads_its_commit_times`, so no open bug or test covers it; RULINGS: round one's findings: "a file whose content last changed in a conflict-resolving merge commit" MOVED (closed at the repository root by `-c`, my mutant dropping `-c` is killed by the conflicted-merge test and `-c` to `-m` by the clean-merge test, but it survives for a project in a folder of its repository, the ISSUES finding above)\\\; "the `--relative` flag is unpinned" CLOSED (dropping it fails `test_a_project_below_the_repository_root_reads_its_commit_times`)\\\; "the `if not retro_id:` guard ... is unpinned" CLOSED (`if True:` at `sprint.py:8423` fails `test_a_named_retro_announces_no_scaffold`, and that test fails when `--retro` is not passed, so its absence check is not vacuous)\\\; "the changelog's claim that each step is named on stderr" CLOSED (`file=sys.stdout` at `sprint.py:10999` fails both CloseProgressTests, now that stdout and stderr are read apart). Repair diff: `verify_ac.py run --id BG1475 --dry-run` passes 3 of 3\\\; `test_review_prep.py`, CloseProgressTests and ReviewCurrentDirtyTests 36 passed in the clone\\\; `-c` to `--cc` survives and is equivalent for `--name-only`. Claim inventory: 2 git processes over this repository's 4,235 records (TRUE)\\\; "about 10 seconds on a loaded host" UNVERIFIABLE, load-dependent (the walk alone took 7.9 to 11.0 s with and without `-c` at load 18 to 25, the whole `staleness` 17.4 s at load 10), and `-c` adds no measurable cost here\\\; the only artefacts any merge names under `-c` here are BG0281 and US0412, and each reads the same time as the base's per-path `git log -1`, as did a random 60 of the rest\\\; the docstring's `-c` and `--relative` sentences are TRUE each alone and silent on the combination above.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1475 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1475 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [regression] in a project kept in a folder of its repository, a file whose content last changed in a conflict-resolving merge still reads the earlier parent's time, because git names a merge's combined-diff path from the repository top and ignores `--relative` (`review_prep.py:80`), so the walk's `line in tracked` check (`review_prep.py:86`) never matches the merge's line: raw git 2.56.0 in the fixture prints the merge's path as `proj/one/sdlc-studio/bugs/BG0001-b.md` and every ordinary commit's as `sdlc-studio/bugs/BG0001-b.md`, and `staleness` over that fixture (t1, side t2, main t3, conflicted merge t4 2026-04-01, `last_reviewed` 2026-03-15) reads 2026-04-01 with `needs_review` True at the base ref and 2026-03-01 with `needs_review` False at HEAD, so a review older than the file's last change reads as current, the direction that matters; this is round one's merge finding surviving in the layout the repair itself declares supported, the changelog's "a merge whose artefact differs from each parent's ... still counts as its last change, and a project kept in a folder of its repository still reads its commit times" (`changelog.d/BG1475.md:9-11`) over-claims the two together, and no test combines `test_a_conflict_resolved_in_a_merge_reads_the_merge_time` with `test_a_project_below_the_repository_root_reads_its_commit_times`, so no open bug or test covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1475 AC1 still passes: Given a repository of many tracked artefacts, when `review_prep.staleness` runs, then the number of git processes it starts does not grow with the number of artefacts. Fails on: one `git log -1` per artefact.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::StalenessTests::test_the_git_calls_do_not_grow_with_the_artefacts
- [ ] **AC3** BG1475 AC2 still passes: Given tracked artefacts committed at different times and one untracked artefact, when `review_prep.staleness` runs, then each tracked record carries its own last commit time with method git and the untracked one its file time with method mtime. Fails on: the single pass giving a file another file's time, or losing the untracked fallback.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::StalenessTests::test_the_single_pass_reads_each_files_own_commit_time
- [ ] **AC4** BG1475 AC3 still passes: Given an open run, when `sprint.py close --dry-run` runs, then it prints a line naming each close step as that step starts, before the step's result. Fails on: no output until the verdict, so a slow close cannot be told from a hung one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseProgressTests::test_the_close_names_each_step_as_it_starts

- [ ] **AC5** Given a project in a folder whose name holds a `"`, a `\` or a tab, below its repository top, when `review_prep.py prep` reads its artefacts' commit times, then each artefact reads its commit time, not its file time. Fails on: git quoting the history paths (`review_prep.py:83` and `:87`), so no path matches and every artefact falls back to its file time (round three, verdict 7a83a2e7510b-7b61087e).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::QuotedAndRelativePathTests
- [ ] **AC6** Given the user's git setting `diff.relative = true` and a project folder at the repository top, when `review_prep.py prep` runs, then commit times are read as without the setting, and the docstring's account of the paths git prints is true under it. Fails on: the setting rewriting the history paths so they no longer match (`review_prep.py:63-64`). The reviewer's likely fix for both: `git log -z --no-relative`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::QuotedAndRelativePathTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | BG1475's ruled round three (D0583) rejected for two regressions in the repair; AC5 and AC6 carry them to the next run with the reviewer's likely fix |
