# BG0735: the checklist's authority field is carried on 22 rows and read by no renderer

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Severity:** Medium
> **Points:** 2

## Summary

BG0463 claim 15, still true at HEAD. All 22 CHECKLIST rows carry an `authority` field and the only read anywhere in the tree is an assertion in test_sprint_report.py. A field whose only reader is its own test is indistinguishable from one nobody needs, and it costs every future editor a decision about what to put in it. Same shape as BG0733, where an unread field laundered a failure into a pass - here the consequence is only waste, which is why this is Low and that was High.

## Steps to Reproduce

1. `grep -c '"authority"' scripts/sprint_report.py` -> 22 rows. 2. Grep for any read outside tests -> none. 3. Delete the field from one row: only its own test fails.

## Proposed Fix

Either render it - the checklist row's provenance is worth showing beside its verdict, which is presumably why it was added - or delete it from all 22 rows and drop the test assertion. Do not leave the third state where it is carried and unread.

## Acceptance Criteria

### AC1: the authority field is read by something other than its own test, or it is gone

- **Given** the 22 CHECKLIST rows, each carrying an `authority` value
- **When** the close renders its checklist
- **Then** either the value appears where a reader meets the row, or the field is removed from all 22 rows and its test assertion with it
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, delete `authority` from one row. Only that field's own test reddens, which is the whole finding - nothing that renders the checklist notices
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistAuthorityTests::test_the_authority_value_reaches_the_rendered_row
- **Verified:** no

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | US0853 AC2 | Minted as its own artefact so no BG0463 survivor is carried as a bullet inside another. The filer routes Low findings into a themed consolidation CR by design, so this was created through `artifact.py new` instead - not a severity inflated to dodge the mechanism, and not the mechanism switched off. BG0731 carries the conflict. |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - 22-row checklist authority field: US0875 moved the checklist off the page; batch 3 deletes it |
