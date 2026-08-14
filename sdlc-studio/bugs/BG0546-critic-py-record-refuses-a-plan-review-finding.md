# BG0546: critic.py record refuses a plan-review finding for carrying no diff origin, when a plan review has no diff to attribute one to

> **Status:** Fixed
> **Verification depth:** functional (executed: a plan-review finding with no origin tag is accepted; a delivery finding with no tag is still refused; test_critic 294 pass)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01KZEF9M, 2026-08-07. Hit recording three plan-review verdicts on BG0541, US0660 and US0661.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic.py record --phase plan-review` applies the origin-tag guard built for delivery reviews. Every finding must be tagged [regression], [new] or [pre-existing], and the refusal instructs the reviewer to decide by execution with `git log -S` against the base ref. A plan review runs BEFORE any code exists - its own brief says so verbatim: 'There is NO diff scope and no code to read.' So none of the three tags can be established the way the refusal demands, and the reviewer either invents an attribution or is blocked. Three verdicts in RUN-01KZEF9M were tagged [new] as the nearest honest reading of a defect in a plan, which is not what [new] means.

## Steps to Reproduce

1. `critic.py brief --unit <id> --seat qa --phase plan-review`, which prints 'There is NO diff scope and no code to read'. 2. `critic.py record --unit <id> --phase plan-review --kind test-plan --verdict REJECT --brief <fp> --issues 'AC4 mutant survives'`. 3. It exits 2 and demands a diff-origin tag decided by `git log -S`.

## Proposed Fix

Scope the origin guard to `--phase delivery`, or give plan-review its own vocabulary - a plan finding is about the plan's own soundness, and the axis that matters there is whether the row's mutant is lethal, not what a diff did. The close prices findings against the batch that caused them, and a plan-review finding's batch is the one being planned, so the attribution the guard exists to protect is already unambiguous without a tag.

## Acceptance Criteria

- [x] **AC1** Given `critic record --phase plan-review` and findings carrying no origin tag, when the record is written, then it is accepted - a plan review happens before any diff exists, so the origin question is unanswerable rather than merely unanswered.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k a_plan_review_finding_needs_no_origin
- [x] **AC2** Given the same untagged findings on a DELIVERY review, when the record is written, then it is still refused - the guard was scoped, not removed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k a_delivery_finding_still_needs_an_origin

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in critic.py `cmd_record`, drop the `phase != 'plan-review'` guard so a plan finding is refused for carrying no diff origin | Given `critic record --phase plan-review` and findings carrying no origin tag, when the record is written, then it is accepted - a plan review happens before any diff exists, so the origin question is unanswerable rather than merely unanswered. |
| AC2 | in critic.py `unclassified_findings`, return [] always so a delivery finding with no origin is accepted | Given the same untagged findings on a DELIVERY review, when the record is written, then it is still refused - the guard was scoped, not removed. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
