# BG0195: apply-signoff tail passes the dashed retro id to retro accuracy, so the velocity row never records

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`_apply_signoff_tail` reads state['`scaffolded_retro`'], which sprint close writes in DASHED display form (RETRO-0049), and passes it straight to 'retro accuracy --id'. That lookup expects the undashed file form (RETRO0049) and fails with 'no retro file for RETRO-0049', so the velocity row is silently not written and the close prints only an advisory. Observed at the RUN-01KXS5JY close (noted as a nit, never filed) and again at RUN-01KXT0YV - the velocity tail US0237 exists to remove has therefore not actually run for two consecutive sprints.

## Steps to Reproduce

1. Run sprint close with no --retro so a retro is scaffolded; observe state['`scaffolded_retro`'] = 'RETRO-0049' (dashed). 2. Fill the retro and re-run sprint close --retro RETRO0049 --apply-signoff --principal '<you>'. 3. Observe 'apply-signoff: velocity not recorded (retro RETRO-0049: no retro file for RETRO-0049 ...)'. 4. Confirm retros/VELOCITY.md has no row for this run.

## Proposed Fix

Normalise the id before the accuracy call - `sdlc_md.norm_id(retro_id)` or the same undashed form transition/validate use - and add a test asserting the velocity row is written when `scaffolded_retro` is in dashed form. Consider making retro.accuracy accept either form, since the dashed id is what the close prints to the operator.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
