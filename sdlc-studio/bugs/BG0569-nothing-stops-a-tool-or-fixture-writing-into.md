# BG0569: nothing stops a tool or fixture writing into the working tree, and it happened three times in two days - each caught by a gate rather than by its author

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** tools/tests/test_repo_writes.py, .githooks/pre-commit, tools/lint-style.sh
> **Evidence:** Three instances, 2026-08-09 to 2026-08-11, all in this repository. (1) BG0536: a fixture helper took its root as a parameter, a placeholder passed `.`, and every run wrote `src/thing.py`, a fake bug and `sdlc-studio/.local/mutation-runs.json` into the real tree - destroying 23 mutation registrations that `.local/` being gitignored made unrecoverable. (2) US0664: a rehearsal harness's own declared mutant pointed its work root at the repository; one run wrote 41 fixture files that `git add -A` swept onto main, in the commit whose criterion asserts nothing is written inside the repository, and a later run deleted a reviewer's git worktree. (3) 2026-08-11: `verify_ac run --batch` started without `--dry-run` back-annotated seven stories nobody had touched, refused by the conformance lane. Every one was caught by a gate, never by the author. (4) And a FOURTH, found while repairing BG0536 an hour later: a stray `sdlc-studio/bugs/BG0001-x.md` from a test fixture sat untracked in the tree and was caught by the duplicate-id lane, not by anything watching for writes - and the guard test written that same hour asserted only over top-level entries, so it could not have seen it either.
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Three different mechanisms, one shape: something that takes a root, or defaults to one, writes where the author did not intend, and a real path looks exactly like a temp path until somebody checks what changed.

Each was repaired locally and each repair is right. `SurvivorGateTests._repo` refuses a non-temp root. The rehearsal harness refuses a work root inside the repository before its cleanup trap is armed. But those are two guards on two callers, and the third instance had neither because nobody had thought of it yet. The pattern is now established well enough to be worth a rule rather than three fixes.

What is missing is a check that the SUITE leaves the tree unchanged. The suite is the population where this happens - fixtures are where roots are parameters - and the invariant is cheap to state: running the tests must not modify a tracked file, create an untracked one, or touch `sdlc-studio/.local/`. The last is the one that hurts most, because it is gitignored and therefore unrecoverable.

## Steps to Reproduce

1. Note the working tree state, including gitignored `sdlc-studio/.local/`. 2. Run the full suite. 3. Compare. There is no check that answers this, so a fixture that writes into the tree is discovered only when a later gate refuses a commit for reasons that look unrelated.

## Proposed Fix

Add a lane that snapshots the working tree - tracked, untracked AND `sdlc-studio/.local/` - runs the suite, and refuses on any difference, naming the paths. It belongs at the push boundary rather than per commit, on the same reasoning as the release rehearsal: it costs a full suite run. Pin it by deliberately writing a file from a fixture and asserting the lane reddens, with a clean run beside it as the positive control - a lane that reddens on everything is the same failure as one that reddens on nothing.

## Acceptance Criteria

- [ ] **AC1** A lane snapshots the working tree including gitignored `sdlc-studio/.local/`, runs the suite, and reports any path that changed
- [ ] **AC2** A fixture that deliberately writes into the tree makes the lane redden, naming the path it wrote
- [ ] **AC3** A clean suite run leaves the lane green, so it discriminates rather than refusing every run
- [ ] **AC4** The lane binds at the push boundary and not per commit, and its measured cost is recorded

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Filed |
