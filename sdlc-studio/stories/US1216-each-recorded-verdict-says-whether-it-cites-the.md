# US1216: Each recorded verdict says whether it cites the file history

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0679
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0331
> **Points:** 1
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Each recorded verdict says whether it cites the file history
**So that** CR0679 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A recorded verdict says whether it cites the file history

- **Given** a full-tier verdict file one of whose findings cites the brief's FILE HISTORY section, a second that cites nothing from it, and a light-tier verdict whose brief carried no FILE HISTORY
- **When** each is recorded with `critic.py record --from-verdict` and read back with `critic.py show`
- **Then** the first row says it cites the file history, the second says it does not, and the third says the brief carried none. Fails on: a row that records nothing either way, or a light-tier row counted as a full-tier review that did not cite it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FileHistoryCitationTests::test_each_recorded_verdict_says_whether_it_cites_the_file_history

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
