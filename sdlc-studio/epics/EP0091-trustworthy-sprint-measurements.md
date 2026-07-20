# EP0091: Trustworthy sprint measurements

> **Status:** Draft
> **Parent:** CR0350
> **Derived Point Total:** 8
> **Parent:** CR0363
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0363 and CR0350. Delivers the measurement-trust work both requested:
the mutation gate reports what its test command actually covered (CR0363), and an
interactive close records its token actuals (CR0350).

## Story Breakdown

- [ ] [US0277: Mutation run reports its selected test files and records the test command in the JSON result](../stories/US0277-mutation-run-reports-its-selected-test-files-and.md)
- [ ] [US0278: Warn when a test file that references the target module falls outside the test command's selection](../stories/US0278-warn-when-a-test-file-that-references-the.md)
- [ ] [US0279: An interactive close captures the harness-tracked token total into the velocity row without hand entry](../stories/US0279-an-interactive-close-captures-the-harness-tracked-token.md)

## Acceptance Criteria (Epic Level)

- [ ] the run reports which test files its test command selects, alongside the survivor list
- [ ] a test file that references the target module but falls outside the command's selection is named as a warning, since that is the manufactured-survivor condition
- [ ] the test command is recorded in the JSON output beside the result, so a survivor cannot be read without knowing what was run against it
- [ ] the warning is advisory and never blocks: a deliberately narrow run stays legal and stays honest about what it covered

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
