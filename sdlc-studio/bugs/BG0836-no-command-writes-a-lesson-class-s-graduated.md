# BG0836: No command writes a lesson class's graduated state, so every graduation CR carries a criterion only a hand edit can meet

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_graduation.py, changelog.d/BG0836.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Evidence:** followups line 46; HEAD 7e53a438 lessons.py:1638 STATES and ~1827-1841 (the criterion text); no writer found by grep
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:42Z

## Summary

`lessons.STATES` names `graduated`, and the CR a close files for a recurring class (`_graduation_cr`, e.g. CR0596-CR0600) has the criterion 'Once the path is fixed, LC-00x reads `graduated` in sdlc-studio/lessons.jsonl'. No code path writes that state; the only route is editing the committed store by hand, which the loop exists to avoid.

## Steps to Reproduce

`grep -n graduated scripts/lessons.py`: a state name and criterion text, no transition.

## Proposed Fix

Add `lessons.py graduate --class LC-00x --by <CR>` (and `retire`), refusing unless the named CR is terminal, and document it in help/lessons.md.

## Acceptance Criteria

- [ ] **AC1** Given a class whose graduation CR is Complete, when `lessons.py graduate` runs, then the class reads graduated; with the CR open it is refused. Fails on: HEAD, which has no such command
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_graduation.py::LessonGraduationTests::test_graduate_needs_a_terminal_cr

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
