# CR-0434: RFC0009 is partially superseded by RFC0038 (complexity-based estimation retired at r=0.03) but carries no supersession a

> **Status:** Complete
> **Decomposed-into:** EP0172
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/rfcs/RFC0009-code-complexity-signals.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

RFC0038 falsified and deleted RFC0009's estimation and prioritisation consumers (`max_cognitive` at r=0.03, complexity WSJF tie-break and `EFFORT_COMPLEXITY_PROXY` deleted), and the project's own convention for this event is visible on RFC0034 (partial-supersession header, per-decision Superseded rows, index note) - RFC0009 got none of it and still records D5 and WS3 as delivered live behaviour, so a reader is sent back to a retired model, the exact stale-record cost CR0280 documents.

## Impact

RFC0038 falsified and deleted RFC0009's estimation and prioritisation consumers (`max_cognitive` at r=0.03, complexity WSJF tie-break and `EFFORT_COMPLEXITY_PROXY` deleted), and the project's own convention for this event is visible on RFC0034 (partial-supersession header, per-decision Superseded rows, index note) - RFC0009 got none of it and still records D5 and WS3 as delivered live behaviour, so a reader is sent back to a retired model, the exact stale-record cost CR0280 documents.

## Acceptance Criteria

- [ ] Apply the RFC0034 convention to RFC0009: status 'Accepted (partially superseded)', a 'Partially superseded by RFC-0038' header line, Superseded markers on the affected decision rows, plus matching notes in the index and RFC0038's header.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |
