# BG1736: The commit-msg attribution note advises a schema 3 id by its dashless key

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py, changelog.d/BG1736.md
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T04:11:09Z

## Summary

`engagement_floor.unnamed_unit_attribution` builds its note from the normalised key, so a commit staging a file that a schema 3 unit (BG-01JQK3F8) owns is told to add `Refs: BG01JQK3F8`, a spelling no artefact carries. BG1574 fixed the same defect in changelog.py's refusal; this is the second site. Found by BG1574's round-three qa review, pre-existing since 70b10324a.

## Steps to Reproduce

1. In a fixture project whose BG-01JQK3F8 record declares src/v3.py in its Affects, stage src/v3.py.
2. Commit with the message fix(BG9002): b.
3. Read the attribution note: it ends add `Refs: BG01JQK3F8`, not `Refs: BG-01JQK3F8`.

## Proposed Fix

Print each id in the note as its own artefact spells it, the way BG1574's repair does in changelog.py, and leave the sequential-id spelling unchanged.

## Acceptance Criteria

- [ ] **AC1** Given a fixture project whose `BG-01JQK3F8` record declares `src/v3.py` in its Affects, when `src/v3.py` is staged with the message `fix(BG9002): b`, then `unnamed_unit_attribution`'s note advises `Refs: BG-01JQK3F8`, the id spelt as its artefact spells it. Fails on: the note ending `Refs: BG01JQK3F8`, a spelling no artefact carries.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::UnnamedUnitAttributionTests::test_the_note_spells_a_schema_3_id_dashed
- [ ] **AC2** Given the same fixture with a sequential id (BG0042) owning the staged file, when the note is built, then it still advises `Refs: BG0042`. Fails on: a fix that re-spells every id and changes the sequential form.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::UnnamedUnitAttributionTests::test_the_note_keeps_a_sequential_id_unchanged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: replaced the placeholder criteria with executable ones pinning the dashed schema 3 spelling and a sequential-id control; Affects gains changelog.d/BG1736.md; not re-checked, filed today |
