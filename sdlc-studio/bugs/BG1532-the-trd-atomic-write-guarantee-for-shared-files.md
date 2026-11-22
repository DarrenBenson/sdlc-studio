# BG1532: The TRD atomic-write guarantee for shared files is false for the signed report, story files and others

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/github_sync.py, sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py, tools/tests/test_lean_trd_refresh.py, changelog.d/BG1532.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md §3 Component Overview, `scripts/` Constraints cell (line 128); §5 Script CLI contract rule 5 (lines 299-306)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:16Z

## Summary

Rule 5 of the script contract in `sdlc-studio/trd.md` (lines 299 to 306) and the scripts row of the component table (line 128) say shared-file writes go through `sdlc_md.atomic_write`, so a crash or a concurrent writer never corrupts a shared file, with the append-only ledgers as the one deliberate exception. Several committed, shared files are in fact rewritten whole with a plain truncating `write_text`. They include the run report JSON and its Markdown twin in `sprint_report.py` (the page a signature is written onto), story files when `verify_ac.py` rewrites the Verified line, the project lessons file in `lessons.py`, epic files in `artifact.py` and the artefact `github_sync.py` stamps. A crash part-way through any of these leaves a truncated file. The TRD never defines what a shared file is, so the guarantee cannot be tested as written, and nothing holds the claim to the code.

## Steps to Reproduce

1. Read `sdlc-studio/trd.md` lines 299 to 301: shared-file writes go through `sdlc_md.atomic_write`, and the ledgers are the one exception.
2. Read `.claude/skills/sdlc-studio/scripts/sprint_report.py` lines 5834 and 5836: the report JSON and its Markdown twin are written with `write_text`.
3. Read `verify_ac.py` line 2865, `lessons.py` line 206, `artifact.py` line 961 and `github_sync.py` line 332: each rewrites a committed file with `write_text`.
4. Search `sdlc-studio/trd.md` for a definition of shared file: there is none.
5. Expected: every committed file a script rewrites whole goes through the atomic helper, or the TRD names the exceptions. Actual: at least five writers of committed files bypass it and the guarantee names no exception for them.

## Proposed Fix

Move the whole-file rewrites of committed files in `sprint_report.py` (report JSON and Markdown twin), `verify_ac.py` (the story Verified rewrite), `lessons.py` (`write_project_file`), `artifact.py` (the epic rewrite) and `github_sync.py` (the artefact stamp) onto `sdlc_md.atomic_write`. In `sdlc-studio/trd.md`, define a shared file as any tracked workspace file a script rewrites whole, and list any writer deliberately left outside the guarantee with its reason. Add a test to `test_confinement.py` that scans the scripts for `write_text` calls on tracked workspace paths and fails on any site not on an explicit allowlist of scratch or untracked targets, so the claim is held to the code.

## Acceptance Criteria

- [ ] **AC1** Given a signed run report on disk, when `sprint_report.py` rewrites the report JSON and its Markdown twin and the write is interrupted before it completes, then both files still hold their previous content in full. Fails on: a truncated or half-written report left where a signature is recorded.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ReportWriteIsAtomicTests::test_an_interrupted_write_leaves_the_previous_report_whole
- [ ] **AC2** Given the scripts under `.claude/skills/sdlc-studio/scripts`, when they are scanned for whole-file rewrites of tracked workspace paths, then every site goes through `sdlc_md.atomic_write`, sits on the explicit allowlist of scratch or untracked targets, or sits on the separate not-yet-moved list that `sdlc-studio/trd.md` names with each writer's reason (D0587; the moves are BG1712), and the story Verified rewrite in `verify_ac.py`, `write_project_file` in `lessons.py`, the epic rewrite in `artifact.py` and the artefact stamp in `github_sync.py` are on neither list because each now goes through `sdlc_md.atomic_write`. Fails on: a whole-file rewrite of a committed file that bypasses the atomic helper.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_confinement.py::SharedFileWriteSweepTests::test_no_tracked_workspace_file_is_rewritten_with_write_text
- [ ] **AC3** Given a script fixture with a planted truncating `write_text` on a tracked workspace path, when the same scan runs over it, then it names that site; the same write to a scratch path on the allowlist is not named. Fails on: a scan that cannot see the defect it exists to catch.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_confinement.py::SharedFileWriteSweepTests::test_the_sweep_catches_a_planted_truncating_write
- [ ] **AC4** Given rule 5 of the script contract and the scripts row of the component table in `sdlc-studio/trd.md`, when they are read, then a shared file is defined as any tracked workspace file a script rewrites whole, and every writer left outside the guarantee is listed with its reason. Fails on: the guarantee stated with no definition of a shared file, or the ledgers still called the one exception while others exist.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdStorageTests::test_a_shared_file_is_defined_and_every_exception_is_listed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | AC2 narrowed under D0587 to agree with AC4: the nine rewrites outside Affects the widened sweep found sit on a not-yet-moved list the TRD names, and move under BG1712 |
