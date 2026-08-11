# BG0522: BG0515's fix reproduces BG0515: a charter with an unresolved Open Question leaves the run open and the charter Queued

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Established by the engineering review seat at the RUN-01KZ79C1 boundary, driven through the shipped CLI in an isolated clone. `Spent` is declared a charter terminal at lib/sdlc_md.py:1279.
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`spend_charter` routes the status write through `transition.main`, which was the right instinct - transition syncs the index and runs the status gates. But `Spent` is a charter TERMINAL in the shared registry, so transition applies its terminal Open-Questions gate to it. A charter carrying one unresolved Open Question is therefore refused.

The refusal is swallowed. `plan --write` exits 0, the run is OPEN, and the charter is still `Queued` - which is precisely BG0515's headline symptom: the queue re-offers a charter whose run is already running. The defect is reproduced through its own fix path.

Two further gaps in the same unit. `except Exception` does not catch `SystemExit`, which is what `transition.main` raises on some paths. And transition's stdout leaks unindented into `plan --write`'s output.

Separately, the AC2 verifier cannot fail on what it claims: `assertIn('"Spent"', src)` is monotone in the number of writers, so it passes harder as writers are added. A second `Spent` writer added to `cmd_next` left the full suite green (788 passed). AC2's `adding a second reddens it` is false.

## Steps to Reproduce

1. Queue a charter carrying an unresolved Open Question.
2. `sprint.py plan --worklist <file> --charter SC0001 --write` through the shipped CLI.
3. rc 0, run open, charter still Queued. Nothing in the output says the charter was refused.
4. Add a second `Spent` writer to `cmd_next` and run the suite: green.

## Proposed Fix

Decide what a refused charter means and say it. The run is already open by then, so the honest outcome is to REPORT loudly and non-zero, or to resolve the gate before opening the run - not to exit 0 with the queue silently unadvanced. Catch `SystemExit` alongside `Exception`, and capture transition's stdout rather than letting it leak. Replace the AC2 existence check with an assertion that is not monotone in writer count - count the call sites, or assert the single writer by name.

## Acceptance Criteria

- [x] **AC1: an unresolved Open Question does not stop a charter being spent.**
  - **Given** a `Queued` charter carrying one unresolved Open Question
  - **When** `sprint plan --write --charter` opens a run from it through the shipped CLI
  - **Then** the charter reads `Spent`, because consuming a charter is not answering its
    questions - the run is opened to answer them - so the terminal Open-Questions gate is stood
    down for that one write and recorded on the artefact. The mutant is dropping `--force` from
    `spend_charter`'s transition argv: the gate refuses again and the charter stays `Queued`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CharterWithAnOpenQuestionIsStillSpentTests::test_an_open_question_does_not_stop_the_charter_being_spent
  - **Verified:** yes (2026-08-11)

- [x] **AC2: a refused write leaves `plan --write` non-zero and says so.**
  - **Given** a transition that refuses the `Spent` write while the run is already open
  - **When** the plan finishes
  - **Then** it exits 3 and names the charter that was not spent, rather than exiting 0 over a
    queue that has not advanced. The mutant is deleting the refusal branch from `cmd_plan` and
    returning 0 unconditionally, which is the shipped behaviour this bug records.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CharterWithAnOpenQuestionIsStillSpentTests::test_a_refused_write_leaves_the_plan_non_zero_and_says_so
  - **Verified:** yes (2026-08-11)

- [x] **AC3: a `SystemExit` from transition is caught, not propagated.**
  - **Given** a transition path that raises `SystemExit` rather than returning
  - **When** `spend_charter` runs it
  - **Then** the plan reports the failure and returns, because `SystemExit` is not an `Exception`
    and the original guard let a process exit out of the middle of a plan whose run was already
    open. The mutant is narrowing the except clause back to `Exception`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CharterWithAnOpenQuestionIsStillSpentTests::test_a_system_exit_from_transition_is_caught_not_propagated
  - **Verified:** yes (2026-08-11)

- [x] **AC4: transition's own output is captured and attributed, never leaked.**
  - **Given** a transition that prints its refusal
  - **When** the plan reports it
  - **Then** every line arrives under the plan's indent prefixed `transition:`, so it cannot be
    read as the plan's own words. The mutant is removing the stream capture and letting the
    lines print where they land.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CharterWithAnOpenQuestionIsStillSpentTests::test_transitions_own_output_is_captured_and_attributed
  - **Verified:** yes (2026-08-11)

- [x] **AC5: the charter terminal has exactly ONE writer.**
  - **Given** the shipped `sprint.py`
  - **When** the writers of the charter terminal are counted
  - **Then** there is exactly one. The previous form asserted `'"Spent"' in src`, which is
    MONOTONE in the number of writers and so passes harder as writers are added - a second
    writer in `cmd_next` left the whole suite green. The mutant is adding a second one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CharterIsSpentWhenItsRunOpensTests::test_the_charter_terminal_has_exactly_one_writer
  - **Verified:** yes (2026-08-11)

## Impact

The queue re-offers a charter whose run is already running, which is the defect BG0515 was filed to close. An operator following the shipped path gets a green plan and a queue that has not advanced, with nothing saying why.

## Verification evidence

Functional. Five mutants executed, `__pycache__` purged and each child run under `python3 -B`,
each anchor asserted to occur exactly once, source restored byte-identical afterwards:

| Mutant | Result |
| --- | --- |
| drop `--force` from `spend_charter`'s transition argv | killed |
| add a second quoted `Spent` writer | killed |
| `cmd_plan` returns 0 whatever the charter did | killed |
| narrow the except clause back to `Exception` | killed |
| stop capturing transition's streams | killed |

The non-zero exit is scoped to a write that was ATTEMPTED and did not take. The two pre-write
refusals - no charter resolves to the id, and a charter that is not `Queued` - keep exiting 0:
neither leaves a `Queued` charter for the next `next` to re-offer, which is the state this bug
is about, and both are already reported in terms.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | {{name the production change this test must fail on}} | |
| AC2 | {{name the production change this test must fail on}} | |
| AC3 | {{name the production change this test must fail on}} | |
| AC4 | {{name the production change this test must fail on}} | |
| AC5 | {{name the production change this test must fail on}} | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
| 2026-08-11 | sdlc-studio | Criteria groomed to name their mutants; fixed |
