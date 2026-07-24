# US0367: anchor the CR0302 freshness guard to the claim so it fails on the stale counts

> **Status:** Draft
> **Delivers:** CR0365
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0129
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the freshness guard fails on the stale counts it was meant to catch

- **Given** the CR0302 freshness guard and a document whose recorded counts no longer match the workspace
- **When** the guard runs
- **Then** it FAILS and names the stale claim - the guard is anchored to the claim itself, not to a file mtime, so a stale number cannot pass by being in a recently-touched file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::ClaimAnchoredTests::test_a_stale_count_fails_and_is_named

### AC2: a correct count passes without a re-run of the whole sweep

- **Given** a document whose counts match
- **When** the guard runs
- **Then** it passes, and the assertion is made against the measured value rather than against the presence of a freshness stamp
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::ClaimAnchoredTests::test_a_correct_count_passes_on_the_value_not_the_stamp

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
