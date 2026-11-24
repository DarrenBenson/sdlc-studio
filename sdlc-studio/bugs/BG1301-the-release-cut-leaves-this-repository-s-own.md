# BG1301: The release cut leaves this repository's own sdlc-studio/.version on the previous release, so `gate.py --release` refuses US0926::AC1 at every cut and the tagged commit moves

> **Status:** Won't Fix
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

- [ ] **AC1** Given a project whose `sdlc-studio/.version` names the previous release while the shipped skill is at the version being cut, so `migrate.py` reports one deterministic upgrade, when `release_cut.py changelog-cut --version <that version>` runs, then it does not exit 0 with the stamp still stale: either the stamp is rewritten by migrate's own step and `migrate.py` then reports none, or the cut exits 2 with the changelog untouched, naming the `migrate.py --apply` to run. Fails on: a finished cut after which `migrate.py` still reports 'sdlc-studio/.version stale'.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::ChangelogCutTests::test_a_cut_never_finishes_over_a_stale_project_stamp
- [ ] **AC2** Given a project whose stamp already names the shipped skill version, when `changelog-cut` runs, then the section is cut as today and `sdlc-studio/.version` is byte-identical. Fails on: a cut that rewrites or refuses over a current stamp.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::ChangelogCutTests::test_a_current_stamp_is_left_as_it_was_and_the_cut_succeeds

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because it lies in this repository's own CI, hooks or tools, which the installed skill does not ship. This repository's own .version at the release cut.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
