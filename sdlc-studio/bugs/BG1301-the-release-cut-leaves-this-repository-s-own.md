# BG1301: The release cut leaves this repository's own sdlc-studio/.version on the previous release, so `gate.py --release` refuses US0926::AC1 at every cut and the tagged commit moves

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Evidence:** devserver1 release gate on ed79b0d9, 2026-11-08: verify lane, 1 red AC, US0926::AC1; commits df925563, 089008d5, 8346763c
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T00:06:58Z

## Summary

`release_cut.py changelog-cut` and the cut's version bump move the skill's version (templates/version.yaml, SKILL.md, CHANGELOG), and tools/`check_versions.py` agrees them, but neither touches the repository's own project stamp, sdlc-studio/.version. US0926::AC1 (this repository runs on the shipped defaults) requires `migrate.py` to report 0 deterministic upgrades, so the first `gate.py --release` after each cut refuses with "sdlc-studio/.version stale". It has happened at three releases running: df925563 restamped it for 6.1.0, 089008d5 for 6.2.0, and 8346763c for 6.3.0. Each costs a paperwork commit after the cut, a new push gate (about 18 minutes on devserver1) and a second release gate (about 21 minutes), because the commit to tag moves.

## Steps to Reproduce

At a724f953 (the 6.3.0 cut), run `python3 .claude/skills/sdlc-studio/scripts/migrate.py`: "1 deterministic upgrade(s) would apply ... sdlc-studio/.version stale (skill 6.2.0 -> 6.3.0)". `gate.py --release` on ed79b0d9 refused on US0926::AC1 alone.

## Proposed Fix

Have the cut restamp this repository's sdlc-studio/.version as part of the release commit (through `migrate.py --apply`'s conventions step, not a hand edit), or have `release_cut.py changelog-cut` refuse to finish while `migrate.py` reports a deterministic upgrade, naming the command to run.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `release_cut.py changelog-cut` and the cut's version bump move the skill's version (templates/version.yaml, SKILL.md, CHANGELOG), and tools/`check_versions.py`...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: At a724f953 (the 6.3.0 cut), run `python3 .claude/skills/sdlc-studio/scripts/migrate.py`: "1 deterministic upgrade(s) would apply ...
- [ ] **AC3** The proposed fix lands, pinned by a test: Have the cut restamp this repository's sdlc-studio/.version as part of the release commit (through `migrate.py --apply`'s conventions step, not a hand edit)...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
