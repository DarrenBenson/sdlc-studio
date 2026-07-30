# BG0333: Product seat calibrates against an End goal Maya's card does not contain

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/personas/seats/product.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

The Product seat's worked example quotes the Primary persona's End goal as 'ship my product without drowning in process I have to police myself', but Maya's card lists four End Goals and none is that sentence - the seat whose Craft Goal demands tracing to a real End goal, not a guess, demonstrates its review behaviour by tracing to a fabricated one, and validate.py seats passes it because it checks only stamps and structure.

## Steps to Reproduce

Evidence (Scenario section, lines 87-93): product.md:88-89 quotes the fabricated goal; maya-okafor-founder-engineer.md:25-28 lists the actual four End Goals (nearest match is an Experience goal); product.md:23 states the trace-to-real-goal rule.

## Proposed Fix

Correct the Scenario to quote one of Maya's actual End Goals verbatim from her card (or add the quoted sentence to her card if it is the intended goal).

## Acceptance Criteria

### AC1: every End goal a seat quotes appears on a persona card

- **Given** each seat card's worked example
- **When** the guard runs
- **Then** the quotation is found verbatim on a persona card, so a seat demanding a trace to a real goal cannot demonstrate the behaviour by tracing to a guess
- **Verify:** pytest tools/tests/test_seat_examples_quote_real_goals.py::SeatExampleGoalsTests::test_every_quoted_end_goal_appears_on_a_persona_card
- **Verified:** yes (2026-07-29)

### AC2: the guard cannot pass by having stopped matching

- **Given** the seat corpus
- **When** the guard runs
- **Then** at least one quoted goal is found and the persona corpus is non-trivial, so an inert scan cannot read as a clean one
- **Verify:** pytest tools/tests/test_seat_examples_quote_real_goals.py::SeatExampleGoalsTests::test_the_persona_corpus_is_readable
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
