# BG0872: next_id.py allocate mints a sequential id on a schema v3 project, where artifact.py new mints a ULID

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_next_id_v3.py, changelog.d/BG0872.md
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

- [ ] **AC1** Given a fresh `init.py run` project at `schema_version: 3`, when `next_id.py allocate --type story --root <fixture>` runs, then it either prints a v3 id (`US-` and a ULID, the shape `artifact.py new` mints) or exits non-zero naming `artifact.py new`, and it never prints a sequential `US0001`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_next_id_v3.py::NextIdV3Tests::test_a_v3_project_gets_no_sequential_id
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD prints `US0001` and exits 0 on a v3 project
- [ ] **AC2** Given a project at `schema_version: 2`, when the same command runs, then it still prints the next sequential id (`US0001` on an empty project).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_next_id_v3.py::NextIdV3Tests::test_a_v2_project_keeps_sequential_ids
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** a fix that mints a v3 id, or refuses, whatever the project's schema

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (groomer) | Groomed: premise executed at 78ae6c43: on a fresh `init.py run` project (`schema_version: 3`), `next_id.py allocate --type epic` prints EP0001 while `artifact.py new --type epic` minted EP-01M3WD5W; criteria authored, Points and Affects set |
