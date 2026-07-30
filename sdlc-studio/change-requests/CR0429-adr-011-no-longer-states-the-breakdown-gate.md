# CR-0429: ADR-011 no longer states the breakdown gate's actual firing rule: the goal-aware design-rung exemption (D0062) shipped b

> **Status:** In Progress
> **Decomposed-into:** EP0168
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/trd.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

ADR-011 says unconditionally that any ungroomed unit makes sprint plan exit non-zero, but the shipped gate is goal-aware per D0062: an ungroomed batch is accepted at --goal design and refused elsewhere, with a close-side grooming report as counterweight - so the ADR of record misdescribes the deterministic fire/skip rule that ADR-006 makes load-bearing.

## Impact

ADR-011 says unconditionally that any ungroomed unit makes sprint plan exit non-zero, but the shipped gate is goal-aware per D0062: an ungroomed batch is accepted at --goal design and refused elsewhere, with a close-side grooming report as counterweight - so the ADR of record misdescribes the deterministic fire/skip rule that ADR-006 makes load-bearing.

## Acceptance Criteria

- [ ] Amend ADR-011 with the D0062 goal-aware exemption and the grooming-report counterweight, marking the amendment and date in the ADR per the project's supersession convention.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |
