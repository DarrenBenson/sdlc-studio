# US0398: an atomic retitle of the H1, the filename slug and the index row, refusing before any write if any cannot be updated

> **Status:** Review
> **Delivers:** CR0406
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0150
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py,.claude/skills/sdlc-studio/scripts/reconcile.py,.claude/skills/sdlc-studio/scripts/tests/test_retitle.py

## User Story

**As a** agent correcting a shipped artefact whose title has turned out to be false
**I want** a single `artifact retitle` command that rewrites the H1, renames the file to the new title's slug and updates the index row's link text as one operation, refusing before any write if any of the three cannot be updated
**So that** the highest-visibility field on an artefact gains the deterministic writer every other field already has, and a correction never lands half-applied with the filename disagreeing with the H1

## Acceptance Criteria

### AC1: the three title surfaces change together in one call

- **Given** an artefact on disk whose H1, filename slug and `_index.md` row link text all carry the old title
- **When** `artifact retitle --id <id> --title "New Title"` is run once
- **Then** the H1 text, the file's slug (the file is renamed) and the index row's link text all read the new title, with no further command needed and no other field altered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle.py::AtomicRetitleTests::test_h1_filename_and_index_row_all_change_in_one_call

### AC2: a blocked surface aborts before any write, leaving all three untouched

- **Given** one of the three surfaces cannot be updated (the destination slug path already exists, or the index row is missing)
- **When** `artifact retitle` is run
- **Then** it exits non-zero and writes nothing: the original filename, the H1 and the index row are byte-identical to before, and no rename has occurred
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle.py::AtomicRetitleTests::test_a_blocked_target_leaves_all_three_untouched

### AC3: the refusal names the blocked surface and the corrective action

- **Given** a retitle that must refuse because a surface cannot be updated
- **When** it exits
- **Then** stderr states which of the three surfaces could not be updated and what to do about it, in the manner the grooming refusal already sets, rather than a bare non-zero exit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle.py::AtomicRetitleTests::test_refusal_names_the_blocked_surface_and_the_fix

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
