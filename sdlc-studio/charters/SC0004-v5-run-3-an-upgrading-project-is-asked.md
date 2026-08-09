# SC0004: v5 run 3: an upgrading project is asked about its own history rather than silently forgiven

> **Status:** Queued
> **Queue rank:** 3
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Appetite:** 480min/8units
> **Scope query:** --crs Proposed

## Sprint Goal

A project adopting v5 is shown the grandfathering it would receive, decides it, and carries a durable record of what was forgiven and what would re-arm it.

## Scope rule

CR0497 once refined, plus BG0497, BG0488, BG0522 and BG0528.

Measured on a v4-era fixture, 2026-08-09: `migrate --apply` runs and reports honestly, and
`gate.py` immediately after it returns FAIL on conformance, reconcile and index-derived.
`conformance.adopt_after` defaults to null, documented as judging every story, so a project's
entire pre-v5 history is held to a gate that did not exist when it was written. The remedy
exists and is correct; nothing offers it, records it, or reports it afterwards.

This run must land AFTER run 1, because run 1's rehearsal fixture is the thing that proves the
grandfathering worked - a migrate that ends in a green gate is the criterion, and asserting it
any other way asserts the mechanism rather than the outcome.

BG0528 needs grooming before it can be planned: it carries no acceptance criteria, only
tool-derived prose restating its own summary. Price the grooming on top of its points rather
than inside them.

## Seat review

_Not yet reviewed._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
