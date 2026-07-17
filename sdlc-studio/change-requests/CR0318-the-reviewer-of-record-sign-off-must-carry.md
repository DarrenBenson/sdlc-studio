# CR-0318: The reviewer-of-record sign-off must carry a decision brief: what shipped, what the critics rejected, gate and cost evidence - inline in the prompt, with hold and delegate paths

> **Status:** Superseded
> **Parent:** RFC0044
> **Priority:** High
> **Type:** process
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, sdlc-studio/rfcs/RFC0044-adversarial-reviewer-vs-reviewer-of-record-an-amigo.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator feedback 2026-07-16

## Summary

Operator feedback at the sprint close. The sign-off ceremony must present a DECISION BRIEF inline in the ask, not counts: per-unit one-liners (what shipped), what each critic REJECTED and how it was repaired (the risk the principal is accepting), gate/mutation results, estimate-vs-actual, and pointers to the retro + diffs for a deeper read. The deterministic composer already exists - `sprint_report.py` builds exactly this page - so the ceremony should render it (or a compact digest of it) into the sign-off prompt. The options must include: approve; hold (I will read first - the close waits); and DELEGATE (the operator names a persona/independent principal to review and sign on their behalf - recorded as the delegated reviewer of record, never silently substituting the author's own seat subagents). Delegation validity (independence requirements, how it is recorded, revocation) is folded into RFC0044's open decisions.

## Impact

The RUN-01KXGPBN close asked the operator to sign off a retro they had not seen: the prompt summarised counts (6/6, gates green) but none of the content being approved - the retro was written moments earlier and unpushed, so the reviewer of record was structurally unable to review. An uninformed sign-off is approval theatre and quietly converts the independent-principal gate into a rubber stamp.

## Acceptance Criteria

- [ ] The close ceremony's sign-off ask embeds a decision brief: per-unit deliveries, critic REJECT findings and their repairs, gate + mutation results, estimate-vs-actual, and file pointers to the retro and dated review
- [ ] The ask offers approve / hold (close waits, nothing recorded) / delegate-to-named-principal; a delegated sign-off is recorded on the retro with the delegation chain (operator -> delegate), and the author's own session subagents are refused as delegates
- [ ] reference-sprint.md's closing-gate section documents the brief-before-signature rule; RFC0044 gains the delegation open decision

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson | Raised |
| 2026-07-17 | Claude Fable 5 | Superseded by CR0323 (US0194/US0198 delivered the inline decision brief with approve/hold/delegate paths - `critic.py signoff-brief`, composed by `sprint close`) |
