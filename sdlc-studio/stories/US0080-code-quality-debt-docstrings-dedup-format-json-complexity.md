# US0080: Code-quality debt: docstrings, dedup, format json, complexity

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0018
> **Persona:** Skill Maintainer
> **Source:** CR-0187

## User Story

**As a** skill maintainer
**I want** the RV0006 code-quality debt cleared
**So that** stale docstrings, duplicated primitives and complexity hotspots stop inviting the next defect

## Acceptance Criteria

### AC1: Accurate docs, shared primitives, even JSON

- **Given** the flagged sites
- **When** cleaned up
- **Then** the reconcile docstring lists all four subcommands, find_by_id/linked_to_epic live in
  lib and the duplicates delegate, and apply/revision/rebuild accept --format json
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k format_json
- **Verified:** yes (2026-07-10)

### AC2: Hotspots decomposed, latent issues fixed

- **Given** the four named complexity hotspots and the test-suite issues
- **When** refactored
- **Then** they are decomposed with no behaviour change, the raw-string escape is fixed, and
  `.local` logs roll with an opt-in SDLC_DEBUG channel
- **Verify:** shell python3 -W error -c "import sys; compile(open(sys.argv[1]).read(), sys.argv[1], 'exec')" .claude/skills/sdlc-studio/scripts/tests/test_table_parsers.py && python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DebugTraceTests
- **Verified:** yes (2026-09-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
| 2026-09-26 | US0940 | AC2 narrowed: the line ran the whole skill suite, which exceeds the verify lane's 300 s ceiling (measured: killed at 300 s) and says nothing about this refactor that the push boundary's full-suite lane does not already say on every push. It now checks the two durable claims: `test_table_parsers.py` compiles with warnings as errors (the raw-string fix), and `DebugTraceTests` (the `.local` log roll and the `SDLC_DEBUG` channel) |
