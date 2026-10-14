# BG1044: A ruling record's note is decided by the whole ledger, and a tab in a reviewer id still forges a field

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py, changelog.d/BG1044.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py
> **Evidence:** BG1003 round-2 QA verdict in sdlc-studio/reviews/critic-verdicts.md (APPROVE, BLOCKING: none), notes 1-5, each executed by the reviewer at a0f85a1b.
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T15:15:17Z

## Summary

BG1003's QA seat approved round 2 with five notes. (1) `_append_ruling` decides whether the section owes its RULING note by searching the whole ledger for 'RULING record', table rows included; this repository's ledger already holds the phrase in a verdict row's issues, so the next ruling records land below the supersession-only introduction ('Each record retires one verdict row above') with no note. (2) `_ruling_value` defuses ' key=' before folding whitespace, so a reviewer id carrying a tab ('qa<TAB>recorded=1999-01-01') forges the recorded field; the changelog says a reviewer id cannot forge one. (3) The ruling is keyed by `row_identity`, which duplicate rows share, so a ruled row repeating an earlier row's cells carries its ruling onto that row too. (4) decisions.standing lower-cases a status only to call it superseded, so an unsuperseded 'Accepted' cell is refused as 'superseded, not accepted'. (5) An unknown decision given below the cap is unpinned: validating it there (round 1's M13) survives the module, and the BG1003 commit message over-claims M13 as killed.

## Steps to Reproduce

On a copy of sdlc-studio/reviews/critic-verdicts.md at a0f85a1b, record BG0993's round 3 with --ruling D0352: the RULING line lands under 'Each record retires one verdict row above' and no note is written.

## Proposed Fix

Decide the note by the Supersessions section alone, looking for the note or the RULING-aware introduction (not a RULING line, so a section that missed it gets it before its next ruling). Fold whitespace before defusing keys. Key the annotation by identity plus the occurrence among identical rows. Compare the status case-insensitively before the lineage reading. Pin an unknown decision below the cap as noted, not refused.

## Acceptance Criteria

- [ ] **AC1** Given a ledger whose table rows mention 'RULING record' and whose section holds only the supersession introduction, when a ruling round is recorded, then the note precedes the RULING line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_the_section_introduction_speaks_of_ruling_records
  - **Verified:** yes (2026-10-14)
- [ ] **AC2** Given a reviewer id carrying a tab before 'recorded=', when a ruling round is recorded, then `read_round_rulings` returns the real recorded date and the whole reviewer id.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_a_reviewer_id_cannot_forge_a_ruling_field
  - **Verified:** yes (2026-10-14)
- [ ] **AC3** Given a ruled row whose cells repeat earlier rows of the unit, when the ledger is read, then only that row carries the ruling.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_the_ruling_stays_with_its_row_and_names_the_delivery_round
  - **Verified:** yes (2026-10-14)
- [ ] **AC4** Given a decision naming the unit first whose Status cell reads `Accepted` and which nothing supersedes, when it is passed as `--ruling` at the cap, then the round is recorded.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_the_subject_is_read_by_the_shared_id_grammar
  - **Verified:** yes (2026-10-14)
- [ ] **AC5** Given a unit below the cap, when a verdict is recorded with an unknown `--ruling`, then it is written and the ruling is noted as not needed, not refused.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_a_ruling_below_the_cap_is_noted_and_not_spent
  - **Verified:** yes (2026-10-14)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | sdlc-studio | Filed |
