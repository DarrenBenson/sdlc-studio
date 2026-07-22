# BG0253: test_the_next_cycle_mints_a_fresh_run asserts inequality of a probabilistically-unique id, so the commit gate fails at random about once in a thousand

> **Status:** Fixed
> **Verification depth:** functional - the collision was reproduced deterministically rather
> than waited for, by driving the mint with a CONSTANT generator (which is also the false
> negative the filed report names: the old assertion would have passed a constant 999 times in
> 1,000). Red first: two consecutive mints returned the same id. Then fixed, then mutation-
> proven with 5 hand-applied mutants, all killed. The flaky test itself now asserts the
> properties that say a fresh run was minted - a new record, the previous one closed and
> archived, and an id no archived run holds.
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

## Acceptance Criteria

- [x] **AC1:** A run id is collision-checked against the runs this project has already
      recorded, so two consecutive mints differ even when the generator returns a constant.
      Pinned by `test_run_state.ARunIdIsUniqueByConstructionNotByLuck`.
- [x] **AC2:** The check reads the ARCHIVE, not only the live record, because a closed run's
      identity outlives the file it was minted into.
      Pinned by `test_run_state.test_an_archived_run_s_id_is_never_minted_again`.
- [x] **AC3:** The cycle-boundary test asserts the properties that say a fresh run was minted,
      not an id inequality alone.
      Pinned by `test_sprint_rolling.test_the_next_cycle_mints_a_fresh_run`.

## Resolution

Both halves of the filed choice, because the report is right that they answer different
questions and wrong that only one is needed.

The GENERATOR could not provide uniqueness, so the ALLOCATOR does. `run_state._mint_run_id`
checks a candidate against every archived run and the run being replaced, retries on a clash,
and extends the suffix on a persistent one - the same shape `sdlc_md.mint_v3_id` has always used
for artefact ids, and the backstop `short_ulid`'s own docstring names. It is minted after the
outgoing run is archived, so the run being replaced is already in the register the new id is
checked against. Nothing retries the test and nothing seeds the random source, which the report
correctly ruled out: both would leave a test a constant generator passes.

The TEST then asserts what it is actually for. The id inequality is kept, because it is now a
property the allocator genuinely provides rather than a 1-in-1,024 bet, and beside it the
boundary asserts a new open record, the previous run closed and archived, and an id no archived
run holds.

The adjacent risk the report flagged is what made this worth more than a flake fix: telemetry,
the run archive and the velocity record all join on the run id, so two runs sharing one is a data
problem, not a test problem. That is the hole the allocator closes.

### Repair round (independent review of RUN-01KY3MFX)

The claim above - "unique BY CONSTRUCTION, not by luck" - was not yet true of the last
candidate. After 16 clashes the mint returned `RUN-{new_ulid()[:12]}` **unchecked**, so driving
both generators constant produced a duplicate: the fallback was exactly the luck the allocator
exists to replace, and the only candidate the register never saw. Every candidate is now
checked, and when even the extended suffix cannot produce a free id the mint RAISES rather than
handing back a known duplicate - that is a broken generator, not an unlucky one, and returning
a duplicate would merge two runs' records. Pinned by
`test_run_state.test_the_extended_fallback_is_checked_against_taken_too` and
`test_run_state.test_both_generators_constant_refuses_rather_than_returning_a_duplicate`.

The review also found `taken.add((outgoing or {}).get("run_id"))` dead: `open_run` archives the
outgoing run before minting, so mutating that line to `pass` killed nothing. It STAYS, and now
says why in the code - the redundancy holds only while the archive write succeeds, and an
archive that could not be written leaves the register without the run being replaced. It is
pinned directly by `test_the_outgoing_run_is_excluded_even_when_the_archive_missed_it`, since
no path through `open_run` can reach it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-22 | sdlc-studio | Fixed: collision-checked run-id mint, and the test asserts the property it is for |
| 2026-07-22 | sdlc-studio | Repair round: the extended fallback is checked too and refuses rather than duplicating; the outgoing-run exclusion kept and pinned directly; 2 hand-applied mutants, both killed |
