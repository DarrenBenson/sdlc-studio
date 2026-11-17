# US1278: The TSD states the script tier's supported platforms and the id lock's limit on Windows

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0719
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/tsd.md, tools/tests/test_lean_tsd_script_pin.py
> **Epic:** EP0358
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The TSD states the script tier's supported platforms and the id lock's limit on Windows
**So that** CR0719 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The TSD states the script tier's platforms and what runs it on Windows

- **Given** `sdlc-studio/tsd.md` and the `windows-smoke` job in `.github/workflows/lint.yml`
- **When** the TSD's scope and its CI jobs row for `windows-smoke` are read against the job
- **Then** the TSD names the platforms the script tier is supported on, and for Windows says what the job does: the named script-test subset where the job runs one, or an explicit known-gap entry where it does not. Fails on: the TSD as it stands at grooming, which is silent on Windows for the script tier, or a row that claims script tests the job does not run
- **Verify:** pytest tools/tests/test_lean_tsd_script_pin.py::PlatformSupportTests::test_the_tsd_states_the_platforms_and_the_windows_gate

### AC2: The id lock's limit on Windows is a stated limit

- **Given** the id-allocation lock in `lib/sdlc_md.py`, which takes no lock where `fcntl` cannot be imported
- **When** the TSD's statements about the allocation lock and shared writes are read
- **Then** the TSD records that on a platform without `fcntl` the allocation lock is not taken and two concurrent allocations are not serialised, and no sentence claims every shared write is serialised on every supported platform. Fails on: a TSD that lists Windows as supported and leaves the lock's absence unsaid
- **Verify:** pytest tools/tests/test_lean_tsd_script_pin.py::PlatformSupportTests::test_the_id_lock_limit_is_stated_for_platforms_without_fcntl

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
