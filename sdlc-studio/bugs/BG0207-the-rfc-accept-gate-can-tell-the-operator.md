# BG0207: the RFC accept gate can tell the operator one decision is open when two are

> **Status:** Fixed
> **Verification depth:** functional (D1-before-fence / D7-after-fence reproduced the incomplete list, then both are named)
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/validate.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The RFC accept gate's fail-closed fallback fires only when the main scan found NO open rows (fence is not None and not `open_rows).` When a fence hides some rows but at least one open row was already found, the fallback never runs and the caller receives an INCOMPLETE list. Both callers print that list to the operator, so with D1 open before a broken fence and D7 after it the operator is told the RFC carries 1 Open decision, D1, when two are open. The gate still blocks, and it converges - closing D1 and re-running makes the fallback fire and surfaces D7 - so this costs a round-trip rather than correctness. It is nonetheless a false completeness claim in operator-facing output, which is the defect class this sprint kept producing.

## Steps to Reproduce

Build an RFC with an Open D1, then an unterminated fence, then an Open D7. Attempt transition to Accepted. Observe the refusal names 1 open decision (D1) though two are open.

## Proposed Fix

Either run the unstructured scan whenever the main scan ended inside a fence, regardless of whether rows were already found, and report the union; or keep the current trigger and mark the printed list as possibly partial when the scan ended inside a fence, so the count is not presented as complete.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
