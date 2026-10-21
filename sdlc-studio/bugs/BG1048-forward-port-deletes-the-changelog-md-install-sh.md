# BG1048: forward-port deletes the CHANGELOG.md install.sh ships into the installed copy

> **Status:** Superseded
> **Superseded by:** BG0986
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/forward-port.sh, tools/tests/test_forward_port.py
> **Evidence:** forward-port dry run on 2026-10-14 listed '*deleting CHANGELOG.md' (installed copy written 2026-10-09 by install.sh, 1441693 bytes); install.sh:487-495 ship_changelog.
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T12:01:10Z

## Summary

install.sh's `ship_changelog` copies the repository's root CHANGELOG.md into the installed skill directory, so `project upgrade` can digest the changes between a project's recorded version and the installed one offline. tools/forward-port.sh mirrors .claude/skills/sdlc-studio/ with `rsync --delete`, and the skill source holds no CHANGELOG.md, so every port deletes the shipped one and `--check` (and the close's installed-copy step) counts its presence as drift. After a port, `project upgrade` in every other project on the machine falls back to its no-changelog message until install.sh runs again.

## Steps to Reproduce

With an installed copy written by install.sh, run `bash tools/forward-port.sh`: the dry run lists '*deleting CHANGELOG.md'.

## Proposed Fix

Ship the changelog as install.sh does: after the rsync, copy the repository's root CHANGELOG.md into the target, and exclude it from the sweep and from --check's comparison.

## Acceptance Criteria

- [ ] **AC1** Given an installed copy holding the CHANGELOG.md install.sh shipped, when forward-port runs with --yes and then --check, then the copy holds the repository's current CHANGELOG.md and --check reports no drift.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): superseded by BG0986: duplicate of BG0986, the same forward-port defect; its changelog-drift point is BG0986's AC3 |
