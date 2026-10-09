# CR-0610: Make the report of record reviewable without .local/, and let it carry money

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0276
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Date:** 2026-10-05
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-05T15:44:19Z

## Summary

Report figures cite their `source` as `sdlc-studio/.local/run-state.json` or `.local/refusals.jsonl`, and `RUN-*.json` records `plan` as `.local/sprint-plan.json`. Those files are gitignored, so a reviewer without the operator's machine cannot follow any of them. Money is computed only by `sprint_report show` from `pricing.<model>`; the report of record carries tokens alone, so a reader who wants cost must re-price with today's prices. Raised from sdlc-studio-lens RV0003 (observability gap analysis, 2026-10-05).

## Impact

A project manager reading the committed record sees provenance links that go nowhere and no cost in money.

## Acceptance Criteria

- [ ] Every figure in a newly filed report cites a committed file (the RUN record or a committed digest) as its source, never a `.local/` path
- [ ] The RUN record carries a committed plan digest instead of a `.local/sprint-plan.json` path
- [ ] The cost section carries an optional pricing snapshot (model, price, currency, date) and money figures computed from it, and an unpriced model is listed as unpriced, never zero
- [ ] Reports filed before the change still check VALID

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-05 | Claude Opus 5.5 | Raised |

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Pricing basis: the panel's product seat answers configured rates only on the report of record (Maya's scenario says 'priced from her own rates'; telemetry.py:446 calls the defaults 'NOT a quote'), with `sprint_report show` keeping the estimates. The money story is written that way; confirm.
- Money scope: (a) delegated-model capture and money, 7 points over two stories, after US0991 (the panel recommends this); or (b) defer both until delegated spend can be priced. Without the delegated model, RPT0006-RPT0011 would price nothing and RPT0016-RPT0019 would leave 81 to 88% of each run unpriced.
- Lane yield: cut the story and amend CR0610's first criterion to exclude the lane-yield appendix (the panel recommends this), or keep it for a later release. It is marked later here.
- BG1007: option B (state that sources are unsigned, delivered by CR0609's fingerprint story; recommended) or option A (sign sources under a rule mark, only after this epic's citations story).
