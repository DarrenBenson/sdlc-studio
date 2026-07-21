# RFC-0049: A test strategy set at sprint planning, derived from the TSD and the unit's risk band

> **Status:** Draft
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md,.claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Sprint planning currently decides WHAT to build and in what order, but says nothing about HOW each unit will be proven. The TSD (sdlc-studio/tsd.md) and the test-specs are consulted by nothing at plan time: sprint.py never reads them, and the only risk signal the planner takes is the QA seat's WSJF `risk_reduction` score, which is immediately collapsed into an ordering number and discarded. Proof strategy is therefore decided per unit, mid-build, by whoever is holding the keyboard - which is how the same project has repeatedly shipped a test that decorates code rather than pinning it, and only caught it by mutating afterwards. This RFC asks whether the plan should carry a per-unit test strategy: what proof this unit needs (characterisation, adversarial, mutation, none beyond the suite), which TSD risk area it touches, and what would falsify it - written before the build, so the build is measured against a stated intent rather than a post-hoc judgement. Deciding this also settles WHEN mutation runs (see BG0238): a stated strategy names the units worth mutating and when, instead of a blanket close-scoped sweep over a whole sprint diff.

## Design Options

- **A: no change - proof strategy stays a build-time judgement by the implementing seat, with the close-scoped mutation sweep and the independent critic as the backstop. Cheapest; keeps the plan short. Accepts that the backstop has repeatedly been the only thing that caught a vacuous test, at the point where repair is most expensive.**
- **B: a per-unit proof line in the plan - each unit carries a one-line strategy (risk band + proof required + what would falsify it) written at plan time, gated at close by comparing what was claimed against what the evidence shows. Small, mechanical, testable. Does not require the TSD to be good.**
- **C: a full test-strategy review at planning, as a QA-seat pass over the batch against the TSD - identifies risk areas the batch touches, names the proof each needs, and flags coverage the TSD demands that the batch would not deliver. Richest signal; adds a planning stage and depends on the TSD staying current, which is itself the thing EP0071 had to repair.**

## Recommendation

B first, and judge C on whether B's proof lines keep coming back the same. B is a plan-time line and a close-time comparison - it makes the strategy falsifiable without adding a stage or a dependency on TSD freshness. If the lines turn out to be substantive and varied, C is the natural extension; if they are boilerplate, C would have been ceremony. Sequence it after RFC0048 option B, since a per-unit proof line that mandates more mutation runs lands on a suite whose cost is already the standing complaint.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: A: no change - proof strategy stays a build-time judgement by the implementing seat, with the close-scoped mutation sweep and the independent critic as the backstop. Cheapest; keeps the plan short. Accepts that the backstop has repeatedly been the only thing that caught a vacuous test, at the point where repair is most expensive., B: a per-unit proof line in the plan - each unit carries a one-line strategy (risk band + proof required + what would falsify it) written at plan time, gated at close by comparing what was claimed against what the evidence shows. Small, mechanical, testable. Does not require the TSD to be good. or C: a full test-strategy review at planning, as a QA-seat pass over the batch against the TSD - identifies risk areas the batch touches, names the proof each needs, and flags coverage the TSD demands that the batch would not deliver. Richest signal; adds a planning stage and depends on the TSD staying current, which is itself the thing EP0071 had to repair. | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
