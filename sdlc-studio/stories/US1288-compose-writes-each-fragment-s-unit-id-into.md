# US1288: Compose writes each fragment's unit id into its entry exactly once, and the dry run reports the same ids

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0728
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py
> **Epic:** EP0365
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Compose writes each fragment's unit id into its entry exactly once, and the dry run reports the same ids
**So that** CR0728 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: An entry that does not name its unit gains the id in one fixed place

- **Given** a fragment `changelog.d/US0001.md` holding two top-level entries, neither naming US0001
- **When** `changelog.py compose --apply` runs
- **Then** each of the two entries in `[Unreleased]` carries `US0001` once, at the same position in the entry, and the entry's own text is otherwise unchanged. Fails on: compose as it stands, which folds the body and deletes the file so the id is lost, or an id written on the first entry only
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::ComposeUnitIdTests::test_an_entry_gains_its_fragments_unit_id_in_one_fixed_place

### AC2: An entry that already names its unit is not given the id twice

- **Given** two fragments, `BG0002.md` whose prose names BG0002 and `US0001.md` whose prose names no id
- **When** `changelog.py compose --apply` runs
- **Then** each resulting entry names its own unit id exactly once, and the BG0002 entry is folded byte for byte as written. Fails on: an id prefixed to an entry that already carries it, or a match so loose that a mention of a different id counts as naming the unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::ComposeUnitIdTests::test_each_entry_names_its_unit_id_exactly_once

### AC3: The dry run reports the ids it would write and changes nothing

- **Given** the same two fragments and a CHANGELOG with an `[Unreleased]` section
- **When** `changelog.py compose` runs without `--apply`, then with it
- **Then** the dry run reports, per fragment, the unit id it would write or that the entry already names it, leaves CHANGELOG.md and both fragments byte-identical, and the ids it reported are the ids the apply then writes. Fails on: a dry run that reports only a count, or one whose ids differ from what apply writes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::ComposeUnitIdTests::test_the_dry_run_reports_the_ids_apply_writes_and_changes_nothing

### AC4: A fragment not named for a unit is folded without an id and reported

- **Given** a fragment `changelog.d/release-notes.md`, whose file name is not a unit id, beside one that is
- **When** `changelog.py compose --apply` runs
- **Then** the first is folded as written with no id added, compose's result and its printed output name that fragment as folded without a unit id, and the second still gains its id. Fails on: a file stem such as `release-notes` written into the entry as though it were an id, or the gap passing unreported
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::ComposeUnitIdTests::test_a_fragment_not_named_for_a_unit_is_folded_without_an_id_and_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
