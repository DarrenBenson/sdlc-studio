# CR-0438: Done stories carry unresolved Open Questions with no gate requiring resolution before terminal status (14 stories)

> **Status:** In Progress
> **Decomposed-into:** EP0169
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/stories/US0298-a-goal-unreachable-by-construction-is-detected-and.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_d141ccb5

## Summary

US0298 shipped Done with two unchecked Open Questions bearing named Owners and no recorded resolution, the second admitting its AC set covers one gate of an unenumerated set; 14 Done stories carry unchecked Open Questions items, and nothing in validate, conformance, or the Done transition requires questions resolved or moved before terminal status, though the discipline exists (US0304's Resolved Questions with recorded rulings).

## Impact

US0298 shipped Done with two unchecked Open Questions bearing named Owners and no recorded resolution, the second admitting its AC set covers one gate of an unenumerated set; 14 Done stories carry unchecked Open Questions items, and nothing in validate, conformance, or the Done transition requires questions resolved or moved before terminal status, though the discipline exists (US0304's Resolved Questions with recorded rulings).

## Acceptance Criteria

- [ ] Add a validate (or Done-transition) check that a terminal-status story has no unchecked items under an Open Questions heading - require each to be resolved into Resolved Questions with a ruling or filed as a follow-up artefact - and sweep the 14 existing stories accordingly.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Raised |
