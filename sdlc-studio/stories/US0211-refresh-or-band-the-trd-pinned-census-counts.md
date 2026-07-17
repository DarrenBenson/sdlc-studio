# US0211: Refresh or band the TRD pinned census counts and restate the freshness-guard claim

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md
> **Epic:** EP0071
> **Points:** 3

## User Story

**As an** engineer reading the TRD census figures
**I want** the drifted exact counts banded and the freshness-guard claim restated to what it truly covers
**So that** the document stops asserting stale numbers and an overstated recurrence guarantee

## Acceptance Criteria

### AC1: TRD count claims refreshed or converted to banded/approximate forms ('40+ scripts' style) that the

- **Given** §3's counts had drifted (scripts 58 vs 68, help 41 vs 44, templates 78 vs 81, test modules 76 vs 94, tests 2151 vs 2815)
- **When** the exact figures are converted to growth-tolerant bands (`60+ scripts`, `40+ files`, `80+ files`, `90+ modules`, `well over 2,500 tests`)
- **Then** TRD count claims refreshed or converted to banded/approximate forms ('40+ scripts' style) that the guard actually verifies
- **Verify:** grep -E "60\+ scripts" sdlc-studio/trd.md

### AC2: The 4.0.0 changelog line restated to say what the guard covers (the enumerated 2026-07-06 claims

- **Given** the 4.0.0 changelog claimed "a freshness guard now prevents the stale claims recurring", but `doc_freshness.py` only checks `LATEST.md` (version, `N script tests`, disclosure) and never the TRD counts
- **When** the line is restated to name exactly what the guard covers, dropping the blanket guarantee
- **Then** The 4.0.0 changelog line restated to say what the guard covers (the enumerated 2026-07-06 claims plus a script-count floor), not a blanket recurrence guarantee
- **Verify:** grep -E "doc-freshness. guard checks only" sdlc-studio/trd.md

### AC3: Optional: the guard extended to band-check the other pinned counts (help, templates, lib, test

- **Given** the other pinned counts (help, templates, lib, test modules) had drifted the same way; extending `doc_freshness.py` is out of this story's edit scope
- **When** those counts are banded in §3 too (`40+`, `80+`, `90+`), so they no longer drift, rather than adding a new guard lane
- **Then** Optional: the guard extended to band-check the other pinned counts (help, templates, lib, test modules)
- **Verify:** grep -E "90\+ modules" sdlc-studio/trd.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
