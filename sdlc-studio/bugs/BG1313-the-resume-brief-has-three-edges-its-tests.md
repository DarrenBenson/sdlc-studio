# BG1313: The resume brief has three edges its tests do not pin: a batch listed out of plan order, a `-qa.none` landing marker read as in flight, and a Sprint Goal holding a newline that breaks `parse`

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/resume_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py
> **Evidence:** US1140-verdict-r1 findings 3-5 (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T13:59:41Z

## Summary

From US1140's QA review (qa-seat-US1140-r1, non-blocking findings 3-5, 2026-11-09). (3) Five code mutants survive `test_resume_brief.py`; the main gap is that no fixture lists its batch in a different order from its plan, so an ordering mutant goes unseen. (4) A landing that wrote a `<unit>-qa.none` marker (no brief written) still reads as in flight rather than as landed with no brief. (5) A Sprint Goal containing a newline breaks the brief's round trip through `resume_brief.parse`.

## Steps to Reproduce

1. Run the reviewer's surviving mutants against `test_resume_brief.py` (US1140-verdict-r1, finding 3).
2. Build a brief for a run where a unit's landing left `.local/briefs/<unit>-qa.none`: it shows the unit in flight.
3. Build and parse a brief for a run whose Sprint Goal holds a newline: the parse does not return the goal.

## Proposed Fix

Add a fixture whose batch order differs from its plan, read a `-qa.none` marker as landed with no brief, and fold or refuse a newline in the goal before rendering; pin each with a test that fails under its mutant.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From US1140's QA review (qa-seat-US1140-r1, non-blocking findings 3-5, 2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Add a fixture whose batch order differs from its plan, read a `-qa.none` marker as landed with no brief, and fold or refuse a newline in the goal before...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
