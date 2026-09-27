# US0961: A verdict recorded against a brief the unit has since outgrown says so

> **Status:** In Progress
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_rebrief.py, changelog.d/US0961.md
> **Epic:** EP0267
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer running a fix round
**I want** `critic.py record` to tell me when the unit's Affects or criteria changed after the reviewer was briefed
**So that** a review is never recorded against a scope narrower than the diff it approves

## Acceptance Criteria

- **AC1:** Given a unit briefed with fingerprint F, then its Affects widened by one file, when `critic.py record --unit <id> --brief F --verdict APPROVE ...` runs, then it records the row and prints on stderr that the unit's brief is now G, naming the changed field (Affects or criteria) and the `critic.py brief` command to re-brief. Fails on: HEAD, which records silently (the retro's widen-after-brief pattern, three units in Sprint 5); refusing the record, which the ratchet forbids
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_rebrief.py::RebriefTests::test_a_widened_unit_is_named_at_record
- **AC2:** Given the same unit with nothing changed since the brief, when record runs, then stderr carries no such line; and a rejoinder brief's fingerprint is compared the way its footer printed it. Fails on: comparing a rejoinder against the base brief, which warns on every round 2
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_rebrief.py::RebriefTests::test_an_unchanged_unit_records_quietly

## Notes

RETRO0125 TRY 'widen-after-brief'. The brief is deterministic over the card, Affects, criteria and tier (no diff content), so a recomputed fingerprint differs exactly when the scope moved. Advisory only: LC-008 permits it because it adds no refusal, and it retires the hand rule 're-brief whenever a fix round touches a new file' that lived only in the orchestrator's scratch script. Cuttable to v6.1 if capacity binds.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (US0961) |
