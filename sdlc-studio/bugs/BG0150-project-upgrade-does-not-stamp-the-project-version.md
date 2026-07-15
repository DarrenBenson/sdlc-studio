# BG0150: project upgrade does not stamp the project version and skips open RFCs/CRs/epics/stories

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/project_upgrade.py
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Operator-reported: running project upgrade on an existing consuming project added personas but left the project version number missing, and did not review or update any open RFCs, CRs, epics or stories. Behaviour observed on a consuming project; investigate `project_upgrade`'s version-stamp step.

## Steps to Reproduce

Run project upgrade on a consuming project that predates the current version and carries open RFCs/CRs/epics/stories.

## Root Cause

`project_upgrade.apply()` computed `installed = version_check.installed_version(...) or "unknown"`.
`installed_version` reads the `version:` field from the installed skill's `SKILL.md` frontmatter and
returns `None` when it is missing or unparseable (a partial/old install). The `or "unknown"` fallback
then silently stamped `skill_version: "unknown"` into `sdlc-studio/.version` - which reads to the
operator as "the version is missing/wrong" and corrupts the metadata that skill-update and migrate
compare against. (The dry-run detection was already correctly guarded with `installed and ...`, so
only the apply write path fabricated the value.)

## Proposed Fix

When the installed skill version cannot be resolved, do NOT stamp a bogus `"unknown"`: append a loud
warning ("could not read the installed skill version ... .version was NOT stamped") and SKIP the
version write. An honest, fixable gap beats a fabricated value. The normal path (a resolvable
version) is unchanged. The broader open-artefact sweep is the migrate RFC's scope; this bug is
scoped to the version stamp.

- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_project_upgrade.ApplyTests.test_unresolvable_skill_version_warns_and_does_not_stamp_unknown tests.test_project_upgrade.ApplyTests.test_real_version_still_stamps_after_the_guard

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
| 2026-07-15 | sdlc-studio | Root cause found (installed_version None -> silent "unknown" stamp) and fixed (warn + skip); regression tests added |
