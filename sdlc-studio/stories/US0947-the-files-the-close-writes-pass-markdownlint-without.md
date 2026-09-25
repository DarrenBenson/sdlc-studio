# US0947: The files the close writes pass markdownlint without a hand fix

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_writers_lint.py, changelog.d/US0947.md
> **Epic:** EP0265
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer whose project lints its markdown at commit
**I want** the lesson-graduation CR and the retro's accuracy block to be written lint-clean
**So that** the close's own paperwork commit is not refused until I trim the files by hand

## Acceptance Criteria

- **AC1:** Given a lesson class that graduates at the close, when its CR is filed, then the line before the first `-` item of its `Hits:` list is blank. Fails on: HEAD's `_graduation_cr` summary (`Hits:\n- ...`), which markdownlint refuses as MD032 (reproduced in a fresh fixture; CR0595-CR0598 were fixed by hand before commit)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_writers_lint.py::CloseWritersLintTests::test_a_graduation_cr_has_a_blank_line_before_its_list
- **AC2:** Given a retro whose last section is an empty `## Estimate vs actual` heading, when `retro.write_accuracy` writes the block, then the file ends with exactly one newline. Fails on: HEAD, which appends `block + "\n\n"` and leaves a trailing blank line (MD012, reproduced)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_writers_lint.py::CloseWritersLintTests::test_accuracy_write_at_the_foot_ends_with_one_newline
- **AC3:** Given a retro where the accuracy section sits between two other sections, when the block is written, then exactly one blank line separates it from the next heading. Fails on: a fix that strips all trailing newlines and joins the block to the next heading
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_writers_lint.py::CloseWritersLintTests::test_accuracy_write_mid_file_keeps_one_blank_line

## Notes

Two of CR0592's consolidated Low items. BG0682 (MD037 on a revision note) was dropped from this unit: the repo's markdownlint with its .markdownlint.json does not refuse a row carrying `_brief_key and _awaits_signoff` at 013a46d0, so its premise does not reproduce (re-ruled in TRIAGE). The tests assert the structure markdownlint checks, not a node binary, so they run without npm.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (N9) |
