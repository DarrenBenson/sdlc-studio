# BG0401: Four of this sprint's repairs can be fully reverted with no test going red: the guard is the delivery, and the guard is inert

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_init.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Independent review of RUN-01KYNKDP applied 39 mutants; 8 SURVIVED. Reverting BG0368, BG0385, BG0392's CLI half or BG0395 reddens nothing.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Eight mutants survived the closing review of RUN-01KYNKDP, and four of that sprint's repairs can be reverted with no test in the suite going red.

- BG0368: the guard's filter stats `<root>/sdlc-studio/sdlc-studio/epics`, because `ARTIFACT_TYPES[t][0]` already carries the `sdlc-studio/` prefix. The predicate is False for every type, so `missing` is unconditionally empty. Skipping the index for a type SURVIVES. The commit says 'The guard is the delivery'; the guard is inert.
- BG0385: `for line in close_goal_judgement(root, state):` -> `for line in []:` SURVIVES. The whole delivery - goal panel, defect judgement, prediction miss, caller-check over the batch - unwires silently. The class docstring claims to assert the CALL from the command; every test calls the function.
- BG0392's CLI half: making `plan`/`close` accept `--content-review` and discard it SURVIVES both mutants. The only assertion is that the flag string appears in the parser - which is US0479's defect, shipped in the sprint that removed it.
- BG0395: reinstating the filter the bug removed SURVIVES, and so does deleting the warning outright. The test asserts `lanes_in_flight` returns a row; the filter was in the brief branch of `cmd_lane`.
- BG0357's sole guard was `assertIn('row["test"] = killer', inspect.getsource(...))` - a grep, green with the assignment dead.
- The `test_an_untimed_lane_prints_no_seconds` test re-implements gate.py's formatting inline and asserts it against itself; no change to gate.py can redden it.
- `test_a_waiver_a_judged_unit_does_carry_is_not_double_reported` guards its only assertion behind `if carried:`, which is always False for its fixture.
- `test_spec_counts_are_not_pinned` has no positive control: its regex matches nothing today, so the subTest loop iterates zero times.

## Steps to Reproduce

Copy the repo, purge `__pycache__`, run with `python3 -B`, and apply each mutant named in the summary. Assert the patch changed the file before running. Each listed mutant leaves the suite green.

## Proposed Fix

Each test asserts a property the production code no longer has to have.

1. BG0368: drop the doubled prefix, and add the `assertTrue(checked)` guard four sibling tests in the same range already carry.
2. BG0385: assert `cmd_close` REACHES `close_goal_judgement` - the mechanism moved, so the caller test must move with it.
3. BG0392: drive the flag through and assert the review is RECORDED, not that the flag parses.
4. BG0395: exercise the brief path where the filter was.
5. Replace every `assertIn(<source text>, inspect.getsource(...))` with a behavioural assertion, or delete it - a grep cannot fail for the reason it claims.
6. Give every scan-style guard a positive control, as `test_dead_flag_docs` and `test_seat_examples_quote_real_goals` already do.

## Acceptance Criteria

- [ ] Each of the eight surviving mutants is killed by a test that fails for the reason it names.
- [ ] No new test asserts source text where the behaviour is reachable - a grep proves the string is present, never that the code runs.
- [ ] Every scan-style guard carries a positive control, so a regex that stops matching reads as a broken guard rather than a clean tree.
- [ ] The vacuous-fixture pattern (an assertion behind an `if` that is always False) is absent from the range.

## Impact

The mutation count is the evidence that these tests are not vacuous. Eight of thirty-nine survived, which means the repairs they cover are unprotected: a later change can revert any of them and every gate stays green. Four are repairs from the sprint that also wrote 'a test written by the author of a fix asserts the shape of the fix' into its own carried lessons.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
