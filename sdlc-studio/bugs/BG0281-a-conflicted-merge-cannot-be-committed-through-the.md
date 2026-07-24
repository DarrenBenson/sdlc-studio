# BG0281: a conflicted merge cannot be committed through the gate: the commit-msg hook tests invoke the hook with the OUTER repo as cwd, so they inherit its MERGE_HEAD, the hook correctly exits early, and five tool-tests fail for the duration of every merge

> **Status:** Open
> **Verification depth:** functional (unit tests, mid-merge regression proven by running the refusal test with the outer repo carrying MERGE_HEAD)
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/test_commit_msg_hook.py
> **Severity:** High
> **Points:** 2

## Summary

The commit-msg hook tests ran the hook with the OUTER repository as its cwd, so during a merge they
read that repository's `MERGE_HEAD`, met the hook's correct in-progress-operation early exit, and
five refusal tests failed - making a resolved conflicted merge un-committable through the gate.

## Steps to Reproduce

1. Leave the repository mid-merge (a `MERGE_HEAD` in the git dir the hook resolves).
2. Run `python3 -m pytest tools/tests/test_commit_msg_hook.py`.
3. Before the fix: five tests fail (both `CommitMsgGateTests` refusal tests and all three
   `NoSecondBypassTests` subtests), because the hook exits 0 on its in-progress guard.

Re-measured on the fixed tree at Sprint 3b, with `MERGE_HEAD` written into this worktree's git
dir: the current file passes 19 tests, and the pre-fix file (`git show adec58ac:`) fails exactly
those five under the same conditions. The bug is real, and it is closed.

## Proposed Fix

Make each hook invocation hermetic: build a throwaway git repo per call and run the hook there,
with the checker script symlinked in at the path the hook resolves so the refusal genuinely
executes. Write the in-progress marker into the FIXTURE when the mid-merge path is what is under
test, so that behaviour is exercised deliberately rather than inherited.

## Detail

Hit merging Sprint 2's parallel agent branches. A merge conflicted on one story file, was
resolved, and the resulting merge commit was then REFUSED by the gate - because five
`test_commit_msg_hook` tests fail while the merge is in progress.

**The mechanism, measured rather than reasoned.** `tools/tests/test_commit_msg_hook.py::_run`
invokes the hook as `subprocess.run(["bash", HOOK, target], cwd=cwd)` with `cwd=None`, so the hook
runs in the OUTER repository. It has to: the hook resolves its checker as
`$repo_root/.claude/skills/sdlc-studio/scripts/engagement_floor.py` and exits 0 when that file is
absent, so a hermetic temp repo would make every test pass vacuously.

Running there, the hook resolves `git rev-parse --absolute-git-dir` to the outer `.git` - which
during a merge holds `MERGE_HEAD`. The hook then correctly exits 0 on its in-progress-operation
guard (that guard exists so `git merge` and `git revert` are not broken by a generated subject
naming several ids). The refusal tests see rc=0 and fail.

Proven directly on the live repo:

```text
git_dir the hook resolves: .../sdlc-studio/.git
  marker present: MERGE_HEAD
hook rc with MERGE_HEAD present: 0   (tests fail)
hook rc with MERGE_HEAD moved aside: 1   (tests pass)
```

The same holds for `REVERT_HEAD`, `CHERRY_PICK_HEAD`, `rebase-merge` and `rebase-apply`.

## Impact

A deadlock on exactly the workflow this project is investing in. Parallel worktree delivery ends
in merges; any merge that conflicts needs a merge COMMIT; and that commit cannot pass the gate
while the merge is in progress. The only exits are `--no-verify` - the bypass the project has
already recorded a lesson about - or resolving without a merge commit. The failure also
misattributes: it reads as five broken engagement-floor tests rather than as a test-isolation
defect.

## Acceptance Criteria

### AC1: the hook tests do not inherit the outer repository's in-progress-operation state

- **Given** the repository is mid-merge (or mid-rebase, revert, or cherry-pick)
- **When** the commit-msg hook tests run
- **Then** they still exercise the refusal path and pass, because the hook under test is not reading the outer repo's markers
- **Verify:** pytest tools/tests/test_commit_msg_hook.py::CommitMsgGateTests::test_multi_id_without_refs_is_refused
- **Verified:** yes (2026-07-24)

### AC2: the isolation does not make the tests vacuous

- **Given** a fixture repository built for the test
- **Then** the hook still finds its checker script there, so a passing test proves the refusal ran rather than proving the hook exited early
- **Verify:** pytest tools/tests/test_commit_msg_hook.py::CommitMsgGateTests::test_partially_covered_multi_id_is_refused_naming_the_gap
- **Verified:** yes (2026-07-24)

### AC3: a merge commit passes the gate while a merge is in progress

- **Given** a conflicted merge that has been resolved
- **When** the merge commit is made through the pre-commit gate
- **Then** the gate passes without a bypass
- **Verify:** manual

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Fixed and mutation-proven - proved by running the refusal test with the outer repo mid-merge |
| 2026-07-24 | sdlc-studio | Re-verified at Sprint 3b: already fixed by c3f20581; ACs 1-2 pass, AC3 (manual) covered by MidMergeIsolationTests |
