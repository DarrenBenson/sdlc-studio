# BG0253: test_the_next_cycle_mints_a_fresh_run asserts inequality of a probabilistically-unique id, so the commit gate fails at random about once in a thousand

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint_rolling.py,.claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by the closing review of RUN-01KY321Q, whose first full suite run failed and whose second passed on an unchanged tree. `PerCycleRunStateTests.test_the_next_cycle_mints_a_fresh_run` asserts two consecutively minted run ids differ, and reported `AssertionError: 'RUN-01KY38CE' == 'RUN-01KY38CE'`. The ids are not unique by construction: `short_ulid()` is 6 timestamp characters covering roughly a 17-minute bucket plus 2 random characters, so two mints milliseconds apart collide with probability about 1 in 1,024. The docstring says so, and `run_state.py` around line 202 already records that `short_ulid` is not monotonic within a second. So the test asserts a property the generator does not provide. This is NOT caused by this sprint or its repair - the only sprint-era edit to that module was BG0242's git confinement, which does not touch minting - but it means the pre-commit gate can fail at random on an otherwise-green tree, and a random red gate is the fastest way to teach people to re-run rather than read. It is also a false negative in the opposite direction: the test would pass a generator that returned a constant 999 times out of 1,000.

## Steps to Reproduce

1. Run the skill suite repeatedly on an unchanged tree: bash tools/skill-tests.sh. 2. About once in a thousand runs, `PerCycleRunStateTests.test_the_next_cycle_mints_a_fresh_run` fails with two identical ids. Observed once during the RUN-01KY321Q review, passing on the immediate re-run and 8 of 8 in isolation. Confirm the mechanism by reading `short_ulid`: 6 timestamp characters at roughly 17-minute granularity plus 2 random characters gives 1,024 distinct values within a bucket.

## Proposed Fix

Decide what the test is actually for, because the two answers differ. If it is that a NEW cycle mints a NEW run rather than reusing the old record, assert the property that matters - that the run record was replaced, that its opened-at moved, that the previous run is closed - none of which depends on the id being unique. If uniqueness of the id itself is the property, then the generator must provide it and the test is correctly failing: widen the random suffix or make the mint collision-checked against existing ids, which the id-allocation path already does elsewhere. Do NOT fix it by retrying or by seeding the random source, which would leave a test that passes a constant generator. Note the adjacent risk while deciding: if run ids can collide, two runs can share an identity in the telemetry and velocity records, which is a data problem rather than a test problem.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
