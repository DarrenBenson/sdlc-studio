# BG1274: US1133 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py, tools/tests/test_commit_msg_hook.py, tools/tests/test_commit_msg_mentions.py, tools/enable-hooks.sh, AGENTS.md, changelog.d/US1133.md, .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:46:36Z

## Summary

US1133 was rejected at round 2, the review cap, by qa-seat-US1133-r1, so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [regression] round-1 blocking finding CLOSED for the directory and glob shapes and OVER-CLAIMED as parity: the hook still refuses a correct `Refs:` line, and writes `Mentions:` for a true owner, on two declaration shapes the close guard credits and the base hook passed. A token whose parenthetical note holds a comma is cut in two (engagement\_floor.py:449 splits on every comma, where sdlc\_md.\_affects\_tokens splits outside parentheses), and a path with a `..` segment is never normalised (engagement\_floor.py:719 takes relative\_to without the resolve sprint.py:5039 applies). 15 units of this tree carry the shapes (CR0021, CR0141, CR0155 the note, US0483, US0495, US0502, US0503, US0504, CR0446, CR0449, CR0464, CR0467 among the `..` ones). So the claims at engagement\_floor.py:895 ("an owner the close credits is an owner here") and changelog.d/US1133.md:6 ("the reading `sprint close` already gives the same declarations") are false, and the parity test (test\_engagement\_floor.py:740) draws its shapes only from families where the two readers agree by construction (test\_engagement\_floor.py:753) [LC-018]; [pre-existing] the tokeniser split and the unresolved `..` key predate this unit (CR0229, 06a65b06, feeding the advisory affects\_owners only, which never refuses). They are reported here only as the cause of the regression above, which is new because this diff makes them feed a refusal

## Steps to Reproduce

1. Read the round 2 REJECT of US1133 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1133 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [regression] round-1 blocking finding CLOSED for the directory and glob shapes and OVER-CLAIMED as parity: the hook still refuses a correct `Refs:` line, and writes `Mentions:` for a true owner, on two declaration shapes the close guard credits and the base hook passed. A token whose parenthetical note holds a comma is cut in two (engagement\_floor.py:449 splits on every comma, where sdlc\_md.\_affects\_tokens splits outside parentheses), and a path with a `..` segment is never normalised (engagement\_floor.py:719 takes relative\_to without the resolve sprint.py:5039 applies). 15 units of this tree carry the shapes (CR0021, CR0141, CR0155 the note, US0483, US0495, US0502, US0503, US0504, CR0446, CR0449, CR0464, CR0467 among the `..` ones). So the claims at engagement\_floor.py:895 ("an owner the close credits is an owner here") and changelog.d/US1133.md:6 ("the reading `sprint close` already gives the same declarations") are false, and the parity test (test\_engagement\_floor.py:740) draws its shapes only from families where the two readers agree by construction (test\_engagement\_floor.py:753) [LC-018]
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] the tokeniser split and the unresolved `..` key predate this unit (CR0229, 06a65b06, feeding the advisory affects\_owners only, which never refuses). They are reported here only as the cause of the regression above, which is new because this diff makes them feed a refusal
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** US1133 AC1 still passes: Given a subject naming two ids that each own a staged file by their Affects and no trailer, when the commit-msg hook runs, then it writes one `Refs: <id>` per owning id into the message and the commit lands at the first attempt (a replay of the BG1213 landing). Fails on: `message-refs` still refusing a message the staged-file map can attribute.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::DerivedTrailerTests::test_owning_ids_get_refs_written_and_the_commit_lands
  - **Verified:** yes (2026-11-06)
- [ ] **AC4** US1133 AC2 still passes: Given a subject naming an id that owns none of the staged files, then the hook writes `Mentions: <id>` for it, never `Refs:`. Fails on: writing `Refs:` for every id the subject names.
  - **Verify:** pytest tools/tests/test_commit_msg_mentions.py::DerivedMentionsTests::test_a_non_owning_id_gets_mentions
  - **Verified:** yes (2026-11-06)
- [ ] **AC5** US1133 AC3 still passes: Given a message whose existing `Refs:` trailer names an id that owns none of the staged files, then `message-refs` refuses naming that id; a trailer that matches ownership passes unchanged and is never written twice. Fails on: the lane deleted outright, or a correct trailer duplicated.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::DerivedTrailerTests::test_a_trailer_that_contradicts_ownership_is_refused
  - **Verified:** yes (2026-11-06)
- [ ] **AC6** US1133 AC4 still passes: Given a consuming project's commit message file, when `engagement_floor.py check-commit-msg --write-trailers <file>` runs, then it appends the derived trailers by the same rule, and `AGENTS.md`'s refusals table and `tools/enable-hooks.sh` describe the hook as writing them. Fails on: the derivation living only in this repository's hook.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CommitMsgCheckTests::test_write_trailers_appends_from_ownership
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Filed |
| 2026-11-06 | Claude Opus 5.5 | Affects widened: the close guard in `sprint.py` now reads declarations through the same `engagement_floor.declared_keys` the hook uses (LL0016) |
