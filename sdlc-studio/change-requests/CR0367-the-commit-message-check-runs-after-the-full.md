# CR-0367: the commit-message check runs after the full test gate, so a subject-line defect costs a whole suite run

> **Status:** Complete
> **Decomposed-into:** EP0131
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .githooks/pre-commit, .githooks/commit-msg
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

git runs pre-commit before commit-msg. The pre-commit gate takes about 140 seconds when scripts are staged. Only after it passes does commit-msg reject a subject naming several work-item ids with no Refs: trailer. Hit live this session: the whole gate ran green, then the commit was refused for a message defect that was knowable before any test executed. The same applies to any other commit-msg rule. This is the serial-discovery cost CR0359 addresses for sprint close, in the commit path.

## Impact

Anyone committing work that touches scripts pays a full suite run to learn about a message defect, then pays it again after fixing the message. Two avoidable suite runs, several minutes, for a fault in one line of prose. It also teaches an agent to reach for --no-verify, which is the outcome the un-skippable gate exists to prevent.

## Acceptance Criteria

- [ ] Given a commit whose message would be refused by commit-msg, when the commit is attempted, then the message is validated BEFORE the expensive lanes run, so the refusal arrives in seconds rather than after the suite
- [ ] Given a commit whose message is valid, when the commit runs, then behaviour is unchanged - the message check adds no new refusal, only moves an existing one earlier
- [ ] Given the message check moves, when the gate runs, then no existing lane is lost or duplicated, pinned the way the lane-order reorder was pinned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
