# EP0309: An escaped defect is traced to the unit and verdict that let it through, and its cause reaches the next build and review

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0693
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0693. Delivers the work CR0693 requested.

## Story Breakdown

- [x] [US1157: A bug records that it escaped to production, the release it shipped in and the unit that let it through](../stories/US1157-a-bug-records-that-it-escaped-to-production.md)
- [x] [US1158: escape.py trace proposes the unit and verdict that let an escaped bug through, from the release and the files the fix touches](../stories/US1158-escape-py-trace-proposes-the-unit-and-verdict.md)
- [ ] [US1159: An escape's root cause becomes a failure class that carries the files it applies to](../stories/US1159-an-escape-s-root-cause-becomes-a-failure.md)

## Acceptance Criteria (Epic Level)

- [ ] A bug found in production records that it escaped, the release it shipped in, and the unit and review verdict that let it through; a command proposes the unit from the release and the files the fix touches
- [ ] An incident is recorded as an issue with a root-cause section and triaged into the escaped bugs it caused, each linked back to it (D0457)
- [ ] The sprint report and the scorecard state escapes per 100 points delivered, from the linked records
- [ ] An escape's root cause becomes a failure class or lesson; at plan time each unit's files are matched against them, and only the matches reach that unit's build and review briefs, under a token cap the engineering seat sets by measuring (D0462, RFC0062)

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
