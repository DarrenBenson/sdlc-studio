# US0974: A v5 upgrade reads clean

> **Status:** Ready
> **Delivers:** CR0592
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_v5_upgrade_clean.py, changelog.d/US0974.md
> **Epic:** EP0270
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** `migrate` on an up-to-date v5 project to report nothing I need to act on, and to name the file when it cannot read one
**So that** a clean upgrade reads clean and a broken file can be found

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0592 bullets 31, 60 and 64, 3 points.

- #31 `sdlc_md.parse_cutoff` raises `ValueError` on a ULID id such as `BG-01KX95QP`, so on schema v3 (the v6 init default) the `adopt_after` remedy that the conformance and engagement-floor lanes name cannot be written.
- #60 a standard directory not yet created (`retros`, project_upgrade.py:439) is listed under needs-a-human although its own text says it is created on first use, so an up-to-date project never reports zero.
- #64 `migrate.py --format json` on a non-UTF-8 or unreadable story exits 1 with a raw traceback, no JSON and no file name.

## Premise at HEAD

Executed at `85042135` in a scratch project after `init.py run`, with a story file holding the bytes `\xff\xfe`:

```text
$ python3 migrate.py --format json --root .
...
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 33: invalid start byte
exit=1
```

## Acceptance Criteria

- [ ] **AC1** Given a schema v3 fixture whose config sets `conformance.adopt_after: BG-01KX95QP`, when `conformance.py check --root <fixture>` runs, then it raises no `ValueError` and exempts a unit whose ULID sorts at or before the cutoff. Fails on: HEAD `parse_cutoff('BG-01KX95QP')` raises `ValueError`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v5_upgrade_clean.py::V5UpgradeCleanTests::test_a_ulid_cutoff_is_accepted
- [ ] **AC2** Given an up-to-date fixture with no `sdlc-studio/retros/`, when `migrate.py --root <fixture>` runs, then the missing directory is not listed under needs-a-human. Fails on: HEAD lists `no retros dir(s) - created when you first use them` there
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v5_upgrade_clean.py::V5UpgradeCleanTests::test_an_unused_standard_dir_needs_no_human
- [ ] **AC3** Given a story file holding non-UTF-8 bytes, when `migrate.py --format json --root <fixture>` runs, then stdout parses as JSON naming that file as unreadable and no traceback is printed. Fails on: HEAD exits 1 with `UnicodeDecodeError` and empty stdout (premise)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v5_upgrade_clean.py::V5UpgradeCleanTests::test_an_unreadable_story_is_named_in_the_json

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
