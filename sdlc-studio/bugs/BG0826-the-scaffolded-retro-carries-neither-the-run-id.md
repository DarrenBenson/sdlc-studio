# BG0826: The scaffolded retro carries neither the run id nor a Known issues carried table, so the run's rulings cannot be found or written

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/reviews/retro.md, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retro_scaffold_run.py, changelog.d/BG0826.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retro.py
> **Evidence:** eval 09 v6-main grader friction; soak F31; HEAD 7e53a438 templates/reviews/retro.md (Date, Batch, Keep, Stop, Try only) and sprint.py _prefill_retro / retro_rulings (~5360-5385)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:26Z

## Summary

`_resolve_retro` scaffolds the retro from templates/reviews/retro.md and pre-fills Batch and Goal only. `retro_rulings` finds a run's retro by searching retro text for the run id, which the scaffold never writes, so a reader without `--retro` (stop, the pre-flight, the dry run) reports `ruling unreadable: no retro carries RUN-...` (soak F31). The template has no `## Known issues carried` section although help/sprint.md makes that table the only place a stop-ship ruling is recorded (`| id | ruling | ruled by | date |`); the eval 09 worker grepped help/sprint.md three times for its format.

## Steps to Reproduce

Open a run, `sprint.py close` with no --retro: the scaffolded retro has no RUN- id and no Known issues carried section; `sprint.py stop` then reports the rulings unreadable.

## Proposed Fix

Add `> **Run:** {{run_id}}` and an empty `## Known issues carried` table with its header to the retro template, and pre-fill the run id in `_prefill_retro`; `retro.py validate` accepts an empty table.

## Acceptance Criteria

- [ ] **AC1** Given a close that scaffolds the retro, then the retro names the run id and carries a Known issues carried table header, and `retro_rulings` finds it without --retro. Fails on: HEAD's template
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retro_scaffold_run.py::RetroScaffoldRunTests::test_the_scaffold_names_the_run_and_the_table
  - **Verified:** yes (2026-10-01)
- [ ] **AC2** Given the scaffolded retro with an empty carried table, then `retro.py validate` does not refuse the table. Fails on: a table the validator reads as a gap
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retro_scaffold_run.py::RetroScaffoldRunTests::test_an_empty_carried_table_validates
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
