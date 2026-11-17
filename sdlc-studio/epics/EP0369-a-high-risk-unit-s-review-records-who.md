# EP0369: A high-risk unit's review records who wrote and who judged it by model family, and a project can require the two to differ

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0732
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0732. Delivers the work CR0732 requested.

## Story Breakdown

- [ ] [US1300: `critic.py record` stores the author's and reviewer's model ids on the verdict and derives each family from one shipped table, reporting an unknown id as unknown](../stories/US1300-critic-py-record-stores-the-author-s-and.md)
- [ ] [US1301: `review.cross_family` (off by default, warn, block) decides whether a same-family verdict counts as a high-risk unit's independent review](../stories/US1301-review-cross-family-off-by-default-warn-block.md)
- [ ] [US1302: The sprint report counts the high-risk units reviewed by a different model family, out of how many](../stories/US1302-the-sprint-report-counts-the-high-risk-units.md)

## Acceptance Criteria (Epic Level)

- [ ] `critic.py record` stores the author's and the reviewer's model id on the verdict row, and refuses a record for a high-risk unit that names neither when `review.cross_family` is warn or block
- [ ] A family is derived from a model id by one shipped table, and an id the table does not know is reported as unknown, never guessed
- [ ] With `review.cross_family: block`, a same-family verdict on a high-risk unit does not count as that unit's independent review; with warn it counts and the report says so; with off nothing changes
- [ ] The sprint report states how many high-risk units were reviewed by a different family, out of how many

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
