# BG0401: Four of this sprint's repairs can be fully reverted with no test going red: the guard is the delivery, and the guard is inert

> **Status:** Fixed
> **Verification depth:** functional + mutation (all five re-run: 2 already KILLED, 2 SURVIVED and now killed, 1 caught at runtime by a writer refusal with the gap stated)
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

### AC1: the kill attribution is exercised through the production path

- **Given** a killed mutant whose runner output names the killing test
- **When** the shipped attribution runs
- **Then** both `killed_by` and `test` carry that name, asserted on the VALUE - the previous guard was `'row["test"] = killer' in inspect.getsource(...)`, a grep that stays green with the assignment dead
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KillerScalarTests::test_the_row_carries_the_killing_test_in_both_fields
- **Verified:** yes (2026-08-02)

### AC2: an unattributed kill invents nothing, and a survivor is not attributed

- **Given** a kill whose output names no test, and a surviving mutant
- **When** the attribution runs
- **Then** neither gains a name - absent is TRUE, and a fabricated one is evidence about the wrong test
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KillerScalarTests::test_an_unattributed_kill_carries_no_invented_name
- **Verified:** yes (2026-08-02)

### AC3: a content review must name the goal it answers

- **Given** a review recorded against an empty goal - which is exactly what the surviving call-site mutant produced
- **When** it is written
- **Then** it is refused, because an answer with no question cannot be scored at the close and reads exactly like one about the sprint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContentReviewGoalTests::test_a_review_recorded_against_no_goal_is_refused
- **Verified:** yes (2026-08-02)

### AC4: a recorded review carries its goal

- **Given** a plan-phase review recorded against a real goal
- **When** it is read back
- **Then** the goal is on the record, so the close has the question its answer belongs to
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContentReviewGoalTests::test_the_plan_records_the_review_against_its_sprint_goal
- **Verified:** yes (2026-08-02)

## What was re-measured rather than assumed

Each of the five surviving mutants in the filing was re-run before any work:

| Mutant | Verdict now |
| --- | --- |
| BG0368 - skipping a type's index | KILLED (already fixed) |
| BG0385 - `close_goal_judgement` unwired | KILLED (already fixed) |
| BG0357 - the killer scalar inert | SURVIVED -> fixed here |
| BG0392 - the plan's goal discarded | SURVIVED -> fixed here |

The attribution was EXTRACTED to `attribute_kill` so the production path is callable: it sat
inline, which is why the only available guard was a grep over source text. Both `row["test"]`
and `row["killed_by"]` mutants are now KILLED.

The `--content-review` call-site mutant is caught at RUNTIME rather than by a unit test: with
the writer refusing an empty goal, the mutated call raises and the review is NOT recorded, so
the data can no longer be silently wrong. A CLI-level test driving `plan --write` needs a full
plan fixture and is not delivered here - stated rather than implied.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
| 2026-07-29 | Claude Opus 5 (RUN-01KYPZ1G) | FOUR of the eight killed, and the bug stays OPEN for the other four. Killed: BG0368's guard (it stated `<root>/sdlc-studio/sdlc-studio/epics`, so the predicate was False for every type and `missing` was unconditionally empty - now stats the real path and carries a positive control); BG0385's call site (a sentinel patched into `close_goal_judgement` and the close RUN, so unwiring the call reddens where every previous test called the function directly); the waiver double-report guard (its only assertion sat behind `if carried:`, always False because the fixture's story was Draft and the lane judges delivered units - the fixture is now Done and the assertion runs); and the untimed-lane guard (it re-implemented gate's formatting inline and asserted it against itself, so no change to gate.py could redden it - `lane_stamp` is now extracted and asserted, with a measured zero pinned as distinct from untimed). STILL OPEN: BG0392's CLI half, BG0395's filter, BG0357's source-grep guard, and `test_spec_counts_are_not_pinned`'s missing positive control. |
