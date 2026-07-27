# BG0307: Retired 'review generate' still shipped as live surface: PRD feature row names a nonexistent script and the Secondary pe

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/prd.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

RFC0033 folded review generate into audit and the retirement shipped (scripts/`review_generate.py` is gone, no help/reference documents the command, help/review.md redirects to 'audit --profile repo'), yet the PRD marks the feature Complete/[HIGH] with scripts/`review_generate.py` as its backing script, and the registry's Secondary persona Jonah is defined around 'points review generate at the inherited repo' with index.md saying he 'owns the review generate on-ramp'. The Location column the PRD defines as naming the backing script points at nothing, and anyone designing the brownfield on-ramp from the registry is pointed at a command that cannot be run.

## Steps to Reproduce

Evidence (prd.md line 229 (feature row); personas/jonah-reyes-team-lead.md lines 58-60; personas/index.md line 14): ls .claude/skills/sdlc-studio/scripts/ has no `review_generate.py` (`lite_profile.py` exists); grep 'review generate|`review_generate`' across help/ and reference-*.md returns nothing; help/review.md:28-31 names audit --profile repo as the zero-setup pass; RFC0033 Accepted 2026-07-14; CR0254:19 lists 'retiring review generate' as a dependency.

## Proposed Fix

Update the PRD row to describe the audit --profile repo on-ramp (backed by audit.py + `lite_profile.py)`, and rewrite Jonah's Scenario and the index.md line to the audit command per RFC0033.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
