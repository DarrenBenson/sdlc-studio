# CR-0189: Routing foundation: route.py difficulty estimator, tier map, config schema

> **Status:** Complete
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** P2
> **Type:** feature-request
> **RFC:** RFC-0026 (WS1)

## Summary

New `scripts/route.py` (pure stdlib, read-only, JSON out) with `estimate` / `pick` /
`escalate` / `tiers` subcommands: a deterministic 0-100 difficulty score from existing
signals (blast-radius `max_cognitive` + `risk_score` via `complexity.assess`, files
affected, unresolved-path novelty, AC count, story points), banded to five abstract tiers.
Shared helpers (`affects_files` from sprint.py, AC counting from audit.py) lift into
`lib/sdlc_md.py` so route.py never imports the planner. New `routing:` config block
(enabled: false default; sparse model map with upward-only degradation; kind floors;
critic_tier match-with-medium-floor; thresholds; escalation.max_same_tier).

## Acceptance Criteria

- [ ] `route.py estimate --unit <path>` emits {difficulty_score, difficulty_band, confidence, missing, signals, subscores}; any unresolved subscore defaults to 0.5 and is listed in `missing`
- [ ] `route.py pick --unit <path> --role author|critic` applies band->tier, kind floors, low-confidence upward bump, and the critic match+medium-floor rule
- [ ] `route.py tiers` resolves a sparse model map upward-only (e.g. {small, large} declared: tiny->small, medium->large, xlarge->large); empty map yields tier names with model: null
- [ ] `route.py escalate --tier <t>` returns the next declared tier up, or reports already-at-max
- [ ] `routing:` block documented in config-defaults.yaml + reference-config.md; enabled: false default
- [ ] Unit tests cover the formula, degradation, floors, escalate stepper, and missing-signal defaults

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | RFC0026 WS1 | Created via `new` (deterministic) |
