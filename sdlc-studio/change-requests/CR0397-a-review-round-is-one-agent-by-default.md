# CR-0397: A review round is one agent by default, so every round after the first is a serial bottleneck

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-review.md,.claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

RUN-01KY3MFX's round 1 fanned three reviewers across disjoint surfaces and returned 11 MAJORs. Rounds 2 through 6 were each a SINGLE reviewer, because the diff was smaller and one agent felt proportionate. That reasoning is wrong in a way worth writing down: rounds after the first review a REPAIR, the most defect-dense code in a sprint - this project has recorded three occasions where a repair masked the defect beside it, and rounds 4, 5 and 6 each found a defect the previous repair had introduced. A small diff is a reason to give reviewers different LENSES, not fewer of them. It also puts every round on the critical path end to end, so six rounds cost six serial latencies. Two reviewers on a forty-line delta, one attacking the code and one attacking the claims about it, costs little more than one and removes the single-observer failure mode.

## Impact

Sprint wall-clock, and the confidence an APPROVE carries. A one-reviewer round finding nothing is much weaker evidence than a two-reviewer round finding nothing, and nothing distinguishes them today.

## Acceptance Criteria

- [ ] The review guidance states a round is at least two reviewers with distinct lenses whatever the diff size, and names the claims lens as one.
- [ ] Where a round runs with one reviewer, the review record says so.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
