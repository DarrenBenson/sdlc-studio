# BG0320: RFC0052 marked Superseded with no superseder named, decision D1 still Open, while its triage line says the work shipped

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/rfcs/RFC0052-the-closing-review-converges-on-code-and-never.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The artefact tells three contradictory stories: Status Superseded with no superseding artefact named (unlike RFC0019 and RFC0054, which name theirs), a Triage line saying DELIVERED via CR0393/EP0109 and CR0404/EP0113, and the sole decision row D1 still Open - a delivered RFC is not a superseded one, and an untraceable supersession plus an Open resolved decision leaves whichever record is wrong to rot.

## Steps to Reproduce

Evidence (Frontmatter lines 3-5 vs decision table line 30): Line 3 Status: Superseded; line 4 Triage: DELIVERED; line 30 decision row ends '| Open |'; grep -i supersed matches only the Status line; contrast RFC0019:7 and RFC0054:16 which name their supersessors.

## Proposed Fix

Reconcile the three records: set the status to the delivered/closed vocabulary (or name the superseding artefacts), close D1 recording that options C and D shipped as CR0393/EP0109 and CR0404/EP0113, and keep the triage line consistent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
