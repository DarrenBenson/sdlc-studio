# CR-0544: Nothing reviews a REPAIR's approach or a PROCEDURE's plan before it is executed, and that is where this session's most expensive findings were

> **Status:** Proposed
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md
> **Priority:** High
> **Type:** enhancement
> **Size:** M

## Summary

`plan_review` reviews a STORY's acceptance criteria before it is implemented. `critic record --phase plan-review --kind test-plan` reviews a TEST PLAN before Done. Neither looks at how a bug is going to be FIXED, or at how a release is going to be CUT. Both of those turned out to be where the expensive mistakes were.

Measured in one session, all by peer review of a written plan, none by any gate:

A plan to close and tag a release had ELEVEN blocking defects. It would have failed at its eighth step on seven separate refusals and again at its eleventh: `critic repair` was missing entirely, and a recorded REJECT is terminal for review coverage, so three units could never have regained it. Mutants were to be registered AFTER the transition, where `report` mode auto-files a bug per survivor into the disclosure list the release was about to freeze. `record-green` was believed to verify a gate and performs no check at all.

A plan for a fix its author called ten minutes' work had FOUR blocking defects, including a normalisation that would have raised IndexError on every line it touched, and an exemption that would have been inherited unscoped - turning the regression being repaired into a rubber stamp. The plan explicitly warned against that outcome in its own text and specified it anyway.

The pattern is that a plan states a DISCRIMINATOR and prose cannot tell you it is wrong. Only executing the surrounding code can. That is the same argument the test-plan gate already makes - reviewing a test costs a fraction of reviewing an implementation - applied one level earlier.

## Impact

Every repair in this project is written straight from the finding, and the review that follows judges the code rather than the approach. Three of five fix clusters in this session came back REJECT, and the findings were wrong discriminators and false claims in prose - the class a plan review catches before anything is written. The cost is paid as a round of code review each time, plus the repair round after it.

## Acceptance Criteria

- [ ] {{criterion}}

## Proposed Fix

Extend the review phase vocabulary so a plan is reviewable as a first-class artefact, alongside `spec` and `test-plan`. Concretely: a `--kind approach` review, briefed by the same `critic brief` machinery so it carries the seat charter, the bounded scope and the claim-inventory pass, and recorded with the same brief provenance.

Then gate it where it matters rather than stating it in a document, which is LL0027: require an approach verdict before a repair on a unit above a risk band reaches terminal, on the same forward-only adoption terms CR0543 asks for. A release or close PROCEDURE is the second population, and the toolchain runbook is where a step with no command is a finding rather than permission to hand-roll it.

What to avoid: making this a document nobody runs. The practice already exists informally in this repository and its value is measured above; what it lacks is a command that refuses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
