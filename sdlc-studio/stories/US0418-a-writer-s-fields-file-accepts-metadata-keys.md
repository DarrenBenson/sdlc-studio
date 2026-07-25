# US0418: a writer's --fields-file accepts metadata keys as well as prose, so one invocation sets both

> **Status:** Review
> **Delivers:** CR0417
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Epic:** EP0156
> **Points:** 3

## User Story

**As a** author driving a writer through its `--fields-file`
**I want** the document to accept the metadata fields the writer's CLI accepts, not just its prose
**So that** one committed, re-runnable document is the whole invocation rather than a half-call needing remembered flags beside it

## Acceptance Criteria

### AC1: a fields-file accepts metadata keys, and only prose is hazard-checked

- **Given** a writer that accepts both prose fields and metadata fields, calling `resolve_prose_fields` with its full field set as `allowed` and the prose subset as `prose_keys`
- **When** a fields-file supplies both a prose field and a metadata field
- **Then** all are returned, and the shell-hazard check runs over the prose keys only - the metadata keys are accepted without being hazard-checked, since a shell never touched the document
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FieldsFileMetadataTests::test_metadata_accepted_and_only_prose_hazard_checked
- **Verified:** yes (2026-07-25)

### AC2: an unknown key is still refused by name

- **Given** a fields-file carrying a key outside the writer's full field set
- **When** it is loaded
- **Then** it is refused, naming the key - widening the accepted set to include metadata must not become accepting anything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FieldsFileMetadataTests::test_an_unknown_key_is_still_refused
- **Verified:** yes (2026-07-25)

### AC3: an existing prose-only caller is unchanged

- **Given** a writer that calls `resolve_prose_fields` without `prose_keys` (the whole allowed set is prose)
- **When** a fields-file and flags are resolved
- **Then** every allowed key is hazard-checked exactly as before - the back-compatible default preserves the narrower contract
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FieldsFileMetadataTests::test_prose_only_caller_unchanged
- **Verified:** yes (2026-07-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-25 | sdlc-studio | Groomed: authored the User Story and three executable ACs; narrowed Affects to the loader it changes |
