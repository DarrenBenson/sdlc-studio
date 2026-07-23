# EP0129: Residuals from the CR0364-derived requests

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0365
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0365. Delivers the work CR0365 requested.

## Story Breakdown

- [ ] [US0367: anchor the CR0302 freshness guard to the claim so it fails on the stale counts](../stories/US0367-anchor-the-cr0302-freshness-guard-to-the-claim.md)
- [ ] [US0368: extend the CR0340 test-relevant set to every path a shipped test reads](../stories/US0368-extend-the-cr0340-test-relevant-set-to-every.md)
- [ ] [US0369: correct the CR0304 TRD sentence and disposition the doc-drift residuals](../stories/US0369-correct-the-cr0304-trd-sentence-and-disposition-the.md)
- [ ] [US0370: record the AC-correction cases as AC defects](../stories/US0370-record-the-ac-correction-cases-as-ac-defects.md)

## Acceptance Criteria (Epic Level)

- [ ] each residual above is either fixed, or refiled as its own unit with a reason, or declined in writing - none is silently dropped
- [ ] CR0302's freshness guard is anchored to the claim it checks, not to the first match in the file, and fails on the stale counts it currently reports green on
- [ ] CR0340's test-relevant set covers every path a shipped test reads, so no commit can skip a suite that its own change can break
- [ ] CR0304's TRD sentence states what SKILL.md actually contains
- [ ] the AC-correction cases (CR0334, and CR0284's AC1) are recorded as AC defects rather than carried as outstanding build work

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
