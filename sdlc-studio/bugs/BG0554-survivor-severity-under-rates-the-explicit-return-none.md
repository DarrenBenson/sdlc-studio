# BG0554: survivor severity under-rates the explicit return-None idiom, which is the shape that matters most in this codebase

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01KZEF9M panel sign-off, 2026-08-07, product seat. Established by execution over a pair of bodies differing only in the form of the return.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_survivor_severity` derives High when a function returns a value on one path and None on another, on the stated ground that this is the codebase's refusal idiom. It detects the None path from a BARE `return` or a body that can fall off its end, and misses the explicit `return None` - which is how this codebase actually writes it. `repair_mutation_gate`, `verify_no_surface_claim` and `_ledger_contradiction` all end `return None`.

So a survivor in exactly the shape the rule exists to flag derives Medium, while a bare `return` in a function nobody gates on derives High. Triage sorts on this field, so the rule's own stated purpose is inverted for the case it names.

## Steps to Reproduce

1. Call `_survivor_severity` over `def f(a):\n    if a:\n        return 1\n    return None\n` at line 3. 2. It derives Medium with the signal 'reports rather than refuses'. 3. Change `return None` to a bare `return` and it derives High. The two bodies are identical in behaviour.

## Proposed Fix

Count an explicit `return None` - a `Return` whose value is a `Constant` of None - as a None path alongside the bare form. Add both to the `HONEST_HIGH` fixtures, so the pair cannot drift apart again.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_survivor_severity` derives High when a function returns a value on one path and None on another, on the stated ground that this is the codebase's refusal...
- [ ] **AC2** The proposed fix lands, pinned by a test: Count an explicit `return None` - a `Return` whose value is a `Constant` of None - as a None path alongside the bare form.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
