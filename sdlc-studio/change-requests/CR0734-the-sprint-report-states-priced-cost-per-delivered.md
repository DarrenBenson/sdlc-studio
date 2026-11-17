# CR-0734: The sprint report states priced cost per delivered line beside cost per point

> **Status:** In Progress
> **Decomposed-into:** EP0371
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/sprint.md, tools/tests/test_sprint_report_cost_per_line.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** competitor review 2026-11-17: published accounts of a commercial autonomous-delivery platform (Blitzy), chiefly its CEO and CTO interview on The Cognitive Revolution (January 2026) and the Quesma audit of its SWE-Bench Pro run; compared against this skill by grep
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T21:37:58Z

## Summary

The sprint report prices a run per story point. Points are this project's own unit, so the figure cannot be set against anything outside it. Commercial autonomous-delivery platforms price on finalised lines of output (one publishes about 20 cents a line, and quotes 10 to 15 dollars a line for a conventional enterprise cycle). The report already holds the run's priced cost and its commits; counting the lines those commits added and removed in the files the batch's units declare gives a second, externally comparable figure at no model cost.

## Impact

Anyone judging whether the skill is cheap or dear against a vendor quote or an internal baseline; today there is no common unit.

## Acceptance Criteria

- [ ] The report states lines added and lines removed over the run's commits, counted only in files the batch's units declare in Affects, with artefact and changelog paths excluded and the exclusion named
- [ ] The report states priced cost per delivered line (added plus removed) beside cost per point, and omits the figure with a reason when the run has no priced cost or no counted lines
- [ ] The figure is recomputable: the report names the commit range it counted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
