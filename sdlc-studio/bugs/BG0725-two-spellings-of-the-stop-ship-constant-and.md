# BG0725: two spellings of the stop-ship constant, and a hand-maintained verb list whose stale entries nothing can report

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG0725.md
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

- [ ] **AC1** Given `NON_CEREMONY_VERBS`, when each listed script's `build_parser()` subcommands are read, then every listed verb is a real subcommand (`sprint checklist` and `critic repair` removed), and the test reddens on an entry naming no verb. Fails on: a guard that only subtracts the list, which can never report a stale entry
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::NonCeremonyVerbTests::test_every_listed_verb_is_a_real_subcommand
- [ ] **AC2** Given `retro.STOP_SHIP` patched to another value and a retro ruling written with it, when the report counts stop-ship rulings, then it still counts that ruling. Fails on: the bare `"stop-ship"` literals at sprint_report.py:1894 and :1896
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::NonCeremonyVerbTests::test_stop_ship_rulings_are_read_through_the_constant

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | QA seat: groomed for Sprint 6 from the triage repro |
