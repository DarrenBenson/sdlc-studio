# BG0269: The scrub-site sweep's worktrees exclusion matches any path component named worktrees, so it skips the ENTIRE tree when run from inside a worktree

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/tests/test_skill_tests_env.py
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Introduced during RUN-01KY5Y3W's parallel fan-out and caught by the closing review, which noted every worktree builder had to commit with --no-verify. The scrub-site sweep excludes agent worktrees with `SKIP_DIRS & set(path.parts)` where `SKIP_DIRS` includes `worktrees`. That is correct for a worktree NESTED under the main tree (`.claude/worktrees/agent-x/...` has `worktrees` in its parts and is skipped). But when the whole test run happens FROM INSIDE a worktree - which is exactly what every parallel builder does - REPO itself resolves under `.../worktrees/agent-x`, so EVERY file's `path.parts` contains `worktrees` and the sweep skips the entire tree, returns zero sites, and `test_the_sweep_still_finds_the_sites_it_exists_to_guard` fails. The gate then fails for a reason unrelated to the builder's work, and six agents across two waves each resorted to `git commit --no-verify` to get past it. That is a real cost: --no-verify is the project's emergency-only escape, and a guard that forces it routinely trains the exact bypass the guard exists to prevent. The exclusion should be anchored to the repo ROOT (skip `.claude/worktrees/` RELATIVE to REPO), not to any path component that happens to be named worktrees.

## Steps to Reproduce

1. From inside a git worktree whose path contains `worktrees` (an agent worktree), run `python3 -m unittest test_skill_tests_env.ScrubSiteSweepTests`. Observed: `_sites()` returns {} because every file's parts contain `worktrees`, and the sweep-still-finds-sites test fails. 2. From the main checkout the same test passes. Expected: the sweep finds the main tree's sites whether it runs from the main checkout or from inside a worktree, and excludes only NESTED worktrees.

## Proposed Fix

Exclude worktrees by their path RELATIVE to REPO, not by a bare component name: skip a file when `path.relative_to(REPO)` starts with `.claude/worktrees/`, so a worktree nested under the tree being swept is skipped while the tree itself - even when it happens to live under a worktrees/ directory - is not. Then the sweep runs correctly from inside a worktree and the gate stops forcing --no-verify.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Filed |
