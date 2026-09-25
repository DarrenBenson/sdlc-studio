# US0945: Changing a stamped test lists the criteria that stamp it before the commit lands

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_changed.py, changelog.d/US0945.md
> **Epic:** EP0265
> **Parent:** CR0595
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer deleting or trimming tests as the lean product sheds machinery
**I want** the existing `stamps --staged` lane to list every `Verified: yes` criterion whose selector names a test node my staged diff changed
**So that** I re-read those criteria's words before the reviewer has to, the class that produced 8 of Sprint 4's 16 REJECT rows

## Acceptance Criteria

- **AC1:** Given a staged diff that edits the body of `test_x`, and a `Verified: yes` criterion whose Verify names `test_x`, when `verify_ac.py stamps --staged` runs, then it prints that criterion's id and its words under a `re-read` heading and exits 0. Fails on: HEAD, which checks only that the node still exists
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_changed.py::StampsChangedTests::test_an_edited_stamped_test_lists_its_criterion
  - **Verified:** yes (2026-09-25)
- **AC2:** Given a staged diff that deletes `test_x`, then the same criterion is reported as orphaned by this commit and the lane exits 1, as it does at HEAD. Fails on: folding deletion into the advisory list, which would stop refusing an orphaned stamp
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_changed.py::StampsChangedTests::test_a_deleted_stamped_test_still_refuses
  - **Verified:** yes (2026-09-25)
- **AC3:** Given a staged diff that edits only a test no criterion stamps, then nothing is listed. Fails on: listing every stamped criterion in any changed test file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_changed.py::StampsChangedTests::test_an_unstamped_edit_lists_nothing
  - **Verified:** yes (2026-09-25)
- **AC4:** Given a staged diff that edits `test_x` in whitespace or comments only, then nothing is listed. Fails on: comparing raw text rather than each node's parsed body
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_changed.py::StampsChangedTests::test_a_cosmetic_edit_lists_nothing
  - **Verified:** yes (2026-09-25)

## Notes

- Depends on: US0944
- Answers CR0595 (LC-002 graduated): 14 of Sprint 4's 16 REJECT rows cited LC-002, and 8 were this shape (US0916, US0910, US0911, US0920, US0917, US0915 x2, US0912). Ratchet (LC-008): advisory in an existing lane; no new refusal, no new lane, no baseline. Measured yield: the 8 rows; it retires the per-unit hand-written `test_no_stamp_names_a_deleted_test` guards each deletion unit wrote for itself. Extends `staged_stamps` (verify_ac.py:3468): compare each live selector's node AST dump between HEAD and the index blob. Lands after N4 (same function region). Close CR0595 Complete when it lands.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (N5) |
