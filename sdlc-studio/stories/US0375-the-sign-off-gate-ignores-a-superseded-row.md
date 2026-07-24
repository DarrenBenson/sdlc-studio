# US0375: the sign-off gate ignores a superseded row while it stays visible

> **Status:** Draft
> **Delivers:** CR0372
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0133
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md

## User Story

**As an** operator who is the reviewer of record on a unit whose verdict log wrongly names me as its adversarial reviewer
**I want** the sign-off gate to read a superseded row as retired while the row stays in the file
**So that** a corrected mis-entry stops stranding the unit, without the audit trail losing the record that it happened

## Acceptance Criteria

### AC1: superseding a verdict does NOT restore independence

**Amended 2026-07-24.** As first written this criterion specified the opposite - that a superseded
reviewer drops out of the session set - and the closing review reproduced a complete bypass of the
two-role gate from it: an author blocked by a REJECT superseded it (the only guard being that the
authoriser is not the row's own author, met by any other string), the reviewer then left the
session set, and the author's own subagent was accepted as reviewer of record. A passing test
defended the hole. The rule below is the corrected one; the mis-attribution case the original was
reaching for is BG0284, and needs a principal-authorised path rather than a guess.

- **Given** a verdict row naming `qa-seat` as reviewer of a unit authored by `builder`, and a recorded supersession retiring that row
- **When** `record_signoff` is called with `qa-seat` as principal and `builder` as author
- **Then** the verdict is retired for the critiqued gate (`verdict_for` returns None) but `_session_reviewer_ids` STILL returns `qa-seat`, so the sign-off is refused - a supersession retires a verdict, it cannot un-make the fact that someone reviewed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersededGateTests::test_superseding_does_NOT_restore_independence
- **Verified:** yes (2026-07-24)

### AC2: latest-row-wins skips a superseded verdict and falls back to the live one

- **Given** a unit with an APPROVE row, then a later REJECT row, and a supersession retiring the REJECT
- **When** `verdict_for` is asked for that unit
- **Then** it returns the earlier live APPROVE rather than the retired REJECT, and a unit whose only row is superseded reads as having no verdict rather than as approved
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersededGateTests::test_verdict_for_skips_the_superseded_row_and_falls_back
- **Verified:** yes (2026-07-24)

### AC3: the superseded row stays visible and is marked, never dropped

- **Given** the same superseded row
- **When** `read_verdicts` reads the log and `critic show` prints it, in both text and json form
- **Then** the row is still returned and printed, flagged as superseded with its reason and authoriser, so a reader sees both that it was recorded and that it was retired
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersededGateTests::test_superseded_row_stays_visible_and_flagged_in_show
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Built: superseded rows skipped by `verdict_for` and the sign-off gate, still returned and flagged in `show`; TDD red-first, mutation-proven |
