# BG0619: a retro and a handoff can be CREATED by the shipped creator but not FOUND by id, so every id-addressed tool refuses the artefacts the close itself mints

> **Status:** Open
> **Severity:** Medium
> **Points:** 8
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/next_id.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** `artifact.py retitle --id RETRO0109` and `--id HO0063` both refused during the RUN-01M0WCCG close on 2026-08-25. Confirmed 2026-08-26 by calling `find_by_id` over seven ids and printing `ARTIFACT_TYPES`. The creator's accepted `--type` list read from its own --help.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`artifact.py new --type` accepts `retro`, `handoff` and `review`, and `sprint close` mints both a retro and a handoff on every run. But `sdlc_md.ARTIFACT_TYPES` holds only bug, charter, cr, epic, issue, plan, rfc, story, test-spec and workflow, and `find_by_id` iterates exactly that map. Measured 2026-08-26: `find_by_id` resolves BG0615, US0676, EP0217, CR0558 and TS0001, and returns None for RETRO0109 and HO0063 - artefacts that exist, are indexed, and were written by the shipped creator minutes earlier. Twelve scripts read `find_by_id`, so the refusal is not local to one verb: `artifact.py retitle --id RETRO0109` answers `no artifact found for id 'RETRO0109'`, and the same is true for the handoff. The creator and the resolver disagree about which types exist.

## Steps to Reproduce

1. `sprint.py close --retro RETROxxxx`, which mints a retro and a handoff. 2. Try to correct either one's title with the deterministic writer: `artifact.py retitle --id RETRO0109 --title '<new>'`. 3. It answers `no artifact found`. Measured on RETRO0109 and HO0063, 2026-08-25, where both had to be renamed by hand across the file, the H1 and the index row, plus an inbound link repaired in the retro body.

## Proposed Fix

NOT by adding the three to `ARTIFACT_TYPES`. Roughly twenty non-test scripts ITERATE that map -
`reconcile.py` derives its scope sweep from it and reddens on a type with no scope, `init.py`
mints an `_index.md` per type, `validate.py` derives its `--type` choices - so a retro added
there lands on the backlogs, through the schema checks and into the derived-index machinery.
(`github_sync.py` was named in an earlier draft of this list and does NOT iterate the map; it
mentions it in a comment.)

The map already exists and is deliberately separate: `next_id.META_TYPES` holds exactly
review/RV, retro/RETRO and handoff/HO with their directories. So: LIFT it into `sdlc_md`, have
`find_by_id` search `ARTIFACT_TYPES` and then the meta map, leave every iterating consumer
reading `ARTIFACT_TYPES` untouched, and keep `next_id.META_TYPES` bound to the lifted object so
the two cannot drift again.

That alone is NOT ENOUGH, and an earlier draft of this section said it was. `find_by_id`
matches files through `extract_record_id`, whose `ID_RE` is a hardcoded pipeline-prefix
alternation, so a `RETRO0109-...` stem returns None whatever the type map holds. A review
measured it: with the three added to `ARTIFACT_TYPES` in a copied tree, `find_by_id` still
returned None and retitle still answered `no artifact found`. `sdlc_md.stem_record_id` already
exists for exactly this and its own docstring says it returns None for a handoff, a retro or a
review - so the stem match is the second half of the repair, not an afterthought.

The retitle path then needs THREE more repairs, all measured rather than read, and all after
`find_by_id` has already returned a path:

- the hard `ARTIFACT_TYPES[type_]` lookups in `artifact.py` and `reconcile.retitle_index_row`
  raise `KeyError` on the type retitle has just resolved;
- `reconcile.py`:3099 matches the index row's ID cell with `ID_SEARCH_RE`, whose alternation
  is the same pipeline-prefix set, so `found` stays False and the command refuses with `no
  index row to update`;
- `artifact.py`:1906 reads `extract_record_id(path.stem) or path.stem`, so for a meta id the
  fallback yields the WHOLE stem and the id handed to the row writer can never match it.

That is FOUR parts, not two, which is why this unit is priced at 8 rather than the 5 an
earlier draft carried on a two-part account.

RETRO is deliberately OUT of the retitle half. `retros/_index.md` is headed `| ID | Sprint |
Date | Delivered | Blocked |` - it has no Title column - while handoffs and reviews are `| ID |
Title | Date |`. There is no row for `retitle_index_row` to update, and rewriting the file
silently while `found=True` passes the dry-run is worse than refusing. That gap is BG0632; here retitle covers handoff and review, and a retro RESOLVES without being
retitleable.

The row's LINK TARGET belongs to THIS unit for the two types it keeps. `_swap`
(`reconcile.py`:3107) resolves it through `extract_record_id`, which fails for HO and RV
exactly as it does for RETRO, so a rename updating the title cell and leaving the link at
the old filename is half a retitle. BG0632 owns the retro's half; AC2 asserts this one.

## Acceptance Criteria

- [ ] **AC1** Given every `--type` the shipped creator accepts, when each is minted and looked up by id, then it RESOLVES and reports its own type string - not merely a non-None path. The type is asserted because the two halves of this fix fail differently: a widened map with the stem match untouched resolves nothing, and asserting non-None alone would not say which half was missing. Paired control: a BG and a US id still resolve to bug and story
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::CreatorResolverAgreementTests::test_every_creatable_type_resolves_to_its_own_type
- [ ] **AC2** Given a handoff and a review, when `artifact.py retitle` is invoked on either as a SUBPROCESS, then it exits 0 and rewrites the H1, the slug, the index row's title cell AND that row's LINK TARGET. The link half fails independently - `_swap` resolves it through `extract_record_id`, which does not recognise a meta stem - so a criterion asserting the title alone passes on a rename that leaves the link dangling. RETRO is excluded and the reason is recorded in the Proposed Fix: its index has no Title column, so there is no row to update. The bug's entire evidence is a CLI refusal, so this criterion runs the command rather than the library
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::CreatorResolverAgreementTests::test_the_retitle_command_renames_a_handoff_and_a_review
- [ ] **AC3** Given the lifted meta map, when `next_id.META_TYPES` is compared to `sdlc_md.META_TYPES`, then they are the SAME OBJECT. Identity, not equality: two maps holding equal contents is the state this bug was filed in, and an equality assertion passes on it. Nothing a mint-and-resolve test does can see the difference
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py::CreatorResolverAgreementTests::test_the_meta_map_is_one_object_not_two_equal_ones
- [ ] **AC4** Given a fixture workspace containing a retro, a handoff and a review, when the backlog and scope census run, then they are UNCHANGED from the same workspace without them. This is the blast radius no other row covers, and its mutant is the honest version of the repair this bug was filed with: `tests/test_reconcile.py` already asserts scope coverage equals `set(ARTIFACT_TYPES)`, so adding the three there reddens it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::CreatorResolverAgreementTests::test_the_meta_types_stay_off_the_backlog_and_the_scope_census

## Impact

The doctrine's rule is that mechanical work goes through a tool and hand-authoring is an error. `retitle` exists because a title lives in three places at once and a hand correction means editing all three plus every inbound link - which is exactly what had to be done twice at the last close, on the two artefacts the close had just written. A gap in the resolver quietly converts the tool-first rule into hand-editing for the artefact class that records what a run did.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py`, add only handoff and review to the meta map, omitting retro - the mistake THIS plan invites, since its retitle half covers exactly those two, and the one that leaves AC2, AC3 and AC4 green | Given every `--type` the shipped creator accepts, when each is minted and looked up by id, then it RESOLVES and reports its own type string - not merely a non-None path. The type is asserted because the two halves of this fix fail differently: a widened map with the stem match untouched resolves nothing, and asserting non-None alone would not say which half was missing. Paired control: a BG and a US id still resolve to bug and story |
| AC2 | in `.claude/skills/sdlc-studio/scripts/reconcile.py`, revert `retitle_index_row`'s directory lookup to a bare `ARTIFACT_TYPES[type_]`, which raises KeyError on the type retitle has just resolved - the omission that 'leave every consumer untouched' invites | Given a handoff and a review, when `artifact.py retitle` is invoked on either as a SUBPROCESS, then it exits 0 and rewrites the H1, the slug, the index row's title cell AND that row's LINK TARGET. The link half fails independently - `_swap` resolves it through `extract_record_id`, which does not recognise a meta stem - so a criterion asserting the title alone passes on a rename that leaves the link dangling. RETRO is excluded and the reason is recorded in the Proposed Fix: its index has no Title column, so there is no row to update. The bug's entire evidence is a CLI refusal, so this criterion runs the command rather than the library |
| AC3 | in `.claude/skills/sdlc-studio/scripts/next_id.py`, replace the import of the lifted map with a fresh dict literal holding equal contents, so the two maps can drift apart again | Given the lifted meta map, when `next_id.META_TYPES` is compared to `sdlc_md.META_TYPES`, then they are the SAME OBJECT. Identity, not equality: two maps holding equal contents is the state this bug was filed in, and an equality assertion passes on it. Nothing a mint-and-resolve test does can see the difference |
| AC4 | in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py`, add the three meta types to `ARTIFACT_TYPES` AND add their matching `SCOPE_TYPES` entries in `reconcile.py` - the COMPLETE careless repair. Without the second half `test_every_artifact_type_is_reachable_by_a_scope` reddens first and this row's kill is borrowed rather than proven | Given a fixture workspace containing a retro, a handoff and a review, when the backlog and scope census run, then they are UNCHANGED from the same workspace without them. This is the blast radius no other row covers, and its mutant is the honest version of the repair this bug was filed with: `tests/test_reconcile.py` already asserts scope coverage equals `set(ARTIFACT_TYPES)`, so adding the three there reddens it |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
