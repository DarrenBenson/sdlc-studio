# BG1123: A review brief now carries two different diffs of the unit: the scope line's `git diff <base> -- <Affects>` (the working tree) and US1094's UNIT DIFF section (base to HEAD)

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_base_ref.py, changelog.d/BG1123.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** US1094 builder report, 2026-10-22: outside-the-unit item 1.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T14:37:21Z

## Summary

US1094's builder (2026-10-22). The brief's scope line still prints `git diff <base> -- <Affects>`, which diffs the working tree against the base, while the new UNIT DIFF section holds `git diff <base> HEAD -- <file>`, committed work only. With uncommitted edits present the two differ, and a reviewer is handed two answers to 'what changed'. `test_lean_brief_base_ref.py` pins the scope line's old form.

## Steps to Reproduce

Brief a unit with an uncommitted edit to an Affects file: the scope command shows it, the UNIT DIFF section does not.

## Proposed Fix

Make the scope line print the same base-to-HEAD command the section holds, and update `test_lean_brief_base_ref.py`'s pin.

## Acceptance Criteria

- [ ] **AC1** Given a unit briefed with an uncommitted edit in its Affects, then the scope line's diff command and the UNIT DIFF section name the same range
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_base_ref.py::BriefBaseRefTests::test_the_scope_line_and_the_diff_section_name_one_range

## Impact

A reviewer can judge a different diff from the one the brief embeds.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
