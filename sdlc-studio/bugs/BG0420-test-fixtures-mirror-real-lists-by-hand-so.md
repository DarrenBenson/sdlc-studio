# BG0420: Test fixtures mirror real lists by hand, so adding one chain step or one gate lane turns dozens of unrelated tests red for a reason none of them is about

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_rolling.py, .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py, tools/tests/hookutil.py
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

- [ ] A fixture that needs the close chain or the hook's tool set DERIVES it from the production definition rather than copying it.
- [ ] A deliberate INVENTORY - a list that is itself the assertion - stays hand-maintained and states in the file why it is not derived, so nobody deletes the assertion by deriving it.
- [ ] Adding a step to the close chain, or a lane to the hook, reddens only tests whose subject is that step or lane.
- [ ] A guard fails when a test file hand-lists a set the production tree already owns, for at least the close chain and the hook's tool invocations.
- [ ] A test proves the derivation is live by adding a step to a fixture chain and asserting the fixture picks it up without edit.

## Impact

The staleness half is the serious one. Three copies of the close chain each omitted a step, which means that step was unstubbed and unasserted in every test that thought it was covering the chain - a coverage gap that no failing test would ever reveal, because the copies were only ever read, never checked.

The blast-radius half is a tax on every future change to either list, and it is the kind of tax that gets paid by not making the change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
