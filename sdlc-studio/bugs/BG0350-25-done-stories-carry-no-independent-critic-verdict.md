# BG0350: 25 Done stories carry no independent critic verdict, waived rather than cleared

> **Depends on:** US0560
> **Status:** Open
> **Severity:** Low
> **Points:** 5
> **Affects:** sdlc-studio/stories, sdlc-studio/reviews/critic-verdicts.md, sdlc-studio/decisions.md
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (surfaced by BG0302's threshold restore); agent; skill v5.0.0

## Summary

Restoring `conformance.adopt_after` to 82 re-armed the conformance gate and surfaced 25 Done stories (US0103-US0310) with no independent APPROVE verdict recorded. They were delivered before the two-role review gate existed. They are waived under D0074, not cleared: back-annotating an APPROVE for a review that never happened would manufacture the evidence the gate exists to demand, which is the false-evidence class this project files bugs about.

## Steps to Reproduce

1. Set `conformance.adopt_after` to 82 in sdlc-studio/.config.yaml. 2. Run conformance.py check: 25 units report missing critiqued. 3. Read D0074 for the waiver and its reasoning.

## Proposed Fix

Run an actual adversarial pass over the range and record real verdicts, then remove the waiver. It can be batched - a sprint-level review covering a tranche satisfies the gate the same way it does for new work. Removing the waiver is one-way: the gate refuses those units from then on, so do it a tranche at a time.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (surfaced by BG0302's threshold restore) | Filed |
