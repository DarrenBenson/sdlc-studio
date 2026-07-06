# BG0063: github_sync gh() wrapper runs network subprocesses with no timeout

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

The `gh()` wrapper - the skill's only network path - runs `gh` subcommands with no `timeout=`.
Every issue list/create/edit funnels through it, and `cmd_push` calls it in a per-record loop.

## Evidence

- `.claude/skills/sdlc-studio/scripts/github_sync.py:68-77` -
  `subprocess.run(["gh", *args], capture_output=capture, text=True, check=False)`, no
  `timeout=`.
- Contrast: `status.py:52`, `mutation.py:313-315`, `complexity.py:227`, `review_prep.py:33`
  all pass timeouts on their local git calls. This is the one network-adjacent call without
  one.

## Impact

Any hung `gh` call (proxy, auth prompt, network black-hole) blocks the sync command
indefinitely; in an agent-driven loop or CI it burns the whole session instead of failing.
Lesser same-class gaps: `next_id.py:122-125`, `mutation.py:313-315`, and
`tools/check_neutrality.py:62` run local git without a timeout.

## Steps to Reproduce

1. Point `gh` at an unreachable endpoint (or a host that stalls the TCP connect).
2. Run `github_sync.py push`/`pull`.
3. The command hangs rather than failing after a bounded wait.

## Proposed Fix

Add a generous `timeout=` (e.g. 120 s) to `gh()` and convert `TimeoutExpired` into the
existing non-zero/stderr failure path. Optionally add timeouts to the local git calls named
above.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; corroborated by architecture and code-level legs |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
