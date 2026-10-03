# BG0941: US0937 AC3 pins BG0717's 'Verified: yes' stamp, which US0978 retired, so the release gate reads it red

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/stories/US0937-work-that-already-shipped-reads-done-so-the.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T20:41:30Z

## Summary

US0937::AC3's shell check ends by requiring '- **Verified:** yes' in BG0717's file. US0978 (4ebc34b8) retired BG0717's criterion with the handoff writers and restamped it 'Verified: manual (2026-10-01) - retired, superseded by US0978', so gate.py --release reads US0937::AC3 red at the v6.1.0 cut. The pin still holds what it was written for - BG0717 is terminal - but not the stamp. LC-015 (a retirement outruns the deletion): the retirement left a criterion that pins the retired stamp.

## Steps to Reproduce

1. gate.py --release on 7c83e26c. 2. verify lane: US0937::AC3 red. 3. BG0717's Verified line reads 'manual ... retired, superseded by US0978'.

## Proposed Fix

Re-point US0937 AC3's last check to accept either a 'yes' stamp or US0978's retirement stamp on BG0717, keeping every other check in the criterion as written. No code change.

## Acceptance Criteria

- [ ] **AC1** Given BG0717 stamped 'Verified: manual ... retired, superseded by US0978', when US0937 AC3's Verify runs, then it passes, and a BG0717 with no Verified line at all, or a non-terminal status, still fails it. Fails on: the current criterion, which requires 'Verified: yes'
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --ids US0937 | grep -q 'fail=0'
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
