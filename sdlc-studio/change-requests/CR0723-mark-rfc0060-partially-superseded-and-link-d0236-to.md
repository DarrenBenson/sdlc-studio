# CR-0723: Mark RFC0060 partially superseded and link D0236 to the decisions that cancelled its plan

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/rfcs/RFC0060-the-dark-factory-a-sprint-that-decides-for.md, sdlc-studio/decisions.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, rfc lens, survived 3 of 3 refute votes; observed at sdlc-studio/rfcs/RFC0060-the-dark-factory-a-sprint-that-decides-for.md Header lines 3 to 4 (Status, Decomposed-into), Open Decisions table lines 197 to 205, workstream table lines 253 to 256, Decision lines 278 to 286, Revision History (last row 2026-09-21); decisions.md D0236 (line 250)
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:03Z

## Summary

RFC0060 reads Accepted and presents Option C with four workstreams as the pending design. Its Decision section says the spawned CRs are to be decided under D0236, each workstream row says CR to be decided, and its Open Decisions table cites D0230 and D0231 as the standing rulings. In fact D0253 and D0254 superseded D0230 and D0231 two days after acceptance, D0290 declined to build the derived domain record and the stop-detection machinery, and all four entries in the RFC's own Decomposed-into line are closed unbuilt: EP0258, EP0259 and CR0593 Superseded, CR0604 Rejected. The RFC has not been revised since 2026-09-21 and names none of those decisions, and D0236 still reads accepted with no supersedes link. D0253 says the persona authority, andon cord and persona independence rulings (D0232, D0233, D0235) stand, so the fitting status is the one RFC0009 already uses, Accepted (partially superseded). The reference calls an Accepted RFC the living design home, so a reader or an agent briefed from it is told that clause-checked goals and a derived domain record are accepted direction.

## Impact

Anyone planning from the RFC list or the decisions log, including an agent briefed from the decisions block, reads a cancelled plan as current direction and may refine units for workstreams the operator has already ruled out. The record of what replaced it exists only in decisions the RFC does not name.

## Acceptance Criteria

- [ ] RFC0060's Status reads Accepted (partially superseded), or another status the operator rules, and the RFC index agrees after reconcile
- [ ] RFC0060's Decision section, Open Decisions table and workstream rows name D0253, D0254 and D0290, state which rulings stand (D0232, D0233, D0235) and which were overturned, and no row still reads CR to be decided
- [ ] RFC0060's Decomposed-into entries each show their closing status, and a revision history row records the change with its date
- [ ] D0236 in sdlc-studio/decisions.md is marked superseded, or a new decision row supersedes it by id, so the log no longer shows the cancelled run plan as accepted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
