# BG0271: the site-sweep test is unrunnable inside a git worktree: an ancestor 'worktrees' path component makes SKIP_DIRS match every file, so sites={} and the pre-commit gate must be bypassed with --no-verify on parallel-worktree builds

> **Status:** Open
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/test_skill_tests_env.py
> **Severity:** Medium
> **Points:** 2

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |

## Detail

Hit by BOTH parallel worktree agents in RUN-01KY7W1F (EP0150 retitle, EP0155 refine): each had to
commit with `--no-verify` because `tools/tests/test_skill_tests_env.py::ScrubSiteSweepTests` fails
only when the gate runs from inside a worktree. `REPO = Path(__file__).resolve().parents[2]`
resolves under `.claude/worktrees/agent-<id>/`, whose path carries a `worktrees` component;
`SKIP_DIRS` (which lists `worktrees` so the sweep ignores transient agent trees) then matches every
file via `set(path.parts)`, the sweep sees zero sites, and the assertion fails on an empty set. The
diff under test touches none of the swept files, so the failure is purely positional.

This directly defeats the un-skippable pre-commit gate for exactly the workflow EP0154 is adding
(parallel worktree delivery): the more we parallelise, the more often the gate is bypassed.

## Acceptance Criteria

- [ ] AC1: the sweep is computed relative to REPO, so an ancestor `worktrees` path component
  (a worktree checkout) no longer makes SKIP_DIRS match every file
- **Given** the test is run with its file resolving under `.../worktrees/agent-X/tools/tests/`
- **When** ScrubSiteSweepTests runs
- **Then** it sees the real site files under REPO and passes, exactly as from the repo root
- **Verify:** pytest tools/tests/test_skill_tests_env.py::ScrubSiteSweepTests
