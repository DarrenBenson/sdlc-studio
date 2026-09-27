# BG0790: An installed release candidate is never prompted to move to its final release, because version comparison ignores the pre-release suffix

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/version_check.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/migrate.py, tools/check_versions.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_prerelease_versions.py, tools/tests/test_check_versions.py, changelog.d/BG0790.md
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T16:24:44Z

## Summary

`version_check._semver` drops a pre-release suffix, so 6.0.0-rc.1 compares equal to 6.0.0: an rc install is not prompted to upgrade, the rc-to-final upgrade digest comes back empty, and migrate stamps a project 6.0.0 rather than 6.0.0-rc.1. Found preparing v6.0.0-rc.1; must be fixed before the v6.0.0 cut.

## Steps to Reproduce

python3 -c 'import `version_check`; print(`version_check._semver(`"6.0.0-rc.1"), `version_check._semver(`"6.0.0"))' from the scripts dir: equal.

## Proposed Fix

Order pre-releases below their final per semver (rc.1 < 6.0.0), and make the upgrade digest and migrate's stamp carry the suffix; tests for each.

## Acceptance Criteria

- [ ] **AC1** Given `version_check._gt`, when versions are compared, then 6.0.0 > 6.0.0-rc.1 > 5.1.0, 6.0.0-rc.10 > 6.0.0-rc.2, and 6.0.0-rc.1 is not newer than itself. Fails on: HEAD's `_semver`, which drops the suffix so 6.0.0-rc.1 reads equal to 6.0.0 (measured), or comparing suffixes as strings, which puts rc.10 below rc.2
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_prerelease_versions.py::PreReleaseVersionTests::test_a_pre_release_orders_below_its_final
  - **Verified:** yes (2026-09-27)
- [ ] **AC2** Given an installed skill whose SKILL.md says 6.0.0-rc.1 and a latest release of 6.0.0, when `version_check` checks, then the status is update-available. Fails on: `installed_version`'s `\d+\.\d+\.\d+` capture, which reads the rc as 6.0.0 and answers up-to-date
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_prerelease_versions.py::PreReleaseVersionTests::test_an_rc_install_is_offered_its_final
  - **Verified:** yes (2026-09-27)
- [ ] **AC3** Given a CHANGELOG with `## [6.0.0]` above `## [6.0.0-rc.1]`, when the upgrade digest runs from 6.0.0-rc.1 to 6.0.0, then it lists 6.0.0's entries only, and from 5.1.0 it lists both. Fails on: `_VER_HEAD_RE`, which does not match the rc heading, so the rc's bullets are read as 6.0.0's
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_prerelease_versions.py::PreReleaseVersionTests::test_the_rc_to_final_digest_holds_only_the_final
  - **Verified:** yes (2026-09-27)
- [ ] **AC4** Given a project stamped `skill_version: "6.0.0-rc.1"` and an installed 6.0.0, when `migrate --apply` runs, then `.version` reads `skill_version: "6.0.0"` and `upgraded_from: 6.0.0-rc.1`; and an installed rc stamps a 5.1.0 project `6.0.0-rc.1`. Fails on: `_read_version`'s `[\d.]+`, which reads the rc stamp as 6.0.0 so `detect` finds nothing to upgrade, or stamping the core without its suffix
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_prerelease_versions.py::PreReleaseVersionTests::test_migrate_stamps_the_exact_version
  - **Verified:** yes (2026-09-27)
- [ ] **AC5** Given package.json at 6.0.0 and SKILL.md at 6.0.0-rc.1, when `tools/check_versions.py --strict` runs, then it exits non-zero naming SKILL.md. Fails on: normalising every home to the semver core (HEAD reports '6.0.0 consistent' over rc.1 homes), which passes a half-bumped cut whose SKILL.md, once AC2 lands, offers the release to itself forever
  - **Verify:** pytest tools/tests/test_check_versions.py::StrictBumpTests::test_a_pre_release_home_beside_a_final_is_named
  - **Verified:** yes (2026-09-27)

## Notes

- Measured at dee380d9: `_semver('6.0.0-rc.1') == _semver('6.0.0')` is True and `installed_version()` returns 6.0.0 for this repo's rc.1 SKILL.md. `latest_release` uses /releases/latest, which excludes pre-releases, so an rc user sees 5.1.0 until 6.0.0 is published; that is correct once ordering is right. Must land before US0926 runs `migrate --apply` here (this repo's `.version` still reads 5.1.0, schema 2) and before the cut. Serialise on migrate.py: BG0790, BG0785, US0960. Ratchet: AC5 tightens an existing check rather than adding one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | Groomed for Sprint 6: five criteria, including the strict version check the fix would otherwise turn into a self-offering release |
