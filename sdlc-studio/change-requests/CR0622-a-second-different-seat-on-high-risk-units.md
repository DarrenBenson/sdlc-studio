# CR-0622: A second, different seat on high-risk units - or a different seat on round 2

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** homelab consuming project, 2026-10-07/08 (RUN-01M4B5HP drift-check sprint, RUN-01M4BZZ9 HA sprint), operator-approved after a session retrospective
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:06:00Z

## Summary

In the homelab the same engineering seat reviewed every round of every unit. Round 2 re-checked round 1's findings well, but nothing brought a different lens: US0188's blocking B2 (host cron content pushed verbatim to Kuma) was a security/SRE-shaped defect that the round-1 reviewer found only because it went looking end to end. Proposal: units flagged high-risk (`affects_production_runtime`: true, a secrets/alerting path, or points >= 8) get a second seat from a different role in the same round - or round 2 is reviewed by a different seat than round 1 - recorded on the critic ledger as distinct seats (BG0539's round-vs-seat distinction already exists). Cost is one more review on a minority of units.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Triage

- Confirmed: every round of every unit can be briefed for one seat. Corrected on 2026-10-09 by the G10 breakdown (D0355): recording a second seat DOES need a new ledger shape. The ledger numbers every verdict on a unit as one sequence of rounds, so an engineering APPROVE then an SRE REJECT records the REJECT as round 2 and carries the unit at the cap, and the opposite order is refused. D0341 and US0872 chose one reviewer per unit for this reason; this CR reverses them for high-risk units.
- Priority Medium stands; Size M. Related: CR-0620 (choose seats by what a change touches); refine together.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Raised |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: behaviour confirmed; Affects made repository paths; Size M; relations recorded |
| 2026-10-09 | Claude Opus 5.5 (triage) | Triage corrected: a second seat needs per-seat rounds on the ledger (found by the G10 breakdown) |
