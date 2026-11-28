# BG1784: A parallel `sprint drive` wave can run one unit's paperwork commit while another unit's step runs git in the root, and the commit dies on index.lock

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_wave.py, changelog.d/BG1784.md
> **Evidence:** Run twenty-eight's second push of main (2026-11-28, 01:08Z): devserver1 refused 823c6a02a with that one red test; the host's boundary-suite-last.log carries the index.lock lines.
> **Created:** 2026-11-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-28T01:28:01Z

## Summary

`sprint drive` walks a wave's units in threads. Land, accept and paperwork take the wave's root lock (lib/drive.py:471, 516, 550), but the review step's headless reviewer and the brief step run in the root without it. Any git command they run, even a read such as `git status` that refreshes the index, can hold `.git/index.lock` at the moment another unit's paperwork commits. That commit then exits 128 with "Unable to create '.../index.lock': File exists", and the drive stops that unit at paperwork as a refusal. It fails safe: nothing is half-written, and rerunning the drive resumes. But it stops an autonomous wave for no fault of the unit. It turned main's pre-push full suite red once, in `test_sprint_drive_wave.py`::SprintDriveWaveTests::`test_a_warning_on_a_green_step_stops_the_unit` on the gate host, where US0101's paperwork hit the lock while US0102's steps ran. The test passes alone.

## Steps to Reproduce

1. Run test_sprint_drive_wave.py's parallel wave under load (the full suite on the gate host, 745 modules in parallel).
2. Now and then one unit's paperwork commit fails with exit 128 and "index.lock: File exists"; the test's `{A} paperwork: committed` assert fails.

## Proposed Fix

Make every git command a wave step runs in the root either take the root lock or not take the index lock: run read-only git with `GIT_OPTIONAL_LOCKS`=0, and run the brief and review steps' root writes under `w.root_lock`. Pin with a test that makes a concurrent root git read hold index.lock while the paperwork commits, and shows the commit no longer fails.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint drive` walks a wave's units in threads.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_wave.py::SprintDriveWaveTests::test_a_root_read_beside_a_paperwork_commit_holds_no_index_lock
  - **Verified:** yes (2026-11-28)
- [ ] **AC2** The proposed fix lands, pinned by a test: Make every git command a wave step runs in the root either take the root lock or not take the index lock: run read-only git with `GIT_OPTIONAL_LOCKS`=0, and...
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_wave.py::SprintDriveWaveTests::test_the_build_and_review_sessions_read_the_root_without_its_index_lock
  - **Verified:** yes (2026-11-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-28 | sdlc-studio | Filed |
