# BG1426: transition.py refuses an RFC at Accepted until every change request it spawned is resolved, though the RFC status flow says Accepted means its decisions are made

> **Status:** Superseded
> **Superseded by:** BG1020
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_rfc_accepted_when_decided.py, changelog.d/BGXXXX.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** Backlog triage 2026-11-14 (D0473, D0474): RFC0062, RFC0063 and RFC0064 forced to Accepted on the operator's ruling
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (backlog triage orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-14T20:53:42Z

## Summary

`_request_terminal_gate` in transition.py treats Accepted as an RFC's delivered terminal, derived from its children (G2), so an RFC whose open decisions are all resolved cannot be Accepted while its workstream change requests are open. reference-outputs.md#rfc-status-flow says the opposite: In Review to Accepted needs every Open Decision resolved and the Decision recorded, the CRs are then spawned, and Accepted is not terminal. D0388 (7) ruled the same. On 2026-11-14 the operator ruled RFC0062, RFC0063 and RFC0064 Accepted (D0474), and the transition refused all three, naming 16 open child CRs, so the ruling went through only with --force.

## Steps to Reproduce

Take an RFC whose Open Decisions table is all Resolved and whose Decomposed-into names a Proposed CR, then run transition.py set --id <RFC> --status Accepted: it is refused as DERIVED from its children.

## Proposed Fix

Judge an RFC's Accepted by its decisions, as the status flow page says: allow it when every Open Decision is Resolved and the Decision section is filled, and keep the children-derived rule for a CR's Complete and an Issue's Resolved.

## Acceptance Criteria

- [ ] **AC1** Given an RFC whose Open Decisions are all Resolved and whose spawned CRs are still Proposed, when it is set to Accepted, then the transition succeeds without --force. Fails on: a refusal naming the open children.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rfc_accepted_when_decided.py::RfcAcceptedWhenDecidedTests::test_decided_rfc_with_open_children_is_accepted
- [ ] **AC2** Given an RFC with an unresolved Open Decision, when it is set to Accepted, then the transition is refused and names the open decision. Fails on: an Accepted RFC with an open decision.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rfc_accepted_when_decided.py::RfcAcceptedWhenDecidedTests::test_open_decision_refuses_accepted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | Claude Opus 5.5 (backlog triage orchestrator) | Filed |
| 2026-11-14 | Claude Opus 5.5 (backlog triage, D0473) | Superseded by BG1020 at the backlog triage, as a duplicate: filed at the triage before the filer named BG1020, the same refusal; its open-decision criterion and the 2026-11-14 evidence, RFC0062, RFC0063 and RFC0064 forced to Accepted on the operator's ruling (D0474), are carried to BG1020 |
