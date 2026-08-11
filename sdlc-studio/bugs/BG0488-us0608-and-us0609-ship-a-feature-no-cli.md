# BG0488: US0608 and US0609 ship a feature no CLI invocation can reach, and their tests survive its deletion

> **Status:** Fixed
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, sdlc-studio/stories/US0609-file-and-close-accepts-a-stale-periodic-review.md
> **Severity:** High
> **Points:** 5
> **Verification depth:** functional

## Summary

EP0200 decouples a stale periodic review from the close. An independent pass showed the delivered pair is inert and unpinned.

US0608: reverting the whole feature - `"blocking": False` back to `True` at gate.py:1397 - SURVIVES all 390 tests of `test_gate.py.` That is the mutant AC1's own docstring names. All four ACs call the private `_batch_is_independently_covered` or grep source text; none asserts the lane's blocking flag and none runs a close, though AC1 says 'When the close runs / Then it proceeds'.

US0609: `_is_cadence_debt` has one call site, and the marker it looks for is produced in exactly one place - gate.py:1398 - which sets `"blocking": False`. `close_preflight` only raises a blocker when `status=="fail" and c.get("blocking")`. Executed on the real repo with the batch forced covered: 25 blockers returned, ZERO carrying the marker. US0608, same epic, converts the blocker to non-blocking before US0609 can ever see it. Deleting `and not _is_cadence_debt(b)` survives all 701 tests of `test_sprint.py.`

The implementations are individually correct - forcing coverage does make `review-current` report status=fail, blocking=False. The wiring between them is what nobody exercised.

## Steps to Reproduce

1. In a worktree, set `"blocking": True` at gate.py:1397. Run `test_gate.py` -> 390 passed.
2. Delete `and not _is_cadence_debt(b)` from sprint.py:6232. Run `test_sprint.py` -> 701 passed.
3. Force the batch covered and call `close_preflight` on the real repo; count blockers carrying the CADENCE DEBT marker -> 0 of 25.

## Proposed Fix

Decide first whether the pair is coherent: if US0608 makes the lane non-blocking, US0609's filing path may be dead by construction rather than by defect, in which case one of the two should be withdrawn rather than repaired. Then pin whichever survives on the CLI - a close that runs, and the close-owed ledger read - not on a private helper or a source grep.

## The decision the fix required

The pair is NOT coherent as shipped, and one half is withdrawn rather than repaired.

US0608 is real and is kept: the lane's blocking flag is the feature, and it is now driven and
read end to end. US0609's classifier - any blocker whose detail contains the string
`CADENCE DEBT` is filable - is WITHDRAWN. It was a second reader of one fact, and it could never
fire: the only lane emitting the string emits it on the branch that also sets the flag, so the
string test was reachable only through a row the flag had already classified. Its filing path is
now the flag itself, which is the declaration that exists.

The wiring defect underneath both was in `close_preflight`: it dropped every non-blocking failing
lane, so "reported, not blocking" meant invisible. The lane's own flag now travels into the
blocker row, `ready` is decided by what HOLDS the close rather than by what is reported, the page
labels a reported row as such, and the bounded exit's classification is a named function
exercised against the rows the pre-flight actually built from the real lane.

## Acceptance Criteria

- [x] **AC1: a covered batch makes the review-current lane report rather than block.**
  - **Given** a stale unified-review anchor and a run whose every unit is independently covered
  - **When** `gate._review_current` judges it
  - **Then** it returns `blocking` False with the cadence detail. The mutant is the one this bug
    names: `"blocking": False` back to `True`, which survived all 390 tests of `test_gate.py`
    because every criterion stopped at the private helper.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReviewCadenceLaneVerdictTests::test_a_covered_batch_makes_the_lane_report_rather_than_block
  - **Verified:** yes (2026-08-11)

- [x] **AC2: the same lane blocks when the batch is not covered.**
  - **Given** the identical fixture with coverage absent
  - **When** the lane judges it
  - **Then** it blocks and says nothing about cadence, so the feature cannot become a way to
    close over a stale review with no coverage at all. The mutant is reporting non-blocking
    regardless of coverage.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReviewCadenceLaneVerdictTests::test_an_uncovered_batch_makes_the_same_lane_block
  - **Verified:** yes (2026-08-11)

- [x] **AC3: the lane's declaration reaches the printed page and the exit code.**
  - **Given** the real lane's output composed into a real pre-flight
  - **When** `sprint.py preflight` runs
  - **Then** it exits 0, prints the cadence detail, and marks the row reported rather than
    blocking. The mutant is dropping non-blocking failures from the pre-flight's gate loop,
    which is what made the whole feature unreachable.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CadenceDebtReachesTheCloseTests::test_the_cadence_lane_is_printed_and_does_not_hold_the_close
  - **Verified:** yes (2026-08-11)

- [x] **AC4: the same lane blocking holds the same close.**
  - **Given** the identical fixture with the batch uncovered
  - **When** the pre-flight runs
  - **Then** it exits 1 naming the stale anchor, so the repair made the gate legible rather than
    switching it off. The mutant is treating every gate row as advisory.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CadenceDebtReachesTheCloseTests::test_the_same_lane_blocking_holds_the_close
  - **Verified:** yes (2026-08-11)

- [x] **AC5: the bounded exit classes the real cadence row as filable.**
  - **Given** the blocker row the pre-flight built from the real lane
  - **When** the hard-blocker classification runs
  - **Then** the row is filable, joining the unit that PRODUCES the declaration to the exit that
    consumes it. The mutant is dropping the lane's flag when the pre-flight builds its row.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CadenceDebtReachesTheCloseTests::test_the_bounded_exit_classes_the_real_cadence_row_as_filable
  - **Verified:** yes (2026-08-11)

- [x] **AC6: a row that declares nothing is treated as holding the close.**
  - **Given** a blocker carrying no blocking declaration
  - **When** it is classified
  - **Then** it holds, because a producer that forgets must fail towards holding rather than
    towards a silent pass. The mutant is defaulting the flag to False, which would make every
    future blocker filable by omission.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CadenceDebtFileAndCloseTests::test_a_row_that_says_nothing_is_treated_as_holding_the_close
  - **Verified:** yes (2026-08-11)

Withdrawing the prose classifier changed what two of US0609's criteria are answered BY, and not
what they claim. Its test selectors are therefore kept - a Done unit whose verifiers point at
nothing is a worse record than one whose verifier changed mechanism - and its third criterion's
prose now names the declaration that is read. All three still pass.

## Impact

Two units of a three-unit epic are recorded delivered on evidence that cannot fail. The cadence-debt path they exist to provide cannot be produced by any command, so the bounded exit the epic promised is not available. This is the same defect class `verify_ac lane-check` was shipped for in the adjacent epic, and it flagged both.

## Verification evidence

Functional. Eight mutants executed, `__pycache__` purged and each child run under `python3 -B`,
each anchor asserted to occur exactly once, source restored byte-identical afterwards:

| Mutant | Result |
| --- | --- |
| `"blocking": False` back to `True` on the covered branch | killed |
| report non-blocking regardless of coverage | killed |
| drop non-blocking failures from the pre-flight's gate loop | killed |
| decide readiness from every reported row again | killed |
| drop the blocking test from the hard-blocker filter | killed |
| classify by a hardcoded lane-name list instead of the flag | killed |
| default the blocking flag to False in the hard filter | killed |
| stop labelling a reported row on the page | killed |

US0609's three criteria still select their own tests and still pass. Two of the three keep their
names deliberately: the claims are unchanged by the swap of declaration, and renaming them would
have left a Done unit's verifiers pointing at nothing. The third criterion's prose now says which
declaration is read, and its test drives two rows differing ONLY in that declaration - an answer
no list of lane names can produce, which is what the criterion has always been about.

The first was the bug's own headline mutant and it now reddens in two places: the lane's verdict
and the close that reads it. Measured before the withdrawal, the string classifier's deletion
still SURVIVED even with the wiring repaired - which is the evidence that it was redundant rather
than merely untested, and the reason it is withdrawn instead of pinned.

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
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-11 | sdlc-studio | Criteria written to name their mutants; one half withdrawn, the other wired and pinned |
