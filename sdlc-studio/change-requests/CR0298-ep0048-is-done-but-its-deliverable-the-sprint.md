# CR-0298: EP0048 is Done but its deliverable, the sprint report, is reachable from no command surface or ceremony - an orphaned command

> **Status:** In Progress
> **Decomposed-into:** EP0074
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/help/, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/reference-retro.md, sdlc-studio/epics/EP0048-the-sprint-report-what-a-sprint-delivered-cost.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

RFC0035's motivating gap was 'there is no report command today', and EP0048 is stamped Done - yet the shipped `sprint_report.py` show is wired into nothing anyone runs: no help/ file, no SKILL.md route, no mention in help/retro.md, help/sprint.md or reference-retro.md (the ceremony the report is FOR), and RETRO0041's own gated close loop has no report step; the sole reference is the scripts catalogue line. Per LL0027 the end-of-sprint report will only ever be drawn if someone already knows the module exists - the same lapse mode RFC0042/EP0046 was just shipped to eliminate for the retro. This is a defect in the Done claim's scope, not in-flight incompleteness: all five stories and the epic are closed, the retro filed, and no open artefact carries the wiring (CR0272's command audit predates `sprint_report.py).` US0176's report.enabled gate even presupposes a flow that draws the report. Verified 3x.

## Impact

RFC0035's motivating gap was 'there is no report command today', and EP0048 is stamped Done - yet the shipped `sprint_report.py` show is wired into nothing anyone runs: no help/ file, no SKILL.md route, no mention in help/retro.md, help/sprint.md or reference-retro.md (the ceremony the report is FOR), and RETRO0041's own gated close loop has no report step; the sole reference is the scripts catalogue line.

## Acceptance Criteria

- [ ] The report has a command route (e.g. /sdlc-studio sprint report) with a help/ entry and a SKILL.md table row
- [ ] reference-retro.md's close ceremony includes the report step (drawn when report.enabled)
- [ ] The scripts catalogue entry cross-references the command surface

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
