# BG0069: Shipped test_gate real-wrapper tests assume the dev-repo path and fail from an install

> **Status:** Fixed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Severity:** low
> **Verification depth:** functional (unit tests)

## Summary

`scripts/tests/test_gate.py` sets `REPO = Path(__file__).resolve().parents[5]`, which is
only the artifact-bearing repo root when the skill sits at
`<repo>/.claude/skills/sdlc-studio/`. Run from an install
(`~/.claude/skills/sdlc-studio/`), `parents[5]` is the home directory, no
`sdlc-studio/` workspace exists there, and two tests fail on environment rather than
code: `test_real_wrappers_run_and_shape` (gate degrades to 1 check, expected 12) and
`test_provenance_blocking_follows_enforce`. 1,270 of 1,272 pass. Misleading signal: a
consuming operator verifying an install sees FAILED and cannot tell it from a real
defect - the suite already skips one test conditionally, so the precedent exists.

## Steps to Reproduce

1. Forward-port the skill to `~/.claude/skills/sdlc-studio/` (rsync, per convention)
2. `cd ~/.claude/skills/sdlc-studio && python3 -m unittest discover -s scripts/tests`
3. Two `GateRealWrapperTests` failures; same suite is green inside the dev repo

## Proposed Fix

The two repo-coupled tests detect the expected shape (`REPO / "sdlc-studio"` exists and
`REPO / ".claude/skills"` contains this file) and `skipTest` with an explicit
"dev-repo-only test, no workspace at expected root" message otherwise - a visible skip,
never a silent pass. Keep the assertion content unchanged in-repo.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | claude | Found during the 3.6.0 forward-port to the local install |
