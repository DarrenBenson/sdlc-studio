# US0377: skill entry points warn or refuse while the inflight sidecar exists, own processes exempt, a stale sidecar still recovers

> **Status:** Draft
> **Delivers:** CR0374
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0135
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_inflight_guard.py

## User Story

**As an** agent or reviewer working in a tree while a mutation evidence run has a mutant applied
**I want** a skill script I invoke to say so, and a write-path script to refuse outright
**So that** I never execute a mutated sibling in silence and attribute its wrong behaviour, or a false review finding, to the wrong cause

## Acceptance Criteria

### AC1: a read-path entry point warns, naming the mutated file, and still runs

- **Given** `sdlc-studio/.local/mutation-inflight.json` exists holding the original bytes of `scripts/status.py`
- **When** a read-path entry point (`status`) is invoked in that root
- **Then** it prints a loud warning on stderr naming the mutated file and the single-writer rule, then completes and exits 0 - a read is degraded evidence, not a blocked one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_inflight_guard.py::InflightGuardTests::test_read_path_warns_naming_the_mutated_file_and_still_exits_zero
- **Verified:** yes (2026-07-24)

### AC2: a write-path entry point refuses and writes nothing

- **Given** the same in-flight sidecar on disk
- **When** `artifact new` and `transition set` are invoked in that root
- **Then** each refuses with exit 2 naming the mutated file and how to clear the sidecar, and no artefact, id or status change is written - a write made against a mutated tool is a write nobody can trust afterwards
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_inflight_guard.py::InflightGuardTests::test_write_path_refuses_and_writes_nothing
- **Verified:** yes (2026-07-24)

### AC3: the mutation run's own processes are exempt and a stale sidecar still recovers

- **Given** the same sidecar, and a process carrying the marker `mutation.py` sets in the environment it runs its suites under
- **When** that process invokes any guarded entry point, and separately when a new `mutation.py` run starts against a sidecar stranded by a killed predecessor
- **Then** the marked process is neither warned nor refused, and `_recover_stranded` restores the stranded original bytes and clears the sidecar exactly as it does today - the guard cannot block the one run whose job is to clean up after itself
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_inflight_guard.py::InflightGuardTests::test_own_run_is_exempt_and_a_stale_sidecar_still_recovers
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc | Built: applied-mutant guard - status warns, artifact/transition refuse, mutation run exempt |
