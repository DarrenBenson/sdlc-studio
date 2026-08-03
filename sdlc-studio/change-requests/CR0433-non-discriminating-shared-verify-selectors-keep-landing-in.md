# CR-0433: Non-discriminating shared Verify selectors keep landing in Done stories after the advisory lint shipped; debt grew 17 to

> **Status:** Complete
> **Decomposed-into:** EP0169
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/stories/US0268-order-the-pre-commit-lanes-cheapest-first-so.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

US0227 set the standard (each AC fails on its own regression) and recorded 17 duplicate-selector offenders as visible debt, but stories groomed and closed afterwards still share one selector across multiple ACs, the lint now reports 19 suspicious lines, and no unit re-ingests the residual - 'visible rather than silent' has decayed into permanently tolerated.

## Impact

US0227 set the standard (each AC fails on its own regression) and recorded 17 duplicate-selector offenders as visible debt, but stories groomed and closed afterwards still share one selector across multiple ACs, the lint now reports 19 suspicious lines, and no unit re-ingests the residual - 'visible rather than silent' has decayed into permanently tolerated.

## Acceptance Criteria

- [ ] Convert the lint's count into a ratchet (fail the gate when it exceeds the recorded baseline) and file a burn-down unit for the current 19.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |
