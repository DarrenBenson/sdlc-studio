# CR-0680: Batch same-wave units of at most 3 points into one reviewer, up to three units with one brief and one verdict file each, and let `critic.py record` accept a round-2 verdict from a fresh reviewer under its own name

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RFC0062 Phase 3, review-economy lens: finding 2; agent-context lens: finding 6 (stable blocks once); run seven friction F3
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:38Z

## Summary

Measured per-unit review cost in run six: a single full round 1 averaged 498k (9 reviews); the two 2-unit round-1 reviews cost 266k a unit against a tier-matched single of 330k; the 3-unit round-2 review 145k a unit against a single round-2 mean of 358k. Run six launched separate reviewers on one commit three times (3 at 11:59:13 on 475b0293, 2 at 14:13:39 on ea1d9572, 5 at 14:29:44 on 931f849c). No finding was lost to batching: all 7 batched unit-verdicts recorded a new finding and the pair found both its blockers (critic-verdicts.md:1747-1764). reference-sprint.md:666 names no optimum. Run seven friction F3: `critic.record_verdict` refuses a round-2 verdict from a reviewer other than round 1's, so a fresh round-2 reviewer is recorded under round 1's name and the cost anatomy cannot attribute its transcript.

## Impact

Each reviewer's fixed start (39k) and orientation calls repeat per agent; the record refusal falsifies attribution and blocks a batched or fresh round 2.

## Acceptance Criteria

- [ ] The review dispatch groups the units of one landing or wave into reviewer batches of at most three units of at most 3 points each and emits one dispatch naming each unit's brief and verdict path, with independence from the author unchanged.
- [ ] `critic.py brief` given several --unit values prints the stable blocks (seat charter, practices, lessons, return contract) once and each unit's scope, criteria and diff apart.
- [ ] `critic.py record` accepts a round-2 verdict from a reviewer other than round 1's and records each under its own name, and the cost anatomy (US1124) attributes the round-2 transcript to it.
- [ ] Before and after: the next sprint reports per-unit review cost and finding yield for batched and single reviews against run six's 330k single and 266k batched round 1.

## Recommendation

Batch under the cap and fix the round-2 record. Saving 0.38M per run, round 1 only: BG1227, US1121 and US1117; BG1190 and BG1217; and US1120 joining BG1224 and BG1226 move 6 units to batched at the measured 64k a unit (330k - 266k). The round-2 share (0.43M) is not carried because the claims-at-observable CR removes both round 2s it counts, and the 4 agents batching removes are taken out of the lean-agent CR's figure. Risks: attention thins on the last unit in a long context and a finding can land on the wrong unit, so the cap, one brief and verdict file per unit and the per-unit Affects scope stay; the evidence is small (2 batched round-1 reviews, 1 round-2), and the 64k comes from full-and-light pairs, so a full-and-full pair may save less.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
