# CR-0270: RFC0038 U7: stamp project and points on every evidence record, so cross-project data is collatable and never blindly pooled

> **Status:** Complete
> **Size:** S
> **Priority:** P1
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Verification depth:** functional - attacked through the public path: a freshly recorded actual carries `project` stamped automatically from the git remote (no argument passed); all 26 measured actuals backfilled value-for-value with velocity numbers unchanged; and `collate_rate` across two projects at 25k/pt and 150k/pt REFUSES a pooled figure and segments per (project, model) cell.
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

The operator will run the forward-ported skill on several projects and pool the data to tune the model. That is the evidence base this whole workstream needs - N=22 on one project and one model is a hypothesis, not a calibration. But the record must carry the right fields BEFORE the data flows, because a measurement is taken once and cannot be backfilled (the BG0133 principle: record it when you make it).

Today a measured evidence record carries id, type, model, tokens, `wall_time_s`, iterations, `critic_verdict.` It does NOT carry the PROJECT. The instant two projects pool into one place, a unit from sdlc-studio is indistinguishable from a unit from another repo, and every cross-project figure is unattributable.

SEQUENCING IS THE SHARP POINT. If the forward-ported copy does not already stamp `project`, the operators FIRST WAVE of data comes back with no project on it, and it is unattributable forever. So this lands in THIS workstream, before the forward-port - not in the analysis phase after.

AND THE COLLATION MUST SEGMENT, NEVER POOL BLINDLY. This is the lesson this project paid for twice in two days: `files_affected` flipped sign between cohorts (LL0035) and the presence of a field became a calendar artefact. A points-vs-cost correlation pooled across a fast project and a slow one, or across two models, describes neither. The correlation must be computed WITHIN each (project, model) cell and reported per cell. tokens-per-point is a per-(project, model) rate, not a global constant.

## Impact

The entire cross-project tuning exercise. Without project on the record the pooled data cannot be attributed; without per-cell segmentation the pooled correlation repeats the exact confounds that produced two withdrawn findings this week. This is the difference between the multi-project run producing evidence and producing noise.

**Points:** 3

## Acceptance Criteria

- [ ] Every evidence record (forecast and actual) carries the project it was produced in, stamped at write time from the repo, so records pooled from several projects remain attributable.
- [ ] points is carried on the record too (from CR0267), so a pooled row has size, cost, model and project together - everything a per-cell correlation needs.
- [ ] The tokens-per-point rate is computed and reported PER (project, model), never as a single pooled number. A correlation across two projects or two models is segmented or refused, exactly as a cross-model accuracy ratio already is (CR0263).
- [ ] A collation reads evidence from several project directories, keeps each records project and model, and reports per-cell - so the multi-project data can tune the model without repeating the cohort confound (LL0035).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
