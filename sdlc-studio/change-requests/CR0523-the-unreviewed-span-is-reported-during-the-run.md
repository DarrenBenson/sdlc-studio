# CR-0523: the unreviewed span is reported DURING the run, not discovered at the close

> **Status:** Proposed
> **Decomposed-into:** EP0226
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/conformance.py
> **Priority:** High
> **Type:** Improvement
> **Size:** M

## Summary

`review-batch --open` exists so a batch is reviewed at its boundary, and its own help says why: a finding is then delivery work in the batch that caused it rather than close overhead. Nothing enforces it during the run. Coverage is computed by `sprint_covers_independently` and read at ONE place, the close, through conformance.

RUN-01KYZKY5 ran 44 units and 25 commits with zero spans opened and zero review rounds recorded, and no command said anything. The operator noticed, not the tooling. The rule was known and stated; nothing that ran between unit 1 and unit 44 asked about it.

This is LL0027's exact shape: a rule that matters is gated in the command people actually run. It is currently gated in the command run once, at the end, when acting on it is most expensive - which converts every finding into precisely the close overhead the design set out to avoid.

## Impact

The batch-boundary review is the mechanism that keeps findings cheap, and it is the one part of the loop with no in-run gate. A run can reach any size unreviewed and only learn at the close, when a REJECT means reopening work believed finished. The larger the run, the worse the discovery, so the failure grows with exactly the runs that can least afford it.

## Acceptance Criteria

- [ ] A unit reaching Review while the open unreviewed span exceeds a threshold is REPORTED by the command that transitions it, naming the span size and the `review-batch --open` invocation that closes it
- [ ] The threshold is configurable and has an honest default derived from what the repo actually does, not a number picked by assertion
- [ ] `sprint status` states the open span: how many delivered units no independent pass covers, so the answer is available without running the close
- [ ] The report is advisory first and its yield measured before it is allowed to block, on the same terms the claim-drift and lane-check lanes shipped under
- [ ] A run with every unit covered says so and stays silent, so the signal does not become noise that gets switched off

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
