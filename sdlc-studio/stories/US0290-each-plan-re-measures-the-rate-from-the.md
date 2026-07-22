# US0290: Each plan re-measures the rate from the velocity record or names why it cannot

> **Status:** Done
> **Delivers:** CR0284
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/telemetry.py
> **Epic:** EP0094
> **Points:** 5

## User Story

**As an** operator reading a plan's token forecast
**I want** the tokens-per-point rate re-measured from the velocity record, or the reason it could
not be
**So that** I can tell a number this project measured from a seed inherited from someone else's

## Context

`VELOCITY.md`'s header says the rate is derived from that file, re-measured every sprint, and
that nothing may hardcode it. `retro.measured_rate` implements exactly that read, and nothing in
`sprint.py` calls it. `sprint.tokens_per_point` measures instead from the per-unit evidence log
(`telemetry.forecasts` and `telemetry.actuals`), which an interactive sprint never writes, so on
this project it returns the `POINTS_RATE_SEED` of 25,000 with source `seed` on every plan. The
record meanwhile holds rows measuring 40,819, 79,687 and 146,336 tokens per point.

The seed's only out-of-sample test is RETRO0028: forecast 250,000, actual 564,066, a ratio of
0.44x. `calibration()` already reads that from the history and `_render_capacity` already prints
the out-of-sample figure, but the rate line itself quotes 25,000 with a basis describing a blind
re-estimation of someone else's 21 units, and nothing beside it says the one live test of that
number failed by more than a factor of two.

Two sources, one answer. The velocity record is the mandated one and wins; the evidence log is
the finer-grained fallback for a runner-driven project that has one. Neither is ever silently
substituted for the other, and a plan is never refused over a token estimate - the existing rule
is that the token half informs and the wall-clock/unit-count appetite is what breaks a run.

## Acceptance Criteria

### AC1: the rate comes from the velocity record when the record has one

- **Given** a project whose `VELOCITY.md` yields a measured tokens-per-point rate
- **When** a plan builds its token forecast
- **Then** the forecast is priced at that rate, and the reported source names the velocity record
  as where it came from rather than the per-unit evidence log or the seed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_the_plan_rate_is_measured_from_the_velocity_record
- **Verified:** yes (2026-07-22)

### AC2: no measured rate means the seed is named as a seed, with what is missing

- **Given** a project whose record yields no rate, because no sprint has recorded both points and
  a token total
- **When** the plan quotes a rate
- **Then** it is marked a seed, the plan states that this project has measured no rate of its own
  yet, and the forecast is still produced, because planning is never refused over a token
  estimate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_no_measured_rate_is_quoted_as_a_seed_and_says_so
- **Verified:** yes (2026-07-22)

### AC3: a refused rate is reported, not collapsed into a silent fallback

- **Given** a record whose rate is refused, because its rows span more than one model or a sprint
  was delivered by more than one
- **When** the plan quotes a rate
- **Then** the refusal reason reaches the plan output naming the models involved, and the plan
  NAMES the source that stood instead - the seed, or the per-unit evidence log - rather than
  falling back with nothing said about why the record was not used
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k "test_a_refused_rate_reaches_the_plan_output or test_the_refusal_reaches_the_plan_whatever_source_stood_instead"
- **Verified:** yes (2026-07-22)

### AC5: re-measuring the rate does not reclassify the rows it was measured from

- **Given** a velocity record whose out-of-sample rows carry a measured whole-sprint excess, and
  a change that moves the live rate - stamping the delivering model on rows that had none is
  enough
- **When** the plan re-measures the rate and re-reads the record
- **Then** every recorded row keeps the sample class its own plan-time constants earned, so the
  measured excess and the calibration band stand rather than emptying to their defaults
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k RowClassSurvivesRemeasurementTests
- **Verified:** yes (2026-07-22)

### AC4: the seed is never presented as calibrated

- **Given** the seed rate in force
- **When** the plan prints the rate line
- **Then** it carries the out-of-sample result recorded against that seed, so a reader sees the
  one live test of the number next to the number itself
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_the_seed_line_carries_its_out_of_sample_result
- **Verified:** yes (2026-07-22)

## Open Questions

- [ ] CR0284 names the RETRO0028 result specifically. The record now holds further out-of-sample
  rows, so whether AC4 should quote that single row or the whole out-of-sample series is a
  presentation choice made at delivery; either satisfies "not presented as calibrated" -
  Owner: operator

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed against CR0284 AC3, retro.measured_rate and sprint.tokens_per_point |
| 2026-07-22 | claude | Repair round 1 - AC5 added and delivered: `sample_class` compared each row's stamped constants against the LIVE rate, so this story's own re-measurement would have turned every historical row `stale-constants` the moment CR0373 stamped a model. It now compares the ESTIMATOR (its parameter names), which a later measurement cannot change. AC3 widened: the refusal now names whichever source stood in |
