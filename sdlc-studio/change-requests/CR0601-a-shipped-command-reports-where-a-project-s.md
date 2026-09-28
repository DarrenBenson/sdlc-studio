# CR-0601: A shipped command reports where a project's own docs still name retired v5 surface

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/retired_surface.py, .claude/skills/sdlc-studio/help/upgrade.md, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py
> **Evidence:** soak F16; HEAD 7e53a438 migrate.py docstring (AGENTS/CLAUDE/DoR/DoD only)
> **Date:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:27:07Z

## Summary

migrate reports retired keys and verbs in AGENTS.md, CLAUDE.md and the DoR/DoD only. A v5 project's README, runbooks and CI docs that teach `close --apply-signoff` or `mutation.py register` are left for the user to grep against the CHANGELOG's Breaking inventory. The scanner this repository uses, `retired_surface.py`, lives under scripts/tests and reads the repo's own CHANGELOG.

## Impact

Every v5 upgrader: stale instructions in their own docs survive the migration unseen.

## Acceptance Criteria

- [ ] Given a v5 project whose docs name a retired verb, when migrate runs, then its needs-a-human report lists each file and line with the retired name and its replacement

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Raised |
