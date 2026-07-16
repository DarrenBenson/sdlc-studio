# RFC-0044: Adversarial reviewer vs reviewer of record: an amigo subagent finds issues, an independent principal signs off

> **Status:** Draft
> **Decomposed-into:** CR0318, CR0323
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-workflow-personas.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The author!=reviewer gate is satisfied by a RECORDED critic verdict. A persona-shaped subagent (an amigo/engineering seat) gives a genuine ADVERSARIAL pass with a fresh context that did not write the code - this session it blocked two sprints and caught a codebase-wide robustness bug. But it cannot be the reviewer OF RECORD: the author spawns, prompts and can re-run it, so recording its own APPROVE is self-review by automation, which the harness self-approval guard correctly refuses. Operator question (2026-07-16): can a subagent of one of the amigos be the independent reviewer in future? Answer: as the FINDER of issues, yes and it already works; as the SIGN-OFF of record, no - separate the two roles. The adversarial reviewer (subagent) produces findings that are INPUT; the reviewer of record is an independent principal the author cannot override (the operator, or a separate-trust-boundary session / CI agent) who records the verdict. Codify both as distinct roles in the seats/amigo model, so the subagent's adversarial pass is always captured as evidence and the recorded sign-off always comes from a non-author principal.

## Design Options

- **Human operator as reviewer of record (what this session did): the amigo subagent reviews adversarially, the operator signs off and the verdict is recorded on their say-so. Simplest, keeps a real independent party, but a human is in the loop every close.**
- **Separate-principal review agent: the adversarial review runs under a DIFFERENT trust boundary (a CI job, or an agent the operator launches in a separate session) that records its OWN verdict. No human bottleneck, but needs the separate-principal infrastructure to exist.**
- **Attach-evidence model: critic.py records the subagent's findings as EVIDENCE, not a verdict; the conformance critiqued stage requires an APPROVE from a non-author principal. The adversarial pass is always captured; sign-off is a separate gated step by an independent principal.**
- **RECOMMENDED - the hybrid: the amigo/seat subagent is the STANDARD adversarial reviewer (always run, findings recorded as evidence); the reviewer-of-record verdict MUST come from a principal the author does not control (operator by default; a separate-session/CI agent where available). Name adversarial-reviewer and reviewer-of-record as two roles in the amigo model (RFC0020/RFC0021 lineage).**

## Recommendation

The hybrid: keep the amigo/seat subagent as the always-run adversarial reviewer (it demonstrably finds real bugs), record its output as evidence, and require the recorded sign-off to come from an independent principal - the operator today, a separate-trust-boundary agent where one exists. This preserves the value of the subagent pass while keeping the gate honest: the party that signs off is never the party that could re-run the reviewer.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Build vs doctrine-only | Resolved: BUILD - conformance critiqued requires adversarial evidence + independent sign-off (operator, 2026-07-17) -> CR0323 |
| D2 | The sign-off prompt must carry a decision brief (per-unit deliveries, critic REJECTs + repairs, gate/cost evidence) - an uninformed signature is approval theatre | Resolved: yes - operator feedback at the RUN-01KXGPBN close (the prompt showed counts, not content); delivery tracked as CR0318 |
| D3 | Delegated sign-off: may the operator name a persona/independent principal to review and sign on their behalf - and what makes the delegation valid (independence from the authoring session, recording of the delegation chain on the retro, revocability)? The author's own seat subagents must be refusable as delegates or the self-approval guard is hollowed out | Resolved: named delegate in a separate trust boundary, delegation chain recorded on the retro, authoring-session subagents refused (operator, 2026-07-17) -> CR0323 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Filed |
| 2026-07-17 | Darren Benson (operator) / Claude Fable 5 | Decisions resolved at the RFC triage session; workstream CRs spawned (Accepted derives when they resolve) |
| 2026-07-16 | Darren Benson (operator) / Claude Fable 5 | Boilerplate D1 replaced with the real decisions; D2 resolved from close feedback (CR0318); D3 delegation added |
