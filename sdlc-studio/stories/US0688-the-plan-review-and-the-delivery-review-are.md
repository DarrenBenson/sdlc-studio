# US0688: The plan review and the delivery review are carried in ONE brief, so a unit takes one round where it took two

> **Status:** Draft
> **Delivers:** CR0555
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0218
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The plan review and the delivery review are carried in ONE brief, so a unit takes one round where it took two
**So that** CR0555 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit at its terminal transition, when a reviewer is briefed, then ONE brief carries both the plan review and the delivery review - two briefs at one point is the round this move exists to remove
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CombinedBriefTests::test_one_brief_carries_both_reviews
- [ ] **AC2** Given that combined brief, when it is generated, then it carries the unit's DIFF beside its plan, so the reviewer can answer whether a declared mutant can actually fail the test its criterion names - the question a pre-code reviewer cannot answer, and which took five rounds to settle by hand on RUN-01M0JD1W
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CombinedBriefTests::test_the_brief_carries_the_diff_beside_the_plan
- [ ] **AC3** Given a verdict recorded from that brief, when it is written, then it satisfies BOTH the plan-review gate and the delivery gate, and neither reads as unreviewed - a combined brief whose verdict only one gate accepts has saved nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CombinedBriefTests::test_one_verdict_satisfies_both_gates
- [ ] **AC4** Given a project still on the pre-move behaviour, when a brief is generated, then it is the plan-only brief exactly as today - the paired control, so the combined form does not reach projects that have not adopted the move
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CombinedBriefTests::test_an_unadopted_project_gets_the_old_brief

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Created via `new` (deterministic) |
