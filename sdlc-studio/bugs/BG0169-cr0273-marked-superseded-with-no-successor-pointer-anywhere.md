# BG0169: CR0273 marked Superseded with no successor pointer anywhere in the artefact graph

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/change-requests/CR0273-track-points-per-worker-hour-as-a-descriptive.md, sdlc-studio/rfcs/RFC0035-the-sprint-report-what-a-sprint-delivered-what.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

The in-flight sprint flips CR0273 Proposed -> Superseded as a one-line diff, recording the supersession nowhere a trace can follow: no Superseded-by header, no Revision History row (last row 2026-07-15 'Reframed'), and absorbing RFC0035 never mentions CR0273 - a repo grep finds the absorption only in RETRO0041/LATEST.md prose, outside the CR->RFC trace. The repo's own convention was skipped: RFC0037 states 'This RFC absorbs CR0264' in-body, and CR0019/CR0139/CR0141/CR0230/CR0231 all record supersession in-file. A reader of CR0273 cannot discover where its five acceptance criteria went, and no guard (validate/reconcile) checks successor pointers. This is a defect in the in-flight work's paperwork (fine per the brief: it is wrong, not merely unfinished). Verified 3x.

## Steps to Reproduce

Read CR0273: Status Superseded, no Superseded-by field, Revision History ends before the flip. grep -rln CR0273 over rfcs/, epics/, stories/ - zero hits in RFC0035/EP0048/US0172-US0176.

## Proposed Fix

Add `> **Superseded-by:** RFC0035` and a revision row to CR0273, and an 'absorbs CR0273' line in RFC0035's body (per the RFC0037/CR0264 precedent), before the sprint commits.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
