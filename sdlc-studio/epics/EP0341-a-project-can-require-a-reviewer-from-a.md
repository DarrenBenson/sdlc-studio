# EP0341: A project can require a reviewer from a different model family, and reads what that buys

> **Status:** Draft
> **Derived Point Total:** 13
> **Parent:** CR0698
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0698. Delivers the work CR0698 requested.

## Story Breakdown

- [ ] [US1239: Each recorded verdict states the reviewer's model and harness, or unknown where the store gives neither](../stories/US1239-each-recorded-verdict-states-the-reviewer-s-model.md)
- [ ] [US1240: With review.reviewer_family set to different, a same-family verdict is refused and an unknown needs a waiver](../stories/US1240-with-review-reviewer-family-set-to-different-a.md)
- [ ] [US1241: The review brief names the harness and model to dispatch the reviewer to when the family setting is on](../stories/US1241-the-review-brief-names-the-harness-and-model.md)
- [ ] [US1242: The sprint report states reviews, upheld rejections and traced escapes for each reviewer model family](../stories/US1242-the-sprint-report-states-reviews-upheld-rejections-and.md)

## Acceptance Criteria (Epic Level)

- [ ] Each recorded verdict states the reviewer's model and harness where the harness's store gives them, and 'unknown' where it does not
- [ ] A project can set `review.reviewer_family: different` (default `any`); with it set, `critic.py record` refuses a verdict whose reviewer model family matches the builder's, naming both, and accepts one whose family is unknown only with a recorded waiver
- [ ] `critic.py brief` names the harness and model to dispatch the reviewer to when the setting is on, using CR0667's headless lanes
- [ ] The sprint report states, per reviewer model family, the reviews done, rejections upheld and escapes later traced to them, so the setting's yield is read rather than assumed

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
