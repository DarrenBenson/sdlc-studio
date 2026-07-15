# CR-0272: Audit and clean up the skill command surface, then rewrite the help files around the core process

> **Status:** Proposed
> **Priority:** P2
> **Type:** Improvement
> **Size:** XL
> **Affects:** .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/help/, .claude/skills/sdlc-studio/scripts/
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The command surface has grown organically and likely carries superseded routes and commands no longer needed. Audit ALL commands, confirm the tooling behind each still works, retire or fold the dead/duplicated ones, then rewrite the help files around the intended process rather than the accreted one.

## Impact

The process the skill should foreground: raise a bug or CR -> break it down into the delivery backlog -> add and run sprints with independent reviews. The main human levers to direct delivery flow are the top-level documents (PRD, TRD, TSD, Personas), which must stay paramount and discoverable. Supporting features are reconcile, review and audit. Everything that does not serve that spine is a candidate for retirement or folding. XL: this is a request, not a unit of work - decompose it (likely an RFC to settle the target surface, then CRs per area) before delivery.

## Acceptance Criteria

- [ ] Every command/route across SKILL.md, help/ and scripts/ is enumerated with a keep / fold / retire disposition mapped to the process spine (raise -> break down -> sprint+review; PRD/TRD/TSD/Personas as the top-level levers; reconcile/review/audit as support)
- [ ] The tooling behind every KEPT command is exercised and confirmed working (no help entry for a command whose script path is dead)
- [ ] Retired/folded commands are removed or redirected, with the change recorded
- [ ] The help files are rewritten around the process spine, not the accreted surface, and `check_links` + `validate_skill` pass
- [ ] The Discovery and Delivery backlogs are surfaced in the `hint` ladder and the main `status` dashboard, not only in `status backlog`: the hint names how many Discovery items await refinement, and the dashboard shows the two-backlog split, so the dual-track split is visible from the commands an operator reaches for first

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Raised |
| 2026-07-15 | sdlc-studio | Added scope: surface the Discovery/Delivery backlogs in `hint` and the main `status` dashboard (they exist in `status backlog` since US0123 but not the first-reach commands) |
