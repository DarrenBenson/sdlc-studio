# EP0375: A review can see the running application

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0738
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0738. Delivers the work CR0738 requested.

## Story Breakdown

- [ ] [US1311: `verify_ac` runs a `Verify: app <command>` line and records the evidence files it wrote, failing a command that exits 0 with no evidence](../stories/US1311-verify-ac-runs-a-verify-app-command-line.md)
- [ ] [US1312: `critic.py brief` lists a unit's recorded app evidence paths, and none without failing when it has no app criterion](../stories/US1312-critic-py-brief-lists-a-unit-s-recorded.md)

## Acceptance Criteria (Epic Level)

- [ ] `verify_ac` runs a `Verify: app <command>` line, passes on exit 0, and records the files the command wrote under the declared evidence folder
- [ ] A command that exits 0 and writes no evidence fails the criterion, naming the folder it looked in
- [ ] `critic.py brief` lists the recorded evidence paths for the unit, and lists none without failing when the unit has no app criterion

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
