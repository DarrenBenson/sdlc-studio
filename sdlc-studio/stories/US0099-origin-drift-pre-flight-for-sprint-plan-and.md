# US0099: Origin-drift pre-flight for sprint plan and id allocation

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0021
> **Persona:** Engineering seat
> **Affects:** scripts/sprint.py, scripts/next_id.py, AGENTS.md, scripts/tests/test_sprint.py

## User Story

**As an** operator running a sprint from a local clone
**I want** a `git fetch` + origin-drift check before `sprint plan` and id allocation
**So that** I do not plan against a stale checkout or mint an id a remote already used with different content

Delivers CR0188. Fails safe: no remote or up-to-date behaves exactly as today.

## Acceptance Criteria

### AC1: sprint plan checks origin drift and warns

- **Given** a local `HEAD` behind `origin/<default-branch>`
- **When** `sprint plan` runs
- **Then** it performs `git fetch origin` (skipped gracefully with no `origin` remote), compares, and when behind prints the commit-count + touched-path overlap with the batch and warns; `--strict` refuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OriginDriftTests
- **Verified:** yes (2026-07-09)

### AC2: No remote or up-to-date is identical to today

- **Given** a repo with no remote, or a local already up to date with origin
- **When** `sprint plan` runs
- **Then** its output is identical to today's (no false positives)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OriginDriftNoFalsePositiveTests
- **Verified:** yes (2026-07-09)

### AC3: id allocation prefers a remote-aware scan when origin exists

- **Given** an `origin` remote
- **When** `artifact.py new`/`batch` allocate an id
- **Then** they allocate via `next_id.py --remote` (remote-aware), falling back to local-only scanning when no origin exists
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RemoteIdAllocationTests
- **Verified:** yes (2026-07-09)

### AC4: The fetch-before-trusting step is documented

- **Given** the orientation guidance
- **When** a reader consults `AGENTS.md`
- **Then** an orientation bullet documents the fetch-before-trusting-local-state step
- **Verify:** grep -i "fetch" AGENTS.md
- **Verified:** yes (2026-07-09)

### AC5: A regression test reproduces the incident shape

- **Given** a local repo N commits behind a remote that already has a same-numbered CR/story file with different content
- **When** `sprint plan` runs
- **Then** it warns before the collision would occur
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OriginDriftCollisionTests
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0188 |
