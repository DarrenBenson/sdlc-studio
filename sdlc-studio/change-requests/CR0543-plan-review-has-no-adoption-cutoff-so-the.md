# CR-0543: plan_review has no adoption cutoff, so the one hard risk-proportional plan gate in the codebase cannot be turned on by any project with history - including this one

> **Status:** Proposed
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/config.py, sdlc-studio/.config.yaml, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py
> **Priority:** High
> **Type:** enhancement
> **Size:** S

## Summary

US0640 decoupled `plan_review.enabled` from the schema version, on the argument that plan review is a review policy and has nothing to do with the shape of artefacts. That removed the wrong barrier. The remaining one is that the gate applies to EVERY story, retroactively, with no forward-only cutoff.

Measured on this repository, mid-release: enabling it fires the trigger on 18 of the open run's 19 units, all of them already built. `plan_review.gate` is consumed at `transition.py:1023`, the Done gate, so those 18 would be refused Done for lacking a plan-review verdict that nobody could have recorded, on work that is finished. The gate would block the release the day it was switched on.

Every sibling gate adopted mid-project carries a cutoff: `conformance.adopt_after` takes an id, `review.two_role_after` takes an id, `review.test_plan_after` takes a date, and the engagement floor grandfathers by id. `plan_review` takes none. So it is adoptable only by a project with no history, and this repository - which built it, ships it, and documents it as the model the rest of the ceremony work copies - has never had it on. A gate nobody can adopt is a gate that is off everywhere, which is indistinguishable from not shipping it.

The principle is already recorded in this codebase's own words, from US0641 on review tiers: `nothing is applied backwards - the rule would otherwise re-open every closed unit in the corpus for a fact nobody could have recorded`. Plan review is the one gate that did not get that treatment.

## Impact

Ships the gate in a state where its own repository cannot use it. Any consuming project with an existing backlog hits the same wall: turn it on, and every story past the trigger is refused Done until a plan review is recorded for work already delivered. The rational response is to leave it off, which is what has happened here for the whole of v5.

## Acceptance Criteria

- [ ] {{criterion}}

## Proposed Fix

Add `plan_review.adopt_after`, following `conformance.adopt_after` exactly: an id at or below which the gate reports exempt (pre-adoption) and above which it enforces. Reuse `config.feature_enabled` and the existing resolution so there is one answer to `is this on`, not two. Then set it in this repository's own `.config.yaml` to the current maximum id and turn `plan_review.enabled: true`, so the gate is in force forward and the repo stops shipping a dormant gate as though it were a live one.

The test that matters is the one that would have caught this: enabling the gate on a corpus with history must leave every pre-cutoff unit reporting `exempt (pre-adoption)` rather than refused, measured on a fixture carrying units on both sides of the line.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
