# CR-0192: Benchmark arm R: routed pipeline variant with cost index

> **Status:** Proposed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** P3
> **Type:** feature-request
> **RFC:** RFC-0026 (WS4)
> **Depends on:** CR-0189, CR-0190, CR-0191, CR-0193

## Summary

Repo-only bench extension (`tools/bench/`, never in the skill payload): a third arm `R`
(pipeline + `routing.enabled: true` + a workspace model map) registered in runner.py's
`ARM_CLAUDE_MD`, with a new `arms/pipeline_routed_CLAUDE.md`. `record` gains `--model-mix`
(e.g. tiny:2,medium:1) and `summary` gains `--price tiny=0.25,small=1,...` computing a cost
index per fixture x arm. Headline metric: equal defect-escape rate to arm A at a lower cost
index; secondary: escalation rate (high = the estimator under-routes).

## Acceptance Criteria

- [ ] `prepare --arm R` produces a workspace with the routed CLAUDE.md and a .config.yaml enabling routing with a model map
- [ ] `record --model-mix` persists the mix; `summary --price` computes a cost index only when prices are supplied (absent -> no cost column, no fabricated zeros)
- [ ] Pricing data lives only in the operator's invocation, never in files under .claude/skills/
- [ ] test_bench_runner.py covers arm R preparation and the cost-index arithmetic

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | RFC0026 WS4 | Created via `new` (deterministic) |
