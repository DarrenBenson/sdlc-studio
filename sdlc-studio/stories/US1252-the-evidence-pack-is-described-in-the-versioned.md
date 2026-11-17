# US1252: The evidence pack is described in the versioned evidence annex, so a consumer reads it without the tool

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0704
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_pack.py, .claude/skills/sdlc-studio/scripts/evidence_pack.py, changelog.d/US1252.md
> **Epic:** EP0345
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The evidence pack is described in the versioned evidence annex, so a consumer reads it without the tool
**So that** CR0704 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The annex catalogues everything the pack writes

- **Given** a pack `release_cut.py evidence-pack` writes in a throwaway repository, and the annex's evidence pack heading
- **When** the pack's headings and entry labels are read against the annex tables
- **Then** every heading and every entry label the pack carries is a row of the annex, with what it means and where its value is read from, and every row the annex lists as always written is on the pack. Fails on: a label the pack writes and the annex lacks, or an annex row no pack carries
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_pack.py::PackAnnexTests::test_a_written_pack_conforms_to_the_annex

### AC2: The pack states the annex version it was written under

- **Given** the same pack
- **When** its head is read
- **Then** it states `evidence_schema` in major.minor form, equal to the annex's version, so a reader with the file and the annex alone knows which tables to read it by. Fails on: a pack carrying no version, or one that differs from the annex it was written under
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_pack.py::PackAnnexTests::test_the_pack_states_the_annex_version

### AC3: The annex's version moves with the new record

- **Given** `reference-evidence-schema.md`
- **When** its version line and the evidence pack heading are read
- **Then** the annex's minor version is raised above 1.0, and the heading says a pack written before the stamp carries none and still reads. Fails on: a new record type added under an unchanged version, or the 6.4.0 pack declared invalid
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_pack.py::PackAnnexTests::test_the_annex_version_is_raised_for_the_pack

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
