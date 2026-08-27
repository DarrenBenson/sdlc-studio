# EP0221: A tag cannot be cut without asking whether the increment is shippable

> **Status:** Draft
> **Derived Point Total:** 19
> **Parent:** CR0499
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0499. Delivers the work CR0499 requested.

## Story Breakdown

- [ ] [US0700: The shipped Release definition-of-done carries a mechanical shippable-increment clause](../stories/US0700-the-shipped-release-definition-of-done-carries-a.md)
- [ ] [US0701: The goal half is DERIVED from the recorded sprint goal verdict and never re-asked at release time](../stories/US0701-the-goal-half-is-derived-from-the-recorded.md)
- [ ] [US0702: The defect half judges the run's own goal clauses, so release and close cannot disagree](../stories/US0702-the-defect-half-judges-the-run-s-own.md)
- [ ] [US0703: `release_cut.tag_check` refuses a tag naming which half failed and what would clear it](../stories/US0703-release-cut-tag-check-refuses-a-tag-naming.md)
- [ ] [US0704: A partial or missed verdict is releasable only as an explicitly recorded operator decision](../stories/US0704-a-partial-or-missed-verdict-is-releasable-only.md)
- [ ] [US0705: The defect judgement reports its own LOWER BOUND when unfiled findings exist](../stories/US0705-the-defect-judgement-reports-its-own-lower-bound.md)
- [ ] [US0706: A project with no adopted definition-of-done inherits the clause from the shipped template](../stories/US0706-a-project-with-no-adopted-definition-of-done.md)

## Acceptance Criteria (Epic Level)

- [ ] The shipped Release definition-of-done carries a clause asserting the increment is shippable, in the same form and with a check tag like its existing mechanical clauses.
- [ ] The goal half is DERIVED from the recorded sprint goal verdict, never re-asked at release time - so the tag cannot get a softer answer than the close did.
- [ ] The defect half calls `critic.judge_defects_against_goal` with the run's own goal clauses, so the release and the close cannot disagree about which defects block.
- [ ] `release_cut.tag_check` refuses a tag when either half fails, naming which half, the verdict or the blocking defects, and what would clear it.
- [ ] A `partial` or `missed` verdict can still be released as an explicitly RECORDED operator decision, in the shape `file-and-close` already uses - so a knowingly partial release is stated on the record and a silent one is impossible.
- [ ] The defect judgement reports its own LOWER BOUND: when findings exist that have not been filed as artefacts, it says so rather than reporting zero blocking, because an unfiled finding is not an absent one.
- [ ] A project that has adopted no definition-of-done inherits the clause from the shipped template, since the gap is what every consuming project inherits rather than a local omission.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
