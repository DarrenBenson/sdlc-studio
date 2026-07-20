# US0276: forward-port excludes the test cache, so a dev machine that has run the suite does not ship it to the installed copy

> **Status:** Done
> **Delivers:** CR0370
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/forward-port.sh
> **Epic:** EP0090
> **Points:** 1

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the test cache is excluded from the port

- **Given** a dev tree containing a `.pytest_cache` directory, which the documented workflow
  produces because the gate runs the suite
- **When** `forward-port.sh` builds its rsync invocation
- **Then** the cache is excluded, so machine-specific test state is never transferred into the
  installed skill copy
- **Verify:** grep "--exclude='\.pytest_cache'" tools/forward-port.sh
- **Verified:** yes (2026-07-20)

### AC2: the existing excludes are untouched

- **Given** the port's guarantee that a consuming copy's local state and bytecode survive
- **When** the exclude list is extended
- **Then** `.local` and `__pycache__` remain excluded exactly as before, because widening the
  list must not quietly narrow it
- **Verify:** shell grep -qF -- "--exclude='.local'" tools/forward-port.sh && grep -qE -- "--exclude='_{2}pycache_{2}'" tools/forward-port.sh
- **Verified:** yes (2026-07-20)

### AC3: a cache already in the installed copy is reaped, not stranded

- **Given** an installed copy that already holds a `.pytest_cache` or bytecode directory from
  before this change
- **When** the port runs
- **Then** it is removed, because excluding a path also removes it from rsync's `--delete` view -
  so the exclude alone converts a reaped orphan into a permanent one. The reap is scoped away
  from `.local`, which is the consuming copy's real state and must survive
- **Verify:** shell grep -qF "name '.local' -prune" tools/forward-port.sh && grep -qF "'.pytest_cache' \\) -type d -prune" tools/forward-port.sh
- **Verified:** yes (2026-07-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
