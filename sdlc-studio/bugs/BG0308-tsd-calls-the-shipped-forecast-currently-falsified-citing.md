# BG0308: TSD calls the shipped forecast 'currently falsified', citing a PRD section that says the falsified predictor was replace

> **Status:** Fixed
> **Verification depth:** functional (executable checks against the specs)
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/tsd.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The TSD tells its reader the sprint planner's token forecast 'is currently falsified out-of-sample (0.55x)' citing PRD section 10, but that section now documents RFC0038's replacement: Fibonacci points cleared a pre-registered bar (r = +0.682 pooled) and are the shipped forecast model - the two specs contradict each other on whether the cost instrument is known-broken or validated.

## Steps to Reproduce

Evidence (Performance Testing section (line 339) vs prd.md lines 569-587 and 215): tsd.md:339 quotes the falsified claim; prd.md:569-575 and :215 document the points predictor clearing the bar; the TSD's 2026-07-24 spec-truth reconcile pass left the paragraph untouched.

## Proposed Fix

Rewrite tsd.md line 339 to describe the shipped points-based forecast and its validation, keeping (if wanted) a historical note that the file-complexity predictor was falsified and retired.

## Acceptance Criteria

### AC1: the specs agree on whether the cost instrument is falsified

- **Given** the TSD's forecast section
- **When** the specs are read
- **Then** it describes the shipped POINTS model and names what was falsified and replaced, rather than calling the shipped instrument known-broken while the PRD documents its validation
- **Verify:** shell ! grep -q 'currently falsified out-of-sample' sdlc-studio/tsd.md
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
