# BG0425: main was one line over its own test-noise ratchet, so the noise gate was enforcing nothing

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/skill-tests.sh, .claude/skills/sdlc-studio/scripts/tests/test_digest.py
> **Evidence:** Found while delivering US0485: the gate reported 130 against a baseline of 129 and I assumed my own new tests had added the line. Measuring HEAD with the change stashed showed the count was already 130 - the assumption was wrong, and checking it is what turned a self-inflicted-looking failure into a standing defect on main.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (delivering US0485); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z
> **Verification depth:** functional

## Summary

`tools/skill-tests.sh` froze `TEST_NOISE_BASELINE` at 129 as a ratchet: the gate fails the moment a change adds a leak, and the number may only be lowered. Measured on 2026-07-30, the shipped suite at HEAD leaked 130 lines - one over - so the lane was RED on main and had been for at least one commit. Every commit since had to either fail that lane or skip the suites, and the skip is what happened: a reused `suite-verdict: green (full)` record let a retry land without running them at all (BG0423). A ratchet that is already breached is not a ratchet; it stops discriminating between a new leak and the standing debt, which is the whole property it exists for.

## Steps to Reproduce

1. `git stash push --include-untracked` to get a clean HEAD (fe1fe2c2).
2. `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests > out 2>&1`, then count leaks with `tools/test_noise.py`: 130.
3. Same measurement with the working change applied: also 130, and the two leak sets are identical apart from randomised temp paths - so the extra line was pre-existing, not newly added.
4. `bash tools/skill-tests.sh` therefore fails its own noise lane on unmodified main.

## Proposed Fix

FIXED. Ten `digest.main(["build", ...])` call sites in `test_digest.py` were leaking a `digest: wrote N closed-artefact digest(s)` line each with nothing capturing stdout; a `_quiet_main` helper captures them and still returns the exit code the tests assert. 130 -> 120, and the ratchet is LOWERED to 120 rather than raised, per the rule recorded beside it. The comment records the measurement so the next reader can tell a captured leak from an amnesty.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `tools/skill-tests.sh` froze `TEST_NOISE_BASELINE` at 129 as a ratchet: the gate fails the moment a change adds a leak, and the number may only be lowered.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (delivering US0485) | Filed |
