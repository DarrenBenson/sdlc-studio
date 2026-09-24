# CR-0593: nothing refuses a batch unit that no goal clause covers, so a run can deliver work its own goal never tested

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Parent:** RFC0060
> **Priority:** Medium
> **Type:** Enhancement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Three-seat goal review, 2026-09-22. The reviewing seats reported: BG0722 appears in no clause; US0862, US0864 and US0865 are unnamed by any clause, being 21 of the batch's points; and the goal's own binding sentence was inaccurate about BG0730, whose defect is a permanent false RED rather than anything reaching a report as a green. The goal text was corrected by hand under D0240 - which is precisely the hand-correction a guard would have forced.
> **Date:** 2026-09-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

RFC-0060 WS1 builds the refusal for one direction: a goal whose clauses carry no check is refused at plan time. The mirror is unguarded. A batch may hold units that no clause names, and the close will then derive `achieved` from clauses that are all green while units outside every clause delivered whatever they delivered - which is the same laundering the RFC diagnosed, arriving by the other door. Found by the three-seat goal review of RUN-01M30-series planning, in the specimen itself: the first draft of that run's goal named four of its five bugs, omitted BG0722 entirely - the very unit RFC-0060's Related Artifacts table calls the evidence that a goal verdict goes unchecked - and left 21 points of stories covered by no clause.

## Impact

A run can report its goal achieved while delivering units that goal never tested, which is the laundering RFC-0060 exists to end, arriving through the door the RFC did not close. The cost is paid twice: the operator signs a report whose green says less than it appears to, and the next run inherits behaviour no clause ever constrained. It is not hypothetical - it occurred in the first batch planned under the new rules, and was caught by a seat review rather than by any gate, which is the weakest place in this repository for a rule to live.

## Acceptance Criteria

- [ ] The plan reports, per batch unit, whether any goal clause names it, and the count of uncovered units
- [ ] A batch in which every unit is named by a clause reports zero uncovered, so the check discriminates
- [ ] A unit named by a clause only through a shared file is not counted as covered, because file overlap is not a claim about behaviour
- [ ] The uncovered count reaches the report of record, so the signer sees how much of the batch the goal did not test

## Recommendation

B first, measured, then A. A new blocking refusal on the planning path earns its place on a number rather than on assertion - the standard this repo held claim-drift and revert-check to. Report which units no clause covers, count it for a run or two, and promote it to a refusal once the figure shows the guard would bite something real.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | sdlc-studio | Raised |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - [+constraint] refuse unit no goal clause covers: no clauses under D0253 |
