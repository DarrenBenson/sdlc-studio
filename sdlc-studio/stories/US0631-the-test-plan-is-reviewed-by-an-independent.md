# US0631: the test plan is reviewed by an independent seat before the code, and that review is recorded like a code review

> **Status:** Draft
> **Delivers:** CR0525
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0207
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** reviewer asked to judge a unit
**I want** to review its test plan as its own artefact before any code exists, briefed by the shipped tool
**So that** I am judging what would falsify the work while it is still cheap to change, instead of judging a finished diff whose tests were written to pass

## Acceptance Criteria

### AC1: the seat brief scopes the reviewer to the plan and the criteria, not to a diff

- **Given** a unit with a derived test plan and no code written
- **When** `critic.py brief --unit <id> --seat qa --phase plan-review` runs
- **Then** the printed brief carries the seat charter, the unit's criteria as law and the test-plan rows as the object of review, and it does NOT carry a diff scope, because there is no diff yet and a brief that asks for one teaches the reviewer to wait for code
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewBriefTests::test_the_plan_brief_scopes_to_the_plan_not_a_diff
- **Caller:** `critic.py brief --phase plan-review` (the CLI verb a review subagent is spawned with)
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - restoring the diff-scope block must turn this test red
- **Verified:** no

### AC2: the verdict records through the existing plan-review phase, and a self-review is refused

- **Given** a plan-review verdict whose reviewer equals the plan's author
- **When** `critic.py record --unit <id> --phase plan-review --verdict APPROVE` runs
- **Then** it is refused by the same independence rule the delivery phase already enforces, and an independent verdict lands in `plan-review-verdicts.md` rather than in the delivery log, so a plan review can never satisfy the conformance `critiqued` gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewBriefTests::test_a_self_plan_review_is_refused_and_phases_stay_separate
- **Caller:** `critic.py record --phase plan-review`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - routing a plan-review row into the delivery log must turn this test red
- **Verified:** no

### AC3: a plan verdict carries brief provenance on the same terms as a delivery verdict

- **Given** a plan-review verdict recorded with no `--brief` fingerprint
- **When** `critic.py record --phase plan-review` runs
- **Then** it is refused unless stood down by a recorded config decision, matching the delivery phase exactly, because a hand-written plan-review prompt substitutes an unbounded surface just as a hand-written code-review prompt does
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewBriefTests::test_a_plan_verdict_without_brief_provenance_is_refused
- **Caller:** `critic.py record --phase plan-review`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - exempting the plan-review phase from the provenance demand must turn this test red
- **Verified:** no

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | sdlc-studio | Groomed: criteria authored against the existing `--phase plan-review` route |
