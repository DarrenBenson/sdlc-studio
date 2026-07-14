# CR-0271: RFC0038 U6: two backlogs - RFCs and CRs are requests, gated so they cannot reach Done without becoming work

> **Status:** Proposed
> **Priority:** P1
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/status.py
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

RFCs and CRs are a REQUEST BACKLOG. Neither is work; both need refinement work to become PRODUCT BACKLOG (epics, stories, bugs). A request enters the product backlog only by being decomposed. The chain is RFC -> CRs -> epics/stories -> delivered, and this project does the first step and jumps the rails: every CR goes straight to a subagent whole, and the CR-to-story step has never once happened - while sprint plan prints "decompose into stories" on every run and BG0132 says only a story carries executable acceptance criteria. So every CR ever marked Complete was Done by assertion, gated on prose.

Doctrine printed and ignored is decoration (LL0027). So, gates:

G1. sprint plan REFUSES an RFC or CR as a sprint unit - a request full stop, not merely an undecomposed one. The product backlog is stories and bugs. This lands hard: --crs Proposed has been our primary command, so we have been sprinting the intake queue for the life of the project.

G2. A request cannot reach a terminal status by ASSERTION. Its status is DERIVED from its children: a CR is Complete when every story and epic it produced is Done; an RFC is Delivered when every CR it produced is Complete. A request with no children cannot be terminal - it produced nothing, so it delivered nothing (LL0034: derive what you can; a status that can be true in the record and false in reality must be computed, not stamped).

G3. Traceability is bidirectional and checkable: the decomposition command writes the parent link on both sides, and reconcile verifies every link resolves both ways.

G4. status reports TWO backlogs. An undecomposed request is intake, not work in progress; counting it as backlog overstates what is ready to deliver (today: 16 non-terminal, of which 8 are CRs that are not work yet).

G5. reconcile reports a non-terminal request with no children as UNDECOMPOSED - a countable drift kind - so the intake queue cannot become a graveyard of requests nobody turned into work.

## Impact

The whole delivery workflow, and it closes the oldest gap in the project: only stories are gated on executable ACs, and we have never produced one from a CR. Every CR marked Complete to date was Done by assertion.

**Points:** 8

## Acceptance Criteria

- [ ] sprint plan refuses an RFC or CR as a sprint unit and names the command that decomposes it; the product backlog it plans is stories and bugs.
- [ ] A request status is derived from its children: a CR is Complete only when every story and epic it produced is Done, an RFC Delivered only when every CR is Complete. A childless request cannot be terminal.
- [ ] Parent links are written on both sides by the decomposition command, and reconcile verifies every link resolves in both directions.
- [ ] status reports the request backlog and the product backlog separately.
- [ ] reconcile reports a non-terminal request with no children as UNDECOMPOSED, a countable drift kind.
- [ ] Validated against the gates they defend (LL0010): a childless CR must FAIL transition to Complete and must be REFUSED by plan; if neither can fail, they are not gates.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
