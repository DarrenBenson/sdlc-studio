# BG0825: ULID ids are printed as their hyphenless comparison key, so plan, brief, carry and the signed report name ids no file carries

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_id_display.py, changelog.d/BG0825.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** soak F5/F18 (website project); eval 09 v6-main transcript (Batch: US01M3KQ7W; RETRO-0001 vs RETRO0001 file) and RPT0001 issue row BG01M3KS98; HEAD 7e53a438 critic.py:2996 prints sdlc_md.norm_id(args.unit)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:25Z

## Summary

`sdlc_md.norm_id` is a comparison key (`US-01M3HR7A` -> `US01M3HR7A`) and is printed as the id in user-facing output: the plan's delivery-mode line, `critic.py brief`'s record footer (critic.py ~2996, ~3025), the carried-at-cap bug's title and slug (`critic.carry_at_cap)`, the retro's Batch line, and the signed report's issue table (eval 09 RPT0001 lists `BG01M3KS98`, whose file is BG-01M3KS98-...). A reader who searches for the printed id finds nothing. The close prints the opposite drift for sequential meta ids: `retro RETRO-0001 scaffolded ... --retro RETRO-0001` while the file is RETRO0001-.... On schema v3, the v6 init default, every user sees it.

## Steps to Reproduce

On a schema v3 project: `critic.py brief --unit US-<ulid> --seat qa` prints `critic.py record --unit US<ulid>`; close a run and read the report's issue table and the retro Batch line.

## Proposed Fix

Add one display helper that returns an id in its file's spelling (the stem's record id), and use it wherever an id is printed or written into prose, titles and slugs; keep `norm_id` for comparison only.

## Acceptance Criteria

- [ ] **AC1** Given a schema v3 unit `US-01ABCDEF`, when the brief footer, the plan's delivery-mode line, a carried bug's title and the report's issue table name it, then each prints `US-01ABCDEF`. Fails on: HEAD, which prints US01ABCDEF
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_id_display.py::IdDisplayTests::test_ulid_ids_print_in_file_spelling
- [ ] **AC2** Given a retro file RETRO0001-x.md scaffolded by the close, then the close's printed id and its `--retro` hint match the file's spelling. Fails on: HEAD's RETRO-0001
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_id_display.py::IdDisplayTests::test_the_scaffolded_retro_id_matches_its_file

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
