# CR-0288: RFC0034 and RFC0038 are both Accepted with opposite canonical sizing decisions - no supersession marking, no cross-reference

> **Status:** Complete
> **Decomposed-into:** EP0071
> **Priority:** Medium
> **Type:** docs
> **Size:** S
> **Affects:** sdlc-studio/rfcs/RFC0034-sprint-sizing-velocity-and-estimate-calibration-close-the.md, sdlc-studio/rfcs/RFC0038-*.md, sdlc-studio/rfcs/_index.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

RFC0034 (Accepted 2026-07-14) records as Decided: D1 'Tokens are canonical, Effort S/M/L maps to calibrated token bands' and D5 'points kept as a within-story aid, not summed for capacity'. RFC0038 (Accepted the same day, shipped 2026-07-15) decides the exact opposite - Fibonacci Points as the ONE size vocabulary replacing Effort, summed for velocity - and is what shipped. RFC0038 contains zero references to RFC0034, RFC0034 has no revision entry after creation, and the RFC index shows Superseded = 0. Two simultaneously-Accepted design records give contradictory answers to 'what is the canonical size unit', RFC0034's spawned CR0257 built S/M/L wiring retired a day later, and reference-rfc.md defines the exact Superseded/'Superseded by' mechanism that was skipped. Note the fix is a partial supersession: RFC0034 D2-D4 remain live. Same defect class the repo filed RFC0011 about. Verified 3x.

## Impact

RFC0034 (Accepted 2026-07-14) records as Decided: D1 'Tokens are canonical, Effort S/M/L maps to calibrated token bands' and D5 'points kept as a within-story aid, not summed for capacity'.

## Acceptance Criteria

- [ ] RFC0034's D1 and D5 rows are marked overtaken/superseded by RFC0038 with in-file cross-links in both RFCs and a revision row in each
- [ ] RFC0034's header records the partial supersession (D2-D4 remain live) or the file is marked Superseded with the surviving decisions re-homed
- [ ] The rfcs index summary reflects the supersession state

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
