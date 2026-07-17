# US0202: Add the shipped Done epics EP0033-EP0047 to the PRD feature tables and populate the -- Epic columns

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md
> **Epic:** EP0071
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: Section 3 tables carry rows for the features shipped by EP0033-EP0047, each marked [Unreleased]

- **Given** the §3 tables listed the released v4.1.0 features but carried no rows for the epics shipped on `main` after the tag (EP0033-EP0047)
- **When** a `Complete **[Unreleased]**` row is added per distinct shipped feature, each naming its owning epic id
- **Then** Section 3 tables carry rows for the features shipped by EP0033-EP0047, each marked [Unreleased] with its owning epic id
- **Verify:** grep "EP0033, EP0034" sdlc-studio/prd.md
- **Verified:** yes (2026-07-17)

### AC2: Existing [Unreleased] rows have their Epic column populated (no '--' against the preamble's mapping

- **Given** five [Unreleased] rows (breakdown gate, sprint capacity, sizing and velocity loop, learning loop, lessons ranking) showed Epic '--', contradicting the preamble's mapping claim
- **When** each Epic cell is filled with its delivering unit: EP0010 for the learning loop and lessons ranking, and the governing RFC/CR for the sizing-family rows built before the epic decomposition
- **Then** Existing [Unreleased] rows have their Epic column populated (no '--' against the preamble's mapping claim)
- **Verify:** grep "scripts/lessons.py . EP0010" sdlc-studio/prd.md
- **Verified:** yes (2026-07-17)

### AC3: The coverage note's parenthetical list of unreleased workstreams matches what the tables actually

- **Given** the Coverage note's parenthetical listed only four unreleased workstreams while the tables now cover many more
- **When** the parenthetical is expanded to name the added workstreams (two-backlog, refine and migrate, Issue and triage, sprint close-down)
- **Then** The coverage note's parenthetical list of unreleased workstreams matches what the tables actually cover
- **Verify:** grep "the two-backlog workflow, the refine" sdlc-studio/prd.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
