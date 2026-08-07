# US0656: The reference index is generated from the filesystem, so no reference can be missing from it

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/docgen.py, .claude/skills/sdlc-studio/help/references.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_docgen.py
> **Epic:** EP0211
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The reference index is generated from the filesystem, so no reference can be missing from it
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the index is generated from the FILESYSTEM, so a reference cannot be missing from it

- **Given** `help/references.md`, and a `reference-*.md` file that no index row names
- **When** `docgen.py references` runs
- **Then** the new file appears. The index is built by walking the directory rather than by
  reading a list somebody maintains, because a hand-maintained index of 50-plus files is a list
  that is wrong the first time somebody adds one and forgets
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReferenceIndexTests::test_a_reference_the_index_never_named_appears

### AC2: a row whose file has gone is REMOVED, not left pointing at nothing

- **Given** an index carrying a row for a reference that no longer exists
- **When** the index is generated
- **Then** the row is gone. Generation has to run both ways or it is only an append, and a link
  to a deleted file is the failure `check_links.py` exists to catch - this must not be a new
  source of them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReferenceIndexTests::test_a_row_whose_file_has_gone_is_removed

### AC3: each row carries the description the reference states about itself

- **Given** each `reference-*.md`
- **When** its row is written
- **Then** the description comes from the file's own first descriptive line, not from a table
  somebody keeps beside it - so a reference that changes what it is about changes its own row
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReferenceIndexTests::test_each_row_carries_the_references_own_description

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | build the index from the existing rows rather than from a directory walk | the index is generated from the FILESYSTEM |
| AC2 | append missing rows without removing the ones whose file has gone | a row whose file has gone is REMOVED |
| AC3 | write a fixed description per row rather than reading the file's own | each row carries the reference's own description |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
