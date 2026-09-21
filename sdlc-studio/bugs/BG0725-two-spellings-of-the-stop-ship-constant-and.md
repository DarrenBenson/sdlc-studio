# BG0725: two spellings of the stop-ship constant, and a hand-maintained verb list whose stale entries nothing can report

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 claims 16 and 17, both still true and both the same shape: a value maintained in two places where only one is authoritative. `retro.STOP_SHIP` is compared against bare `"stop-ship"` literals at `sprint_report.py`:2033 and :3651, so a change to the constant silently stops matching. `NON_CEREMONY_VERBS` still lists `checklist` under `sprint`, which is no longer a sprint verb - and the guard that reads it only SUBTRACTS the list, so it can never report an entry naming a verb that does not exist. Verified by executing each script's `build_parser()` subcommands against the list: `sprint checklist` is the only stale entry, and nothing in the tree would ever say so.

## Steps to Reproduce

1. `grep -n 'stop-ship' scripts/sprint_report.py` -> two bare literals beside uses of `retro.STOP_SHIP.` 2. Compare `NON_CEREMONY_VERBS[`'sprint'] against `sprint.py build_parser()` subcommands -> `checklist` is absent from the parser. 3. Rename the constant's value: the literals keep matching the old string.

## Proposed Fix

Replace both literals with `retro.STOP_SHIP`. For the verb list, add the opposite direction to its guard: redden when an entry names a verb no `build_parser()` exposes. It would fire today, which is the test.

## Acceptance Criteria

### AC1: the stop-ship constant has one spelling

- **Given** `retro.STOP_SHIP` and the two bare `stop-ship` literals in sprint_report.py
- **When** the constant's value is changed in a test
- **Then** every comparison follows it, so no site keeps matching the old string
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, restore the bare `"stop-ship"` literals at the two comparison sites - a rename then leaves them silently matching nothing while the code reads as though it still works
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::StopShipConstantTests::test_every_comparison_follows_the_constant

### AC2: a verb list entry naming a verb no parser exposes is reported

- **Given** `NON_CEREMONY_VERBS`, which lists `checklist` under `sprint` where `sprint`'s parser no longer exposes it
- **When** the guard runs
- **Then** the stale entry is named - today it would fire on exactly that one
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, keep the guard subtracting the list only, so it can report a verb missing FROM the list but never an entry naming a verb that does not exist
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::StopShipConstantTests::test_a_verb_list_entry_with_no_parser_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
