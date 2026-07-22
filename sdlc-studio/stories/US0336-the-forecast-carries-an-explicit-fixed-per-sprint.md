# US0336: The forecast carries an explicit fixed per-sprint term alongside the per-point term, and the plan shows both rather than a single product

> **Status:** Draft
> **Depends on:** BG0265, BG0256
> **Delivers:** CR0391
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0114
> **Points:** 3

## User Story

**As an** operator sizing a sprint from a plan's token forecast
**I want** the forecast to carry an explicit fixed per-sprint cost beside the per-point
cost, and to show me both
**So that** a small batch is not priced as though the ceremony, the review rounds and the
close were free

## Context

CR0391 fitted two measured sprints and found a marginal term of roughly 13,105 tokens per
point against a fixed term of roughly 3,884,023 per sprint. The marginal term is the right
order as the shipped 25,000 seed, so the model was never badly wrong about the build - it
has no parameter at all for the rest. This story is the SHAPE change: two terms where there
was one, and both on screen. Where the fixed term's number comes from, and whether it may be
applied at all, are US0337 and US0338.

## Acceptance Criteria

### AC1: the forecast is a fixed term plus a per-point term, carried separately

- **Given** a project whose evidence supports a fixed per-sprint term
- **When** a plan is built over a batch
- **Then** the forecast carries the fixed per-sprint term and the marginal per-point rate as
  two separate figures, and its total is the fixed term plus points times the marginal rate,
  so neither term can be recovered by dividing the other out
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheForecastCarriesAFixedTermTests::test_the_total_is_a_fixed_term_plus_points_times_the_marginal_rate

### AC2: the plan shows both terms, never a single product

- **Given** that same plan
- **When** its token forecast is rendered
- **Then** the output names the fixed per-sprint term and the per-point term on their own
  lines, so a reader can see which half of the number their batch size moves; output that
  quotes only points times a rate fails this
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheForecastCarriesAFixedTermTests::test_the_rendered_forecast_shows_both_terms_and_not_one_product

### AC3: halving the batch does not halve the forecast

- **Given** two batches over the same project, one carrying half the points of the other
- **When** both are forecast
- **Then** the smaller batch is forecast at MORE than half the larger's total and at a
  strictly higher cost per point, because the fixed term is amortised over fewer points - a
  model that is linear in points returns exactly half and fails this
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheForecastCarriesAFixedTermTests::test_a_half_size_batch_costs_more_than_half_and_more_per_point

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
