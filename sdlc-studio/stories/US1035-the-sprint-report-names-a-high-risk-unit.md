# US1035: The sprint report names a high-risk unit only one seat reviewed

> **Status:** Draft
> **Delivers:** CR0622
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_report_high_risk_one_lens.py, changelog.d/US1035.md
> **Epic:** EP0284
> **Points:** 3
> **Depends on:** US1034
> **Persona:** Maya Okafor

## User Story

**As** a team lead signing a sprint report for work agents built and reviewed
**I want** the report's review-attribution row to name any high-risk unit that only one seat reviewed, and the seat it was owed
**So that** a skipped second lens is in front of me when I sign, rather than a rule nobody followed

## Acceptance Criteria

- **AC1:** Given a closed run holding an 8-point unit the engineering seat alone approved and an 8-point unit the engineering and sre seats both approved, when `sprint_report.py checklist` draws the review-attribution row, then it names the first unit as high risk with one seat and the second seat `critic.py seats` derives, and does not name the second unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_high_risk_one_lens.py::HighRiskOneLensTests::test_a_high_risk_unit_one_seat_reviewed_is_named
- **AC2:** Given `review.second_seat.points: 5` in the project config, when the report is drawn over a 5-point unit one seat approved, then the row names it, as `critic.py seats` does
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_high_risk_one_lens.py::HighRiskOneLensTests::test_the_report_reads_the_projects_threshold
- **AC3:** Given a closed run whose 8-point unit one seat reviewed, when a later run records a second seat's verdict on the same unit and the closed run's page is drawn again, then the row still names the unit as reviewed by one seat in that run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_high_risk_one_lens.py::HighRiskOneLensTests::test_a_closed_pages_seats_come_from_its_own_rows

## Notes

- Release: later (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the row counts lenses over the whole batch (HEAD's MIN_LENSES reading) rather than per high-risk unit, so neither unit is named
- AC2 must fail on: the report holds its own copy of the threshold (8) instead of calling critic's derivation
- AC3 must fail on: the row reads the live ledger (verdict_for, sprint_report.py:2124-2127) rather than the run's own rows frozen at PREPARE (REVIEW_ROWS, sprint_report.py:3332)
- Reported, never refused: the row stays ANSWERED, and the line is evidence for the signature (LL0056).
- A unit's seats are the lanes the per-seat rounds story defines, read over the run's frozen rows, so the report and the ledger cannot disagree on what a second seat is. The report fingerprint hashes leaf figures only (sprint_report.py:2837), so AC3 is a consistency fix, not a signature change.
- The candidate to cut first within CR0622: `critic.py seats` already tells the orchestrator the second seat is owed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
