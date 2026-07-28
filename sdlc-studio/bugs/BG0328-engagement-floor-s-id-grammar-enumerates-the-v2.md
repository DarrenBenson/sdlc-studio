# BG0328: Engagement floor's id grammar enumerates the v2 4-digit form, silently exempting v3 ULID and 5-digit units

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

Every floor entry point recognises only US/BG/CR plus exactly four digits, so a unit with a v3 short-ULID or 5-digit id is invisible: the floor-pending lane drops it before judging, the git leg cannot count it in a multi-id subject (mis-attributing the file set to the 4-digit unit), and the commit-msg multi-id rule never fires - on a schema-v3 project the floor reports clean while checking nothing. The shared library already widened its grammar for this exact lesson; the floor never adopted it.

## Steps to Reproduce

Evidence (Line 101 `_JUDGED_ID_RE`; pending lane ~line 350; git attribution leg ~line 183; `check_commit_message` ~line 640; .githooks/commit-msg line 96): `engagement_floor.py`:101 regex \d{4}; lib/`sdlc_md.py`:38-43 documents the widened \d{4,} plus ULID-first `ID_RE`; grep for ulid/v3 in `engagement_floor.py` returns nothing; the commit-msg hook's paste-hint grep repeats the 4-digit enumeration.

## Proposed Fix

Replace `_JUDGED_ID_RE` (and the commit-msg hint grep) with the `sdlc_md` `ID_RE` grammar - \d{4,} plus the v3 ULID alternative - so v3 and 5-digit units are judged.

## Acceptance Criteria

### AC1: a v3 ULID multi-id subject is judged

- **Given** a commit subject naming two v3 short-ULID ids and no `Refs:` trailer
- **When** `check_commit_message` runs under `--strict`
- **Then** it refuses and names both ids, instead of reading an empty id set and passing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::IdGrammarCoversV3AndFiveDigitTests::test_a_v3_ulid_multi_id_subject_is_nudged_for_a_refs_trailer

### AC2: a five-digit id is judged

- **Given** a subject naming `US01010` and `US01011`
- **When** the same check runs
- **Then** it refuses and names them - the fixed four-digit run matched neither
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::IdGrammarCoversV3AndFiveDigitTests::test_a_five_digit_multi_id_subject_is_nudged_for_a_refs_trailer

### AC3: the remedy it prints actually satisfies the rule

- **Given** a v3 multi-id subject
- **When** a `Refs:` trailer naming both ids is added in the form the warning prints
- **Then** the check is clean, so the pasted trailer is one the grammar accepts
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::IdGrammarCoversV3AndFiveDigitTests::test_a_v3_refs_trailer_still_clears_the_nudge

### AC4: a v3 artefact path names its owning unit

- **Given** a staged path `sdlc-studio/bugs/BG-01JQK3F8-sample.md`
- **When** `_path_owner` reads it
- **Then** it returns that unit rather than None
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::IdGrammarCoversV3AndFiveDigitTests::test_a_v3_artefact_path_names_its_owning_unit

### AC5: a mixed-era subject counts as the batch it is

- **Given** a commit whose subject names one v2 id and one v3 id
- **When** the git leg attributes its files
- **Then** neither id is credited with the shared file set, because two ids is a batch whichever eras they come from
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::IdGrammarCoversV3AndFiveDigitTests::test_a_mixed_era_subject_counts_as_the_batch_it_is

### AC6: the pending lane sees a v3 unit's staged violation

- **Given** a staged v3 bug declaring one file alongside three staged source files
- **When** `detect(root, include_staged=True)` runs
- **Then** the unit is reported in violation with at least three source files, instead of being dropped before judgement
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::IdGrammarCoversV3AndFiveDigitTests::test_a_v3_unit_the_pending_commit_puts_below_the_floor_is_seen

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-28 | delivery lane (RUN-01KYJZGZ) | Acceptance criteria authored; fix + regression tests landed |
