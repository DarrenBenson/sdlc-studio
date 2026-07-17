# US0205: TRD ADR-008 ULID: state the real 6+2-char guarantee and cross-machine residual risk; drop the collision-free absolute

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md
> **Epic:** EP0071
> **Points:** 2

## User Story

**As an** engineer relying on the TRD as spec truth
**I want** ADR-008 and §6/§8 to state the ULID scheme's actual, probabilistic guarantee
**So that** nobody trusts a "collision-free" absolute the shipped code does not deliver

## Acceptance Criteria

### AC1: §6, ADR-008 and §8 state the actual guarantee: 6+2 chars, ~1/1024 per pair inside a ~17-minute

- **Given** §6/§8 described ULID identity without the char layout or collision odds, and ADR-008 named no backstop mechanism
- **When** §6, ADR-008 and §8 are rewritten to `short_ulid`'s shipped guarantee (6 timestamp + 2 entropy chars, ~17-minute bucket, glob-retry backstop)
- **Then** §6, ADR-008 and §8 state the actual guarantee: 6+2 chars, ~1/1024 per pair inside a ~17-minute window, glob-retry as the single-writer local backstop
- **Verify:** grep "1 in 1024" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

### AC2: ADR-008 gains a residual-risk paragraph covering the cross-machine case and naming `next_id.py`'s

- **Given** ADR-008 listed consequences but never the residual cross-machine collision the glob-retry cannot see
- **When** a Residual risk paragraph is added, naming `next_id.py collisions` as the merge-time guard
- **Then** ADR-008 gains a residual-risk paragraph covering the cross-machine case and naming `next_id.py`'s collisions detector as the merge-time guard
- **Verify:** grep "collisions. is the guard" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

### AC3: The ADR title no longer claims 'collision-free' unconditionally

- **Given** the ADR-008 title asserted "Collision-free ULID artefact ids" as an absolute
- **When** the title is changed to "Collision-resistant short-ULID artefact ids"
- **Then** The ADR title no longer claims 'collision-free' unconditionally
- **Verify:** grep "Collision-resistant short-ULID artefact ids" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
