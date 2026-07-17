# CR-0323: Build the two-role review gate: adversarial evidence + non-author principal sign-off with named-delegate chain (RFC0044 D1+D3, integrates CR0318)

> **Status:** Complete
> **Decomposed-into:** EP0064
> **Parent:** RFC0044
> **Priority:** High
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-workflow-personas.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; RFC triage decisions, filed by Claude Fable 5

## Summary

RFC0044 accepted as build (operator): the critiqued/close gates gain the two roles as machinery. The seat subagent's adversarial pass records as EVIDENCE (critic.py evidence entry: findings, reviewer seat, author); the reviewer-of-record verdict must come from a principal the author does not control - the operator by default, or a NAMED DELEGATE run in a separate trust boundary (another session, CI, another human) with the delegation chain recorded on the retro; the authoring session's own subagents are refused as delegates. The sign-off ceremony presents CR0318's decision brief. Conformance's critiqued stage requires BOTH: evidence from the adversarial pass AND the independent sign-off.

## Impact

Today the two-role model (seat subagent finds, independent principal signs) is practice, not machinery: nothing refuses an uninformed or self-controlled sign-off, and the operator was asked to approve a retro they could not see at the RUN-01KXGPBN close.

## Acceptance Criteria

- [ ] critic.py records the adversarial pass as evidence distinct from the verdict; conformance critiqued requires evidence + a sign-off whose principal differs from the author AND from the authoring session's subagents
- [ ] Delegated sign-off carries the recorded chain (operator -> delegate, trust boundary named); an authoring-session subagent as delegate is refused loudly
- [ ] The sign-off request embeds the CR0318 decision brief (deliveries, critic REJECTs + repairs, gate/cost evidence) with approve/hold/delegate paths

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson | Raised |
