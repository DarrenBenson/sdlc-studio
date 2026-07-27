# BG0333: Product seat calibrates against an End goal Maya's card does not contain

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/personas/seats/product.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The Product seat's worked example quotes the Primary persona's End goal as 'ship my product without drowning in process I have to police myself', but Maya's card lists four End Goals and none is that sentence - the seat whose Craft Goal demands tracing to a real End goal, not a guess, demonstrates its review behaviour by tracing to a fabricated one, and validate.py seats passes it because it checks only stamps and structure.

## Steps to Reproduce

Evidence (Scenario section, lines 87-93): product.md:88-89 quotes the fabricated goal; maya-okafor-founder-engineer.md:25-28 lists the actual four End Goals (nearest match is an Experience goal); product.md:23 states the trace-to-real-goal rule.

## Proposed Fix

Correct the Scenario to quote one of Maya's actual End Goals verbatim from her card (or add the quoted sentence to her card if it is the intended goal).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
