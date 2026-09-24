# US0894: The close-owed report walks the corpus once, not once per epic

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_owed_cache.py
> **Epic:** EP0262
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** developer committing and closing sprints on a large artefact corpus
**I want** `close_owed` to read the artefact corpus once per report instead of once per epic
**So that** `close_owed detect` drops from 55s to under a second with the same answer, and the doc-freshness lane and test_close_owed stop being the long pole

## Acceptance Criteria

- **AC1:** Given a fixture with 20 epics and their stories, when `close_owed.owed` runs once, then the artefact tree is walked once for that call however many epics it holds - `children_of` no longer re-reads every file per epic (201 calls and 515k reads on this repository)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_owed_cache.py::CloseOwedCacheTests::test_one_call_walks_the_corpus_once
- **AC2:** Given a fixture with covered, grandfathered, epic-inherited and dead-id cases, when `close_owed.py detect --format json` runs, then its output is byte-identical to the same computation with the corpus cache off
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_owed_cache.py::CloseOwedCacheTests::test_the_report_is_byte_identical_to_the_uncached_walk
- **AC3:** Given a retro covering an owed unit written between two calls in one process, then the second call no longer lists that unit - the cache lives for one call, never for the process
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_owed_cache.py::CloseOwedCacheTests::test_a_write_between_calls_is_seen

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
