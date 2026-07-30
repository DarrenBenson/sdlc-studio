# BG0448: eight bugs stand at the terminal status Fixed carrying no Verify line and no ticked criterion, and a ninth is Fixed while two of its own ACs are titled NOT YET FIXED

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, sdlc-studio/bugs/BG0402-close-goal-judgement-compares-seat-names-against-a.md, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** amigo seat review of RUN-01KYPZ1G (independent, isolated worktrees); agent; v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

Nine bugs of the RUN-01KYPZ1G batch are at `Fixed`, which `lib/sdlc_md.py` treats as terminal. Eight of them - BG0403, BG0404, BG0405, BG0407, BG0411, BG0412, BG0414, BG0416 - carry ZERO `Verify:` lines and have every acceptance criterion still unticked: 31 unticked criteria across eight terminal artefacts, with no oracle of any kind. `validate.py check` reports errors=0 over them, so nothing in the toolchain objects. The ninth, BG0402, is worse in a different direction: it is at `Fixed` while its own AC3 and AC4 are TITLED `- NOT YET FIXED`, their Verify lines read `manual - open, not yet delivered`, and its Revision History says in terms 'this bug stays open for them'. The artefact contradicts its own status in its own text.

## Steps to Reproduce

Measured at d7a1ad8f, 2026-07-30, over the nine bugs in the batch:

```text
BG0403 verify=0 unticked=4 ticked=0
BG0404 verify=0 unticked=3 ticked=0
BG0405 verify=0 unticked=3 ticked=0
BG0407 verify=0 unticked=3 ticked=0
BG0411 verify=0 unticked=4 ticked=0
BG0412 verify=0 unticked=5 ticked=0
BG0414 verify=0 unticked=4 ticked=0
BG0416 verify=0 unticked=5 ticked=0
BG0402 verify=4 unticked=0 ticked=0
```

BG0402 scores `ac=4 pass=2 fail=0 manual=2` under `verify_ac.py run` - green, because `conformance.py` accepts `manual` alongside `yes`. So half the bug has no oracle and the toolchain reports it satisfied.

Independently reported by two of the three amigo seats (product and QA) on this batch, and re-measured by the author before filing. The QA seat spot-checked BG0404 by execution and confirmed its fix IS real - `close_cost(root, None)` now returns `NOT ATTRIBUTABLE` rather than a whole-ledger sum - which sharpens rather than softens the finding: the work was done and the record does not say so.

## Proposed Fix

Two separable halves.

BG0402 first, because it is a false terminal status rather than a thin one: either update its criteria to describe only what shipped and move the two undelivered halves to a new bug, or return it to Open. It must not stand at Fixed while declaring itself unfinished - that is a status the artefact itself contradicts, and it is the one shape no reader can be expected to catch.

Then the eight: a bug reaching a terminal status should be held to an oracle the way a story is. `transition -> Done` is gated on executable ACs for stories; `Fixed` has no equivalent gate, which is why eight terminal artefacts carry 31 unticked boxes and pass validation. Decide during refine whether the answer is to gate `Fixed` on the same criteria machinery or to declare that bugs are exempt and say so explicitly - what cannot stand is the current state, where the criteria exist, are unticked, and nothing reads them. Each of the eight also asserts in prose that its fix was 'verified by applying its mutant, bytecode purged, python3 -B'; there is no verifier, no ticked criterion and no mutation record on disk for any of them, so that claim is UNVERIFIABLE across the whole set.

## Acceptance Criteria

- [ ] The behaviour described is corrected: Nine bugs of the RUN-01KYPZ1G batch are at `Fixed`, which `lib/sdlc_md.py` treats as terminal.
- [ ] Following the recorded steps no longer reproduces the defect: Measured at d7a1ad8f, 2026-07-30, over the nine bugs in the batch: BG0402 scores `ac=4 pass=2 fail=0 manual=2` under `verify_ac.py run` - green, because...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | amigo seat review of RUN-01KYPZ1G (independent, isolated worktrees) | Filed |
