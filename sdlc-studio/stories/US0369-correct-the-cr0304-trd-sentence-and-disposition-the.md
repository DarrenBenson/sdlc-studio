# US0369: correct the CR0304 TRD sentence and disposition the doc-drift residuals

> **Status:** Draft
> **Delivers:** CR0365
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0129
> **Points:** 3
> **Affects:** sdlc-studio/trd.md

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the TRD sentence CR0304 flagged is corrected

- **Given** the TRD sentence CR0304 recorded as false
- **When** a reader compares it with the shipped behaviour
- **Then** the sentence states what actually ships, and the correction is dated in the TRD's revision history rather than made silently
- **Verify:** grep 'Revision History' sdlc-studio/trd.md

### AC2: every doc-drift residual is dispositioned, none left silent

- **Given** the doc-drift residuals CR0365's sweep found
- **When** the pass finishes
- **Then** each residual is either corrected or explicitly declined with a reason - the discipline the retro already enforces, applied here, because silence is what let twelve requests derive Complete over unmet criteria
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::DocDriftResidualTests::test_every_residual_is_corrected_or_declined_with_a_reason

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
