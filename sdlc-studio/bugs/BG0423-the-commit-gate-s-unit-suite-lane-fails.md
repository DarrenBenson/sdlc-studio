# BG0423: The commit gate's unit-suite lane fails on the first attempt and passes on an identical retry, twice in one session, costing a full 8-minute gate run each time

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, tools/skill-tests.sh
> **Evidence:** RUN-01KYPZ1G, two occurrences. (1) Commit of the US0462 review repairs: `git commit` reported a skill-tests failure and 'Commit blocked'; `bash tools/skill-tests.sh` run standalone immediately afterwards reported `Ran 5392 tests ... OK`; the identical `git commit -F` then succeeded as 31913621. (2) Commit of US0463 AC5: same shape, blocked once, succeeded on retry as 263c2072. In both cases the full suite had been run green by hand minutes before, and `reconcile detect` reported drift_items=0.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

Twice in one session the gate blocked a commit on its unit-suite lane and then passed the byte-identical commit on retry. Nothing about the tree changed between the two attempts.

This matters more than the eight minutes it costs. A gate that fails intermittently trains an operator to retry rather than to read, and the whole argument for an un-skippable gate is that a red lane means something. Two false reds in one session is enough to start discounting the third, which is the one that will be real.

What is NOT yet known is the failing test, because the blocking output was not captured either time: the lane prints its failure into the hook's own output, and by the time the retry succeeded that output was gone. The first diagnostic step is therefore to make the failure survivable - tee the suite output to a file under `.local/` so a blocked commit leaves evidence behind rather than a memory of one.

Two hypotheses worth testing, neither confirmed:

A race on bytecode. The session purges `__pycache__` before running suites by hand, and the hook runs its own suite immediately afterwards; a partially-written `.pyc`, or a purge landing mid-run, would produce exactly this shape. Recorded scars in this project already cover stale bytecode producing false mutation verdicts, so the mechanism is known to bite here.

A verdict cache keyed to the wrong revision. The blocked output carried `suite-verdict: green (full) recorded for <the PREVIOUS commit's sha>`, which suggests the verdict file records against HEAD rather than against the tree being committed. If a stale entry is consulted, the lane could refuse on evidence belonging to a different tree.

## Steps to Reproduce

1. Make a substantive change touching `scripts/`, so the hook selects the unit suites.
2. Run the full suite by hand and see it green.
3. `git commit` - observe the suite lane fail and the commit blocked.
4. Re-run `git commit` with the identical message and staged tree - observe it pass.

## Proposed Fix

1. **Tee the suite output to `sdlc-studio/.local/gate-suite-last.log` first.** Without evidence surviving the retry, every later step is guesswork. This is the whole fix for the first iteration.
2. Then reproduce with the log in hand and name the failing test.
3. Check whether `gate-suite-verdict.json` is keyed to the committed tree or to HEAD, and whether a stale entry can be consulted.
4. Only then decide the repair. Do NOT 'fix' this by adding a retry to the hook: a lane that passes on the second run is not a lane, and a hook that hides its own flake is worse than one that costs eight minutes.

## Acceptance Criteria

- [ ] A blocked commit leaves the suite output in `sdlc-studio/.local/`, so the failing test is named after the fact rather than lost with the terminal.
- [ ] The flake is reproduced with that log in hand and the failing test is named in this bug before any repair is attempted.
- [ ] Whether `gate-suite-verdict.json` is keyed to the committed tree or to HEAD is stated, with the answer read from the code rather than assumed.
- [ ] The repair is not a retry inside the hook: a test asserts the suite lane runs exactly once per commit attempt, so a flake cannot be papered over by re-running it.
- [ ] A test covers whichever cause is found - a bytecode race or a stale verdict - so the same shape reddens the guard instead of recurring.

## Impact

The gate is the project's argument that its records mean something - AGENTS.md calls it un-skippable and the pre-commit hook exists to make it so. An intermittent red teaches the operator to retry past it, and a gate people retry past protects nothing. It also costs about eight minutes per false failure, against a lane already 59% over its declared 380s budget, which is the pressure that gets guards switched off.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Filed |
