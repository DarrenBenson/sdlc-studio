# CR-0043: churn-weighted composite + complexity-driven test risk (RFC0009 WS4)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Feature
> **Requester:** Autosprint (RFC0009)
> **RFC:** RFC-0009
> **Date:** 2026-06-21
> **Affects:** scripts/complexity.py, templates/config-defaults.yaml, reference-test-best-practices.md
> **Depends on:** CR0028 (complexity), the 2026-06-21 calibration (94bcde6)
> **GitHub Issue:** --

## Summary

Delivers RFC0009 WS4 + the composite score, now empirically grounded by the calibration
against consuming repo A/consuming repo B (churn predicts defects ~3x more strongly than
complexity). `complexity.py` gains a git `churn` signal and a churn-weighted
`composite_risk` band; `assess` returns a `risk_band` (low/medium/high). The
test-strategy reference maps the band to coverage / scenario / verification-tier depth,
so test effort concentrates where defects actually land. WS5 (wave-sizing by run cost)
stays deferred - the calibration proves defect risk, not cost.

## Proposed Changes

- `complexity.py`: `churn(repo_root)` (commits-touching-file from git, degrades to {} off
  git); `composite_risk(cognitive, churn, root)` weighting churn 3x complexity, each
  normalised to its `*_high` threshold, with a floor so either signal alone over
  threshold is at least medium; `assess` adds `risk_band`/`risk_score` + per-file churn
  (absolute paths resolve to the repo-relative churn key).
- `config-defaults.yaml`: `complexity.cognitive_high` / `complexity.churn_high`.
- `reference-test-best-practices.md#complexity-test-risk`: the band -> test-depth table.

## Acceptance Criteria

- [x] `composite_risk` weights churn ~3x complexity (the calibration), bands low/medium/high, and floors a complex- or hot-alone file to at least medium.
- [x] `churn` reads git history (quotepath-safe), degrades to {} off git; `assess` exposes `risk_band` and resolves absolute paths to the repo-relative churn key.
- [x] The test-strategy reference documents scaling coverage / scenarios / verification tier by the band; WS5 noted as deferred.
- [x] Unit-tested (weighting, floor, churn-from-git, absolute-path churn, degradation); independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (RFC0009) | Complete - churn-weighted composite + WS4 test-risk band; critic REJECT (abs-path churn miss, complex-no-churn under-warn, quotepath) -> all fixed + tests |
