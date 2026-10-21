# BG1011: LL0056 ships with its label doubled and the template's placeholder sections left in, and nothing refuses a lesson with an unfilled placeholder

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/lessons/, .claude/skills/sdlc-studio/lessons/_template.md, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons_placeholders.py, changelog.d/BG1011.md
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

- [ ] **AC1** No shipped lesson carries a repeated `**Lesson.**` label or an unfilled `{{...}}` placeholder section
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_placeholders.py::LessonPlaceholderTests::test_no_shipped_lesson_carries_a_placeholder_or_a_doubled_label
- [ ] **AC2** `lessons.py add --global` writes a lesson with no unfilled `{{...}}` section: an optional section the author did not supply is omitted, not left as a placeholder
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_placeholders.py::LessonPlaceholderTests::test_add_global_leaves_no_placeholder

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
