# BG0298: resolve_prose_fields takes prose_keys as the checked set, so the hazard check defaults to the UNSAFE direction: a prose field a caller forgets to list in prose_keys is silently treated as metadata and never shell-hazard-checked

> **Status:** Fixed
> **Verification depth:** functional
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Severity:** Low
> **Points:** 2

## Summary

US0418 added `resolve_prose_fields(...`, `prose_keys)` where `prose_keys` names the subset the shell-hazard check covers. That is the unsafe default direction: a caller that adopts the feature and OMITS a genuine prose field from `prose_keys` silently drops that field's hazard check - a backtick or dollar-paren that a shell mangled goes unreported. The safe direction is to name the METADATA (the keys that are NOT prose and need no check); anything not named then stays checked, so an omission fails safe.

## Steps to Reproduce

1. A writer accepts prose fields (title, summary) and metadata (tags). 2. It calls `resolve_prose_fields(ff`, flags, allowed=(title,summary,tags), `prose_keys`=(title,)) - forgetting summary. 3. A shell-mangled summary flag is now NOT hazard-checked, because summary was omitted from `prose_keys` and defaults to metadata.

## Proposed Fix

Invert the parameter to `metadata_keys`: the hazard check covers allowed MINUS `metadata_keys`, so a key nobody classified stays checked (fail-safe). prose is checked by default; only an explicitly-declared metadata key is skipped. Update US0418's caller/tests to the `metadata_keys` form.

## Acceptance Criteria

### AC1: a forgotten prose field stays checked (fail-safe direction)

- **Given** a caller that declares some fields as `metadata_keys` but omits a genuine prose field from every classification
- **When** `resolve_prose_fields` runs
- **Then** the omitted prose field is STILL hazard-checked - a key nobody classified defaults to checked, never to skipped
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FieldsFileMetadataTests::test_a_forgotten_prose_field_stays_checked
- **Verified:** yes (2026-07-26)

### AC2: declared metadata is still skipped, and the whole feature still works

- **Given** a fields-file supplying prose and declared-metadata fields
- **When** it is resolved with `metadata_keys`
- **Then** both are accepted and only the declared metadata is skipped from the hazard check
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FieldsFileMetadataTests::test_metadata_accepted_and_only_prose_hazard_checked
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
