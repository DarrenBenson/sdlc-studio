# US0399: inbound references are rewritten or named via check_links, and the retitle is recorded on the artefact

> **Status:** Draft
> **Delivers:** CR0406
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0150
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py,.claude/skills/sdlc-studio/scripts/transition.py,tools/check_links.py,.claude/skills/sdlc-studio/scripts/tests/test_retitle_refs.py

## User Story

**As a** agent retitling a well-cited artefact
**I want** the retitle to find every inbound reference and rewrite it, or refuse and name the references it cannot rewrite, and to record the change on the artefact itself
**So that** a rename never leaves a dangling link, and a reader can see the title changed and what it was rather than finding a filename that disagrees with git history for no stated reason

## Acceptance Criteria

### AC1: inbound references are found and rewritten to the new slug

- **Given** other artefacts link to the target by its old filename slug, discoverable by the `check_links` inbound scan
- **When** the retitle renames the target
- **Then** every one of those inbound links is rewritten to the new slug, so the link resolution `check_links` runs reports no new break
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_refs.py::InboundRefTests::test_inbound_links_are_rewritten_to_the_new_slug

### AC2: an unrewritable reference blocks the rename and is named

- **Given** an inbound reference the retitle cannot safely rewrite
- **When** the retitle is run
- **Then** it refuses (no rename occurs) and names the referencing files, rather than renaming the artefact and leaving the references dangling
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_refs.py::InboundRefTests::test_an_unrewritable_reference_blocks_the_rename_and_is_named

### AC3: the retitle is recorded on the artefact with the previous title

- **Given** a retitle that succeeds
- **When** it completes
- **Then** a dated Revision History row is written recording the retitle and the previous title, via the same annotate/revision machinery, so the old title is legible on the artefact
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_refs.py::RetitleRecordTests::test_a_revision_row_records_the_old_title

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
