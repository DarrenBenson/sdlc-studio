# US0990: A Cursor CLI run records its token actual from the store the CLI persists, or says why it cannot

> **Status:** Draft
> **Delivers:** CR0611
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/US0990.md
> **Epic:** EP0274
> **Points:** 3
> **Depends on:** US0986, US0989
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer running a sprint from the Cursor CLI on my own machine (Maya)
**I want** the close to read the usage the CLI persists, or to say plainly that it kept none
**So that** a local Cursor sprint is measured when it can be, and never shown a guessed figure when it cannot

## Acceptance Criteria

- **AC1:** Given a fixture derived from the session store the current Cursor CLI writes for this repo, when it records usage, then the reader returns input + output + cache write with cache reads apart, and the source names the store. Fails on: a hard-coded guessed path with no fixture taken from a real store
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorCliTests::test_persisted_usage_counts_one_basis
- **AC2:** Given a CLI session that persisted no usage (interactive or ACP mode, or a print run whose stdout has gone), then the reading is tokens None and the reason says the CLI kept no usage record, never zero, and no terminal output is scraped. Fails on: an absent record read as zero
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorCliTests::test_no_persisted_usage_is_not_attributable
- **AC3:** Given both a cloud key and run id and a CLI store, then the cloud reading alone is used; given only the CLI store, the CLI reading alone; the two surfaces are never added together. Fails on: summing the cloud total and the CLI store for the same run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorCliTests::test_cloud_and_cli_surfaces_are_never_mixed

## Notes

- Depends on US0989 (same module). A Cursor CLI store exists on the development machine under `~/.cursor/projects/<slug>/`; read it at implementation to pin what, if anything, it records about usage.
- If the pinned store keeps no usage at all, AC1 is re-groomed with a note saying so before the build, and the story delivers AC2 and AC3.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-06 | Claude Opus 5.5 (engineering seat) | Groomed for the next skill sprint from CR0611 and D0346: the store the Cursor CLI persists, pinned from a real store, never mixed with the cloud API |
