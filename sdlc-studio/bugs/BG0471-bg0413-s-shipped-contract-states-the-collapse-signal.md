# BG0471: BG0413's shipped contract states the collapse signal exits 2 while the code returns 3

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional (both prose sites corrected and verified against the code: `scope` returns 3, asserted by the test whose docstring was stale. The unreachable line's deadness proved exhaustively over peak in {1,10,100,1000,5645} x every count - zero cases where collapsed and ok are both true)
> **Affects:** changelog.d/BG0413.md, tools/gate_timing.py, tools/tests/test_gate_timing.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Found by an independent seat briefed from the SHIPPED `critic.py brief`, unit-scoped to the unit's own `Affects` against base `edb9fdf0`, with findings classified by execution. Repaired in the same session; recorded here because the repair is post-close work on a unit already at Fixed, and must be a filed unit rather than an ad-hoc edit.

The round-3 repair moved the collapse exit code from 2 to 3 - deliberately, because python itself exits 2 for an argparse error and for a missing script file - and the prose describing it was not moved with it. `changelog.d/BG0413.md` still stated 'exits 2', and so did the docstring of `test_a_collapsed_run_exits_distinctly_from_a_declined_recording`, which is the very test asserting `rc == 3`. `changelog.d` fragments assemble into `CHANGELOG.md` at release, so the stale claim ships as the contract and a consumer wiring `[ $rc -eq 2 ]` off it reintroduces the collision a prior review round rejected this unit for. A second, non-blocking finding: `ok = False` inside the collapse branch is provably unreachable, since `COLLAPSE_FLOOR` 0.5 sits below `SCOPE_FLOOR` 0.8 so every collapsed count has already failed the floor above.

## Steps to Reproduce

1. grep 'exits 2' changelog.d/BG0413.md -> present.
2. grep 'return 3' tools/`gate_timing.py` -> present.
3. Seed a peak of 5645 and run `gate_timing.py` scope --suite total --tests 510 -> exit 3.
4. The docstring on the test pinning rc == 3 also read 'exit 2 blocks'.

## Proposed Fix

Correct both prose sites to 3 and state why three rather than two. Delete the unreachable line, documenting the floor ordering that makes it dead.

## Acceptance Criteria

- [x] The behaviour described is corrected: Found by an independent seat briefed from the SHIPPED `critic.py brief`, unit-scoped to the unit's own `Affects` against base `edb9fdf0`, with findings...
- [x] The proposed fix lands, pinned by a test: Correct both prose sites to 3 and state why three rather than two.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Filed |
