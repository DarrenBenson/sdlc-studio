# RFC-0045: Micro-requests and the one-story epic: should a small CR decompose to a story without a container epic?

> **Status:** Draft
> **Decomposed-into:** CR0322
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/reconcile.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; dogfood retro 2026-07-16

## Summary

The two-backlog gate correctly blocked completing CR0283/0292/0297 undecomposed (2026-07-16), and the uniform remedy minted one epic per CR - three epics of exactly one story each (EP0049-EP0051, 2-3 points apiece) for ~7 points of delivered work. The epic index gains three permanent one-row containers per small-batch session; at the current filing rate (25 audit CRs today, mostly S), full-discipline delivery would mint dozens more. The question is whether the container layer should be elastic for S-sized requests, without weakening the gate's core rule that a request delivers nothing until a sized delivery unit exists.

## Design Options

- **Status quo: every request gets an epic, uniformity beats index growth; archive.py absorbs the one-row containers**
- **Direct story children: allow 'Parent: CRxxxx' on a story; gates/reconcile/completion cascade treat a story child as satisfying decomposition for S-sized requests**
- **Shared batch epic: refine gains a --into EPxxxx mode so one session's small deliveries share a container epic (e.g. 'Persona layer made load-bearing' instead of three singletons)**

## Recommendation

Option 3 preserves every existing invariant (epics still the only story parents, cascade unchanged) and maps to how small CRs actually get delivered - in themed batches; option 2 is cleaner long-term but touches every gate that walks the hierarchy

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Decomposition shape for small requests | Resolved: batch epic (refine --into EPxxxx); direct story-children rejected for blast radius; status quo rejected for index accretion (operator, 2026-07-17) -> CR0322 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Filed |
| 2026-07-17 | Darren Benson (operator) / Claude Fable 5 | Decisions resolved at the RFC triage session; workstream CRs spawned (Accepted derives when they resolve) |
