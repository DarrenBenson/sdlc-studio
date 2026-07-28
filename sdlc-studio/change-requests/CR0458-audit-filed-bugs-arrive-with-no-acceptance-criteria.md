# CR-0458: Audit-filed bugs arrive with no Acceptance Criteria, so a delivery lane has nothing to deliver against

> **Status:** Complete
> **Decomposed-into:** EP0178
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

`file_finding` writes Steps to Reproduce and a Proposed Fix but no acceptance criteria, so a lane picking the unit up must infer the contract - and the engagement floor then refuses the batch for carrying no plan. The same filer also writes Affects from where the evidence was READ rather than where the fix lands (BG0343), which recurred on every unit this sprint.

## Impact

`file_finding` writes Steps to Reproduce and a Proposed Fix but no acceptance criteria, so a lane picking the unit up must infer the contract - and the engagement floor then refuses the batch for carrying no plan. The same filer also writes Affects from where the evidence was READ rather than where the fix lands (BG0343), which recurred on every unit this sprint.

## Acceptance Criteria

- [ ] The behaviour described in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Raised |
