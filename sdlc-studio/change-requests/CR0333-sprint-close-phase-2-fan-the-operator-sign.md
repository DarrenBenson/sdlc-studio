# CR-0333: sprint close phase 2: fan the operator sign-off into the terminal cascade

> **Status:** In Progress
> **Decomposed-into:** EP0077
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

sprint close now carries the ceremony up to the printed decision brief, but everything AFTER the operator's approval is still hand-carried: at the RUN-01KXPJG9 close the orchestrator hand-looped critic signoff x8, transition Done x8 (with a vacuous `verify_ac` refresh forced by the transition's own edit), artifact close x8, epic transitions x8, CR transitions x8, and the RFC acceptances - the exact shape of seam CR0328 was raised to remove. Ship the second phase: 'sprint close --apply-signoff --principal NAME [--delegate ... --boundary ...]' (or a sibling command) that records the sign-off per batch unit, transitions each to Done, closes it with telemetry, derives parent epics/CRs/RFCs terminal, writes the velocity row, and runs the final reconcile - refusing without a recorded principal, never inventing one.

## Impact

Every sprint close under the two-role gate repeats ~40 hand-sequenced commands after the sign-off; each is a skippable seam and the parent-derivation steps are easy to forget entirely.

## Acceptance Criteria

- [ ] One command fans a recorded operator approval into per-unit sign-offs, Done transitions, telemetry closes, parent derivations and the velocity row, stopping loudly at the first refusal
- [ ] It never runs without an explicit principal; authoring-session subagents are refused as principals exactly as critic signoff refuses them
- [ ] Re-running after a mid-cascade stop is idempotent

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
