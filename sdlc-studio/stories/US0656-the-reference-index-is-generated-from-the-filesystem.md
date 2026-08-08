# US0656: The reference index is generated from the filesystem, so no reference can be missing from it

> **Status:** Done
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
- **Then** the new file appears, and every byte OUTSIDE the generation markers in
  `help/references.md` is unchanged - the hand-written prose around the table survives, or this
  story becomes a new source of the broken links `check_links.py` exists to catch. The index is
  built by walking the directory rather than by reading a list somebody maintains, because a
  hand-maintained index of 50-plus files is wrong the first time somebody adds one and forgets
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::GenerationThroughTheCliTests::test_references_is_generated_from_the_filesystem_through_the_cli
- **Verified:** yes (2026-08-08)

### AC2: a row whose file has gone is REMOVED, not left pointing at nothing

- **Given** an index carrying a row for a reference that no longer exists
- **When** the index is generated
- **Then** the row is gone AND every row whose file still exists survives - both asserted,
  because a test checking only that the stale row went also passes against a generator emitting
  an empty table. Generation has to run both ways or it is only an append, and a link to a
  deleted file is the failure `check_links.py` exists to catch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReferenceIndexTests::test_a_row_whose_file_has_gone_is_removed
- **Verified:** yes (2026-08-08)

### AC3: each row carries the description the reference states about itself

- **Given** each `reference-*.md`
- **When** its row is written
- **Then** the description comes from the file's own first descriptive line, not from a table
  somebody keeps beside it - so a reference that changes what it is about changes its own row.
  A file with NO first descriptive line - front matter only, or a heading followed straight by a
  table - gets its filename stem and says so, stated here rather than left for the implementer
  to pick and the test to be unable to fail on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReferenceIndexTests::test_each_row_carries_the_references_own_description
- **Verified:** yes (2026-08-08)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | build the index from the existing rows rather than from a directory walk | the index is generated from the FILESYSTEM |
| AC1 | rewrite the whole of `help/references.md` rather than only the marked region | the index is generated from the FILESYSTEM |
| AC2 | append missing rows without removing the ones whose file has gone | a row whose file has gone is REMOVED |
| AC2 | emit an empty table, so nothing stale survives and nothing live does either | a row whose file has gone is REMOVED |
| AC3 | write a fixed description per row rather than reading the file's own | each row carries the reference's own description |
| AC3 | emit an empty cell for a file with no first descriptive line | each row carries the reference's own description |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-08 | sdlc-studio | Plan review round 1 APPROVEd, and its three majors are folded in rather than carried: the generation markers were named in US0658 and not here, so a compliant implementation could have rewritten `help/references.md` wholesale; AC2 had no positive control, so an empty table passed it; and AC3 left the no-description fallback for the implementer to pick, which is a thing a test cannot fail on |
