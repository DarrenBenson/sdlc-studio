# US0217: a global doc-coverage failure is attributed once, not fanned across every unit

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Epic:** EP0072
> **Depends on:** US0220
> **Points:** 3

## User Story

**As an** operator reading a conformance failure
**I want** a repo-wide gap reported once as itself
**So that** one uncatalogued command does not read as a hundred broken units

## Acceptance Criteria

### AC1: A repo-wide failure is reported once, not charged to every unit

- **Given** a repository whose doc-coverage reports an undocumented item, and Done stories that would otherwise be conformant
- **When** conformance is checked
- **Then** the failure appears once in a `globals` list naming the stage, the reason and its remedy, and no unit counts it in its own `missing` - so the output reads as one doc gap rather than N broken units.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_conformance.GlobalAttributionTests.test_global_failure_reported_once
- **Verified:** yes (2026-07-18)

### AC2: The unit still records that a repo-wide stage failed for it

- **Given** the same repository
- **When** a unit's record is read
- **Then** the globally-caused stage appears in `missing_global` (so nothing is hidden) while `missing` holds only that unit's own gaps, keeping the two kinds of finding distinguishable.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_conformance.GlobalAttributionTests.test_unit_records_global_separately
- **Verified:** yes (2026-07-18)

### AC3: Attributing once must not enforce less

- **Given** a repository whose only conformance problem is repo-wide
- **When** the gate lane and the CLI run
- **Then** both still fail - the lane counts the global failure and `conformance check` exits non-zero - so improving the report does not quietly weaken the gate.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_conformance.GlobalAttributionTests.test_global_failure_still_blocks
- **Verified:** yes (2026-07-18)

### AC4: Genuine per-unit gaps are unaffected

- **Given** a repository with no repo-wide failure but a unit with its own missing stage
- **When** conformance is checked
- **Then** `globals` is empty and the unit's `missing` is exactly as before, so the change is confined to the global case.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_conformance.GlobalAttributionTests.test_per_unit_gaps_unaffected
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: ACs and executable Verify lines authored |
