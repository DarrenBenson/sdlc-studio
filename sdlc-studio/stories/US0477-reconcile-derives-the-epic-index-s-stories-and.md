# US0477: reconcile derives the epic index's Stories and Deps cells from the census and syncs them

> **Status:** Review
> **Delivers:** CR0436
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, tools/tests/test_epic_index_derived.py, sdlc-studio/epics/_index.md, .claude/skills/sdlc-studio/reference-reconcile.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/help/reconcile.md, CHANGELOG.md
> **Epic:** EP0172
> **Points:** 3

## User Story

**As an** agent navigating from an epic to the work under it
**I want** the Stories cell censused from the story files and the Deps cell derived only where the epic actually declares dependencies
**So that** the only forward epic-to-story surface holds real data instead of `--` on 156 of 165 rows, without inventing data for the 157 epics that declare nothing

## Acceptance Criteria

### AC1: the Stories cell is censused, and zero is a pinned answer

- **Given** an epic with three story files naming it in their Epic field and an index row showing `--`, plus an epic with no story files at all
- **When** `reconcile detect` runs and then `reconcile apply`, then detect again
- **Then** the first reports `epic-index-derivable` found `--` expected 3 and apply writes 3; the second is written as `0`, a derived fact rather than a placeholder; the second pass is silent - pinning the zero case once, so the sibling story's mint-agreement check has a deterministic answer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EpicIndexDerivedTests::test_the_stories_cell_is_censused_and_zero_stories_writes_zero

### AC2: Deps has three states and absence is never rewritten as None

- **Given** one epic whose `## Dependencies` Blocked By table names two epic ids, one that declares the section with no entries, and one with no `## Dependencies` section at all (the shape 157 of the 167 epic files on disk have, and the one artifact.py's epic scaffold never emits)
- **When** the detector and apply run over all three
- **Then** the first cell becomes the two ids in file order, the second becomes the declared-none value already in use on EP0001's row, and the third is left untouched and NOT reported as drift, following the rule detect_linked_epics already states - a placeholder over an absent declaration is honest, and stamping 157 rows from absence of evidence would reproduce the defect CR0436 was filed for
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EpicIndexDerivedTests::test_deps_has_three_states_and_an_absent_section_is_not_drift

### AC3: only the target cell is rewritten, on a shifted column and an escaped pipe

- **Given** an index whose Stories column sits at a different offset and whose rows contain an escaped `\|` inside a title
- **When** apply writes the derived cells
- **Then** the column is located by header and the row split on unescaped pipes only, so every other cell survives byte-identical - the data-loss failure apply_linked_epics already documents as load-bearing on both halves
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EpicIndexDerivedTests::test_apply_rewrites_only_the_derived_cell_on_a_shifted_or_escaped_row

### AC4: the canonical epic columns are one importable answer

- **Given** the derivation and the index row writer
- **When** the epic column set and the per-cell derivation are read from the single definition this story adds to lib/sdlc_md.py
- **Then** both consult it rather than each carrying its own list, so the sibling mint story has an API to agree with instead of re-deriving the same rules a second time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EpicIndexDerivedTests::test_the_derivation_and_the_row_writer_read_one_column_definition

### AC5: the committed index holds derived data, over every row

- **Given** the repo as committed, after apply has run over sdlc-studio/epics/_index.md
- **When** the sweep runs over every row in the index, and again over a copy with one row's Stories cell mutated
- **Then** the committed tree reports nothing, every epic with stories on disk shows its censused count, every epic with none shows 0, no epic lacking a Dependencies section has an invented Deps cell, and the mutated copy fails - the sweep is over all rows, not a sample, and is shown able to go red
- **Verify:** pytest tools/tests/test_epic_index_derived.py::EpicIndexRepoTests::test_every_row_is_derived_and_a_mutated_row_fails

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
| 2026-07-30 | Claude Opus 5 | Wired as the `epic-index-derivable` drift kind, with `apply`. The nine-row question is settled by a RULE, not a decision: a placeholder or a count the census EXCEEDS is filled, a count the census FALLS SHORT of is advisory and left alone - so the eight downward rewrites never happen. 11/11 mutants killed |

## Evidence

The nine-row question this story was held on is answered by a rule, so no operator decision is
needed to introduce the kind.

`apply` is governed by whether the write LOSES anything, not by whether the cell looks empty:

| Row state | Verdict | Why |
| --- | --- | --- |
| Placeholder (`--`) | filled | 182 rows here; nothing is lost |
| Count the census EXCEEDS (EP0008, 6 -> 7) | filled | the tree holds every story the row claims and more, so the row was merely stale |
| Count the census FALLS SHORT of (8 rows) | advisory, left alone | the row counts stories the tree cannot show; those files exist nowhere, live or archived, so the number is their only trace |
| No `## Dependencies` section (157 epics) | never written | an absence is not a declaration that there are none |

Two things the direction test bought that a placeholder-only rule could not. It makes the eight
downward rewrites impossible rather than merely unchosen, so the kind can block from the day it
lands. And it keeps the derivation able to update its own output: a minted epic's row carries a
censused `0`, which is a real value - under a placeholder-only rule the first story wired to that
epic could never move the cell, which is exactly the failure the sibling story US0478 surfaced.

The uncorroborated rows are printed as `advisory (epic-index-uncorroborated)`, never as drift and
never silently, on the same terms as `already_delivered_advisory`: a blocking lane that can only be
cleared by destroying a record is a lane that gets switched off.

Two costs found by measuring rather than assuming. The census re-read every story file once per
epic row - 191 rows over ~600 files, 3.3s on a lane that runs on every commit - so it is memoised
on a `stat` signature, and a test proves the memo sees a story reparented in the same process (a
root-keyed memo would serve the previous answer). And `apply` read the index twice, so the column
offsets could belong to a different revision than the rows being written; it now reads once, which
removed both the window and an unreachable bounds guard that a mutant showed changed no test.
