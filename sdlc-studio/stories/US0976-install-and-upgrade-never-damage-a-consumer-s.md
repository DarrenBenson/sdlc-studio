# US0976: Install and upgrade never damage a consumer's files

> **Status:** Ready
> **Delivers:** CR0592
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, install.sh, tools/tests/test_lean_consumer_files_preserved.py, changelog.d/US0976.md
> **Epic:** EP0270
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** `init --force`, `migrate --apply` and `install.sh` to leave my own files as I left them
**So that** re-scaffolding or upgrading never costs me my version record, my line endings, my symlink or my notes

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0592 bullets 42, 65 (parts 1 and 2 only; parts 3-5 rejected as pin residue) and 66, 3 points.

- #42 `init.py run --force` rewrites `sdlc-studio/.version` with the current version, erasing the version the project was created at, which the version check compares against.
- #65 migrate's `sdlc-studio/.gitignore` append reads through universal newlines and writes LF, so a CRLF file becomes a whole-file diff; and its `os.replace` writes a regular file over a symlinked `.gitignore`, leaving the link's target unchanged.
- #66 `install.sh --target copilot` over an `sdlc-studio/` folder holding only a user's `notes.txt` removes it at exit 0. The sweep already skips such a folder with `no sdlc-studio SKILL.md - not touching it`; the explicit install will skip it the same way.

## Premise at HEAD

Executed at `85042135` in a scratch project after `init.py run`, with `.version` edited to `skill_version: "5.0.0"`:

```text
$ python3 init.py run --root . --force; echo exit=$?
exit=0
$ grep skill_version sdlc-studio/.version
skill_version: "6.0.0"
```

## Acceptance Criteria

- [ ] **AC1** Given an initialised fixture whose `.version` records `skill_version: "5.0.0"`, when `init.py run --force --root <fixture>` runs, then `.version` still records `5.0.0`. Fails on: HEAD rewrites it to `6.0.0` (premise)
  - **Verify:** pytest tools/tests/test_lean_consumer_files_preserved.py::ConsumerFilesPreservedTests::test_init_force_keeps_the_version_record
- [ ] **AC2** Given a fixture whose `sdlc-studio/.gitignore` uses CRLF, and a second whose `.gitignore` is a symlink, when `migrate.py --apply --root <fixture>` appends the runtime-dir rule, then the first keeps CRLF on every line and the second stays a symlink whose target now holds the rule. Fails on: HEAD writes LF and replaces the symlink with a regular file
  - **Verify:** pytest tools/tests/test_lean_consumer_files_preserved.py::ConsumerFilesPreservedTests::test_the_gitignore_append_keeps_endings_and_links
- [ ] **AC3** Given `HOME` pointed at a fixture whose `.agents/skills/sdlc-studio/` holds only `notes.txt`, when `bash install.sh --target copilot --from <skill dir>` runs, then `notes.txt` survives and the installer prints the sweep's `no sdlc-studio SKILL.md - not touching it` warning for that folder. Fails on: HEAD removes `notes.txt` and exits 0
  - **Verify:** pytest tools/tests/test_lean_consumer_files_preserved.py::ConsumerFilesPreservedTests::test_an_explicit_install_skips_a_foreign_folder

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
