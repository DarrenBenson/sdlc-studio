# BG1264: US1133's trailer check skips a single-id subject though its docs say it does not, refuses this repository's paperwork-commit convention, and leaves two ownership rules unpinned

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, tools/enable-hooks.sh, tools/tests/test_commit_msg_mentions.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Evidence:** run eight (RUN-01M6RZQZ) US1133 review round 1 ([new]), and the orchestrator's friction log (R8-F13)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:37:58Z

## Summary

(1) The `Refs:` contradiction refusal runs only for a subject naming two or more ids: the early return `if len(written) <= 1 or not paths` (`.claude/skills/sdlc-studio/scripts/engagement_floor.py:922`) precedes it, so a single-id subject carrying `Refs:` for a unit that owns none of the staged files lands, while `changelog.d/US1133.md:10`, the `tools/enable-hooks.sh:12-14` header and the `cmd_check_commit_msg` comment say the hook now refuses such a line, with no qualifier. (2) The refusal refuses this repository's own paperwork commits: of the 60 most recent multi-id commits before `71120f12`, replayed message-for-diff, 18 that the base hook passed are refused, every one a verdict, self-check or Done-transition commit carrying `Refs:` for a unit whose `Affects` declares none of the ledger files staged (for example `2b3eb23b`, `e247df8d`, `089008d5`). Each now costs a retry rewriting `Refs:` as `Mentions:`, against the first-attempt landing CR0681 (In Progress) and US1133 exist for. (3) Ownership by filename (`_path_owner` in `owns()`, claimed by the fragment and the `derive_trailers` docstring) has no test: dropping it survives all four AC tests, yet alone it turns a commit staging only `changelog.d/US0001.md` from landed with `Refs: US0001` into refused. (4) The exemption of an id with no artefact from the contradiction check (`i in fp`) is unpinned: its mutant survives all four AC tests.

## Steps to Reproduce

(1) In a fixture, stage a file owned by US0001 only and commit with subject `fix(US0002): x` and body `Refs: US0002`: it lands. (2) Replay the 60 multi-id commits before `71120f12` through the hook, message against diff: 18 refusals, all paperwork commits. (3) Remove `_path_owner(f) == rid` from `owns()` and run the US1133 tests: green. (4) Remove `i in fp` from the contradicted list and run them: green.

## Proposed Fix

Either run the contradiction check for a single-id subject too, or say in the fragment, the `enable-hooks.sh` header and the comment that only a multi-id subject is judged; treat the ledgers a paperwork commit stages (`sdlc-studio/reviews/critic-verdicts.md`, `sdlc-studio/reviews/author-self-checks.md`, the unit's own artefact) as owned by the unit the commit records, or derive `Mentions:` for such an id rather than refusing; add a test for ownership by filename and one for the no-artefact exemption.

## Acceptance Criteria

- [ ] **AC1** The hook and its prose agree on a single-id subject: in a fixture staging a file only US0001 owns, `fix(US0002): x` with body `Refs: US0002` lands, and the `tools/enable-hooks.sh` header and the `derive_trailers` docstring each say the `Refs:` contradiction refusal judges only a subject naming two or more ids. The positive control: the two-id subject `fix(US0001, US0002): x` with the same `Refs: US0002` is refused, naming US0002. Fails on: either text stating the refusal with no multi-id qualifier, or the two-id case landing.
  - **Verify:** pytest tools/tests/test_commit_msg_mentions.py::DerivedMentionsTests::test_a_single_id_refs_lands_and_a_multi_id_one_is_refused
- [ ] **AC2** Following recorded step (2) no longer reproduces the defect: a two-id paperwork commit whose `Refs:` names the unit a staged `sdlc-studio/reviews/critic-verdicts.md` or `sdlc-studio/reviews/author-self-checks.md` records, or whose staged file is that unit's own artefact, lands at its first attempt through the real hook (the ledger read as owned by that unit, or the id written `Mentions:`), with no line to rewrite. The positive control: a `Refs:` naming a unit that owns none of a staged source file is still refused.
  - **Verify:** pytest tools/tests/test_commit_msg_mentions.py::DerivedMentionsTests::test_a_paperwork_commit_refs_lands_and_a_source_contradiction_is_refused
- [ ] **AC3** Recorded steps (3) and (4) now turn a test red: a two-id commit staging only `changelog.d/US0001.md` with `Refs: US0001` lands, so removing `_path_owner(f) == rid` from `owns()` makes it refused; and a `Refs:` naming an id with no artefact in the workspace is not reported contradicted, so removing `i in fp` makes it contradicted. The positive control in each: a `Refs:` for a unit with an artefact that owns none of the staged files is contradicted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CommitMsgCheckTests::test_a_file_named_for_its_unit_is_owned_by_that_unit .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CommitMsgCheckTests::test_a_refs_id_with_no_artefact_is_not_contradicted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
