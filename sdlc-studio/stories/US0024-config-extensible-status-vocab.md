# US0024: config-extensible status vocabulary

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint (CR0027)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As a** maintainer of a project with custom statuses
**I want** to declare extra statuses in `.config.yaml`
**So that** reconcile/validate/conformance recognise them instead of parsing the row
as `Unknown` - without polluting the shared skill vocabulary for every other project.

## Acceptance Criteria

### AC1: Blocked in the base story vocab

- **Given** no project config
- **When** `status_vocab("story")` is read
- **Then** it includes `Blocked` (a universal lifecycle state)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::StatusVocabTests::test_blocked_in_base_story_vocab
- **Verified:** yes (2026-06-20)

### AC2: Project extension adds without replacing

- **Given** `.config.yaml` with `status_vocab.story: [Gated]`
- **When** `status_vocab("story", root)` is read
- **Then** the result contains both `Gated` and the base statuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::StatusVocabTests::test_project_extension_adds_without_replacing
- **Verified:** yes (2026-06-20)

### AC3: Degrades on missing / malformed / type-confused config

- **Given** no config, malformed YAML, or a type-confused override (string/list where a list/dict is expected)
- **When** `status_vocab` / `project_override` runs
- **Then** it returns the base vocabulary and never raises (parser-critical path)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::StatusVocabTests::test_type_confused_override_degrades_to_base
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/lib/sdlc_md.py`: `project_override(root, dotted, default)` (self-contained,
degrading) + `status_vocab(type_, root)` + `Blocked` in base story vocab. 13 call
sites across reconcile/validate/conformance/status/audit/integrity/autosprint/resume/rfc
migrated to `status_vocab(type_, root)`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0027) | Decomposed from CR0027; critic APPROVE |
