# BG0190: apply-signoff tail does not derive parent epics terminal; US0237 AC2 over-claimed it

> **Status:** Open
> **Severity:** Low
> **Depends on:** US0214
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

US0237 AC2 states the apply-signoff tail derives parent epics/CRs terminal, but `_apply_signoff_tail` only writes the velocity row + runs reconcile; the per-unit transition cascade ticks the epic breakdown checkbox without setting the epic Status. With `two_backlog.enforce` off (default) reconcile does not derive it either, so after --apply-signoff transitions all of an epic's stories Done the epic stays Draft. The AC's Verify line only covered the reconcile-drift half, so the gap passed review.

## Steps to Reproduce

1. Run a sprint whose batch is all of an epic's stories. 2. sprint close --apply-signoff transitions them Done. 3. Observe the parent epic (e.g. EP0077, EP0080 at the RUN-01KXS5JY close) stays Draft; reconcile detect reports 0 drift; the epic had to be transitioned Done by hand.

## Proposed Fix

Either have `_apply_signoff_tail` transition a parent whose children are all terminal (respecting the transition gate), or correct US0237's AC2 to not claim auto-derivation and document that epic terminal status is a separate step when `two_backlog.enforce` is off.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
