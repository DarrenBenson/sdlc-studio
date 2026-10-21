# US0988: An OpenCode run records its token actual from the read-only OpenCode database, child sessions included

> **Status:** Draft
> **Delivers:** CR0611
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_opencode.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/US0988.md
> **Epic:** EP0274
> **Points:** 5
> **Depends on:** US0986
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer running a sprint from OpenCode (Maya)
**I want** the close to record the run's token spend from OpenCode's own database, subagent sessions included
**So that** the run is measured on the same basis as a Claude run, without the skill touching or shelling out to OpenCode

## Acceptance Criteria

- **AC1:** Given a fixture SQLite database at `$OPENCODE_DB` (else `$XDG_DATA_HOME/opencode/opencode.db`, else `~/.local/share/opencode/opencode.db`) holding messages for a session whose directory is this repo and for a child session (`parent_id` set), when the OpenCode reader runs, then `tokens` is folded from each message's JSON as input + output + cache write, with reasoning added once where the store reports it apart from output, cache reads reported apart, child sessions included, and a basis saying subagent spend is included. Fails on: reading the session aggregate columns, which migrated rows leave at zero, or dropping the child session
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py::OpenCodeReaderTests::test_messages_fold_one_basis_with_child_sessions
- **AC2:** Given the fixture database, then it is opened read-only (a `mode=ro` URI and `PRAGMA query_only`), a session in another directory is excluded, and no `opencode` process is started. Fails on: opening the database read-write, or shelling out to `opencode stats`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py::OpenCodeReaderTests::test_read_only_this_repo_and_no_binary
- **AC3:** Given no database and a legacy JSON tree under `storage/message`, then the same messages are read from it on the same basis. Fails on: returning not attributable whenever the database is absent
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py::OpenCodeReaderTests::test_legacy_json_store_reads_the_same_basis
- **AC4:** Given neither store, an empty store or a malformed token value, then the reading is tokens None with a named reason, never zero, whether or not an `opencode` binary is on PATH. Fails on: a missing binary or an empty store becoming zero
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py::OpenCodeReaderTests::test_missing_or_malformed_store_is_not_attributable
- **AC5:** Given a fixture repository and database with `SDLC_STUDIO_HARNESS=opencode`, when `sprint.py plan --write` opens a run, then the baseline it stamps names opencode and the database. Fails on: the reader passing its unit tests while the plan path never reaches it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py::OpenCodeLaneTests::test_plan_write_stamps_an_opencode_baseline

## Notes

- Depends on US0986, and its includes-subagents flag is what US0991 reads to leave `delegated_tokens` out.
- Pin the message JSON shape (where `tokens.reasoning` sits relative to output) from a real OpenCode database at implementation; the development machine holds only OpenCode's log and repos directories today.
- Adds the OpenCode line to the Token meters subsection in `reference-sprint.md`.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- External precondition: Notes require the message JSON shape (where tokens.reasoning sits) to be pinned from a real OpenCode database; ~/.local/share/opencode exists but holds no opencode.db and no storage/ tree (ls 2026-10-21), as the Notes already said on 2026-10-06.
- Release note stale: the story says 'Release: 6.2' but D0382 (2026-10-20, supersedes D0381) sets the path to the 6.2.0 tag as run three plus run four's doc refreshes only, so this lands after 6.2.0; re-tag when a run takes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-06 | Claude Opus 5.5 (engineering seat) | Groomed for the next skill sprint from CR0611 and D0346: OpenCode database read-only, child sessions included, legacy JSON fallback |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
