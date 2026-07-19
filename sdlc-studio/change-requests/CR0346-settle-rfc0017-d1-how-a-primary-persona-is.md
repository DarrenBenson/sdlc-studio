# CR-0346: settle RFC0017 D1: how a Primary persona is selected when candidates compete

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/rfcs/RFC0017-cooper-goal-directed-persona-model-the-canonical-persona.md, .claude/skills/sdlc-studio/reference-persona.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

RFC0017 is Accepted but its D1 decision - how to choose the Primary persona when several candidates compete - was never recorded. Its two options were Cooper's goal-coverage method or an operator pick. Checked and found nothing: the RFC's own Decision section is silent on D1 (its 'decided in the deep-dive' note covers cast, goal tiers, well-formedness and the no-identity-compiler stance only), reference-persona.md end to end, `persona_gen.py` has no Primary-selection logic at all, and CHANGELOG and git log searches for the concept return nothing. The nearest shipped rule is one-Primary-per-interface, which CONSTRAINS the outcome but is not a selection method and is nowhere tied to D1. Surfaced by the widened decision reader: the row sat in a 7-column table that the first version of the accept gate could not parse, so it passed silently while eight sibling RFCs were being closed.

## Impact

Anyone generating a persona cast where two candidates both look Primary has no documented method to choose, and the accept gate now reports RFC0017 on every run until the row is settled or the override is cleared.

## Acceptance Criteria

- [ ] the D1 row records the selection method actually intended, or the option is chosen and documented in reference-persona.md
- [ ] the Decision-Override recorded on RFC0017 is removed once D1 is closed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
