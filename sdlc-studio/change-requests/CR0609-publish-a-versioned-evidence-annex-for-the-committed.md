# CR-0609: Publish a versioned evidence annex for the committed sprint records

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0275
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

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Drift-test reach (left to the operator). Drafted to the panel's recommendation: full key drift for the report and the four ledgers; for the run record, only the keys a consumer reads are contracted (report linkage, lifecycle, signature and the fields the report reads), the suite fails when one is removed or renamed, and unknown keys are tolerated as reference-schema.md:127-128 already rules for artefacts. The alternative is full drift on all 49 run-record keys, which puts the annex in the Affects of most sprint-machinery stories (LL0056).
- Minimum cut (left to the operator). If capacity forces the 9-point cut (report, fingerprint, stamp), split CR0609 so the run-record and ledger parts become their own request, rather than ship a CR whose first and fourth criteria are part-met.
- BG1007 (left to the operator): option B, delivered here (recommended), or option A after CR0610's citation story. If B, should 'sources are unsigned' also appear on the page itself, as BG1007's criterion reads? This draft states it in the annex and reference-sprint.md only, because a new template sentence makes `check` print a 'not comparable' note on every earlier page in a consuming project, whose installed template has no history to compare against (sprint_report.py:5407); BG1007's criterion would be amended to match.
