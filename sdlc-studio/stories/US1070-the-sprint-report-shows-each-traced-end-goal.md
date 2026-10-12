# US1070: The sprint report shows each traced End goal's result beside the goal verdict

> **Status:** Draft
> **Delivers:** CR0629
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_report_end_goal_results.py, changelog.d/US1070.md
> **Epic:** EP0287
> **Points:** 3
> **Depends on:** US1069, US0992
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, signing a run's report
**I want** the sprint report to show each traced End goal's result beside the goal verdict, and to name a red End goal under an achieved verdict
**So that** the page I sign shows whether the persona's goal was met by its own check, not only by the team's word

## Acceptance Criteria

- **AC1:** Given a closed run whose goal verdict is achieved with End goal 2 passing and End goal 4 failing, when `sprint.py close` files the report, then its goal section lists both results with their selectors and names End goal 4 as red under an achieved verdict, and the annex's report catalogue holds the new keys.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_end_goal_results.py::ReportEndGoalTests::test_the_report_shows_end_goal_results_beside_the_verdict
- **AC2:** Given a committed schema-2 page whose run record carries no End goal results, when `sprint_report.py check` re-derives it, as `sprint sign` does, then it is byte-identical and its fingerprint unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_end_goal_results.py::ReportEndGoalTests::test_a_page_with_no_end_goal_results_rederives_unchanged

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the results kept on the run record only, so the signer never sees them, or a report key added with no annex row (US0992's conformance test)
- AC2 must fail on: an always-present empty section, so every earlier page stops re-deriving and its signature reads stale
- Serves: Maya Okafor #4.
- The section renders only when the run record carries results. Whether the results sit inside the digest is US0993's rule to state; the draft keeps them inside, as the verdict word is.
- Depends on US0992 so the annex (reference-evidence-schema.md) exists to receive the rows.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
