# US0209: TRD section 6 data architecture: add the issue type, story Blocked, the inbox triage lane and a two-backlog subsection

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md
> **Epic:** EP0071
> **Points:** 5

## User Story

**As an** engineer reading §6 to learn the data model
**I want** the `issue` type, story `Blocked`, the inbox triage lane and the two-backlog model documented
**So that** §6 matches `lib/sdlc_md.py` instead of describing a v3-era-obsolete registry

## Acceptance Criteria

### AC1: §6's type registry includes issue with its directory, prefix and status vocabulary

- **Given** the §6 registry table omitted `issue`, though `ARTIFACT_TYPES` ships it (`sdlc-studio/issues`, `IS`)
- **When** an `issue` row is added to the registry table and its own status row to the vocabulary table
- **Then** §6's type registry includes issue with its directory, prefix and status vocabulary
- **Verify:** grep "issue .+sdlc-studio/issues.+IS" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

### AC2: The story status vocabulary includes Blocked

- **Given** the §6 story vocabulary row lacked `Blocked`, though `STATUS_VOCAB["story"]` includes it
- **When** `Blocked` is inserted into the story row (after `Review`) and noted as re-activatable, not terminal
- **Then** The story status vocabulary includes Blocked
- **Verify:** grep "Review, Blocked, Done" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

### AC3: The inbox triage lane on findings is documented (types, statuses, triage targets)

- **Given** §6 never described the v3 `inbox` lane on findings (`bug`/`cr`/`rfc`) nor its `TRIAGE_TARGET` map
- **When** a subsection documents the lane: types, the prepended `inbox` status, and the per-type triage targets
- **Then** The inbox triage lane on findings is documented (types, statuses, triage targets)
- **Verify:** grep "Inbox triage lane .findings, schema v3" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

### AC4: The two-backlog model gets a §6 subsection: request/discovery/product type sets

- **Given** §6 documented no two-backlog model, though `DISCOVERY_TYPES`/`REQUEST_TYPES`/`PRODUCT_TYPES` and the G1/G2 gates ship
- **When** a "Two backlogs" subsection is added: the three type sets, `two_backlog.enforce` with G1/G2, and the Parent:/Decomposed-into: link primitives
- **Then** The two-backlog model gets a §6 subsection: request/discovery/product type sets, `two_backlog.enforce` and its G1/G2 gates, Parent:/Decomposed-into: primitives and their reconciliation
- **Verify:** grep "Two backlogs .dual-track: discovery feeds delivery" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
