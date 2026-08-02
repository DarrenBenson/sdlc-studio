# BG0420: Test fixtures mirror real lists by hand, so adding one chain step or one gate lane turns dozens of unrelated tests red for a reason none of them is about

> **Status:** Fixed
> **Verification depth:** functional (a seventh copy written into the suite on purpose and KILLED, then removed; the declared-inventory control asserted beside it)
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/tests/test_test_census.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_trd_freshness.py
> **Evidence:** RUN-01KYPZ1G hit this six times. Adding one close-chain step reddened 17 tests in test_sprint.py, then 27 more across test_autosprint.py and test_sprint_rolling.py - each file held its own copy of the chain, and all three copies had ALREADY drifted (every one omitted `review-anchor`). Adding one gate lane then reddened 41 tests across four tools/tests files, each carrying a hand-copied list of the tools the hook invokes. Seven copies of two real lists, none of them derived, none of them in the file that owns the list.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

A test fixture that mirrors a production list by hand is a second copy of that list, and it goes stale the way every second copy does - silently, and in the direction that makes the tests pass while covering less.

The cost is paid twice. First in staleness: all three copies of the close chain omitted `review-anchor`, so for however long that step has existed, no test stubbed it and no test asserted it ran. Second in blast radius: adding one step to the chain turned 44 tests red across three files, and adding one lane to the hook turned 41 red across four more. None of those 85 failures was about the test it appeared in. A developer reading them has to work out that the whole set has one cause before they can fix any of it, which is exactly the cost this project's grouping rules exist to remove elsewhere.

The distinction that matters, and it is not subtle: **a MIRROR should be derived; an INVENTORY should not.** `_CLOSE_STEP_NAMES` in a test is a mirror - it exists so the fixture can stub whatever the chain runs, and it should read the chain. `EXPECTED_LANES` is an inventory - it IS the record of what the gate does, and deriving it would reduce the assertion to 'the hook agrees with itself'. Getting that backwards in either direction is a defect: a derived inventory asserts nothing, and a hand-copied mirror rots.

This run converted the six mirrors and left the two inventories hand-maintained, with the reason stated at each. The bug is filed for the general rule, because nothing stops the seventh copy being written next week.

## Steps to Reproduce

1. Add a step to `sprint._CLOSE_CHAIN`.
2. Run the full skill suite: `test_sprint.py`, `test_sprint_rolling.py` and `test_autosprint.py` all fail, in tests whose subject is unrelated to the new step.
3. Add a lane to `.githooks/pre-commit` invoking a new `tools/*.py`.
4. Run the tools suite: four files fail because their fixtures write a hand-listed set of tool stubs that does not include the new one.

## Proposed Fix

1. **A mirror is derived at import.** A fixture needing to know what the chain runs, or what the hook invokes, reads it from the thing that owns it. This run added `tools/tests/hookutil.py` as the single reader for the hook side; the sprint side reads `_CLOSE_CHAIN` directly.
2. **An inventory stays hand-maintained and SAYS SO.** `EXPECTED_LANES` carries a comment explaining that it is the record rather than a copy, so the next person does not 'fix' it by deriving it and quietly delete the assertion.
3. **A guard against the seventh copy.** A check that fails when a test file hand-lists a set the production tree already owns - at minimum for the two known shapes, the close chain and the hook's tool invocations.
4. The three chain mirrors and four hook mirrors converted in this run are the regression fixtures: adding a step or a lane must not redden a test whose subject is neither.

## Acceptance Criteria

### AC1: a new hand-copied script list is refused

- **Given** a test file hand-listing shipped scripts the production tree already owns
- **When** the guard runs
- **Then** it is reported, because a hand-written mirror goes stale silently and in the direction that makes the tests pass while covering less
- **Verify:** pytest tools/tests/test_test_census.py::HandCopiedMirrorTests::test_no_new_hand_copied_script_list
- **Verified:** yes (2026-08-02)

### AC2: the deliberate inventory stays recognised

- **Given** `EXPECTED_LANES`, a list that IS the assertion rather than a mirror of one
- **When** the guard runs
- **Then** it is exempt by DECLARATION and the file states why - derived from the hook it checks, it would agree with any hook including one that lost a lane, and without the note the next reader derives it and deletes the assertion
- **Verify:** pytest tools/tests/test_test_census.py::HandCopiedMirrorTests::test_the_declared_inventory_is_still_recognised
- **Verified:** yes (2026-08-02)

> **Verified adversarially.** A seventh copy was written into the suite on purpose and the
> guard KILLED it, then removed. The one pre-existing hit it found - a probe set in
> `test_trd_freshness.py` - was declared rather than derived: its assertion is that MORE THAN
> ONE writer appears, so deriving it would make the test agree with any rule that happens to
> name whatever exists, which is not what it checks.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
