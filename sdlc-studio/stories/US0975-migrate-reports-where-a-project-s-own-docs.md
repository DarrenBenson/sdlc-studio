# US0975: migrate reports where a project's own docs name retired v5 surface

> **Status:** Ready
> **Delivers:** CR0592
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/retired_surface.py, .claude/skills/sdlc-studio/scripts/tests/retired_surface.py, .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_retired_docs.py, changelog.d/US0975.md
> **Epic:** EP0270
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** `migrate` to tell me which lines of my own README and runbooks still teach a v5 command that v6 retired
**So that** I do not have to grep my docs against the CHANGELOG's Breaking inventory

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0601, merged into CR0592, 3 points. `migrate` reports retired keys and verbs only in AGENTS.md, CLAUDE.md and the DoR/DoD. The scanner this repository uses, `retired_surface.py`, lives under `scripts/tests/` and reads this repository's CHANGELOG, so it cannot ship.

The fix moves the scanner to `scripts/lib/retired_surface.py`, deriving verbs, config keys and check ids from the shipped registries it already reads (`RETIRED_VERBS`, `sdlc_md.RETIRED_CONFIG_KEYS`, `sdlc_md.RETIRED_CHECK_IDS`). `scripts/tests/retired_surface.py` becomes a thin import that adds the CHANGELOG's retired-flag tables for this repository's own doc tests, so the existing importers do not change. `migrate` scans the project's tracked markdown outside `sdlc-studio/` and the skill directory, excluding CHANGELOG.md (history names retired surface on purpose), and lists each hit as `file:line` with the retired name under its existing needs-a-human list. It never rewrites a project file. No new report section, flag or refusal.

## Premise at HEAD

Executed at `85042135` in a scratch project after `init.py run`, whose README.md line 3 reads "After review run `mutation.py register` then `sprint.py close --apply-signoff`.":

```text
$ python3 migrate.py --root . | grep -c README
0
$ python3 -c "import retired_surface; print(retired_surface.live_mentions(open('README.md').read())[:2])"   # scripts/tests on sys.path
[(3, 'mutation.py register', ...), (3, 'sprint.py close --apply-signoff', ...)]
```

## Acceptance Criteria

- [ ] **AC1** Given a fixture project whose README.md line 3 names `mutation.py register` and `sprint.py close --apply-signoff`, when `migrate.py --root <fixture>` runs, then its needs-a-human list names `README.md:3` with both retired names, and README.md is byte-identical afterwards, with and without `--apply`. Fails on: HEAD's migrate names no README line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_retired_docs.py::MigrateRetiredDocsTests::test_migrate_names_each_retired_line_and_rewrites_nothing
  - **Verified:** yes (2026-10-01)
- [ ] **AC2** Given the shipped skill with no CHANGELOG.md beside it, when `scripts/lib/retired_surface.py` is imported, then `live_mentions` finds a retired verb and a retired config key, and `scripts/tests/retired_surface.py` holds no second list of them. Fails on: HEAD's only copy lives under `scripts/tests/` and reads the repository's CHANGELOG
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_retired_docs.py::MigrateRetiredDocsTests::test_the_scanner_ships_and_needs_no_changelog
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
