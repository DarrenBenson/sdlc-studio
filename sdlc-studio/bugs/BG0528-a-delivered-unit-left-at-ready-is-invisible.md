# BG0528: a delivered unit left at Ready is invisible to every close gate: twenty blockers were reported and not one of them said the units had never been transitioned

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Evidence:** RUN-01KZ9315, 2026-08-06, at commits 9dc330f5 through f1762b8c. `sprint.py preflight` output showing twenty blockers with no status line; `critic.py signoff --panel --from-run` writing 4 of 12 units and skipping 8 with the status reason; the same command writing all 8 after `transition.py set --status Review`.
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Eight of RUN-01KZ9315's twelve units had their code committed with a green full suite and were never transitioned out of `Ready`. The close then reported twenty unmet prerequisites across four categories - no independent review coverage, no critic verdict, no reviewer-of-record sign-off, and a blocked Done gate on each story - and not one of them named the actual cause. Every message described a downstream consequence of a status that had not moved.

The cost was a run held open for more than twenty-four hours. The diagnosis arrived only when `critic.py signoff` refused with the one message in the chain that reads the status directly: `its status is 'Ready', which is neither terminal nor awaiting sign-off - the work has not been delivered`. That message exists, it is exact, and nothing upstream of it asks the question.

The pre-flight is the command whose whole purpose is to report every blocker in one pass (US0638). It reports what is missing from the ledgers and never that the units are not yet in a state where a ledger entry is meaningful. A unit at `Ready` with committed code is a state the tooling can detect for nothing: its `Affects` files carry commits inside the run window and its status has not moved.

## Steps to Reproduce

Observed on RUN-01KZ9315, 2026-08-06. 1. Twelve units delivered across six commits, full suite green at each. 2. Four bugs reached `Fixed`; eight stories stayed at `Ready`. 3. `sprint.py preflight` exits 1 with `20 unmet prerequisite(s) - ALL of them`, listing review coverage, sign-off and Done-gate failures for the eight stories. No line mentions their status. 4. `critic.py signoff --panel` is the first command to say it: `sign-off SKIPPED for US0638: its status is 'Ready', which is neither terminal nor awaiting sign-off`. 5. `transition.py set --id <id> --status Review` on each, and the same sign-off command then writes all eight.

## Proposed Fix

Add a status pre-condition to `close_preflight`, ahead of the review-coverage check, that names any batch unit still in a pre-delivery status whose declared `Affects` carry commits inside the run window - and prints the transition that moves it. It belongs there rather than at the sign-off step because the pre-flight is the command that promises to report every blocker in one pass, and a blocker it cannot see makes the other nineteen unreadable.

Derive the pre-delivery set from the status vocabulary rather than listing `Ready` and `In Progress` by name, or the check exempts whatever status a project adds next.

The deeper fix is that nothing makes a commit and a status agree. A unit whose files were committed inside the run window and whose status never moved is a detectable disagreement, and it is the same shape as the claim-drift lane: the code and the record say different things.

## Acceptance Criteria

- [x] **AC1: the pre-flight names a delivered unit whose status never moved.**
  - **Given** a batch unit at a pre-delivery status whose declared `Affects` carry commits inside
    the run window
  - **When** `sprint.py preflight` runs through the shipped verb
  - **Then** it prints a `[status]` blocker naming the unit, its status and the transition that
    moves it. The mutant is deleting the check's call from `close_preflight`: the library
    function then still exists and answers correctly, which is exactly the shape of a feature no
    invocation reaches.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveredUnitLeftAtReadyTests::test_a_ready_unit_whose_code_landed_is_named_by_the_preflight
  - **Verified:** yes (2026-08-11)

- [x] **AC2: the cause is reported before its consequences.**
  - **Given** the same run, whose untransitioned units also fail review coverage, sign-off and
    the Done gate
  - **When** the blockers are composed
  - **Then** the status blocker comes first, because twenty messages describing consequences of a
    status that had not moved is what made the real fault unreadable. The mutant is appending the
    status rows after the coverage rows instead.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveredUnitLeftAtReadyTests::test_the_cause_is_reported_before_its_consequences
  - **Verified:** yes (2026-08-11)

- [x] **AC3: a unit awaiting sign-off is not accused.**
  - **Given** a batch unit at `Review` with commits behind it
  - **When** the check runs
  - **Then** nothing is reported, because `Review` means delivered and awaiting the reviewer of
    record - the state a sign-off exists to resolve. The mutant is dropping the
    awaiting-sign-off half and testing terminality alone, which fires on every correct run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveredUnitLeftAtReadyTests::test_a_delivered_unit_at_its_review_status_is_not_accused
  - **Verified:** yes (2026-08-11)

- [x] **AC4: a pre-delivery unit with no commits behind it is not accused.**
  - **Given** a batch unit at `Ready` whose declared `Affects` are untouched in the run window
    and which no commit names
  - **When** the check runs
  - **Then** nothing is reported, because a unit that is simply not started yet is at `Ready` for
    the honest reason. The mutant is accusing on status alone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveredUnitLeftAtReadyTests::test_a_pre_delivery_unit_with_no_commits_behind_it_is_not_accused
  - **Verified:** yes (2026-08-11)

- [x] **AC5: a commit naming the unit counts even when `Affects` is untouched.**
  - **Given** a commit in the run window whose message names the unit and which touches no
    declared path
  - **When** the check runs
  - **Then** the unit is reported, and the detail says the evidence was the commit message.
    `Affects` is a declaration and it goes stale; the subject naming the unit is the stronger
    signal. The mutant is deleting the message pass and reading `Affects` alone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveredUnitLeftAtReadyTests::test_a_commit_naming_the_unit_counts_even_when_affects_is_untouched
  - **Verified:** yes (2026-08-11)

- [x] **AC6: the pre-delivery set is derived from the vocabulary, not a name list.**
  - **Given** a batch unit at a pre-delivery status that is neither `Ready` nor `In Progress`
  - **When** the check runs
  - **Then** it is still reported, because a name list exempts whatever status a project adds
    next. The mutant is replacing the vocabulary test with that pair of literals.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveredUnitLeftAtReadyTests::test_the_pre_delivery_set_is_derived_from_the_vocabulary_not_a_name_list
  - **Verified:** yes (2026-08-11)

## Impact

Every run. The failure is silent, it costs the whole close, and the operator's visible symptom is a long list of blockers none of which is the problem.

## Verification evidence

Functional. Six mutants executed, `__pycache__` purged and each child run under `python3 -B`,
each anchor asserted to occur exactly once, source restored byte-identical afterwards:

| Mutant | Result |
| --- | --- |
| delete the check's call from `close_preflight` | killed |
| report the cause after its consequences | killed |
| drop the awaiting-sign-off half of the pre-delivery test | killed |
| accuse on status alone, with no git evidence | killed |
| delete the commit-message pass and read `Affects` alone | killed |
| hard-code the pre-delivery names instead of asking the vocabulary | killed |

Two discriminators, because one is not enough. A commit whose message names the unit is
decisive; a commit merely touching the declared `Affects` is also made true by a SIBLING unit
sharing the file, so it is reported in those words rather than as proof. The window is the run's
own recorded base ref rather than a wall-clock date, so a neighbouring run's commits on a busy
day are not swept in, and a run with no recorded base ref makes no claim at all.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | {{name the production change this test must fail on}} | |
| AC2 | {{name the production change this test must fail on}} | |
| AC3 | {{name the production change this test must fail on}} | |
| AC4 | {{name the production change this test must fail on}} | |
| AC5 | {{name the production change this test must fail on}} | |
| AC6 | {{name the production change this test must fail on}} | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
| 2026-08-11 | sdlc-studio | Criteria groomed to name their mutants; fixed |
