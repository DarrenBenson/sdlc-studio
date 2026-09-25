# US0944: `verify_ac stamps` never reports green on nothing, and no stale stamp ships in v6

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_honest.py, sdlc-studio/stories/US0063-consolidated-audit-check-command-over-the-team-schema.md, sdlc-studio/bugs/BG0357-mutation-py-records-no-per-test-attribution-so.md, changelog.d/US0944.md, tools/tests/test_verify_corpus.py, tools/verify-corpus-baseline.txt, tools/verify-corpus.sh
> **Epic:** EP0265
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer whose one review signal is a green test
**I want** `verify_ac.py stamps` to refuse an id it cannot find and to resolve an id to its file
**So that** a stamp check that read nothing can never report that every verifier resolves

## Acceptance Criteria

- **AC1:** Given `verify_ac.py stamps --story NOSUCH`, then it exits 2 naming the unknown id. Fails on: HEAD, which skips the missing path, prints `1 file(s) checked, every stamped verifier still resolves` and exits 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_honest.py::StampsHonestTests::test_an_unknown_story_is_refused
  - **Verified:** yes (2026-09-25)
- **AC2:** Given a fixture story US0001 whose `Verified: yes` criterion names a deleted test node, when `stamps --story US0001` runs (an id, not a path), then it exits 1 naming US0001 and the criterion. Fails on: refusing ids instead of resolving them to the story or bug file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_honest.py::StampsHonestTests::test_an_id_resolves_to_its_file
  - **Verified:** yes (2026-09-25)
- **AC3:** Given this repository, then `verify_ac.py stamps --bugs` exits 0, with US0063 AC2 and BG0357 AC4 and AC5 retired in the D0259 pattern or re-pointed to live nodes. Fails on: HEAD, which reports those three stamps as resolving to nothing
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/verify_ac.py stamps --bugs
  - **Verified:** yes (2026-09-25)

## Notes

Release bar item: `verify_ac stamps --bugs` green at the tag. Premises measured at 013a46d0: cmd_stamps `if not p.exists(): continue` at verify_ac.py:3575; `stamps --bugs` exits 1 on exactly US0063 AC2, BG0357 AC4 and BG0357 AC5. US0936 edits verify_ac.py too (the retraction floor), so do not put the two in one wave. AC3 must be re-run after US0936 and US0914 land, since both retire stamps.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (N4) |
