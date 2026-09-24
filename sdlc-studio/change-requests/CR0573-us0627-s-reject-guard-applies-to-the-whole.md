# CR-0573: US0627's REJECT guard applies to the whole existing backlog with no cutoff and no adoption report

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py
> **Evidence:** Stakeholder consult on CR0526's stories, RUN-01M2JA6J 2026-09-15 (sdlc-studio/reviews/consult-CR0526-stakeholders-2026-09-15.md).
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Unlike the dated review.*_after gates, the guard US0627 adds (a unit carrying an unanswered delivery REJECT cannot reach Done or Fixed) has no cutoff key, and neither migrate nor the upgrade path counts the units it will refuse. In this repository 16 bugs at Fixed will refuse Verified or Closed the day it lands.

## Impact

Consuming projects upgrading: their next close refuses units they believed finished, with no warning beforehand.

## Acceptance Criteria

- [ ] migrate and the upgrade path name every unit the unanswered-REJECT guard will refuse, before the guard binds
- [ ] Nothing is forgiven silently: a dated cutoff key exists only if the operator rules for one

## Recommendation

A report line in migrate/upgrade naming the units the guard will refuse (nothing forgiven silently, CR0497's principle); a dated key only if the operator rules for one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - REJECT guard cutoff: US0872 replaced REJECT handling (fixed unit clears, round-2 REJECT carried) |
