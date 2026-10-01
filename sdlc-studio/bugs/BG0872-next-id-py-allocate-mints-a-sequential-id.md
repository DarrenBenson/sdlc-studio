# BG0872: next_id.py allocate mints a sequential id on a schema v3 project, where artifact.py new mints a ULID

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_next_id.py
> **Evidence:** US0974 QA review round 1 (RUN-01M3VF2J), re-executed by the orchestrator on a fresh init
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T15:09:52Z

## Summary

On a fresh `schema_version` 3 project, `next_id.py` allocate --type story prints US0001 while artifact.py new mints a v3 ULID id. The doctrine tells agents to allocate ids with `next_id.py`, so a v3 project gets mixed id schemas, and a conformance or validate ULID cutoff treats every sequential id as pre-v3 and exempt (US0974's documented assumption).

## Steps to Reproduce

1. init.py run in an empty git repo (`schema_version` 3). 2. python3 `next_id.py` allocate --type story --root . -> US0001. 3. artifact.py new --type story -> a US-01... id.

## Proposed Fix

Make `next_id.py` allocate mint the project's schema: a v3 id on a v3 project, or refuse with the artifact.py route named.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: On a fresh `schema_version` 3 project, `next_id.py` allocate --type story prints US0001 while artifact.py new mints a v3 ULID id.
- [ ] **AC2** The proposed fix lands, pinned by a test: Make `next_id.py` allocate mint the project's schema: a v3 id on a v3 project, or refuse with the artifact.py route named.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
