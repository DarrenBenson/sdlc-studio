# US0665: A v4-era fixture is driven through migrate --apply to a GREEN gate, asserting the upgrade's outcome rather than the migrate's report

> **Status:** Draft
> **Delivers:** CR0542
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/rehearse-release.sh, .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py
> **Epic:** EP0214
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A v4-era fixture is driven through migrate --apply to a GREEN gate, asserting the upgrade's outcome rather than the migrate's report
**So that** CR0542 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1

- **Given** an empty temporary directory outside the repository
- **When** `tools/rehearse-release.sh upgrade` is run
- **Then** it builds a v4-era workspace - `schema_version: 2`, a Done story carrying neither
  `Affects` nor `Points`, and a request carrying a legacy `Effort` - runs `migrate.py --apply`
  through the shipped CLI, then runs `gate.py`, and reports the gate's lane verdicts.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py -k upgrade_migrates_then_gates
- **Verified:** yes (2026-08-10)

### AC2

- **Given** that the upgrade path does NOT reach a green gate today - conformance, reconcile and
  index-derived all fail on a freshly migrated project, and the remedy is CR0497's grandfathering,
  which is not in this run
- **When** the rehearsal runs
- **Then** it compares the failing lanes against a RECORDED baseline of lanes known to fail, exits
  0 while they match it exactly, and exits non-zero the moment a lane fails that the baseline does
  not name, or a baselined lane starts passing. The baseline is the honest statement of a known
  gap; claiming green here would be the false claim this lane exists to prevent, and a baseline
  that only ever tolerates is one that never empties.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py -k the_upgrade_baseline_reddens_in_both_directions
- **Verified:** yes (2026-08-10)

### AC3

- **Given** the recorded baseline
- **When** it is read
- **Then** each entry names the lane, the artefact that will clear it, and what the lane will say
  once cleared - so a reader can tell a known gap from an unexplained failure without leaving the
  file.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py -k every_baselined_lane_names_the_artefact_that_clears_it
- **Verified:** yes (2026-08-10)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `tools/rehearse-release.sh`, change the upgrade step to run `gate.py` before `migrate.py --apply` | |
| AC2 | in `tools/rehearse-release.sh`, change the baseline comparison to a subset test so a lane that starts passing is tolerated | |
| AC3 | in `tools/rehearse-release.sh`, change the baseline reader to ignore the clearing-artefact column | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Created via `new` (deterministic) |
