# BG0287: the review-current lane goes stale against the close's own transitions, so it blocks the close step that would refresh the anchor

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Severity:** Medium
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Hit closing RUN-01KY8M6Q, twice, and it is self-inflicted by design.

`gate`'s `review-current` lane refuses when any artefact is newer than `reviews/LATEST.md`. The
close chain's own steps 5-7 transition the batch - 48 artefacts on this run - and step 7 is the
step that refreshes the anchor. But the gate is step 4. So:

1. close runs, gate passes, steps 5-7 transition 48 artefacts and refresh the anchor
2. the paperwork is committed
3. close is re-run (as the two-invocation flow requires) and now FAILS at step 4, because the
   artefacts its own previous run transitioned are newer than the anchor

The remedy printed is "run `review` before closing" - which re-runs an adversarial review over a
tree whose only change is the close's own status transitions. The real remedy is to touch the
anchor, which the operator can only do by editing it, which is the thing the lane exists to stop
being done casually.

`_only_close_status_block_differs` already carves out exactly this case for the anchor's own
stamp. The carve-out does not extend to the transitions the close makes in the same chain.

## Impact

Any close re-run after its first pass - which the documented sign-off flow requires. It teaches
the operator that the honest remedy for a currency gate is to backdate the thing it measures.

## Acceptance Criteria

### AC1: the close's own transitions do not stale the anchor against itself

- **Given** a close chain that transitioned N artefacts and refreshed the anchor in the same run
- **When** the close is re-run
- **Then** `review-current` does not report those artefacts as stale - a change made by the close chain after the anchor was refreshed is not evidence the review is out of date
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReviewCurrentSelfStalenessTests::test_the_close_own_transitions_do_not_stale_the_anchor

### AC2: the remedy names something that changes the state it measures

- **Given** a genuinely stale anchor and a self-staled one
- **Then** the two produce different remedies, and neither instructs an edit whose only effect is to move a timestamp
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReviewCurrentSelfStalenessTests::test_the_two_staleness_causes_give_different_remedies

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
