# EP0357: The eval scenarios have a stated place in the release steps

> **Status:** Draft
> **Derived Point Total:** 7
> **Parent:** CR0718
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0718. Delivers the work CR0718 requested.

## Story Breakdown

- [ ] [US1272: The release check names a missing eval report for the version being cut](../stories/US1272-the-release-check-names-a-missing-eval-report.md)
- [ ] [US1273: A release's recorded eval result is kept as committed evidence](../stories/US1273-a-release-s-recorded-eval-result-is-kept.md)
- [ ] [US1274: The TSD names the eval step in its release stage and its coverage row matches the scenarios on disk](../stories/US1274-the-tsd-names-the-eval-step-in-its.md)

## Acceptance Criteria (Epic Level)

- [ ] The TSD's Before a release tag stage either names the eval report step and where its result is recorded, or the TSD states that eval scenarios are run on demand and are not a gate, with the same wording in every section that mentions them.
- [ ] If the step is kept, a release check refuses or warns by name when no eval report exists for the version being cut, and a test in `tools/tests/test_eval_run.py` covers both the present and the absent case.
- [ ] A recorded eval result for a release is kept as committed evidence, or the TSD says where it is kept and why it is not committed.
- [ ] The TSD's Coverage row for eval scenarios agrees with the scenario files on disk, held by a test that fails when a scenario is added without the row changing.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
