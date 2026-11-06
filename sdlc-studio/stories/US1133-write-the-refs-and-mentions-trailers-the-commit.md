# US1133: Write the Refs and Mentions trailers the commit-msg hook now refuses for

> **Status:** Ready
> **Delivers:** CR0681
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py, tools/tests/test_commit_msg_hook.py, tools/tests/test_commit_msg_mentions.py, tools/enable-hooks.sh, AGENTS.md, changelog.d/US1133.md
> **Epic:** EP0300
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Write the Refs and Mentions trailers the commit-msg hook now refuses for
**So that** a multi-id commit lands at its first attempt with the same attribution the Affects fields already hold, instead of costing the orchestrator a refusal and a retry

## Acceptance Criteria

- **AC1:** Given a subject naming two ids that each own a staged file by their Affects and no trailer, when the commit-msg hook runs, then it writes one `Refs: <id>` per owning id into the message and the commit lands at the first attempt (a replay of the BG1213 landing). Fails on: `message-refs` still refusing a message the staged-file map can attribute.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::DerivedTrailerTests::test_owning_ids_get_refs_written_and_the_commit_lands
- **AC2:** Given a subject naming an id that owns none of the staged files, then the hook writes `Mentions: <id>` for it, never `Refs:`. Fails on: writing `Refs:` for every id the subject names.
  - **Verify:** pytest tools/tests/test_commit_msg_mentions.py::DerivedMentionsTests::test_a_non_owning_id_gets_mentions
- **AC3:** Given a message whose existing `Refs:` trailer names an id that owns none of the staged files, then `message-refs` refuses naming that id; a trailer that matches ownership passes unchanged and is never written twice. Fails on: the lane deleted outright, or a correct trailer duplicated.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::DerivedTrailerTests::test_a_trailer_that_contradicts_ownership_is_refused
- **AC4:** Given a consuming project's commit message file, when `engagement_floor.py check-commit-msg --write-trailers <file>` runs, then it appends the derived trailers by the same rule, and `AGENTS.md`'s refusals table and `tools/enable-hooks.sh` describe the hook as writing them. Fails on: the derivation living only in this repository's hook.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CommitMsgCheckTests::test_write_trailers_appends_from_ownership

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria and Verify checks authored |
