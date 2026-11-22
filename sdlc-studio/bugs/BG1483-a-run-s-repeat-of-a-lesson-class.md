# BG1483: A run's repeat of a lesson class is counted only from a cited REJECT or retro Try item, so a repeat caught by the land or the push gate goes unrecorded

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, changelog.d/BG1483.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-retro.md
> **Evidence:** sdlc-studio/reviews/verdicts/BG1474/8dc244746ca5-ede8b0eb.txt, finding 4; sdlc-studio/bugs/BG1468.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T21:31:20Z

## Summary

Run thirteen repeated LC-019 (BG1468: two boundary-only reds the lanes' selections skipped) and LC-021 (markdownlint refusals at the land), yet both rows show 0 hits: the close counts hits only from cited REJECTs and retro Try items (lessons.py near 2185, sprint.py `_close_retro_extract).` Before BG1474 that let a recurring class retire as quiet; after it, a build class leaves only by graduating at `GRADUATE_AT`=2, so uncounted repeats keep a recurring trap from ever graduating to a mechanical fix. BG1474's QA review (verdict 8dc244746ca5-ede8b0eb, finding 4) found it.

## Steps to Reproduce

Read LC-019 and LC-021 in sdlc-studio/lessons.jsonl: 0 hits, though BG1468 and run thirteen's land refusals repeated both.

## Proposed Fix

Count a hit when a bug filed in the run cites the class (an `LC-xxx` token in its summary) and when the retro's Stop or Keep section cites it, not only Try items and REJECT verdicts; backfill LC-019 and LC-021 from BG1468 and BG1474.

## Acceptance Criteria

- [ ] **AC1** Given an open run in which a bug is filed whose summary cites a recorded class by its code, when the run closes, then that class gains one hit for the run, naming the bug. Fails on: a repeat caught by the land or the push gate, and filed as a bug, leaving the class at the hits it had.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RunRepeatHitTests::test_a_bug_filed_in_the_run_citing_a_class_is_a_hit
- [ ] **AC2** Given a retro whose Stop or Keep section cites a class code, when the run closes, then the class gains one hit for the run. Fails on: only Try items and cited REJECTs being counted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RunRepeatHitTests::test_a_stop_or_keep_item_citing_a_class_is_a_hit
- [ ] **AC3** Given one repeat cited by a bug of the run and by the retro, and a bug citing the class that was filed before the run opened, when the run closes and then closes again, then the class holds one repeat for the run and the earlier bug adds none. Fails on: the same repeat counted twice, a re-run close adding a hit, or a bug from outside the run counted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RunRepeatHitTests::test_a_repeat_is_counted_once_and_only_from_this_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | Affects widened in-run on lane R's BLOCKED hand-in: reference-retro.md says a hit is keyed on the retro and the unit, never on the run, which the new run-keyed citation hits make untrue |
