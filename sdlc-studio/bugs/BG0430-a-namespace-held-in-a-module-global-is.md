# BG0430: a namespace held in a module global is invisible to the dead-flag detector, so a live flag is reported dead with no cannot-judge reason

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py
> **Evidence:** Executed by an independent reviewer.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`_track_namespaces` registers the target of `X = parse_args()` against the ENCLOSING FUNCTION's scope, and `global ARGS` is not modelled. A read from a sibling function walks the scope chain out to Module, finds nothing and returns False - so the read is invisible, no escape is recorded, and the destination falls straight through to `dead`. The module-global namespace is a mainstream Python idiom and it is not among the bounds the detector's docstring declares. The failure is a false positive on a blocking lane with no warning attached.

## Steps to Reproduce

1. `ARGS = None` at module level; `main()` does `global ARGS; ARGS = ap.parse_args()`.
2. A sibling `work()` reads `if ARGS.verbose:`.
3. `--verbose` is reported DEAD with an empty unjudged list.

## Proposed Fix

Model `global` (and `nonlocal`) in `_track_namespaces`, or - if that is judged out of scope - detect the shape and record it as a cannot-judge reason rather than reporting dead.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `_track_namespaces` registers the target of `X = parse_args()` against the ENCLOSING FUNCTION's scope, and `global ARGS` is not modelled.
- [ ] The proposed fix lands, pinned by a test: Model `global` (and `nonlocal`) in `_track_namespaces`, or - if that is judged out of scope - detect the shape and record it as a cannot-judge reason rather...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
