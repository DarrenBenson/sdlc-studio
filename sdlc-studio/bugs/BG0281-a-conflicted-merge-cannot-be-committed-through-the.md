# BG0281: a conflicted merge cannot be committed through the gate: the commit-msg hook tests invoke the hook with the OUTER repo as cwd, so they inherit its MERGE_HEAD, the hook correctly exits early, and five tool-tests fail for the duration of every merge

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/test_commit_msg_hook.py
> **Severity:** High
> **Points:** 2

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

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

### AC2: the isolation does not make the tests vacuous

- **Given** a fixture repository built for the test
- **Then** the hook still finds its checker script there, so a passing test proves the refusal ran rather than proving the hook exited early
- **Verify:** pytest tools/tests/test_commit_msg_hook.py::CommitMsgGateTests::test_partially_covered_multi_id_is_refused_naming_the_gap

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
