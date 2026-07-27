# US0478: The mint path writes the canonical epic row, and the shipped template declares the same columns

> **Status:** Ready
> **Delivers:** CR0436
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/templates/indexes/epic.md, CHANGELOG.md
> **Epic:** EP0172
> **Points:** 3

## User Story

**As an** agent minting an epic and then a story under it
**I want** the minted row to equal what the derivation would write, and the shipped template to declare the columns the tooling maintains
**So that** a freshly minted epic is not born drifted and the template does not teach a consuming project a column set nothing writes

## Acceptance Criteria

### AC1: the minted row equals the derived row

- **Given** the canonical epic column definition and per-cell derivation shipped by the derive-and-sync story in lib/sdlc_md.py - this story is sequenced AFTER it and imports that API rather than restating it
- **When** an epic is minted through `artifact.py new --type epic` and its appended row is compared cell by cell with the derived row for the same epic
- **Then** they are identical (Stories `0`, Deps left at the not-stated placeholder) and `reconcile detect` reports no epic-index drift for it, so a new epic is not born drifted the way row_from_header's unrecognised-column `--` branch mints one today
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::EpicRowAgreementTests::test_the_minted_row_equals_the_derived_row

### AC2: wiring a story updates the epic's Stories cell on both mint paths

- **Given** an epic whose row records 0 stories
- **When** a story naming that epic is minted singly, and again through `new_batch`
- **Then** the Stories cell reflects the new count on each path and `reconcile detect` is immediately silent, so the index is not stale until someone remembers to reconcile - and the batch path is asserted separately, because it is the path that skipped the wiring before
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::EpicRowAgreementTests::test_wiring_a_story_updates_the_stories_cell_on_both_mint_paths

### AC3: the shipped template declares the canonical columns

- **Given** the shipped templates/indexes/epic.md, which declares `| ID | Title | Status | Owner | Stories | Target |` while this repo's index declares `| ID | Title | Status | Stories | Deps | Created | Updated |` - and row_from_header has no branch for owner or target, so both fill with `--` on every mint
- **When** the template's data-table header is parsed from the file and compared with the canonical column definition imported from source
- **Then** the two lists are equal, with neither restated as a literal in the test - so whichever column set is chosen, the template and the tooling cannot disagree again
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::EpicRowAgreementTests::test_the_template_header_equals_the_canonical_column_definition

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
