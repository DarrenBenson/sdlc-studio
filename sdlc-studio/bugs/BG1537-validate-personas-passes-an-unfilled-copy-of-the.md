# BG1537: validate personas passes an unfilled copy of the persona template, and status then reports personas present

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, personas lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/templates/personas/persona-template.md persona-template.md header comment (line 3) against `check_personas` in .claude/skills/sdlc-studio/scripts/validate.py lines 1278-1335
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:26:45Z

## Summary

`persona-template.md` states its own bar on line 3: a persona is well-formed when every section is filled. `check_personas` in `validate.py` (lines 1278 to 1335) tests only that each expected heading exists and never looks under a heading, although the same file already has `_check_placeholders`, which it applies to stories. A card that is the template copied byte for byte, with every placeholder intact including the title, passes with no warning, and the cast-role parser reads the placeholder cell listing all six roles as a declared Primary. `status.py` then counts the project as having personas. The seat validator refuses the equivalent unfilled amigo template, so the two card validators disagree on what unfilled means. This is a success message for something not achieved (LL0008) from a check that cannot fail on the defect it is named for (LL0010).

## Steps to Reproduce

1. Create a scratch root containing only `sdlc-studio/personas/someone.md`, an unmodified copy of `.claude/skills/sdlc-studio/templates/personas/persona-template.md`.
2. Run `validate.py` with `--root` set to the scratch root and the `personas` subcommand.
3. Observe the output 'personas look well-formed.' and exit status 0.
4. Run `status.py` with `--root` set to the scratch root: the Requirements line reads personas=yes.
5. As a control, copy `amigo-template.md` to `personas/seats/engineering.md` in the scratch root and run the `seats` subcommand: it reports the error `seat-no-role`.
6. Expected: the personas check warns on each unfilled placeholder and on a cast-role cell that is still the template's list. Actual: a clean pass.

## Proposed Fix

In `check_personas` in `validate.py`, apply the existing placeholder check to each persona card and warn, naming the file and section, when a required section holds only template placeholders or is empty. Make `_persona_cast_role` return no role when the cell is the unfilled template list of roles, so the existing missing-cast-role warning fires. Keep the check advisory. Add tests to `test_validate.py`: a verbatim template copy produces placeholder and cast-role warnings and no well-formed message, and a filled card beside it passes clean.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `persona-template.md` states its own bar on line 3: a persona is well-formed when every section is filled.
- [ ] **AC2** The proposed fix lands, pinned by a test: In `check_personas` in `validate.py`, apply the existing placeholder check to each persona card and warn, naming the file and section, when a required section...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
