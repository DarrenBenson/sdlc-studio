# BG0554: survivor severity under-rates the explicit return-None idiom, which is the shape that matters most in this codebase

> **Status:** Fixed
> **Verification depth:** functional (executed over four shapes: bare return, explicit return None, both-arms-valued control, and fall-off-the-end; test_transition 261 pass)
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

## Acceptance Criteria

- [x] **AC1** Given a function returning a value on one path and an explicit `return None` on another, when `_has_none_path` reads it, then it reports a None path - `return None` is the form this codebase writes at a refusal, and it was rated Medium where the bare `return` rated High.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k an_explicit_return_none_is_a_none_path
- [x] **AC2** Given a function returning a value on BOTH arms of an if/else, when the same reader runs, then it reports no None path - widening the recognition must not invent one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k both_arms_valued_is_not_a_none_path

## Proposed Fix

Count an explicit `return None` - a `Return` whose value is a `Constant` of None - as a None path alongside the bare form. Add both to the `HONEST_HIGH` fixtures, so the pair cannot drift apart again.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in transition.py `_has_none_path`, delete the ast.Constant arm so only a bare return counts | Given a function returning a value on one path and an explicit `return None` on another, when `_has_none_path` reads it, then it reports a None path - `return None` is the form this codebase writes at a refusal, and it was rated Medium where the bare `return` rated High. |
| AC2 | in transition.py `_has_none_path`, return True unconditionally so a both-arms-valued function invents a None path | Given a function returning a value on BOTH arms of an if/else, when the same reader runs, then it reports no None path - widening the recognition must not invent one. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
