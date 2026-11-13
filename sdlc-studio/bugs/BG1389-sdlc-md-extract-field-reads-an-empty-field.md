# BG1389: sdlc_md.extract_field reads an empty field on into the next line and returns '>', and two is_swallowed_run branches are unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_empty_field_read.py, changelog.d/BG1389.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane integrity builder; BG0990 review
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:08:38Z

## Summary

`extract_field` (`sdlc_md.py`:1186) returns '>' for an empty field because it runs into the next line; the new `metadata_fields` leaves such a field out instead. In `is_swallowed_run` (line 1224) the re.escape and match-versus-search branches are untested, and a field name recurring after an empty first occurrence reads wrongly.

## Steps to Reproduce

`extract_field(`'> **Affects:**\n> **Next:** x', 'Affects').

## Proposed Fix

Share one rule between the two readers and pin both branches.

## Acceptance Criteria

- [ ] **AC1** Given a header whose field is empty and recurs later, when `extract_field` and `metadata_fields` read it, then both give the same empty answer. Fails on: '>' returned.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_empty_field_read.py::EmptyFieldReadTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
