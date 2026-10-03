# BG0882: harness_project_slug does not truncate a long project path or map non-BMP characters as the harness does

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_dir_harness.py, changelog.d/BG0882.md
> **Evidence:** BG0835 QA review (RUN-01M3VF2J), rule read from the installed Claude Code 2.1.284 binary
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T17:43:53Z

## Summary

Claude Code 2.1.284 names a project's transcript folder by mapping each UTF-16 code unit outside [A-Za-z0-9] to '-', and truncates a slug longer than 200 characters to 200 plus '-' and a base36 hash. `run_state.harness_project_slug` maps per code point and never truncates, so a repo under a deep path, or with an emoji in its path, reads its token meter as NOT ATTRIBUTABLE.

## Steps to Reproduce

1. A repo at a path whose slug exceeds 200 characters. 2. `run_state.session_tokens` -> no transcript found (337-char slug vs the harness's 207).

## Proposed Fix

Mirror the harness rule: map per UTF-16 code unit and truncate past 200 with the harness's hash suffix, or locate the folder by matching the recorded cwd inside each transcript.

## Acceptance Criteria

- [ ] **AC1** Given a repo whose path holds one non-BMP character (an emoji) and a transcript in the folder the harness names (that character mapped to two dashes, one per UTF-16 code unit), when `run_state.session_tokens(root)` runs with HOME at a fixture and no override, then it reads the tokens.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_dir_harness.py::TranscriptDirHarnessTests::test_a_non_bmp_character_maps_to_two_dashes
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD maps the emoji to one dash and reports `no harness transcript directory`
- [ ] **AC2** Given a repo whose slug exceeds 200 characters and a transcript under `projects/` in a folder that is not the untruncated slug, whose records carry `cwd` equal to the repo's path, when the same call runs, then it reads that transcript; a folder whose records carry a different `cwd` is never read.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_dir_harness.py::TranscriptDirHarnessTests::test_a_long_path_is_found_by_its_recorded_cwd
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD looks only in the untruncated slug folder and reports `no harness transcript directory`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (groomer) | Groomed: premise executed at 78ae6c43: `run_state.harness_project_slug` maps each code point outside [A-Za-z0-9-] to `-` and never truncates, so an emoji (two UTF-16 units) yields one dash where the harness writes two, and a slug past 200 characters is looked up untruncated; transcript records carry `cwd`; criteria authored, Points and Affects set |
