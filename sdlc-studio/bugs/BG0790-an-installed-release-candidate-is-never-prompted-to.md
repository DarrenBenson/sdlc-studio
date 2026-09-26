# BG0790: An installed release candidate is never prompted to move to its final release, because version comparison ignores the pre-release suffix

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/version_check.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_version_check.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py
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

- [ ] **AC1** The behaviour described is corrected: `version_check._semver` drops a pre-release suffix, so 6.0.0-rc.1 compares equal to 6.0.0: an rc install is not prompted to upgrade, the rc-to-final upgrade...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: python3 -c 'import `version_check`; print(`version_check._semver(`"6.0.0-rc.1"), `version_check._semver(`"6.0.0"))' from the scripts dir: equal.
- [ ] **AC3** The proposed fix lands, pinned by a test: Order pre-releases below their final per semver (rc.1 < 6.0.0), and make the upgrade digest and migrate's stamp carry the suffix; tests for each.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
