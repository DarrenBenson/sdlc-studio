# BG1509: release_cut never restamps the releasing repository's own sdlc-studio/.version, so each release needs a hand migrate --apply and CI's corpus check reds on US0926::AC1 until it gets one

> **Status:** Won't Fix
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/templates/workflows/release-gate.md, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:51:38Z

## Summary

The cut moves the skill's version, but this repository's own sdlc-studio/.version stays at the previous release. 6.1, 6.2, 6.3 and 6.4 each needed `migrate --apply` by hand after the cut (6.4: D0500, commit cd0e478e). Until then the scheduled corpus check (gate.py --release) reds on US0926::AC1.

## Steps to Reproduce

1. Cut a release with `release_cut.py.`
2. Read sdlc-studio/.version: `skill_version` still names the previous release.
3. Run gate.py --release: US0926::AC1 is red until migrate --apply runs.

## Proposed Fix

Have the cut restamp .version (`skill_version` and `upgraded_from)` in the same change that moves the version, or have tag-check refuse while .version names an older release, naming the command that fixes it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The cut moves the skill's version, but this repository's own sdlc-studio/.version stays at the previous release.
- [ ] **AC2** The proposed fix lands, pinned by a test: Have the cut restamp .version (`skill_version` and `upgraded_from)` in the same change that moves the version, or have tag-check refuse while .version names an...

## Impact

Every release spends a commit, a push gate and a CI cycle on paperwork the cut could have written.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |

## Resolution

Duplicate of BG1301, which is still Open and describes the same fault; this is its fourth recurrence (6.1, 6.2, 6.3, 6.4; for 6.4 the hand fix was D0500, cd0e478e). Filed after the v6.4.0 tag and closed as Won't Fix so BG1301 carries the work.
