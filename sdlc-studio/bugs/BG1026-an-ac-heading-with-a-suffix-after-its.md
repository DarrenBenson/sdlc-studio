# BG1026: An AC heading with a suffix after its id (`### AC3 (DEFERRED)`) is not parsed as a criterion, so its Verify line is folded into the criterion above

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_ac_heading_with_suffix.py, changelog.d/BG1026.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-12T10:31:47Z

## Summary

`AC_HEADING_RE` (`lib/sdlc_md.py:58`) is `^###\s+(AC\d+[a-z]?)(?::\s*(.*))?$`: after the id it accepts only a colon and a title, or nothing. A heading such as `### AC3 (DEFERRED)` or `### AC3 - title` does not match, so the parser does not open a new criterion there, and the heading's own `Verify: manual` line attaches to AC2. Split out of BG1024, where a consuming project's release-gate triage found it beside the grep-flag defect.

## Steps to Reproduce

In a story, write `### AC2: works` with a Verify line, then `### AC3 (DEFERRED)` with `- **Verify:** manual`. Run `verify_ac` against the story: AC3 is not listed, and AC2 carries the manual Verify line.

## Proposed Fix

Accept any text after the id that is not a further id character, so `### AC3 (DEFERRED)`, `### AC3 - title` and `### AC3: title` all open AC3; keep `### AC10` from reading as AC1.

## Acceptance Criteria

- [ ] **AC1** Given a story whose third criterion heading is `### AC3 (DEFERRED)` with its own `Verify: manual` line, when `verify_ac` lists the story's criteria, then AC3 is listed with the manual Verify line and AC2 keeps only its own
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ac_heading_with_suffix.py::AcHeadingWithSuffixTests::test_a_suffixed_heading_opens_its_own_criterion
- [ ] **AC2** Given a heading `### AC10: title`, when the criteria are parsed, then it opens AC10, never AC1 with a suffix
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ac_heading_with_suffix.py::AcHeadingWithSuffixTests::test_ac10_is_not_ac1_with_a_suffix

## Impact

A deferred or suffixed criterion's manual marker attaches to the wrong criterion, so the executable-AC gate reads AC2 as manual and never sees AC3.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | Claude Opus 5.5 (triage) | Filed |
