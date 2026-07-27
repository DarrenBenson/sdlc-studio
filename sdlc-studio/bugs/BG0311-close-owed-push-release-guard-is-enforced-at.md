# BG0311: Close-owed 'push/release guard' is enforced at neither moment: no pre-push hook, no CI flag, and --release does not bind

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/tsd.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The TSD documents --require-close as a Blocking push-or-release guard and reference-retro.md says it is 'enforced at the push/release moment', but nothing at either moment runs it: gate.py binds the close-owed lane only when the flag is passed, --release does not imply it, the TSD's own pre-release stage prescribes plain gate.py --release, no pre-push hook exists, CI runs the plain gate, and the `close_guard.py` fallback is wired nowhere - reproducing the exact 'ceremony with no detector' failure the lane was built to close.

## Steps to Reproduce

Evidence (Bound-lane table line 421; CI/CD stage 4 line 532; gate.py lines 1595-1597; reference-retro.md line 56; help/gate.md lines 168-206): gate.py:1595-1597 'if `require_close`: ... registry["close-owed"]'; tsd.md:532 pre-release stage omits the flag; .githooks/ contains only pre-commit and commit-msg; lint.yml:60 runs plain gate.py; help/gate.md:176-183 shows the flag only as a manual snippet.

## Proposed Fix

Bind the close-owed lane into --release (or add a pre-push hook / CI step running gate --require-close), and update the TSD stage and reference-retro.md to describe the binding that actually executes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
