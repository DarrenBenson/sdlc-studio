# CR-0557: BG0463's twenty batch-boundary findings need re-triage against HEAD before any of them is engineered

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/bugs/BG0463-twenty-non-blocking-findings-from-the-run-01kytka1.md
> **Evidence:** `verify_ac.py testplan derive --unit BG0463` refuses with "the plan would carry 0 row(s) for 4 criterion/criteria". BG0463's closure record on the artefact carries the full reasoning.
> **Date:** 2026-08-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 aggregated twenty non-blocking findings from the RUN-01KYTKA1 batch-boundary review in July. It was closed on 2026-08-25 as unbuildable: its items are bare `- [ ]` bullets with no `**ACn**` ids, so `testplan derive` yields zero rows for four criteria and no terminal gate can read it. Its content is not thereby worthless - twenty observations from an independent pass are worth re-reading - but they must be re-triaged against HEAD individually before any is sized, because the aggregate has been sitting for six weeks and this repository has a recorded case of five closed bugs that were never defects.

## Impact

Nobody, until somebody tries to plan from it - at which point it welds critic.py, `sprint_report.py` and lib/`sdlc_md.py` into a single atomic block worth twenty points, for a unit that cannot produce a test plan. That planning cost is the concrete harm and it was measured while planning the bug-backlog sprint.

## Acceptance Criteria

- [ ] Given each of the twenty findings, when it is re-triaged, then its verdict against HEAD is recorded as reproduces, already-fixed or superseded, with the source line that settles it
- [ ] Given a finding that still reproduces, when it is re-filed, then it carries its own `**ACn**` criteria and an executable `Verify:` line, so a test plan can be derived from it
- [ ] Given a finding that no longer reproduces, when it is dispositioned, then it is recorded as such rather than dropped silently - the failure mode BG0577 names
- [ ] Given the re-triage as a whole, when it completes, then BG0463 names where its content went, so the aggregate is traceable rather than merely closed

## Recommendation

Option 1, and not before the current bug backlog is cleared. Six weeks of drift is exactly the interval over which this project has measured findings going stale - four of twenty-four open bugs failed premise verification on 2026-08-25 - so re-triage without re-verification would re-import the same problem the aggregate already caused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Raised |
