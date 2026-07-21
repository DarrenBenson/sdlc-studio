# BG0233: refine's heading truncation and epic T-shirt derivation are both unpinned: two mutants survive

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional (both named survivors re-applied by hand and shown to change the file: the invert-guard at refine.py:63 and the no-op-mapper at refine.py:38 each SURVIVED the pre-fix `test_refine.py` and each is now KILLED - 6 failures and 2 failures respectively, `python3 -B` over a purged `__pycache__`. Boundary cases pinned at the limit, one over it, a cut that exposes punctuation, and a raw form over the limit whose stripped form fits; `_tshirt_for` pinned at every band edge and once through the real epic-creation path)
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The close-time mutation run over RUN-01KY03GS survived two mutants in refine.py, both real coverage gaps rather than equivalent mutants. At line 63 an invert-guard on the heading length test survives: inverting it truncates short headings and leaves long ones whole, and nothing notices - `test_refine.py`, added this sprint for BG0221, covers the epic AC merge but never the heading path. At line 38 a no-op-mapper on `_tshirt_for` survives, so the T-shirt Size an epic is born with is derived by code no test references at all; grep finds neither `_tshirt_for` nor `size_for_points` anywhere under tests. The size band feeds sprint planning, where a wrong Size is the kind of error that reads as a plausible number rather than an obvious fault. Neither survivor is manufactured by the narrow test command: the run named its selection and warned only about sprint, retro and validate targets.

## Steps to Reproduce

Run mutation.py run --files .claude/skills/sdlc-studio/scripts/refine.py with a test command covering `test_refine.py.` Mutants at line 63 (invert-guard) and line 38 (no-op-mapper) both SURVIVE. Confirm directly: grep -rn "`heading_title`\|limit" on `test_refine.py` returns nothing, and grep -rln "`_tshirt_for`\|`size_for_points`" over the tests directory returns nothing.

## Proposed Fix

Pin the heading path at its boundary - a criterion under the limit is unchanged, one over it truncates at a word boundary without trailing punctuation, and one whose stripped form fits keeps its last word (the behaviour the code comment claims and nothing checks). Pin `_tshirt_for` at each band edge rather than mid-band, since a no-op or an off-by-one band only shows at the edges. Mutation-check both, because a heading test asserting only "some string came back" passes against the inverted guard.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
