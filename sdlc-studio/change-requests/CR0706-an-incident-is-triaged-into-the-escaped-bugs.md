# CR-0706: An incident is triaged into the escaped bugs it caused, the report states escapes per 100 points, and an escape's class reaches only the briefs whose files it matches

> **Status:** Proposed
> **Parent:** RFC0063
> **Priority:** Medium
> **Type:** feature
> **Size:** M
> **Evidence:** Run thirteen (RUN-01M7EYR3): CR0693 derived Complete by reconcile after EP0309 (US1157-US1159) resolved; its incident, escape-rate and file-matching parts were deferred at grooming (D0482)
> **Date:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run thirteen orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T09:04:50Z

## Summary

CR0693's part 2. Run thirteen delivered its first criterion and part of its last (EP0309: a bug records its escape, `escape.py trace` proposes the unit and verdict, `escape.py to-class` makes the root cause a failure class carrying its files), and reconcile derived CR0693 Complete when those children resolved. This request carries what was deferred at grooming: an incident recorded as an issue with a root-cause section and triaged into the escaped bugs it caused (D0457); escapes per 100 points delivered on the sprint report and the scorecard; and plan-time matching of each unit's files against the failure classes, so only the matches reach that unit's build and review briefs, under a token cap.

## Impact

Serves Abena Osei's End goal 4: an escaped defect is traced to where it got through and the mistake is not repeated.

## Acceptance Criteria

- [ ] An incident is recorded as an issue with a root-cause section and triaged into the escaped bugs it caused, each linked back to it
- [ ] The sprint report and the scorecard state escapes per 100 points delivered, from the linked records
- [ ] At plan time each unit's files are matched against the failure classes, and only the matches reach that unit's build and review briefs, under a token cap

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run thirteen orchestrator) | Raised |
