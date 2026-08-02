# BG0448: eight bugs stand at the terminal status Fixed carrying no Verify line and no ticked criterion, and a ninth is Fixed while two of its own ACs are titled NOT YET FIXED

> **Status:** Fixed
> **Verification depth:** functional (the unticked-and-unverified refusal plus both satisfying oracles, each pinned separately)
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

### AC1: a bug reaching Fixed is held to an oracle

- **Given** a bug whose criteria are all unticked and carry no `Verify:` line
- **When** it is transitioned to Fixed
- **Then** it is refused, because a criterion nobody ticked and nothing runs is a sentence rather than an oracle - and the status then contradicts the artefact's own body
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TerminalOracleTests::test_an_unticked_unverified_bug_cannot_reach_fixed
- **Verified:** yes (2026-08-02)

### AC2: either oracle satisfies it

- **Given** a bug with a ticked criterion, and one with an executable `Verify:` line
- **When** each is transitioned
- **Then** both are allowed, because a tick is a human saying so and a Verify is the machine saying so - demanding both would refuse the ordinary judgement call a bug fix often is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TerminalOracleTests::test_a_ticked_criterion_satisfies_it
- **Verified:** yes (2026-08-02)

### AC3: the machine oracle is accepted on its own

- **Given** a bug whose criterion carries a `Verify:` line and no tick
- **When** it is transitioned
- **Then** it is allowed, so the gate cannot be satisfied by ticks alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TerminalOracleTests::test_an_executable_criterion_satisfies_it
- **Verified:** yes (2026-08-02)

> **Measured before shipping it.** 273 of 465 terminal bugs in this repo (58%) carry no
> oracle - neither a ticked criterion nor a `Verify:` line. That is the size of the debt the
> bug describes, and it is why the gate is on the TRANSITION rather than on the artefact:
> history keeps its status and its debt stays visible, while nothing new joins it.
>
> **Scoped to bugs.** A story reaching `Done` already passes the AC-verify gate, which
> EXECUTES its criteria - a stronger oracle than either of these. Applying this on top refused
> stories that stronger gate accepts, while talking about "this fix"; caught by 20 failing
> fixtures before it shipped.
>
> **The eight already at Fixed are not retro-blocked.** This gates the TRANSITION, so the
> existing terminal artefacts keep their status and the debt stays visible in their bodies.
> BG0402 - the one whose criteria declared it unfinished while it stood at Fixed - is scoped
> to what shipped, with the two undelivered halves carved out to BG0485.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | amigo seat review of RUN-01KYPZ1G (independent, isolated worktrees) | Filed |
