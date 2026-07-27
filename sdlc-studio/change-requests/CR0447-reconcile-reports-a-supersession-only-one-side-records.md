# CR-0447: reconcile reports a supersession only one side records

> **Status:** In Progress
> **Decomposed-into:** EP0175
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (scope residue from the D0069 cap); agent; skill v5.0.0

## Summary

US0476 records RFC0009's partial supersession by RFC0038 as CR0434 asked. Nothing detects the general case: a supersession one artefact declares and its counterpart does not, which the corpus carries in at least four spellings.

## Impact

Who: anyone navigating the RFC graph, and reconcile, which reports zero drift over one-sided supersessions today. What breaks: a superseded design keeps reading as live from one direction.

## Acceptance Criteria

- [ ] reconcile detects a supersession declared on one side and absent on the other, over a pinned declaration grammar rather than one hand-enumerated spelling.
- [ ] The four spellings already in the corpus are each either detected or explicitly waived with a reason.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (scope residue from the D0069 cap) | Raised |
