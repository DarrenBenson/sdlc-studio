# CR-0512: A unit review is scoped to that unit's own diff and blocks only on a NEW defect; an already-logged finding is reported, never blocking

> **Status:** In Progress
> **Decomposed-into:** EP0194
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-doctrine.md
> **Priority:** High
> **Type:** Improvement
> **Size:** M

## Summary

OPERATOR POLICY. The review process currently rejects on the whole repository's condition rather than on what the unit under review changed, which makes a REJECT the default outcome and the review worthless to a working developer. Three rules, mechanised rather than left as doctrine.

1. SCOPE IS THE UNIT'S OWN DIFF. A seat judges the change the unit made - its declared `Affects` against the run's base ref - and nothing else. `critic.py brief` ALREADY emits this scope; nothing obliges a caller to use it, and a hand-written prompt silently substitutes an unbounded surface.

2. BLOCK ONLY ON A NEW DEFECT. A finding blocks when the unit introduced it. Anything true of the tree before the unit landed is REPORTED and does not hold the gate.

3. AN ALREADY-LOGGED FINDING NEVER BLOCKS. If an open Bug/CR already covers it, the reviewer cites the id and moves on. Re-finding known debt is not a review result.

This is not a new idea here - RETRO0085 recorded it as a lesson and nothing was built: 'Sort every finding into REGRESSION, new-but-better, or pre-existing, with git log -S deciding rather than judgement. Twelve findings collapsed to one regression on that test; six of the twelve were older than the batch being judged.' An 11-in-12 reduction in blocking findings has been sitting unimplemented in a retro.

## Impact

Measured on RUN-01KYX375: four review rounds over nine units, seven units rejected, and by the author's own classification eleven of the twenty-one open bugs concern this repository's dogfooding paperwork rather than any behaviour a consuming developer experiences. A review that audits the whole artefact graph on every unit has an unbounded surface and will always find something, so APPROVE becomes unreachable and the operator's rational response is to switch the reviews off - which would discard the passes that found a crash-on-default-install and a ten-second lock self-contention. The cost is not rigour; it is scope.

Cheapest first: rule 3 needs only a cross-reference against the open backlog, and rule 1 is already emitted by the shipped brief and merely unenforced.

## Acceptance Criteria

- [ ] A seat brief produced by any path other than `critic.py brief` is refused, and the refusal names the command.
- [ ] A recorded review verdict carries a per-finding classification, and a verdict whose findings are unclassified is refused.
- [ ] A PRE-EXISTING finding is reported in the verdict and does NOT appear in the blocking set, proven by a test whose only variable is whether the defect predates the run's base ref.
- [ ] A finding whose text matches an open Bug/CR is annotated with that id and does not block.
- [ ] A genuine REGRESSION still blocks - the positive control, so the change cannot be satisfied by a gate that stopped blocking.
- [ ] Applied retrospectively to the RUN-01KYX375 review record, the blocking-finding count falls, and the measured before/after is recorded rather than asserted.

## Proposed Fix

1. `critic.py brief` is the ONLY sanctioned way to brief a seat, and an orchestrator that hand-writes a review prompt is refused rather than advised - the same shape as the breakdown gate. The brief already carries the bounded diff scope, the canonical ACs as law, and the claim-inventory pass; a hand-written prompt carries none of them.
2. A recorded verdict classifies every finding REGRESSION / NEW / PRE-EXISTING, decided by `git log -S` against the run's base ref rather than by the reviewer's judgement.
3. Only REGRESSION and NEW hold a gate. PRE-EXISTING is reported and, where no artefact covers it, filed as a new Bug at its own severity - so nothing is lost, it simply stops blocking this unit.
4. A finding matching an open Bug/CR is annotated with that id automatically and never blocks.
5. State the rule in the shipped doctrine so a consuming project inherits the scope, not just the ceremony.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
