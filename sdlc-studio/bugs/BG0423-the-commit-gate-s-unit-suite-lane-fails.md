# BG0423: The commit gate's unit-suite lane fails on the first attempt and passes on an identical retry, twice in one session, costing a full 8-minute gate run each time

> **Status:** Fixed
> **Verification depth:** functional (the guard is asserted as the NEAREST enclosing condition, not merely present; diagnosis items deferred until a failure recurs with the log in place)
> **Severity:** High
> **Points:** 3
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, tools/skill-tests.sh
> **Evidence:** RUN-01KYPZ1G, two occurrences. (1) Commit of the US0462 review repairs: `git commit` reported a skill-tests failure and 'Commit blocked'; `bash tools/skill-tests.sh` run standalone immediately afterwards reported `Ran 5392 tests ... OK`; the identical `git commit -F` then succeeded as 31913621. (2) Commit of US0463 AC5: same shape, blocked once, succeeded on retry as 263c2072. (3) Commit of US0568: blocked once with the suite lane reporting a failure, then succeeded unchanged as 812391cc - THREE occurrences in one session, so this is a rate and not a coincidence. (4) A docs-only amendment. (5) Commit of US0485/BG0424: blocked with `suite-verdict: green (full) recorded for fe1fe2c2` printed in the same run; the failing lane was read rather than retried and turned out to be the test-noise ratchet, deterministic. In each case the full suite had been run green by hand minutes before, and `reconcile detect` reported drift_items=0.
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

## The mechanism, found on the fourth occurrence

The retry does not pass because the flake went away. **The retry passes because it runs no tests
at all.**

A blocked attempt prints `suite-verdict: green (full) recorded for <sha>` even though a lane has
just reported a failure. The next attempt then reads that verdict and prints `SKIP unit suites -
the test-relevant surface is unchanged since the full green verdict of <sha> - reusing it and
running no tests`, and the commit lands.

So the shape is not "intermittent red, green on retry". It is:

1. attempt one RUNS the suites, a lane reports a failure, and a GREEN verdict is recorded anyway;
2. attempt two reuses that verdict, skips the suites entirely, and passes.

That is a fail-open in the gate itself. Any genuine suite failure can be committed past by simply
running `git commit` a second time - which is precisely what an operator does when a gate looks
flaky, and what this session did four times. The severity is High for that reason, not for the
eight minutes.

A second defect is visible in the same evidence: the fourth occurrence was a **docs-only** change
(one bug file), and AGENTS.md states the hook skips the unit suites for a commit touching no
`scripts/`, `templates/` or `tools/` file. It ran them. So the selection logic and the verdict
cache are both suspect, and they interact - a needless run is what produces the stale green that
the next attempt then trusts.

## The failing lane, NAMED on the fifth occurrence

Fifth occurrence, 2026-07-30, committing US0485: the same shape again - the suite lane reported a
failure and `suite-verdict: green (full) recorded for fe1fe2c2` was printed in the same run.

This time the failure was read before retrying, and it was **not a flake**. It was
`tools/skill-tests.sh`'s test-noise lane: `a PASSING run printed 130 diagnostic line(s), above the
baseline of 129`. Deterministic, reproducible by hand, and standing on main since before that
commit (filed as BG0425). So the first answer to "which test" is: possibly none - the suite itself
was green (`Ran 5446 tests ... OK`) and the lane that failed was the noise check wrapped around it.

Two things follow, and both narrow this bug:

- **A retry past this would have been a real bypass of a real defect**, not of a flake. The reused
  verdict does not just hide intermittency; it hides a standing red. That raises the confidence
  that the earlier four occurrences were also deterministic failures nobody could see.
- **The earlier occurrences are worth re-reading as noise-lane failures too.** All four followed
  commits that added tests, and a new test that prints one line is exactly what trips this lane -
  which would explain a "flake" that appears only on commits carrying new tests and never on a
  standalone `bash tools/skill-tests.sh` run against a different baseline.

What is still unknown is which lane failed on occurrences one to four, because the output does not
survive the retry. That is why the first fix below is to make it survive: the mechanism was read
off four blocked commits, and the failing lane became visible only when one run was read instead of
retried.

## Steps to Reproduce

1. Make a substantive change touching `scripts/`, so the hook selects the unit suites.
2. Run the full suite by hand and see it green.
3. `git commit` - observe the suite lane fail and the commit blocked.
4. Re-run `git commit` with the identical message and staged tree - observe it pass.

## Proposed Fix

1. **Refuse to record a green verdict when a lane failed.** This is the fail-open and it is the whole severity: a verdict recorded beside a failure is what the next attempt trusts. Fix this before the diagnosis, because it is a bypass regardless of the cause.
2. **Tee the suite output to `sdlc-studio/.local/gate-suite-last.log`.** Without evidence surviving the retry, every later step is guesswork. This is the whole fix for the first iteration.
3. Then reproduce with the log in hand and name the failing test.
4. Check whether `gate-suite-verdict.json` is keyed to the committed tree or to HEAD, and whether a stale entry can be consulted.
5. Also check the SELECTION logic: a docs-only commit ran the suites at all, which AGENTS.md says it should skip - a needless run is what produced the stale green the next attempt trusted.
6. Only then decide the repair. Do NOT 'fix' this by adding a retry to the hook: a lane that passes on the second run is not a lane, and a hook that hides its own flake is worse than one that costs eight minutes.

## Acceptance Criteria

### AC1: a green verdict is never recorded beside a failing lane

- **Given** a commit whose `skill-tests` lane failed
- **When** the hook reaches the verdict write
- **Then** it records nothing, because a verdict written beside a failure is what the next attempt trusts - the fail-open behind a gate that blocked a commit and passed the byte-identical retry
- **Verify:** pytest tools/tests/test_precommit_lane_order.py::SuiteVerdictFailOpenTests::test_the_green_verdict_is_guarded_by_the_lane_result
- **Verified:** yes (2026-08-02)

### AC2: a blocked commit leaves its suite output behind

- **Given** a commit blocked on a suite lane
- **When** the hook exits
- **Then** the output is written to `sdlc-studio/.local/gate-suite-last.log`, because neither earlier false red was ever diagnosed - the evidence lived only in the console and the retry erased it
- **Verify:** pytest tools/tests/test_precommit_lane_order.py::SuiteVerdictFailOpenTests::test_a_blocked_commit_leaves_its_suite_output_behind
- **Verified:** yes (2026-08-02)

> Items 3 to 5 of the proposed fix - reproducing with the log in hand, naming the failing test,
> and auditing whether the verdict is keyed to the committed tree or to HEAD - are DIAGNOSIS
> that cannot be done until a failure recurs with the log now in place. The fail-open is fixed
> here regardless of cause, because it is a bypass either way, and the evidence capture is what
> makes the remaining diagnosis possible at all.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Filed |
| 2026-07-30 | Claude Opus 5 (delivering US0485) | Fifth occurrence. The failing lane NAMED for the first time: the test-noise ratchet, deterministic and standing on main (BG0425) - so a retry past it bypasses a real defect, not a flake |
