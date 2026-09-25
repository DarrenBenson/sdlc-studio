# BG0778: The retro reads only four-digit ids in dispositions and carried rows, so a v3 project's ULID ids are dropped

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retro_v3_ids.py, changelog.d/BG0778.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T18:43:47Z

## Summary

`retro.ARTEFACT_ID_RE` (retro.py:172) matches only (CR|BG|US|RFC|EP|LL)-?NNNN. A fresh v6 project is schema v3 and mints ULID ids, so retro dispositions and carried-issue rows naming them are not read. Same class as the Batch grammar US0951 fixed with `BATCH_ID_RE.` Found by US0951's builder.

## Steps to Reproduce

1. init a fresh project (schema v3). 2. write a retro whose disposition or carried-issue row names a ULID id. 3. the retro's readers skip it.

## Proposed Fix

Reuse the id grammar US0951 introduces (`BATCH_ID_RE`, or the shared `sdlc_md` id pattern) for `ARTEFACT_ID_RE`, with a v3 fixture test.

## Acceptance Criteria

- [ ] **AC1** Given a schema-v3 project whose retro names ULID ids (bare and normalised) in its dispositions and `Known issues carried` rows, when the retro's readers parse it, then every such id is read, as a four-digit id is. Fails on: `ARTEFACT_ID_RE` matching only `(CR|BG|US|RFC|EP|LL)-?NNNN`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retro_v3_ids.py::RetroV3IdTests::test_dispositions_and_carried_rows_read_v3_ids
- [ ] **AC2** Given prose in a retro that mentions a word shaped like an id prefix but no id (e.g. `USB`, `EPIC`), when the readers parse it, then no id is read from it. Fails on: a widened grammar that matches any prefix followed by letters
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retro_v3_ids.py::RetroV3IdTests::test_prose_is_not_read_as_an_id

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | sdlc | Groomed for Sprint 5: criteria and Verify selectors written |
