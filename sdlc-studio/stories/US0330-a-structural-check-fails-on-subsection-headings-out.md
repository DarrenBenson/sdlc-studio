# US0330: A structural check fails on subsection headings out of order, duplicated within one release, or empty - the shapes a bad hand-insert produces

> **Status:** Draft
> **Depends on:** BG0265, BG0256
> **Delivers:** CR0405
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py,.claude/skills/sdlc-studio/scripts/tests/test_changelog.py
> **Epic:** EP0112
> **Points:** 3

## User Story

**As a** reader of the release notes, and as the author about to commit them
**I want** CHANGELOG.md's own headings checked for the shapes a bad insert produces
**So that** a block that reparents an existing list under the wrong heading is caught by the
tooling rather than by someone happening to re-read the file

## Context

**The premise of CR0405 was corrected before refinement, and this story is scoped to what
survived it.** The helper the CR said did not exist is `scripts/changelog.py`: fragments land
under `changelog.d/`, `compose` folds them into `## [Unreleased]`, creates a missing section
heading, consumes the fragment and refuses loudly before writing anything it cannot place. Two
of the CR's four criteria were already met when it was filed. Nothing here rebuilds them.

What nothing covers is CHANGELOG.md's own structure. The RUN-01KY3MFX incident inserted a block
beginning `### Added` and ending `### Fixed`, which silently reparented the whole existing Added
list under Fixed; markdownlint saw only an unrelated blank line. Note the tension the check has
to settle: `compose` creates a missing heading at the HEAD of `[Unreleased]`, so a check with a
canonical order is a constraint on the writer as well as on the hand-editor. AC4 is where that
is decided rather than discovered.

US0331 is where this check is bound into the gate.

## Acceptance Criteria

### AC1: subsection headings out of canonical order fail

- **Given** a release section whose `###` subsections appear in an order other than the canonical
  one `changelog.SECTIONS` declares, for instance Fixed above Added
- **When** the structural check runs over the file
- **Then** it fails, naming the release, the heading that is out of place and the order expected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::StructureCheckTests::test_subsections_out_of_canonical_order_fail

### AC2: a subsection repeated inside one release fails, naming both occurrences

- **Given** a release carrying two `### Added` headings, which is the exact shape the incident
  produced and under which every entry between them reads as belonging to the second
- **When** the check runs
- **Then** it fails, naming the release, the repeated heading and both line numbers, so the
  author is told where the reparenting happened rather than that something is wrong
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::StructureCheckTests::test_a_repeated_subsection_in_one_release_fails_naming_both_lines

### AC3: an empty subsection fails, and a well-formed release passes

- **Given** two files: one with a `###` heading carrying no entry before the next heading or the
  end of its release, and one well-formed release with entries under ordered, unrepeated headings
- **When** the check runs over each
- **Then** the first fails naming the empty heading and the second passes, so the check
  discriminates rather than refusing any file it is pointed at
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::StructureCheckTests::test_an_empty_subsection_fails_and_a_well_formed_release_passes

### AC4: the composer cannot produce a file its own check rejects

- **Given** a CHANGELOG.md that passes the check and a fragment declaring a section absent from
  `[Unreleased]`, the case where `compose` creates the heading
- **When** `compose` runs and the check is re-run over its output
- **Then** the file still passes, so the ordering rule binds the deterministic writer as well as
  the hand-editor and the two cannot end up in a standoff
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::StructureCheckTests::test_compose_output_still_passes_the_structural_check

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed against CR0405's CORRECTED summary: 4 acceptance criteria, none of them over the fragment machinery that already exists; `Affects` extended with the test file |
