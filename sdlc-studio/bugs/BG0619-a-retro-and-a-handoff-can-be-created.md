# BG0619: a retro and a handoff can be CREATED by the shipped creator but not FOUND by id, so every id-addressed tool refuses the artefacts the close itself mints

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
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

Make the resolver's type map agree with the creator's. NOT by adding them to `ARTIFACT_TYPES`: ten non-test scripts ITERATE that map (`validate.py`, `integrity.py`, `init.py`, `project_upgrade.py`, `migrate_v3.py`, `schema_check.py`, `provenance.py`, `backfill_authorship.py`, `github_sync.py`, `next_id.py`), so a retro added there lands on the backlogs, in the schema checks and in the derived-index machinery. The map already exists and is deliberately separate: `next_id.META_TYPES` (`next_id.py`:33) holds exactly review/RV, retro/RETRO and handoff/HO with their directories, and its own comment says it is kept out of `ARTIFACT_TYPES` so the pipeline machinery ignores them. So: LIFT that map into `sdlc_md`, have `find_by_id` search `ARTIFACT_TYPES` and then the meta map, leave every iterating consumer reading `ARTIFACT_TYPES` untouched, and keep `next_id.META_TYPES` as an alias of the lifted map so the two cannot drift again - two maps and one resolver is the defect. Refusing to mint is not the alternative, per D0173: the close mints two of the three on every run. A test that asserts every `--type` choice the creator offers is resolvable by `find_by_id` would pin whichever answer is chosen, and is the piece missing today.

## Acceptance Criteria

- [ ] **AC1** Given every `--type` the shipped creator accepts, when each is minted and then looked up by id, then it RESOLVES - the creator and the resolver state one rule between them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::CreatorResolverAgreementTests::test_every_creatable_type_is_resolvable
- [ ] **AC2** Given a retro and a handoff, when `artifact.py retitle` is invoked on either, then it retitles them across the H1, the slug and the index row - the two artefacts the close itself mints were the two it could not touch
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::CreatorResolverAgreementTests::test_a_retro_and_a_handoff_can_be_retitled
- [ ] **AC3** Given the three types the creator mints and the resolver did not hold - retro, handoff and review - when each is minted and looked up, then all three resolve, per D0173. Refusing to mint them is not the available alternative, because the close itself mints two of them every run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::CreatorResolverAgreementTests::test_retro_handoff_and_review_all_resolve

## Impact

The doctrine's rule is that mechanical work goes through a tool and hand-authoring is an error. `retitle` exists because a title lives in three places at once and a hand correction means editing all three plus every inbound link - which is exactly what had to be done twice at the last close, on the two artefacts the close had just written. A gap in the resolver quietly converts the tool-first rule into hand-editing for the artefact class that records what a run did.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
