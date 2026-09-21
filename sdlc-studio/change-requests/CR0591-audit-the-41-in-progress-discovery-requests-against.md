# CR-0591: audit the 41 In-Progress discovery requests against HEAD and close what is dead

> **Status:** Complete
> **Decomposed-into:** EP0257
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** sdlc-studio/change-requests, sdlc-studio/rfcs, .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py
> **Date:** 2026-09-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

D0216: 41 of the 68 open discovery items are In Progress with children still open, sitting above 26 requests awaiting refine. Several carry five to twelve unresolved children - CR0555 has 12, CR0499 seven, CR0535 and CR0551 six each.

WIP at that depth is not work in flight, it is work abandoned at different depths, and the backlog count is lying about how much of it is real. `status` reports Discovery=67 and a planner reads that as 67 live options; most of it is neither live nor an option. Refining more requests on top of it makes the lie bigger, which is why D0216 puts the audit first.

The audit is a sweep, not a build: each of the 41 is re-read against HEAD, and each is ruled into one of four outcomes - already delivered by other work (close it), overtaken by events (retire it with the reason), still wanted and correctly In Progress (leave it, with its open children named), or still wanted but never actually started (return it to Proposed so it rejoins the refine queue honestly). The ruling matters more than the count: this project's own bar is the RULING, not the number (D0186), and a sweep that just closes things to make a figure fall is the failure mode that bar exists to prevent.

## Impact

Anyone planning a run, and every figure derived from the discovery backlog. Today a planner choosing work cannot tell a request with one criterion left from one abandoned eight months ago, so the choice is made on title and recency rather than on state. The report of record carries backlog figures too, so the distortion reaches the page an operator signs.

The cost is a run's worth of reading with no feature at the end of it, which is exactly why it keeps not happening. The risk to manage is the opposite of the obvious one: a sweep measured by how many items it closes will close things that should have stayed open, so the outcome to hold it to is that every one of the 41 carries a dated ruling afterwards - including the ones ruled still-wanted.

## How this is run, and what else it takes

**D0222:** executed as PARALLEL agents over file-disjoint groups, not as one serial pass. Reading an artefact against HEAD and ruling it is independent work, so it parallelises almost perfectly, and the precedent is this project's own audit-backlog sprint. The orchestrating session keeps the rulings and the close: the agents produce EVIDENCE, not verdicts of record. RUN-01M2SPNS priced at 116,439 tokens per point, and this run buys rulings rather than code, so a serial pass would be the most expensive way to the least shippable output.

**Scope also takes five delivery-side items** that are the same judgement: US0677, US0684, US0817 and US0840 sit at the 8-point ceiling where estimation reliability falls off, and US0793/US0794 share four files and 50% of their wording. Settling them here leaves the delivery backlog honest when the build run plans from it.

**Not in scope:** feature work. D0221 defines this run as ruling-only and that line is what lets one reviewer judge the whole of it - BG0719 was deliberately kept out and sent to the build run (D0223) for exactly that reason. The ONE exception is this request's own AC4 guard, which is not a feature but the thing that stops the state this sweep clears from silently rebuilding; without it the audit is a one-off tidy. An earlier draft of this note said `any code change`, which contradicted AC4 - the criteria are the authority, not the note.

## Acceptance Criteria

- [ ] Every one of the 41 In-Progress discovery requests carries a dated ruling afterwards, naming which of the four outcomes it took and why. A request left In Progress is a RULING that it is still wanted and correctly started, not the absence of a decision - the sweep is judged on having ruled all 41, never on how many it closed.
- [ ] A request whose work another unit has already delivered is closed with that unit named, so the claim is checkable rather than asserted. Where the premise is that the work is done, it is verified by execution against HEAD, not by reading the title - this project has already shipped a finding whose premise had stopped being true.
- [ ] A request still wanted but never actually started returns to Proposed and rejoins the refine queue, so `status` counts it where it belongs. After the sweep, the In Progress count and the awaiting-refine count each describe what their name says.
- [ ] The tooling can tell these apart afterwards without a human re-reading them: a check reports a discovery request that is In Progress with no unresolved child and no dated ruling, so the state this sweep clears cannot silently rebuild. Without it the audit is a one-off tidy and the count drifts back.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Raised |
