# BG1025: sprint sign moves every batch unit to its terminal status, overriding a unit an operator ruling deliberately left open (Watching), and the seal then blocks transition from restoring it

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_respects_carried_units.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/BG1025.md
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-12T07:03:24Z

## Summary

In a consuming project's run (2026-10-12) `sprint.py sign` reported 'BG0445 -> Fixed ... 1 moved to their terminal status' (sprint.py ~6201). BG0445 had been ruled by the operator not-stop-ship and left 'Open (WATCHING ...)' on purpose: its own closure rule requires an upstream fix plus 14 clean days, recorded in the bug and the retro's known-issues table. The sign overwrote that status with Fixed. `transition.py set --id BG0445 --status Open` was then refused ('belongs to RUN-..., which is SEALED'), so the only route back was hand-editing the file's status line and letting `reconcile apply` sync the index - the very hand edit the skill otherwise forbids.

## Steps to Reproduce

Plan a run whose batch includes a unit an operator rules not-stop-ship and leaves Open; close with the unit listed under 'Known issues carried'; sign: the unit is moved to Fixed.

## Proposed Fix

Do not move a unit that the close records as a carried known issue (or whose status carries an operator ruling) to a terminal status at sign; or ask first and name each unit it will move. Allow an operator-attributed status correction on a sealed run's unit through transition (recorded, not silent).

## Acceptance Criteria

- [ ] **AC1** Given a closed run whose retro carries a batch bug as a known issue left Open, when `sprint sign` runs, then that bug keeps its status, sign names it as carried, not moved, and the signed page still checks VALID
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_respects_carried_units.py::SignRespectsCarriedUnitsTests::test_a_carried_unit_keeps_its_status
- [ ] **AC2** Given the same run, when `sprint sign` runs, then every batch unit the retro does not carry is still moved to its terminal status
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_respects_carried_units.py::SignRespectsCarriedUnitsTests::test_uncarried_units_are_still_moved
- [ ] **AC3** Given a unit of a sealed run, when `transition.py set` changes its status with `--principal` and `--reason`, then the principal is judged as `sprint sign` judges its signer (refused when it is the unit's author or a reviewer recorded on it), an accepted change is recorded on the unit with both, and without them the existing refusal stands
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_respects_carried_units.py::SignRespectsCarriedUnitsTests::test_a_sealed_unit_is_corrected_only_with_attribution

## Impact

Signing a run silently contradicts recorded operator rulings and the bug's own closure rule.

## Triage

- Confirmed at 19415be3 by the code path: sign's walk (`sprint.py:6167-6190`) moves every batch story unit that is neither terminal nor ruled out (`_batch_abandoned_units`) to its type's terminal, and reads nothing from the close's carried known issues. The carried rows are already readable: `_carried_rulings` (`sprint.py:5364`) reads them from the run's retro through `retro.carried_issues`. Pre-existing.
- Severity Medium stands: sign silently overwrites a recorded operator ruling, and the seal then forces the hand edit the skill otherwise forbids. Points raised to 3 for the two parts (sign, and an attributed correction through transition). Private project name generalised; changelog fragment and the help page added to Affects.
- AC3 changes what a seal permits, so the reviewer should judge that an attributed correction is recorded and never silent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Filed |
| 2026-10-12 | Claude Opus 5.5 (triage) | Triaged: confirmed on current code; project name generalised; criteria split into three on a new test module (BG0980); changelog fragment named for the unit |
| 2026-10-12 | Claude Opus 5.5 (planning) | Goal review: AC3 defines the principal by sign's own rule; AC1 re-checks the signed page VALID (LC-016) |
