# US0617: the close-owed ledger distinguishes a close-time repair from an unaccounted unit

> **Status:** Ready
> **Delivers:** CR0527
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Epic:** EP0204
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator reading the close-owed advisory
**I want** a unit that reached terminal AFTER the retro was written reported as a close-time repair
**So that** the advisory stops naming a run that has genuinely accounted for itself

## Notes

Delivers criterion 3 of CR0527. `close_owed` compares terminal units against what some retro's
`> **Batch:**` names, so anything reaching terminal after the retro is written is unaccounted -
and a repair made during the close is exactly such a unit. The advisory then fires on a run that
did account for itself, which is how it comes to cry wolf.

Two facts already on disk make the distinction derivable without a new record: the retro's own
`> **Date:**` (or the commit that added it) and the unit's terminal timestamp. Derive the split
rather than asking anybody to declare it - a flag somebody must remember to pass is a flag that
records the honest case and misses the careless one.

Note the ordering with US0616: once the close refuses over an uncommitted batch repair, the
close-time repair becomes rare. This story is what makes the residue readable rather than
alarming, and it is also what tells an operator that US0616's gate is holding.

## Acceptance Criteria

### AC1: a unit reaching terminal after the retro is reported as a close-time repair

- **Given** a retro accounting for a batch, and a unit that reached terminal after that retro was
  written
- **When** `close_owed.py detect` runs
- **Then** the unit is reported as a CLOSE-TIME REPAIR, named separately from the unaccounted
  units, and the wording distinguishes the two - "fixed after the account was written" and
  "nobody accounted for this" are different facts and must not read the same
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::CloseTimeRepairTests::test_a_unit_terminal_after_the_retro_is_reported_as_a_close_time_repair

### AC2: a genuinely unaccounted unit is still reported as one

- **Given** a unit no retro's `Batch` names and which reached terminal before any retro was
  written
- **When** the detect runs
- **Then** it is reported as unaccounted exactly as today, so the new state is a split of the
  reported set and never an escape hatch that empties it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::CloseTimeRepairTests::test_an_unaccounted_unit_is_still_reported_as_unaccounted

### AC3: the split is derived from timestamps already on disk

- **Given** the retro and the units, with no additional field written by anybody
- **When** the classification is made
- **Then** it is computed from the retro's recorded date and each unit's terminal timestamp, so
  no caller has to declare which kind a unit is - a declaration would record the honest case and
  miss the careless one, which is the population the advisory exists for
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::CloseTimeRepairTests::test_the_classification_is_derived_not_declared

### AC4: the exit code still reflects a genuine debt only

- **Given** a run whose only outstanding units are close-time repairs
- **When** detect runs
- **Then** it reports them and exits zero, because the ledger's job is to refuse an unaccounted
  run - a close-time repair is visible and countable, which is what CR0527 asks for, and gating
  on it would re-create the unconvergeable close from the other side
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::CloseTimeRepairTests::test_close_time_repairs_alone_do_not_hold_the_exit_code

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Groomed against CR0527 criterion 3; `Affects` corrected - it named `tools/tests/test_close_owed.py`, which does not exist, and the module is under `scripts/tests/` |
