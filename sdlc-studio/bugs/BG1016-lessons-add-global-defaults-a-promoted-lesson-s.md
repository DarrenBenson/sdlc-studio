# BG1016: lessons add --global defaults a promoted lesson's origin to the working directory's name, so a consuming project's directory name is written into a shipped lesson

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons_global_origin.py, changelog.d/BG1016.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Evidence:** lessons.py:501 `origin = args.origin or Path.cwd().name`.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T09:28:54Z

## Summary

`lessons.py add --global` sets `origin = args.origin or Path.cwd().name` (lessons.py:501). Promotion is run from a consuming project with `skill_source_repo` pointing at the skill checkout, so with no `--origin` the consuming project's directory name lands in the `origin:` field of a lesson file the skill ships, the leak the neutrality blocklist exists to stop, caught (if at all) only at the skill repository's next commit. Confirmed by the code path at fd2db47a; found by the G3 breakdown of CR0612 (D0355).

## Steps to Reproduce

From a project directory named after a private project, with `skill_source_repo` set, `lessons add --global --title t --body b` (no --origin) -> the new LL file's front matter reads `origin: <that directory name>`.

## Proposed Fix

Default `origin` to a neutral value (`a consuming project`) rather than the directory name, and run the neutrality check over the rendered lesson before writing it (CR0612's check at filing).

## Acceptance Criteria

- [ ] **AC1** `lessons add --global` without `--origin` writes a neutral origin, never the working directory's name
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_global_origin.py::GlobalOriginTests::test_the_default_origin_is_neutral

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
