# BG0652: status.py hint takes 56 seconds on this corpus: its close-owed advisory runs outside any corpus sweep

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Evidence:** BG0646 product seat, delivery r1, 2026-09-07, timed on this corpus: 56 s after the fix, 123 s at e61b98fb.
> **Created:** 2026-09-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0646 put the dashboard's census and advisories inside one `corpus_cache()` sweep, so `python3 status.py` answers in under a second on this corpus. `status.py hint` (`cmd_hint)` calls the same `close_owed_advisory` with no sweep open, so the advisory's 189 `children_of` calls each walk and read all 2,340 artefacts again: 56 s measured at BG0646's delivery review (123 s at the base ref). The orientation command AGENTS.md sends a reader to after `status` still pays the cost `status` no longer pays.

## Steps to Reproduce

1. On this repository, `time python3 .claude/skills/sdlc-studio/scripts/status.py hint`.
2. Observe about 56 s against under 1 s for `status.py` alone.
3. Read status.py's `cmd_hint`: `close_owed_advisory(Path(args.root))` runs with no `sdlc_md.corpus_cache()` around it.

## Proposed Fix

Run `cmd_hint`'s advisories inside one `corpus_cache()` sweep as `cmd_pillars` does, and pin it with the BG0646 fixture: `status.py hint` as a subprocess exits inside the same bound.

## Acceptance Criteria

- [ ] **AC1** Given the fixture corpus BG0646's tests generate, when `status.py hint` runs as a SUBPROCESS over it, then it exits 0 inside 15 s and its advisories are entered inside the same sweep as its census, asserted in-process by identity as BG0646 AC2 does for the dashboard.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::HintPerformanceTests::test_the_hint_command_answers_the_corpus_shaped_fixture_inside_the_bound

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/status.py, move `close_owed_advisory` and the other advisories in `cmd_hint` back outside the `corpus_cache()` sweep (today's code): measured at plan time over `_corpus_shaped_fixture`, `status.py hint` takes 22.9 s at today's code against 0.7 s for the dashboard, so the 15 s bound dies on it with a 1.5x margin | Given the fixture corpus BG0646's tests generate, when `status.py hint` runs as a SUBPROCESS over it, then it exits 0 inside 15 s and its advisories are entered inside the same sweep as its census, asserted in-process by identity as BG0646 AC2 does for the dashboard. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Filed |
| 2026-09-07 | Claude Fable 5.1 | Goal review round 3 (all seats yes): Test Plan titles re-synced to the criteria |
| 2026-09-07 | Claude Fable 5.1 | Test Plan rows rewritten as edits led by a verb and the Mutant sentences moved out of the criteria, so `testplan derive` reads the plan as its own shape |
