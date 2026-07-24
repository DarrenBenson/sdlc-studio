# US0394: verify_ac run accepts an id list, a worklist or the run-state batch

> **Status:** Done
> **Delivers:** CR0395
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0147
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py,.claude/skills/sdlc-studio/help/verify.md,.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py

## User Story

**As an** agent closing a sprint whose batch is a couple of dozen stories in a
workspace holding hundreds
**I want** `verify_ac.py run` to take the batch as a scope - an explicit id list, a
worklist file, or the ids the open run state already records
**So that** the close gate gets a verified report for exactly the units the sprint
touched, without re-running every AC in the workspace or paying process startup once
per story

## Acceptance Criteria

### AC1: an explicit id list scopes the run to exactly those stories

- **Given** a stories directory holding several stories, only some of which are in
  the batch
- **When** `verify_ac.py run --ids US0001,US0003` is run (the flag accepting a
  comma-separated value or repetition, case-insensitively, and resolving each id
  under `--dir` the way `--id` already does)
- **Then** only those stories are verified and only their entries are written, in
  one process - and an id that resolves to no story file exits 2 naming the id,
  never a silent skip that a gate would read as green
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::IdListScopeTests::test_only_the_named_ids_run_and_an_unresolvable_id_exits_2
- **Verified:** yes (2026-07-24)

### AC2: a worklist file is accepted as the batch source

- **Given** a worklist file naming the batch one id per line, with markdown bullets
  and `#` comment lines present
- **When** `verify_ac.py run --worklist <file>` is run
- **Then** it verifies exactly the story ids the file names, tolerating the bullet
  and comment forms and de-duplicating a repeated id, matching the tranche-file
  shape the sprint planner already reads so one file drives both
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::WorklistScopeTests::test_bullets_comments_and_duplicates_resolve_to_the_named_stories
- **Verified:** yes (2026-07-24)

### AC3: the open run state supplies the batch with no id typed by hand

- **Given** an open run state whose approved batch names story and bug ids
- **When** `verify_ac.py run --from-run` is run
- **Then** it verifies the story units of that batch and no others, and with no run
  open it exits 2 saying so rather than falling back to a whole-workspace run that
  would silently cost the nine minutes the flag exists to avoid
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RunStateScopeTests::test_batch_stories_run_and_no_open_run_exits_2
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Built: `--ids` / `--worklist` / `--from-run` batch scopes, all 3 ACs verified |
