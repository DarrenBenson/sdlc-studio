# RFC-0010: Audit-filed RFCs (0003-0008) have boilerplate 'act vs status quo' options that never weigh the real design choices

> **Status:** Draft
> **Priority:** Medium
> **Author:** Project Audit
> **Date:** 2026-06-20
> **Spans:** sdlc-studio workspace
> **Related:** RV0003 (project audit)
> **Supersedes / Superseded by:** --

## Summary

Every RFC the audit filed carries an identical content-free single Open Decision ('Act on this finding or keep status quo') and an 'Option A act / Option B status quo' section, with several (RFC0004, RFC0008, RFC0006) burying genuine two-way design forks inside Option A and Recommendation 'TBD' - the exact 'options never weighed' defect RFC0002's own lens hunts.

## Context & Problem

RFC0003-0008 each contain the boilerplate D1 'Act on this finding or keep status quo | Option A / Option B | Operator | spike or operator call | Open' with Option B literally 'Keep the current behaviour and accept the trade-off' and Recommendation 'TBD - pending the Open Decision below'. RFC0004 nests adopt-PageRank vs scope-down-and-document inside Option A; RFC0008 nests merge vs add-router-rows; RFC0006 nests phase-gating vs fresh-context-isolation. The act/status-quo framing means the real decisions are never set out as comparable weighed options, contrasting the hand-authored RFC0001 (three weighed options, recommendation, six distinct decisions). RFC0002:120 defines this very defect as in-scope for the Design/RFC lens.

## Proposed Direction

For each RFC, split Option A into the competing approaches it already names (RFC0004: A1 PageRank symbol graph vs A2 scope-down-and-document; RFC0008: A1 full merge vs A2 keep-separate-add-router-rows; RFC0006: phase-gating vs fresh-context-isolation as separable decisions) with per-option pros/cons/effort, split D1 into one decision per real fork with owner and resolution path, and replace 'Recommendation: TBD' with a reasoned lean. Keep act/status-quo as the Decision gate, not the only design option. Reclassify any genuinely-bounded single-approach finding (RFC0003's --apply, RFC0007's template+generator) as a CR.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | How to resolve this finding | see Proposed Direction | Operator | spike or operator call | Open |

## Evidence

RFC0003-promote-reconcile-s-mechanical-apply...md:37 'D1 | Act on this finding or keep status quo | Option A / Option B | Operator | spike or operator call | Open' (identical across RFC0004-0008)

## Impact

The RFC backlog gives a false impression of design deliberation; an operator cannot triage these because no option is recommended and no real decision is framed - the audit's headline self-validation ('options never weighed is a real defect we catch') is undercut by its own filings exhibiting that defect.

## Decision

**Outcome:** TBD
**Rationale:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: design-rfc) |
