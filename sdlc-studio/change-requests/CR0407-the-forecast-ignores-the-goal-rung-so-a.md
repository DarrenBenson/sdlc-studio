# CR-0407: The forecast ignores the goal rung, so a design run that writes no code is priced at the full build cost of the batch it grooms

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Hit while planning the design pass ahead of this sprint. `sprint plan --goal design` over 38 units quotes 'token forecast: ~2,700,000 tokens = 108 point(s) x 25,000 tokens per point', which is the same number `--goal done` quotes for the same worklist. The rung the run is driven to changes nothing about the estimate, so a run whose entire output is acceptance criteria and a dependency graph is priced as though it will build all 38 units.

This is the CR0391 class seen from the other end. BG0254 established that the forecast prices the BUILD and says so; the forecast text here even repeats that caveat. But it is being applied to a run that by definition does NOT do the build, so the caveat is not a caveat any more - it names the entire missing thing. A number that is wrong in a stated direction is still the number an operator plans capacity against, and here it is wrong by whatever fraction of a unit's cost is design rather than construction.

The interaction with the grooming lesson makes it worse. `refine apply` mints stories with placeholder acceptance criteria, so a design rung is the honest way to pay for grooming rather than absorbing it silently into the build. But the moment an operator does the honest thing, the forecast tells them it will cost the same as building everything, and the retro will then measure a tokens-per-point figure from a run that delivered no points at all - feeding a wrong row into the velocity record CR0391 is trying to fit against.

Note what is NOT being asked for: a design-rung rate nobody has measured. Inventing a multiplier would be the same false precision the estimator work exists to remove.

**OBSERVED AT RUN-01KY5EJX's CLOSE, which is the run this CR was filed during.** The predicted
failure happened exactly as AC3 describes. `retro.py accuracy --tokens-from-harness --write`
published `RETRO0067 ... 2,502,024 tokens ... 834,008 tokens/point` to VELOCITY.md. The
denominator is 3, because `_delivered_points` counts only TERMINAL units and a design rung
terminates nothing by design - the whole output is acceptance criteria on Draft stories. The
same row calls 38 units delivered, so it is internally inconsistent as well as wrong: two
columns counting the same batch by different rules. The figure was caught by reading the row,
not by any check, and it was one command away from being the number a future plan re-measured
its rate against. The row now carries the token total with the rate deliberately blank and
the reason in the notes column.

## Impact

Any project that uses the design rung as intended, which is the rung this project's own lesson about skeleton stories tells operators to run first. Two consequences: capacity is planned against a build figure for a run that does no building, and the retro records a points-delivered figure of zero or near-zero against a real token spend, which is a wrong row in the file the planner re-measures its rate from.

## Acceptance Criteria

- [ ] The forecast states which rung it prices. A `--goal design` or `--goal plan` run does not silently present the build forecast as its own.
- [ ] Where no rate has been measured for the rung, the forecast reads UNMEASURED for that rung rather than substituting the build rate - the same refusal the cross-model rate check already makes.
- [ ] A run that closes at a non-`done` rung records its token spend WITHOUT a tokens-per-point figure, so no partial-rung row can contaminate the velocity record the planner re-measures from.
- [ ] reference-sprint.md states that the rungs cost differently and that only the build rung has a measured rate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
