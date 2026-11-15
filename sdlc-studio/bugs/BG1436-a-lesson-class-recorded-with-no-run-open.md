# BG1436: A lesson class recorded with no run open retires at the next close in a clone with more than the quiet-run count of archived runs, from class-add and from retro extract alike

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons_class_add.py, .claude/skills/sdlc-studio/scripts/tests/test_lesson_no_run_retire.py, changelog.d/BG1436.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** Run twelve (RUN-01M7E52T) review of BG1268, qa-seat-BG1268-r1, verdict sdlc-studio/reviews/verdicts/BG1268/e18c8c20902a-568dad03.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T02:32:06Z

## Summary

`lessons.py class-add` stamps an empty `recorded_run` when no run is open (lessons.py:2630-2636), and `retro.py extract` falls back to the retro id (retro.py:4005-4016); `close_pass` retires a class whose recorded run names no archived run (lessons.py:2177), so with more than `QUIET_RUNS` archived runs the class retires at the very next close unless hit (probed: LC-001 retired at the first close after six archived runs). Neither help page says so. The same review found BG1268's blank-field refusal tested for `--rule` only, no test of the unreadable-run-state refusal, and a run-on sentence at reference-scripts.md:258-259.

## Steps to Reproduce

In a fixture with six archived runs and no open run, run `lessons.py class-add ...`, then close a run without hitting the class: the class is retired.

## Proposed Fix

Treat a class recorded with no run as recorded at the next run to open (or count its quiet runs from its recorded date), so a new class gets its full quiet window; test every blank field and the unreadable run state; split the run-on sentence.

## Acceptance Criteria

- [ ] **AC1** Given six archived runs and no open run, when a class is recorded by class-add or by retro extract and the next run closes without a hit, then the class is still active. Fails on: it retiring at that close.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lesson_no_run_retire.py::NoRunRetireTests
- [ ] **AC2** Given class-add with any one required field blank, or an unreadable run state, when it runs, then it refuses and the store is byte-identical. Fails on: any field accepted blank.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lesson_no_run_retire.py::ClassAddRefusalTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
