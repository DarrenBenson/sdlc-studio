# US0086: Benchmark v2 harness: subdirs, environmental isolation, metrics capture, arm R

> **Status:** Draft
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Epic:** EP0017
> **Persona:** Sam Eriksson (QA)
> **CR:** CR-0192, CR-0193

## User Story

**As a** benchmark operator
**I want** the harness to score multi-file fixtures, isolate arms environmentally, capture metrics automatically, and support a routed arm R with a cost index
**So that** the v2 protocol's runs are fair, reproducible and cheap to record

## Acceptance Criteria

### AC1: Multi-file hidden suites score correctly

- **Given** a fixture whose hidden/ contains subdirectories
- **When** `runner.py score` runs
- **Then** the whole hidden tree is copied for scoring (copytree, like prepare) and the suite executes; default timeout is 120s
- **Verify:** pytest tools/tests/test_bench_runner.py -k subdir

### AC2: Environmental arm isolation

- **Given** workspaces prepared outside the repo
- **When** `prepare --arm A` or `--arm R` runs
- **Then** the skill is copied INTO the workspace (.claude/skills/sdlc-studio); an arm-B workspace contains no such directory
- **Verify:** pytest tools/tests/test_bench_runner.py -k isolation

### AC3: Automatic metrics capture with disclosed fallback

- **Given** an orchestrator per-run usage JSON
- **When** `record --metrics-json <path>` runs
- **Then** tokens/wall-time come from the file; hand-typed flags still work but stamp `metrics_source: manual`
- **Verify:** pytest tools/tests/test_bench_runner.py -k metrics

### AC4: Arm R and the cost index

- **Given** arm R registered with a routed CLAUDE.md and a workspace .config.yaml enabling routing
- **When** `summary --price tiny=0.25,small=1,...` runs over records carrying `--model-mix`
- **Then** a cost index is computed per fixture x arm; without prices no cost column appears (no fabricated zeros); pricing never lives under .claude/skills/
- **Verify:** pytest tools/tests/test_bench_runner.py -k cost_index

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sprint: CR0192+CR0193 | Created via `new` (deterministic) |
