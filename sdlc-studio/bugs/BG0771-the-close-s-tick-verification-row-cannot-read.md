# BG0771: The close's tick-verification row cannot read the lean criterion shape

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG0771.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T12:01:16Z

## Summary

`sprint_report._ticked_criteria` reads a criterion as done only from a '- [x]' tick or a 'Verified: yes' line under a '### ACn' heading. The lean story shape every Sprint 4 unit uses is a '- **ACn:**' bullet with '- **Verify:**' and '- **Verified:** yes' sub-bullets, so at RUN-01M3BK9Y's close the row examined none of 35 units and refused 'no ticked criteria found'. Sprint 3 passed only because BG0742 carried '[x]' ticks.

## Steps to Reproduce

1. sprint.py close --retro RETRO0124 --dry-run on RUN-01M3BK9Y (2026-09-25). 2. The checklist refuses tick-verification: 'none of the 35 unit(s) carries a criterion this row can read'. 3. Every batch unit carries '- **Verified:** yes' under '- **ACn:**' bullets.

## Proposed Fix

Treat a '- **ACn:**' bullet as the heading for the Verified line that follows it in `_ticked_criteria`, with a fixture in the lean shape.

## Acceptance Criteria

- [ ] **AC1** Given a unit in the lean criterion shape (bold `ACn:` bullets, each with a `Verify:` sub-bullet and a `Verified: yes` sub-bullet), `sprint_report._ticked_criteria` names each verified criterion; a bug-shape `- [ ] **ACn**` criterion with a `Verified: yes` sub-bullet is read the same way; a `Verified: no` stamp or a retired `manual` stamp is not a tick; and the existing `### ACn` and `- [x]` readings are unchanged. Reads the bullet through the shared `sdlc_md.AC_BULLET_RE`, not a new pattern. Fails on: HEAD, which reads none (measured: 0 ticks across Sprint 4's 27 lean-shape units); treating every `**ACn**` bullet as ticked without its Verified line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationReadsTheLeanShapeTests::test_a_lean_bullet_criterion_is_read
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given a closed fixture run on a build rung whose units are in the lean shape, when `sprint_report.py checklist` runs, then the tick-verification row reads RAN with the count of ticked criteria supported by the diff when the declared Affects changed, and names the unsupported criteria when they did not. Fails on: HEAD's `no ticked criteria found`; fixing a copy of the reader that the row does not call
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationReadsTheLeanShapeTests::test_the_close_row_judges_lean_units
  - **Verified:** yes (2026-09-25)

## Notes

- - Sized 1, not QA's 2. The reader already exists (`sdlc_md.AC_BULLET_RE`, line 59); the fix is a handful of lines in `_ticked_criteria` (1389) and the row's logic does not change. Probed read-only at 013a46d0 with the fix applied in memory: Sprint 4's 27 lean-shape units go from 0 ticks read to 93, and no story or bug in the corpus loses a tick it reads today. What would make it 2 is a regression beyond the reader, and that probe found none.
- Without it, Sprint 5's close hands over the same unanswered row again (D0271).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | sdlc-studio v6 planning | Sprint 5 grooming (engineering seat): criteria regroomed from file_finding's generic restatement into two falsifiable criteria with executable selectors; sized 1 from a read-only probe of the fix |
