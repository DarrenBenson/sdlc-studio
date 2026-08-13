# BG0491: lane-check scans only stories, so 487 bugs are outside the number a blocking decision would rest on

> **Status:** Open
> **Verification depth:** functional (executed: lane-check --ids BG0529 printed '0 unit(s)' before and '1 unit(s)' after; the corpus figure moves 181 -> 280)
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Severity:** Medium
> **Points:** 3

## Summary

`lane-check`'s corpus sweep globs `US*.md` (`verify_ac.py`:2106), so bug units are never scanned - `--ids BG0487` silently prints '0 unit(s)' rather than saying the type is out of scope. The measured yield the lane will be judged on is therefore taken over 615 stories while 487 bugs go unlooked-at, and this sprint's own evidence is that bug repairs are where the library-only verifier is commonest.

Separately, `_LANE_MARKERS` (`verify_ac.py`:817) matches a bare `"main("` substring, so a docstring reading 'deliberately does NOT call main()', the identifier `remain(`, and the literal `"domain("` each credit a library-only test as entering the lane. An independent pass measured the honest corpus impact at 4 of 615 - small, and worth closing before the number is used to justify blocking.

## Steps to Reproduce

1. `verify_ac.py lane-check --ids BG0487` -> '0 unit(s)', with no note that bugs are out of scope.
2. Read the glob at `verify_ac.py`:2106 - `US*.md`.
3. Put `# this deliberately does NOT call main()` in a library-only test's node and re-run - reported clean.

## Proposed Fix

Widen the sweep to bug units and restate the yield over the combined corpus. Match the lane markers on a call, not a substring - the AST approach used for the BG0401 seam check in 307ce91d is the shape. Then re-measure and restate the recorded figure once.

## Impact

CR0520 makes the decision to let this lane BLOCK rest on its measured yield. That number currently excludes 487 units and includes a small false-negative rate. Both push in the direction of understating the lane's value, so the decision would be taken on the wrong figure.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
