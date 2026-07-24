# BG0286: sprint close --apply-signoff fans into story units only, leaving the batch's bugs Open while the close reports goal-reached

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Severity:** High
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Hit closing RUN-01KY8M6Q. The batch held 18 stories and 10 bugs. `sprint close --apply-signoff`
reported:

```text
apply-signoff: 18 transitioned Done, 18 newly signed, 0 already complete
apply-signoff: derived EP0121, EP0123, ... Done (all children terminal)
apply-signoff: HO-0025 refreshed - 18 delivered, 10 remaining
```

The 10 bugs were built, reviewed and covered by the same sprint-level APPROVE as the stories.
They stayed `Open`. The sign-off pre-flight had not named them either - it resolves through
`_batch_story_units`, so a bug is not a unit it asks about, and not a unit it fans into.

Two things then go wrong together. The run closes `goal-reached` with 36% of its batch still
open, and the handoff it writes says "10 remaining" - so the close's own artefacts disagree with
its own verdict, and the next sprint's plan inherits ten units it thinks are undelivered.

Clearing it by hand also surfaced that bugs carry a gate the fan-out never has to satisfy: every
one refused `-> Fixed` for a missing `Verification depth` field, which nothing in the sprint had
asked for while they were being built.

## Impact

Every sprint whose batch mixes stories and bugs, which is most of them. The failure is silent in
the direction that matters: the close reports success.

## Acceptance Criteria

### AC1: the fan-out reaches every unit in the batch, or says which it did not

- **Given** a closed run whose batch holds both stories and bugs
- **When** `--apply-signoff` runs
- **Then** each non-story unit is either transitioned to its own terminal status or NAMED in the output as not fanned into, with the reason - the count reported must equal the batch size or account for the difference
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ApplySignoffBatchCoverageTests::test_bugs_in_the_batch_are_transitioned_or_named

### AC2: goal-reached is not reported over an unfanned batch

- **Given** the same run
- **When** the close writes its outcome and its handoff
- **Then** a batch unit left non-terminal by the fan-out blocks `goal-reached`, or the outcome states the shortfall - the handoff's "N remaining" and the run's verdict cannot contradict each other
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ApplySignoffBatchCoverageTests::test_outcome_and_handoff_agree_on_the_delivered_count

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
