# US0184: deploy metrics computes the four keys from ledger + git + bug dates, refusing absent sources, not-applicable without a ledger

> **Status:** Draft
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/deploy.py, .claude/skills/sdlc-studio/scripts/tests/test_deploy.py, .claude/skills/sdlc-studio/reference-deploy-readiness.md
> **Epic:** EP0054
> **Points:** 3

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** the DORA four keys computed from records the project already keeps
**So that** a deploying project reads its delivery performance with zero token spend

## Acceptance Criteria

### AC1: Four keys from ledger, git and bug dates

- **Given** a workspace with a deploy ledger, git history and severity-marked bugs
- **When** deploy metrics runs
- **Then** deployment frequency, lead time for changes, change failure rate and MTTR are computed with their measurement windows stated
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_deploy.py -k DoraKeys

### AC2: Absent sources are refused, not guessed

- **Given** a workspace missing one source (e.g. no severity dates)
- **When** deploy metrics runs
- **Then** the affected key is reported unmeasurable by name; the others still compute
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_deploy.py -k DoraRefus

### AC3: Not-applicable without a ledger

- **Given** a workspace with no deploy records
- **When** deploy metrics runs
- **Then** it reports not-applicable cleanly and nothing nags a non-deploying project
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_deploy.py -k DoraNotApplicable

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
