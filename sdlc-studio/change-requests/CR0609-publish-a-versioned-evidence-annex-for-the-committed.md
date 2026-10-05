# CR-0609: Publish a versioned evidence annex for the committed sprint records

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py
> **Date:** 2026-10-05
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-05T15:44:18Z

## Summary

`reference-schema.md` contracts only the markdown artefacts and names 'a future separately versioned annex' as the route for evidence consumers. A consumer such as sdlc-studio-lens now needs that annex: the report of record (`reports/RPT####.json`), the signed run record (`reports/runs/RUN-*.json`), `lessons.jsonl`, `retros/evidence/{actuals,forecasts,audit-cost}-*.jsonl`, and the table columns of `critic-verdicts.md`, `VELOCITY.md`, `decisions.md` and `deploy-log.md` are all uncontracted. The report shape has already changed once (RPT0002-0005 schema 1; RPT0006 on schema 2, with `lessons`, `lane_yield` and `unmeasured` appearing partway through). Raised from sdlc-studio-lens RV0003 (observability gap analysis, 2026-10-05).

## Impact

Any external reader of sprint evidence (a dashboard, a PM report) breaks silently when a section is renamed or dropped, because nothing versions the shape.

## Acceptance Criteria

- [ ] A `reference-evidence-schema.md` documents RPT schema 1 and 2 with a section catalogue marking each section required or optional, the RUN record, `lessons.jsonl`, the evidence JSONL lines and the four table layouts
- [ ] The fingerprint algorithm is stated canonically enough that a consumer can recompute it, and a test recomputes it from the annex text against a filed report
- [ ] An `evidence_schema` version is stamped where a consumer can read it without running the skill
- [ ] A conformance test fails when an emitted report, run record or lessons line drifts from the annex
- [ ] The annex states a compatibility policy: an added field is minor, a removed or renamed one is major and carries a migration note

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-05 | Claude Opus 5.5 | Raised |
