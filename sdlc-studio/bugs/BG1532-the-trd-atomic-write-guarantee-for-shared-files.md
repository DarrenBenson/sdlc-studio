# BG1532: The TRD atomic-write guarantee for shared files is false for the signed report, story files and others

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/github_sync.py, sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py
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

- [ ] **AC1** The behaviour described is corrected: Rule 5 of the script contract in `sdlc-studio/trd.md` (lines 299 to 306) and the scripts row of the component table (line 128) say shared-file writes go...
- [ ] **AC2** The proposed fix lands, pinned by a test: Move the whole-file rewrites of committed files in `sprint_report.py` (report JSON and Markdown twin), `verify_ac.py` (the story Verified rewrite)...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
