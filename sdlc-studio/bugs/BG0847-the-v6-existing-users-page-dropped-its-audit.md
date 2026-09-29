# BG0847: The v6 existing-users page dropped its audit --profile repo mention, so US0242's criterion that four surfaces name the audit on-ramp is red at the release gate

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** docs/existing-users.md, changelog.d/BG0847.md
> **Evidence:** gate.py --root . --release on a fresh clone of 96bd94d1, 2026-09-29: verify lane red on US0242::AC2
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T02:17:02Z

## Summary

US0955 (3a980993) rewrote docs/existing-users.md for v6 and removed the v5 page's 'Reviews: Repository audit (`audit --profile repo`)' row. US0242 AC2 (Done) requires README.md, docs/why-sdlc-studio.md, docs/existing-users.md and SKILL.md to each name `audit --profile repo`; `gate.py --release` on the v6.0.0 release commit 96bd94d1 held it red (3 of 4). Unit reviews run only the unit's own criteria, so the regression surfaced only at the release gate.

## Steps to Reproduce

grep -l 'audit --profile repo' README.md docs/why-sdlc-studio.md docs/existing-users.md .claude/skills/sdlc-studio/SKILL.md lists 3 files, not 4.

## Proposed Fix

Name `audit --profile repo` where it helps a v6 upgrader, for example as the zero-setup way to see what an existing project's history holds before or after migrating, in one sentence; keep the page's other claims as they are.

## Acceptance Criteria

- [ ] **AC1** Given docs/existing-users.md, then it names `audit --profile repo` in a sentence that tells an existing project's reader what the audit is for, and US0242 AC2's Verify passes. Fails on: the v6 page at 3a980993, which names it nowhere
  - **Verify:** shell test $(grep -l "audit --profile repo" README.md docs/why-sdlc-studio.md docs/existing-users.md .claude/skills/sdlc-studio/SKILL.md | wc -l) -eq 4
  - **Verified:** yes (2026-09-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
