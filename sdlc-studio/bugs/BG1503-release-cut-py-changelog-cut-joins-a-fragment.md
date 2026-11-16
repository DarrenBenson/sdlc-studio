# BG1503: release_cut.py changelog-cut joins a fragment that does not start with a bullet onto the entry above it, so about 60 of 6.4.0's 131 entries run together in CHANGELOG.md

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, CHANGELOG.md, changelog.d/BG1503.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) US1173 QA verdict c77c085cb9be-4ee4be50, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T07:25:15Z

## Summary

Run fifteen's QA seat found, approving the v6.4.0 cut (US1173, verdict c77c085cb9be-4ee4be50), that 6.4.0's CHANGELOG section holds 75 bullets for 131 fragments: a fragment written as plain prose, with no leading list bullet, is appended to the entry above it, so about 60 units' entries read as part of another unit's. Nothing at authoring time (the fragment lane, the self-check, the commit hook) requires a fragment to open with a bullet, and changelog-cut neither adds one nor refuses. A reader of the release's CHANGELOG cannot tell which change belongs to which unit for those entries.

## Steps to Reproduce

awk the 6.4.0 section of CHANGELOG.md and count lines starting with '- ' (75) against the 131 fragments the cut folded.

## Proposed Fix

Have changelog-cut start every fragment on its own bullet (adding a list bullet to a fragment that lacks one) or refuse a fragment that does not open with one, and have the fragment lane check new fragments the same way; then re-cut 6.4.0's section so each unit's entry stands alone before the tag.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run fifteen's QA seat found, approving the v6.4.0 cut (US1173, verdict c77c085cb9be-4ee4be50), that 6.4.0's CHANGELOG section holds 75 bullets for 131...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: awk the 6.4.0 section of CHANGELOG.md and count lines starting with '- ' (75) against the 131 fragments the cut folded.
- [ ] **AC3** The proposed fix lands, pinned by a test: Have changelog-cut start every fragment on its own bullet (adding a list bullet to a fragment that lacks one) or refuse a fragment that does not open with one, and have...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
