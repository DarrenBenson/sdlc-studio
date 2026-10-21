# BG1069: critic escalation reads verdicts across a reopen: a reopened unit's first new-round REJECT is reported as a panel split against the previous delivery's APPROVE

> **Status:** Open
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_reopen_escalation.py, changelog.d/BG1069.md
> **Severity:** Low
> **Points:** 2

## Summary

Found in a consuming project on 2026-10-19, on that project's BG0497. Its BG0497 was delivered and APPROVEd on 2026-10-07 (seat `engineering-seat-BG0497-r1`), then reopened when its live check failed; the new delivery's first review was a REJECT by a different reviewer (`claude-code-reviewer-bg0497-r2`). `critic.py record` printed `ESCALATED for the operator - BG0497: the panel split: claude-code-reviewer-bg0497-r2 rejected while engineering-seat-BG0497-r1 approved`. On main (35a795df) `.claude/skills/sdlc-studio/scripts/critic.py` ~1663-1694 returns early only when the latest verdict is APPROVE; otherwise it counts every REJECT in the unit's whole history against `PANEL_REJECT_LIMIT` and compares every seat's latest verdict, so the previous, closed delivery's approving seat is read as a dissenting seat in the current round - and a second REJECT in the reopened round would read as 'rejected twice - not converging' even if the first delivery converged. BG0539 fixed the round-versus-seat confusion within one delivery; a reopen starts a new delivery, which the verdict history does not partition (sibling of BG0416, reopen not retracting state).

## Steps to Reproduce

Record APPROVE for unit X (seat A); transition X from Fixed back to Open; record REJECT for X (seat B): critic prints 'the panel split: B rejected while A approved'.

## Proposed Fix

Partition the verdict history at the unit's last reopen (a transition out of a closed status, or a recorded delivery epoch) and evaluate the escalation only over the current delivery's rows.

## Acceptance Criteria

- [ ] **AC1** A REJECT recorded after a unit is reopened is evaluated only against verdicts recorded since the reopen
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_reopen_escalation.py::ReopenEscalationTests::test_a_reject_after_a_reopen_is_judged_against_the_new_delivery_only

## Impact

A routine reopen raises a false split escalation, which teaches the operator to ignore the real ones.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | Claude Opus 5.5 | Neutralised on the operator's instruction: the consuming project's name replaced by 'a consuming project' before commit (the private-name rule; CR0612 is the filed fix for the filer). The finding is otherwise as filed by its session |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
