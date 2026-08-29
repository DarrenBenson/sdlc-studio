# BG0619: a retro and a handoff can be CREATED by the shipped creator but not FOUND by id, so every id-addressed tool refuses the artefacts the close itself mints

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/next_id.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** `artifact.py retitle --id RETRO0109` and `--id HO0063` both refused during the RUN-01M0WCCG close on 2026-08-25. Confirmed 2026-08-26 by calling `find_by_id` over seven ids and printing `ARTIFACT_TYPES`. The creator's accepted `--type` list read from its own --help.
> **Verification depth:** functional [[derived: criteria 8; plan rows 11; executed 11; killed 11; survived 0; not-run 0; entry point 3 of 8 criteria through the shipped CLI, 4 in-process; 1 undetermined (the named node could not be isolated) | fp 2083762bb54f ]] (six criteria, every mutant applied to the real file with bytecode purged and the tree restored after each. Two reach the shipped command, which is where the bug's evidence lives - a CLI refusal - and they are what catch the four further `ARTIFACT_TYPES[type_]` lookups on the retitle path that no mutant names individually. AC4 is asserted apart from AC3 because the link half fails independently: a rename can leave the H1, the slug and the title cell all correct, exit 0, and only the index link dangling.)
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`artifact.py new --type` accepts `retro`, `handoff` and `review`, and `sprint close` mints both a retro and a handoff on every run. But `sdlc_md.ARTIFACT_TYPES` holds only bug, charter, cr, epic, issue, plan, rfc, story, test-spec and workflow, and `find_by_id` iterates exactly that map. Measured 2026-08-26: `find_by_id` resolves BG0615, US0676, EP0217, CR0558 and TS0001, and returns None for RETRO0109 and HO0063 - artefacts that exist, are indexed, and were written by the shipped creator minutes earlier. Twelve scripts read `find_by_id`, so the refusal is not local to one verb: `artifact.py retitle --id RETRO0109` answers `no artifact found for id 'RETRO0109'`, and the same is true for the handoff. The creator and the resolver disagree about which types exist.

## Steps to Reproduce

1. `sprint.py close --retro RETROxxxx`, which mints a retro and a handoff. 2. Try to correct either one's title with the deterministic writer: `artifact.py retitle --id RETRO0109 --title '<new>'`. 3. It answers `no artifact found`. Measured on RETRO0109 and HO0063, 2026-08-25, where both had to be renamed by hand across the file, the H1 and the index row, plus an inbound link repaired in the retro body.

## Proposed Fix

Settled by D0174: `find_by_id` resolves a META artefact by GLOBBING that type's own directory
and matching on `stem_record_id`, not by routing it through the pipeline walker.

Two designs were tried and both fail, which is why the decision exists rather than a preference.
Adding the three to `ARTIFACT_TYPES` puts them on the backlogs, through validate and into the
derived-index machinery across roughly twenty iterating consumers. Lifting a separate meta map
and widening `find_by_id` alone resolves NOTHING, measured: `_walk_artifact_files` guards on
membership of `ARTIFACT_TYPES`, unpacks it, and applies its own stem match, so handoff, review
and retro all still return None. And `conventions.is_artifact` drops every retro outright - 110
retro files on disk, 0 pass - because a retro carries no Status line and its H1 uses the dashed
id form.

The direct glob sidesteps the walker, the membership guard and `is_artifact` together, and it
is the honest shape: a retro is not a pipeline artefact, which is why it was kept out of
`ARTIFACT_TYPES` in the first place.

`find_by_id` has TWO branches and both must be widened. The `_CORPUS_CACHE` branch builds its
by-id index from a second iteration over `ARTIFACT_TYPES` with its own stem match, so patching
the plain branch alone leaves every corpus-cached consumer refusing while a naive test stays
green.

The RETITLE half then needs three more repairs, all measured, and it is scoped to HANDOFF and
REVIEW: the hard `ARTIFACT_TYPES[type_]` lookups in `artifact.py` and
`reconcile.retitle_index_row`; `reconcile.py`:3099, which matches the index row's ID cell with
`ID_SEARCH_RE` and its pipeline-prefix alternation; and `artifact.py`:1906, which falls back to
the whole stem so the id handed to the row writer can never match. RETRO is NOT excluded by any code, and saying so was wrong:
`retros/_index.md` does carry a row, `retitle_index_row` matches its ID cell and returns
found, so the dry-run guard passes and `retitle --id RETRO0109` exits 0 - renaming the
file, rewriting the H1 and rewriting the index LINK, while leaving the row's title text
stale because that index has no Title column. That silent-success path is BG0632, filed
and carried; this unit does not repair it and must not claim an exclusion it never
implemented.

The row's LINK TARGET belongs to this unit for the two types it keeps: `_swap` resolves it
through `extract_record_id`, which fails for HO and RV exactly as it does for RETRO, so a
rename updating the title cell and leaving the link at the old filename is half a retitle.

## Acceptance Criteria

- [x] **AC1** Given every `--type` the shipped creator accepts, when each is minted and looked up by id, then it RESOLVES and reports its own type string - including RETRO, which D0174's direct glob reaches and which `is_artifact` rejects. Paired control: a BG and a US still resolve to bug and story
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::CreatorResolverAgreementTests::test_every_creatable_type_resolves_to_its_own_type
  - **Verified:** yes (2026-08-27)
- [x] **AC2** Given the CORPUS-CACHED path rather than the plain one, when a meta id is looked up, then it resolves identically. `find_by_id` has two branches, each with its own iteration and stem match, and patching one leaves every cached consumer refusing while AC1 stays green
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::CreatorResolverAgreementTests::test_the_corpus_cached_branch_resolves_a_meta_id_too
  - **Verified:** yes (2026-08-27)
- [x] **AC3** Given a handoff and a review, when `artifact.py retitle` is invoked on either as a SUBPROCESS, then it exits 0 and rewrites the H1, the slug and the index row's title cell. RETRO is out of this row's scope and NOT excluded by any code: it exits 0 and leaves the row's title text stale, which is BG0632, filed and carried
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::CreatorResolverAgreementTests::test_the_retitle_command_renames_a_handoff_and_a_review
  - **Verified:** yes (2026-08-27)
- [x] **AC4** Given the same rename, when the index row's LINK TARGET is read, then it points at the new filename. This is asserted apart from AC3 because it fails independently: `_swap` resolves the target through `extract_record_id`, so a rename can leave the H1, slug and title cell all correct, exit 0, and only the link dangling
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::CreatorResolverAgreementTests::test_the_renamed_index_row_link_resolves
  - **Verified:** yes (2026-08-27)
- [x] **AC5** Given the lifted meta map, when the copies `next_id` AND `reconcile` hold are compared to `sdlc_md`'s, then all three are the SAME OBJECT. `reconcile.py`:765 keeps a third literal, commented as avoiding an import it already makes at module scope, and a fix lifting the map while leaving that literal preserves exactly the drift this row forbids. Identity, not equality: two maps with equal contents is the state this bug was filed in, and an equality assertion passes on it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py::CreatorResolverAgreementTests::test_the_meta_map_is_one_object_not_two_equal_ones
  - **Verified:** yes (2026-08-27)
- [x] **AC6** Given a fixture workspace containing a retro, a handoff and a review, when the backlog and scope census run, then they are UNCHANGED from the same workspace without them - the blast radius D0174 exists to avoid
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::CreatorResolverAgreementTests::test_the_meta_types_stay_off_the_backlog_and_the_scope_census
  - **Verified:** yes (2026-08-27)
- [x] **AC7** Given `file_finding.py file --parent <RETRO/HO/RV id>` run as a SUBPROCESS, when the parent resolves but carries no `> **Status:**` line to anchor a child link after, then the command REFUSES with NOTHING written - no artefact file and no index row - and names the missing field; and given a `--parent` that CAN carry the link, the child is still minted and indexed. Both halves: a guard refusing every parent satisfies the refusal half on its own. This is a REGRESSION this unit introduced, found at delivery review: widening `find_by_id` made resolving and being linkable diverge, so the pre-mint guard passed, the child was written AND indexed AND stamped with a one-way `> **Parent:**` line, and only then did `write_decomposed` raise - the command printed "file refused" over a finding that exists on disk
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ParentMustBeAbleToCarryTheLinkTests
  - **Verified:** yes (2026-08-28)
- [x] **AC8** Given a meta directory holding a pipeline id misfiled into it, a companion note beside the artefact it annotates, and a DIRECTORY whose name ends `.md`, when `find_by_id` resolves each id, then none of the three is returned as an artefact. A direct glob that keeps what the pipeline walker drops resolves ids the rest of the toolchain does not believe in, and `_meta_files` had dropped the walker's prefix guard, its companion-suffix filter and its `is_file` test while its own docstring claimed the glob could not mint a phantom artefact
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::CreatorResolverAgreementTests::test_the_meta_glob_keeps_only_what_the_walker_would_keep
  - **Verified:** yes (2026-08-28)

## Impact

The doctrine's rule is that mechanical work goes through a tool and hand-authoring is an error. `retitle` exists because a title lives in three places at once and a hand correction means editing all three plus every inbound link - which is exactly what had to be done twice at the last close, on the two artefacts the close had just written. A gap in the resolver quietly converts the tool-first rule into hand-editing for the artefact class that records what a run did.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py`, replace the meta directory glob with a call to `artifact_files`, so `_walk_artifact_files`' membership guard and `is_artifact` both apply and retro resolves to nothing | Given every `--type` the shipped creator accepts, when each is minted and looked up by id, then it RESOLVES and reports its own type string - including RETRO, which D0174's direct glob reaches and which `is_artifact` rejects. Paired control: a BG and a US still resolve to bug and story |
| AC2 | in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py`, widen only the plain branch of `find_by_id` and leave the `_CORPUS_CACHE` index loop reading `ARTIFACT_TYPES` alone | Given the CORPUS-CACHED path rather than the plain one, when a meta id is looked up, then it resolves identically. `find_by_id` has two branches, each with its own iteration and stem match, and patching one leaves every cached consumer refusing while AC1 stays green |
| AC3 | in `.claude/skills/sdlc-studio/scripts/reconcile.py`, restore `retitle_index_row`'s directory lookup to a bare `ARTIFACT_TYPES[type_]`, which raises KeyError on the type retitle has just resolved | Given a handoff and a review, when `artifact.py retitle` is invoked on either as a SUBPROCESS, then it exits 0 and rewrites the H1, the slug and the index row's title cell. RETRO is out of this row's scope and NOT excluded by any code: it exits 0 and leaves the row's title text stale, which is BG0632, filed and carried |
| AC4 | in `.claude/skills/sdlc-studio/scripts/reconcile.py`, revert `_swap`'s target resolution to `extract_record_id`, whose pipeline-prefix alternation returns None for a meta stem, so the rewriter finds no target to swap and silently leaves the old one in place | Given the same rename, when the index row's LINK TARGET is read, then it points at the new filename. This is asserted apart from AC3 because it fails independently: `_swap` resolves the target through `extract_record_id`, so a rename can leave the H1, slug and title cell all correct, exit 0, and only the link dangling |
| AC5 | in `.claude/skills/sdlc-studio/scripts/reconcile.py`, revert `_META_INDEX` to its own dict literal after the lift, so two of the three copies converge and the third goes on drifting | Given the lifted meta map, when the copies `next_id` AND `reconcile` hold are compared to `sdlc_md`'s, then all three are the SAME OBJECT. `reconcile.py`:765 keeps a third literal, commented as avoiding an import it already makes at module scope, and a fix lifting the map while leaving that literal preserves exactly the drift this row forbids. Identity, not equality: two maps with equal contents is the state this bug was filed in, and an equality assertion passes on it |
| AC6 | in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py`, add the three meta types to `ARTIFACT_TYPES` AND add their matching `SCOPE_TYPES` entries in `reconcile.py` - the complete careless repair, so no pre-existing test fires first and this row's kill is its own | Given a fixture workspace containing a retro, a handoff and a review, when the backlog and scope census run, then they are UNCHANGED from the same workspace without them - the blast radius D0174 exists to avoid |
| AC7 | in `.claude/skills/sdlc-studio/scripts/file_finding.py`, remove the `> **Status:**` check from the parent guard, restoring the resolve-only test that let a child be minted against a parent that cannot hold the back-link | Given `file_finding.py file --parent <RETRO/HO/RV id>` run as a SUBPROCESS, when the parent resolves but carries no `> **Status:**` line to anchor a child link after, then the command REFUSES with NOTHING written - no artefact file and no index row - and names the missing field; and given a `--parent` that CAN carry the link, the child is still minted and indexed. Both halves: a guard refusing every parent satisfies the refusal half on its own. This is a REGRESSION this unit introduced, found at delivery review: widening `find_by_id` made resolving and being linkable diverge, so the pre-mint guard passed, the child was written AND indexed AND stamped with a one-way `> **Parent:**` line, and only then did `write_decomposed` raise - the command printed "file refused" over a finding that exists on disk |
| AC7 | in `.claude/skills/sdlc-studio/scripts/file_finding.py`, invert the parent guard to raise whenever the field IS present, so every parent is refused and the mint never happens | Given `file_finding.py file --parent <RETRO/HO/RV id>` run as a SUBPROCESS, when the parent resolves but carries no `> **Status:**` line to anchor a child link after, then the command REFUSES with NOTHING written - no artefact file and no index row - and names the missing field; and given a `--parent` that CAN carry the link, the child is still minted and indexed. Both halves: a guard refusing every parent satisfies the refusal half on its own. This is a REGRESSION this unit introduced, found at delivery review: widening `find_by_id` made resolving and being linkable diverge, so the pre-mint guard passed, the child was written AND indexed AND stamped with a one-way `> **Parent:**` line, and only then did `write_decomposed` raise - the command printed "file refused" over a finding that exists on disk |
| AC8 | in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py`, drop the `norm_id(rec).startswith(want)` test from `_meta_files`, so a pipeline id filed under `reviews/` resolves as a review | Given a meta directory holding a pipeline id misfiled into it, a companion note beside the artefact it annotates, and a DIRECTORY whose name ends `.md`, when `find_by_id` resolves each id, then none of the three is returned as an artefact. A direct glob that keeps what the pipeline walker drops resolves ids the rest of the toolchain does not believe in, and `_meta_files` had dropped the walker's prefix guard, its companion-suffix filter and its `is_file` test while its own docstring claimed the glob could not mint a phantom artefact |
| AC8 | in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py`, remove the `p.is_file()` test, so a directory named `RETRO0003-adir.md` is yielded as an artefact path | Given a meta directory holding a pipeline id misfiled into it, a companion note beside the artefact it annotates, and a DIRECTORY whose name ends `.md`, when `find_by_id` resolves each id, then none of the three is returned as an artefact. A direct glob that keeps what the pipeline walker drops resolves ids the rest of the toolchain does not believe in, and `_meta_files` had dropped the walker's prefix guard, its companion-suffix filter and its `is_file` test while its own docstring claimed the glob could not mint a phantom artefact |
| AC8 | in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py`, delete the `p.stem.endswith(suffixes)` test, which `conventions.companion_suffixes` supplies and the pipeline walker applies at the same point | Given a meta directory holding a pipeline id misfiled into it, a companion note beside the artefact it annotates, and a DIRECTORY whose name ends `.md`, when `find_by_id` resolves each id, then none of the three is returned as an artefact. A direct glob that keeps what the pipeline walker drops resolves ids the rest of the toolchain does not believe in, and `_meta_files` had dropped the walker's prefix guard, its companion-suffix filter and its `is_file` test while its own docstring claimed the glob could not mint a phantom artefact |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
