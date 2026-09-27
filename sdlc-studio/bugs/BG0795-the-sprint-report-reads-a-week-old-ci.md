# BG0795: The sprint report reads a week-old CI cache as current, so DORA's failure rate and restore time read no forge data

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_frozen_report_inputs.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py, changelog.d/BG0795.md
> **Parent:** CR0599
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T07:29:10Z

## Summary

`sprint_report._ci_runs` reads sdlc-studio/.local/ci-runs.json whenever it exists and writes it only when absent. The file was written 2026-09-18 and never refreshed, so RPT0010 (RUN-01M3CK1K, 2026-09-25 to 26) found no CI run in its window and printed change failure rate and time to restore as NOT MEASURED - no forge run data, while the forge holds every run. The cache is described as 'for this run' but is per clone.

## Steps to Reproduce

ls -la sdlc-studio/.local/ci-runs.json (Sep 18); `sprint_report.py` render --report RPT0010: DORA rows read no forge run data.

## Proposed Fix

Key the cache to the run (or refresh when the run window ends after the cache's newest row), so a report re-derives from the data it was built from and a new run reads the forge; test with a stale cache and a window past it.

## Acceptance Criteria

- [ ] **AC1** Given a `.local/ci-runs.json` written before the run opened and a stub `gh` answering a push run inside the run's window, when the close prepares the report, then DORA counts the stub's run and the run record carries it. Fails on: HEAD's `_ci_runs`, which returns the cache whenever it exists (RPT0010 read no forge data from a cache written 2026-09-18)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_frozen_report_inputs.py::FrozenCiRunsTests::test_the_close_reads_the_forge_not_a_stale_cache
- [ ] **AC2** Given a signed fixture whose run record carries its CI runs, when `sprint_report.py check` runs with a stub `gh` answering a different set of runs, then it exits 0. Fails on: re-deriving DORA from a live `gh run list`, which reads RPT0010 INVALIDATED in a forge-connected clone (`dora_value[0]` signed 72, now 7; measured at dee380d9)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_frozen_report_inputs.py::FrozenCiRunsTests::test_a_signed_report_rederives_dora_from_its_record
- [ ] **AC3** Given the scripts, then nothing reads or writes `sdlc-studio/.local/ci-runs.json`. Fails on: keeping the per-clone cache as a second source beside the record
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_frozen_report_inputs.py::FrozenCiRunsTests::test_no_per_clone_ci_cache_remains

## Notes

- Folded into CR0599's design for Sprint 6: PREPARE (`sprint._file_the_report`) fetches the window's CI runs fresh and records them on the run as `ci_runs` (empty when `gh` cannot answer, with the reason as the source, which is outside the fingerprint); `build_report` reads them from the record whenever the key exists and fetches live only for an unfrozen preview. Land after US0959. Ratchet: retires the per-clone cache; no check added.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | Re-scoped for Sprint 6: the CI runs are frozen on the run record at PREPARE, which also lets a signed report re-derive in any clone (CR0599); 2 to 3 points |
