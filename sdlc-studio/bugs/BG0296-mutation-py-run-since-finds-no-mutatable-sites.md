# BG0296: mutation.py's test-file scan descends into gitignored worktree copies (.claude/worktrees/agent-*/), padding the covering command with dozens of stale duplicate test paths

> **Status:** Fixed
> **Verification depth:** functional
> **Created:** 2026-07-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Severity:** Medium
> **Points:** 3

## Summary

`_candidate_test_files` walks the tree with `rglob` and skips only a fixed `_SKIP_DIRS` set. It
does NOT skip gitignored paths, so it descends into the git worktrees this project creates under
`.claude/worktrees/agent-*/` (gitignored). Each holds a full duplicate of every test, so the
reference scan and `--suggest-test` covering command are padded with dozens of stale worktree
copies, and running that command re-runs those copies.

**The original filing blamed guard-clause blindness. That premise was DISPROVED before this was
built:** the `invert-guard` profile matches an `if <cond>:` line and inverts it cleanly, and a real
file (changelog.py) enumerated 97 sites including guards. The "nothing to mutate" that motivated
the filing was an invocation artefact (passing `--files` and `--since` together), not a real
guard-clause gap. The reproducible defect is the gitignored-worktree pollution, and this bug is
repointed to it.

## Steps to Reproduce

1. Have one or more git worktrees under `.claude/worktrees/agent-*/` (the parallel-build layout).
2. Run `mutation.py run --since HEAD --suggest-test`.
3. Observe the covering command padded with `.claude/worktrees/agent-*/tests/test_*.py` paths -
   duplicate copies of the repo's own tests, from stale worktrees.

## Proposed Fix

Filter gitignored paths out of the candidate test set (one batched `git check-ignore`), rather than
adding `worktrees` to `_SKIP_DIRS`: a component match on `worktrees` reproduces the recorded scar
where the tool, run from INSIDE a worktree, matches an ancestor component and skips the whole tree.
Filtering on `.gitignore` excludes the worktree copies wherever they sit and never blanks a real
tree. Best-effort: on any git failure the scan returns its candidates unfiltered rather than
breaking.

## Acceptance Criteria

### AC1: gitignored worktree copies are excluded, the real tests survive

- **Given** a repo with a tracked `tests/test_x.py` and a gitignored `.claude/worktrees/agent-*/tests/test_x.py`
- **When** the test-file scan runs
- **Then** the tracked test is returned and no worktree copy is - the covering command is not padded with stale duplicates
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::WorktreeScanExclusionTests::test_gitignored_worktree_copies_are_excluded
- **Verified:** yes (2026-07-26)

### AC2: a real tree under a 'worktrees' ancestor is not blanked

- **Given** a repo whose root legitimately sits under a path component named `worktrees`, with tracked tests
- **When** the scan runs
- **Then** its tests are found - the exclusion is by `.gitignore`, not by a component name, so the recorded whole-tree-skip scar does not recur
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::WorktreeScanExclusionTests::test_a_real_tree_is_not_skipped_by_a_worktrees_ancestor
- **Verified:** yes (2026-07-26)

### AC3: the filter degrades, never breaks

- **Given** a directory that is not a git repository
- **When** the filter runs over its candidates
- **Then** it returns them unfiltered rather than raising - a git failure never breaks the scan
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::WorktreeScanExclusionTests::test_scan_degrades_when_git_is_unavailable
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-26 | sdlc-studio | Repointed from the disproved guard-clause premise to the reproducible gitignored-worktree scan defect |
