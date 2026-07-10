# CR-0221: Cooper usage pass: personas that arbitrate, not decorate

> **Status:** In Progress
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

RFC0028, slimmed per consult. One-Primary ships as a WARNING (error only when two Primaries declare the same optional Interface: field - Sam); the Serves: convention ships in PRD/story templates with the coverage checker DORMANT until first use or config opt-in, and named personas must resolve to files (Sam blocking + Lena deferral both satisfied); arbitration is one instruction line in consult ('does this serve the Primary's End Goals? if not, cut it') not a ceremony step; the anti-sycophancy quota lands in consult templates (each seat raises >=1 objection or states why none) and is eval-graded; anti-fluff splits into the mechanical denylist (lives in the seats check) plus named judgement in persona review; Life goals generate only on a strategy-tier signal.

## Acceptance Criteria

- [ ] validate.py warns on two Primary design personas (error only when both declare the same Interface:); optional Interface: field documented in the persona Quick Reference
- [ ] Serves: convention in PRD/story templates; the coverage check activates only when the project carries >=1 Serves: tag (or config opt-in) and verifies named personas resolve to persona files; emits a coverage table, advisory
- [ ] Consult templates carry the Primary-arbitration line and the >=1-objection-per-seat quota; persona review names the influences-no-decision judgement; reference-persona.md documents the scenario taxonomy (validation scenarios test robustness, never drive layout)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
