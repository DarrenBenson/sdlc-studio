# BG0808: init records no project version, so a fresh project's first migrate reports work and its upgrade digest reads the range as unknown

> **Status:** Open
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_init_version.py, changelog.d/BG0808.md
> **Severity:** Medium
> **Points:** 1

## Summary

`init.py run` writes no `sdlc-studio/.version`. On a project it has just created, `migrate` at once reports '1 deterministic upgrade(s) would apply: no sdlc-studio/.version', and `project_upgrade`'s capability digest has no recorded version, so after the skill moves (rc.1 to 6.0.0, or 6.0 to 6.1) it prints 'version range unknown' instead of what changed. Every project initialised on v6, the website's included, meets this at its first upgrade.

## Steps to Reproduce

In an empty scratch directory: `git init`, then `python3 <skill>/scripts/init.py --root . run`, then `python3 <skill>/scripts/migrate.py --root .`: the first deterministic item is '[conventions] no sdlc-studio/.version'. `ls sdlc-studio/.version` fails. Reproduced 2026-09-27 at dee380d9.

## Proposed Fix

`init run` stamps `sdlc-studio/.version` through the writer `migrate --apply` already uses, with the running skill's version including any pre-release suffix (BG0790) and the schema it seeded.

## Acceptance Criteria

- [ ] **AC1** Given an empty git repository, when `init.py run` and then `migrate.py` run, then `sdlc-studio/.version` names the installed skill version with its pre-release suffix and `migrate` reports no deterministic upgrade for the version. Fails on: HEAD, where init writes no .version and the fresh project's first migrate reports a missing one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_init_version.py::InitVersionTests::test_init_stamps_the_skill_version
- [ ] **AC2** Given a project initialised at 6.0.0-rc.1 and the skill then at 6.0.0, when `project_upgrade` renders its digest, then it names the range 6.0.0-rc.1 to 6.0.0 and lists 6.0.0's entries. Fails on: HEAD's 'version range unknown (recorded ?, installed 6.0.0)'
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_init_version.py::InitVersionTests::test_a_fresh_project_gets_its_upgrade_digest

## Notes

- Depends on: BG0790
- Found by the product seat rehearsing `init` for the website soak (scratch copy, dee380d9). The website project is initialised on rc.1 and reinstalled at 6.0.0 inside this release, so without this fix its first upgrade shows nothing. Depends on BG0790 for the suffix and the rc-to-final ordering.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0808) |
