# US0115: Advisory lanes earn their signal: mutation wired into sprint close, disclosure triaged to zero

> **Status:** Done
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new
> **Epic:** EP0026
> **Persona:** repo maintainer (dogfooding operator)
> **CR:** CR0203

## User Story

**As a** gate consumer (agent or operator)
**I want** every standing `[warn]` in a routine gate run to mean something actionable
**So that** warns stop training readers to skim past them - the selective-attention failure behind the lint breakage

## Context

RV0007: the mutation lane had warned on 100% of runs since it was built (no report has ever
existed) and disclosure carried 17 standing advisories. A lane that always warns is noise.
CR0203's decision (ledgered at plan time): wire a bounded run in, do not remove the lane.

## Acceptance Criteria

### AC1: disclosure advisories triaged to zero

- **Given** the repo at HEAD when this story shipped
- **When** `disclosure.py --root .` runs
- **Then** the advisories present at delivery are triaged (orphan pages catalogued, scripts executable, module-only libraries expose --help)
- **Verify:** manual at delivery (2026-07-13) the disclosure advisories then present were triaged to zero. This is a point-in-time triage, not a standing invariant: new advisories accrue as the project grows, which is the disclosure lane's ongoing job to surface, so an executable check re-asserting "zero now" wrongly un-Dones this story on advisories filed by later, unrelated work (BG0234).
- **Verified:** manual

### AC2: a real bounded mutation run exists and the lane reads it

- **Given** a mutation run over this sprint's changed surface (`--since` the sprint base, ceiling from config)
- **When** `gate.py --only mutation` runs
- **Then** the lane reads the report (PASS or survivor detail), not "not run"
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/gate.py --only mutation --root . 2>&1 | grep -v 'not run'
- **Verified:** yes (2026-07-10)

### AC3: the sprint close mandates the run mechanically

- **Given** the sprint reference
- **When** an agent follows the closing gate
- **Then** a bounded `mutation.py run --since <sprint base>` step is a named part of the close, before the retro gate
- **Verify:** grep "mutation.py run --since" .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
| 2026-07-10 | sprint (CR0203 decomposition) | ACs authored; wire-in decision carried from the plan ledger |
