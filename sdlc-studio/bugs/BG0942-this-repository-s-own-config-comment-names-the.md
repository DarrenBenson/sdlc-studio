# BG0942: This repository's own config comment names the retired review.policy key, so US0926 AC1 reads red at the release gate

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/.config.yaml
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T21:25:11Z

## Summary

sdlc-studio/.config.yaml line 71 carries a comment explaining that 'review.policy' was retired by BG0831. US0926 AC1 checks that the repository's config names no retired key, comments included, so gate.py --release read it red on d52c7285 at the v6.1.0 cut. The comment's meaning is right; naming the key literally is what trips the check.

## Steps to Reproduce

1. gate.py --release on d52c7285. 2. verify lane: US0926::AC1 red. 3. The check's first half finds review.policy at .config.yaml:71.

## Proposed Fix

Reword the comment to describe the retired review policy setting without naming the key, keeping its reason and its BG0831 reference. No code change.

## Acceptance Criteria

- [ ] **AC1** Given this repository's .config.yaml, when US0926 AC1's Verify runs, then it passes, and the comment still says the review policy setting was retired by BG0831 and why. Fails on: the current comment naming review.policy
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --ids US0926 | grep -q 'fail=0' && grep -q 'BG0831' sdlc-studio/.config.yaml
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
