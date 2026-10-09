# BG1011: LL0056 ships with its label doubled and the template's placeholder sections left in, and nothing refuses a lesson with an unfilled placeholder

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/lessons/LL0056-every-check-must-earn-its-place-a-constraint-added-without-retiring-one-is-how-a-process-ratchets-shut.md, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons_placeholders.py, changelog.d/BG1011.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Evidence:** LL0056 lines 12 and 18-38 at 31f63fae.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T08:38:09Z

## Summary

`lessons/LL0056-every-check-must-earn-its-place...md`, added on 2026-09-24 (9169d403) and shipped with the skill, opens its body with `**Lesson.** **Lesson.**` and keeps the template's unfilled sections below the written ones: `**Why / what it cost.** {{the failure or friction that taught it}}`, `{{the concrete check or habit...}}`, `{{the class of situations...}}`, `**Guard.** {{the test or gate...}}` and a `{{What happened...}}` narrative (lines 18-38). It reads as two lessons, one empty. No lane refuses a lesson file carrying `{{` placeholders. Found by the G1/G2 panel review (D0355).

## Steps to Reproduce

`grep -n '{{' .claude/skills/sdlc-studio/lessons/LL0056-*.md` -> five placeholder lines; the body's first line repeats `**Lesson.**`.

## Proposed Fix

Remove the duplicated label and the leftover template sections from LL0056; refuse, in `lessons.py add --global` and the lessons registry's lint, a lesson file carrying an unfilled `{{...}}` placeholder.

## Acceptance Criteria

- [ ] **AC1** LL0056 carries no `{{` placeholder and no repeated label
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_placeholders.py::LessonPlaceholderTests::test_ll0056_is_clean
- [ ] **AC2** A lesson file with an unfilled `{{...}}` placeholder is refused by the registry's lint, naming the file and line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_placeholders.py::LessonPlaceholderTests::test_a_placeholder_lesson_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
