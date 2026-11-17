# CR-0708: file_finding writes criteria a plan can take, or marks a bug ungroomed, instead of truncated stubs with no Verify line

> **Status:** In Progress
> **Decomposed-into:** EP0348
> **Priority:** Medium
> **Type:** Enhancement
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run fourteen grooming at 8abcfb17: 60 open bugs hold derived stub criteria.
> **Date:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:23:34Z

## Summary

When a finding is filed without --ac, `file_finding.py` (near lines 847-851) derives criteria from the summary, truncated with an ellipsis and with no Verify line. Sixty open bugs carry these stubs. Each must be groomed by hand before a sprint can take it, and nothing on the bug says so: it reads as groomed until a grooming pass opens it (BG1260 in the run-fourteen grooming).

## Impact

Grooming cost on every filed bug, and bugs that look sprint-ready but are not, against Abena Osei's End goal 3 (cost per point).

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Proposed Fix

Either refuse a bug filed with no criteria unless --ungroomed is given, or mark derived criteria with a status the plan's readiness check reports (for example 'Groomed: no'), and have `sprint.py breakdown` list them as needing criteria.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Raised |
