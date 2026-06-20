# RFC-0011: RFC0006 reopens the default-autonomy decision RFC0001 declares settled, with no cross-reference

> **Status:** Withdrawn
> **Priority:** Medium
> **Author:** Project Audit
> **Date:** 2026-06-20
> **Spans:** sdlc-studio workspace
> **Related:** RV0003 (project audit)
> **Supersedes / Superseded by:** --

## Summary

RFC0001 declares the default autonomy ceiling already settled and bakes it as a Goal, while RFC0006 (same day) proposes phase-gating that would change that same default; neither lists the other in Related and neither acknowledges the conflict.

## Context & Problem

RFC0001:47-49 states 'the operator has already settled the central design choice ... stop once after triage for approval, then run autonomously' and Goal :59 keeps that ceiling as default. RFC0006:1/13/23 ('Reconsider the default autonomous execution model') proposes optional --require-approval phase gates contrary to that default. RFC0006's Related names only 'RV0002', RFC0001's Related does not mention RFC0006. Two open RFCs own the same decision with no supersede/conflicts link.

## Proposed Direction

Add a reciprocal 'Related / conflicts-with' link between RFC0001 and RFC0006 and fold RFC0006's phase-gating question into RFC0001 D1 (or explicitly mark RFC0006 as challenging RFC0001's settled premise). Resolve the default-autonomy model in one place.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | How to resolve this finding | see Proposed Direction | Operator | spike or operator call | Open |

## Evidence

RFC0001-autonomous-delivery-loop.md:47-49 'operator has already settled the central design choice' vs RFC0006:8 'Related: RV0002 (audit run)' (no RFC0001 link) and RFC0006 proposing phase gates

## Impact

An operator could accept RFC0001's default-autonomy design while RFC0006 silently argues the default should be gated, producing contradictory direction for the same epic-implement behaviour; the decision graph is broken so resolving one RFC does not flag the other.

## Decision

**Outcome:** TBD
**Rationale:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: design-rfc) |
| 2026-06-20 | Autosprint (backlog-closeout) | Withdrawn - moot once RFC0006 is withdrawn; the autonomy decision stands with RFC0001. |
