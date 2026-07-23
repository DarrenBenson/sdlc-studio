# BG0278: sprint plan CRASHES with KeyError fixed-fit once a project has enough measured sprints to apply the fixed-term fit: the fixed-fit branch overrides rate_source but leaves rate_refused set, breaking the exhaustive-lookup invariant _render_rate_provenance documents

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Severity:** High
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Hit opening Sprint 2. `sprint plan` exits with a traceback:

    File ".../sprint.py", line 2713, in _render_rate_provenance
      instead = {RATE_EVIDENCE: ..., RATE_SEED: ...}[tf["rate_source"]]
    KeyError: 'fixed-fit'

**Why it detonated now.** Closing Sprint 1 recorded the whole-sprint actual that finally gave the
project enough rows to FIT the fixed per-sprint term. From that moment `_token_forecast` takes its
fixed-fit branch, which sets `rate_source = RATE_FIXED_FIT`. So the crash appears the first time a
project becomes well-calibrated enough to use its own fitted term - the reward for measuring.

**Why the lookup was believed safe.** `_render_rate_provenance`'s own docstring argues the two-key
lookup is exhaustive: "the velocity record is the source that refused, and `tokens_per_point`
returns `refused: None` on every answer the record itself supplies, so the record can never also
be what stands. A generic fallback sentence under that pair could not be reached, and unreachable
prose is one more claim nothing checks."

That reasoning held when written. It was broken later by the fixed-term feature, which overrides
`rate_source` in `_token_forecast` while passing `rate_refused` through UNCHANGED from `rate_info`.
So a forecast can now carry `rate_refused` truthy AND `rate_source == fixed-fit` together - the
exact combination the docstring proves impossible.

This is the enumeration-as-boundary failure this project has already recorded as a lesson: an
exhaustive-by-argument lookup is only exhaustive until someone adds a member, and nothing here
fails loudly when they do.

## Impact

`sprint plan` is unusable on any project calibrated enough to apply its fixed term - it cannot
plan at all. The run state is written BEFORE the render, so the run opens and then the command
dies, leaving the operator with a half-reported plan and a live run.

## Acceptance Criteria

### AC1: a fixed-fit forecast carrying a refused velocity record renders without crashing

- **Given** a forecast where the fixed-term fit is applied and the velocity record refused a rate
- **When** the plan renders its rate provenance
- **Then** it prints what stood in place of the record and does not raise
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RateProvenanceExhaustiveTests::test_a_fixed_fit_rate_source_with_a_refused_record_renders

### AC2: the lookup cannot silently gain a third unhandled member again

- **Given** every rate source the forecast can emit
- **When** the provenance renderer is exercised across all of them with a refused record
- **Then** each is handled explicitly, and a rate source with no mapping fails loudly at test time rather than at an operator's plan
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RateProvenanceExhaustiveTests::test_every_rate_source_is_handled

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
