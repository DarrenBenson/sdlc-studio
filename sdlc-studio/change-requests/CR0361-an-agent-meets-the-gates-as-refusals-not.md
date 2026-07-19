# CR-0361: an agent meets the gates as refusals, not as a briefing: generate a per-unit pre-flight from the gates themselves

> **Status:** Complete
> **Decomposed-into:** EP0086
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/transition.py, tools/pre-commit.sh
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

An agent working a sprint meets the gates' requirements as REFUSALS rather than as a briefing, one at a time, each costing a full gate run. Delivering a single 3-point bug in RUN-01KXWWM3 hit five: `file_finding` wants a T-shirt size on a CR and a severity on a bug; a bug needs a Verification depth field before it may reach Fixed; scripts are consuming-facing so an internal id in a code comment fails the style guard; a commit naming several ids needs a Refs trailer; the pre-commit hook needs a 250 second timeout rather than the 120 second default. Every one of those is already documented - in AGENTS.md, reference-scripts.md, help/, reference-test-best-practices.md, or the guard's own remedy text. Nothing is missing. The knowledge is simply spread across the places a router discloses progressively, and a per-unit checklist is the one thing an agent needs ALL of, every time. The style refusal alone cost about 130 seconds of unit suite before it reported, because it sits behind the gate rather than in front of the work.

## Impact

Every avoidable refusal on the commit path costs a full gate run, and the agent learns the procedure by being stopped rather than by being told. It also reads as the tool moving the goalposts, which erodes trust in gates whose value depends on being followed rather than worked around. Narrower than it looks: this is mechanical friction only. The expensive failures of the previous run came from repair judgement inside one function, and no checklist would have caught those.

## Acceptance Criteria

- [ ] sprint plan prints the unit lifecycle and the gates each unit will meet, generated from the gate definitions rather than hand-written prose
- [ ] a unit close names the fields that unit type requires before its terminal transition, before the work rather than on refusal
- [ ] the pre-flight has no hand-maintained duplicate of a requirement that already lives in a guard
- [ ] cheap guards (style, artefact fields) run before the unit suites, so a reworded comment does not cost a full test run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
