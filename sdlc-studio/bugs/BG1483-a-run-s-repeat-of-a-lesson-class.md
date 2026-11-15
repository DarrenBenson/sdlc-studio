# BG1483: A run's repeat of a lesson class is counted only from a cited REJECT or retro Try item, so a repeat caught by the land or the push gate goes unrecorded

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, changelog.d/BG1483.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
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

- [ ] **AC1** The behaviour described is corrected: Run thirteen repeated LC-019 (BG1468: two boundary-only reds the lanes' selections skipped) and LC-021 (markdownlint refusals at the land), yet both rows show...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read LC-019 and LC-021 in sdlc-studio/lessons.jsonl: 0 hits, though BG1468 and run thirteen's land refusals repeated both.
- [ ] **AC3** The proposed fix lands, pinned by a test: Count a hit when a bug filed in the run cites the class (an `LC-xxx` token in its summary) and when the retro's Stop or Keep section cites it, not only Try...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
