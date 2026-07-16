# BG0171: gate.py --require-close help text claims the close-owed lane 'WARNS on every gate by default'; the plain gate never runs it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

The --require-close help string (gate.py:749) states 'The close-owed lane WARNS on every gate by default; this makes it block.' The first clause is false: close-owed is absent from `DEFAULT_CHECKS`, the lane's own docstring says the opposite ('a BOUND lane, added by its mode and never part of the plain gate'), `test_gate.py`:1461-1462 asserts the plain gate excludes it, and the soft nudge actually lives in status.py's `close_owed_advisory.` An operator reading gate --help is told every gate run will at least surface owed closes; in reality the plain gate CI and the pre-commit hook run says nothing, so a skipped close-down is invisible until someone passes --require-close - the LL0008 silent-misleading class on the exact ceremony RFC0042 shipped to make un-skippable. Verified 3x.

## Steps to Reproduce

Run `gate.py --help` and read the --require-close text; then run a plain gate in a workspace with owed closes - no close-owed output appears (`DEFAULT_CHECKS` has no such lane).

## Proposed Fix

Correct the help string to match reality (the soft nudge lives in status/hint; the lane exists only under --require-close) - or, if the always-warn behaviour is wanted, add close-owed as an advisory `DEFAULT_CHECKS` lane and keep the text. Pick one; the docstring's bound-only doctrine suggests the text fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
