# US1289: The release cut reports every fragment folded without a unit id, and the script catalogue describes the id carry

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0728
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, .claude/skills/sdlc-studio/reference-scripts-domain.md
> **Epic:** EP0365
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The release cut reports every fragment folded without a unit id, and the script catalogue describes the id carry
**So that** CR0728 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The cut names every fragment folded without a unit id

- **Given** pending fragments of which one, `release-notes.md`, is not named for a unit
- **When** `release_cut.py changelog-cut --version 9.9.9` runs
- **Then** it cuts the section, exits 0 and prints the name of each fragment folded without a unit id, and with every fragment named for a unit it prints no such line. Fails on: a cut that discards what compose reported, so the gap is invisible at the one moment the fragment still exists
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::ChangelogCutTests::test_the_cut_names_each_fragment_folded_without_a_unit_id

### AC2: The script catalogue describes the id carry

- **Given** `reference-scripts-domain.md`
- **When** its `changelog.py` and `release_cut.py` entries are read
- **Then** they say compose writes each fragment's unit id into its entries unless the entry already names it, where in the entry the id goes, that the dry run reports the same ids, and that the cut names any fragment folded without one. Fails on: a catalogue that still describes compose as folding the fragment body alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::ChangelogCutTests::test_the_catalogue_describes_the_unit_id_carry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
