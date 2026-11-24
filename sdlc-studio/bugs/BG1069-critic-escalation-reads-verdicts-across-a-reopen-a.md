# BG1069: critic escalation reads verdicts across a reopen: a reopened unit's first new-round REJECT is reported as a panel split against the previous delivery's APPROVE

> **Status:** Fixed
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_reopen_escalation.py, changelog.d/BG1069.md
> **Severity:** Low
> **Points:** 1

## Summary

Found in a consuming project on 2026-10-19, on that project's BG0497. Its BG0497 was delivered and APPROVEd on 2026-10-07 (seat `engineering-seat-BG0497-r1`), then reopened when its live check failed; the new delivery's first review was a REJECT by a different reviewer (`claude-code-reviewer-bg0497-r2`). `critic.py record` printed `ESCALATED for the operator - BG0497: the panel split: claude-code-reviewer-bg0497-r2 rejected while engineering-seat-BG0497-r1 approved`. On main (35a795df) `.claude/skills/sdlc-studio/scripts/critic.py` ~1663-1694 returns early only when the latest verdict is APPROVE; otherwise it counts every REJECT in the unit's whole history against `PANEL_REJECT_LIMIT` and compares every seat's latest verdict, so the previous, closed delivery's approving seat is read as a dissenting seat in the current round - and a second REJECT in the reopened round would read as 'rejected twice - not converging' even if the first delivery converged. BG0539 fixed the round-versus-seat confusion within one delivery; a reopen starts a new delivery, which the verdict history does not partition (sibling of BG0416, reopen not retracting state).

At HEAD (cecc9dfe) the round count has been partitioned since: `delivery_rounds` reads only the current delivery (the rows past the unit's `REVIEW_BASE` in an open run holding it, or the rows after the APPROVE that closed the previous delivery outside one), and `round_refusal` uses it. The escalation does not: `escalation_notice` still builds its rounds from `review_rounds_across_ledgers` and its seats from `seat_verdicts`, both over `unit_review_rounds`, the unit's whole history.

## Steps to Reproduce

1. Outside a run: record an APPROVE for unit X by seat A; reopen X; record a REJECT for X by seat B. `critic.py record` prints `ESCALATED for the operator - X: the panel split: B rejected while A approved`, while `delivery_rounds` holds the REJECT alone as round 1.
2. Inside a run: record a REJECT then an APPROVE for X by seat A outside any run; open a run holding X; record a REJECT by seat B. `critic.py record` prints `the panel rejected this unit twice (2 REJECTs) - the repair is not converging`, while `delivery_rounds` holds the REJECT alone as round 1.

## Proposed Fix

Build `escalation_notice`'s rounds and seat verdicts from the current delivery's rows, as `delivery_rounds` already partitions them, rather than from the unit's whole history. No transition change is needed: the partition exists.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose previous delivery closed on seat A's APPROVE, when seat B's REJECT is recorded through `critic.py record` as round 1 of the new delivery, then no escalation is printed. Fails on: `ESCALATED for the operator - <unit>: the panel split: B rejected while A approved`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_reopen_escalation.py::ReopenEscalationTests::test_a_reject_after_a_reopen_is_judged_against_the_new_delivery_only
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given a unit whose earlier delivery recorded seat A's REJECT then APPROVE, and an open run holding it, when seat B's REJECT is recorded as round 1 of the run's delivery, then no escalation is printed. Fails on: the closed delivery's REJECT is counted and `the panel rejected this unit twice (2 REJECTs)` is printed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_reopen_escalation.py::ReopenEscalationTests::test_a_closed_deliverys_reject_is_not_counted_in_a_new_run
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given two REJECTs by one seat within one delivery, when the second is recorded, then the escalation `the panel rejected this unit twice` is still printed. Fails on: a fix that stops counting the current delivery's REJECTs too (this guard holds today).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_reopen_escalation.py::ReopenEscalationTests::test_two_rejects_in_one_delivery_still_escalate
  - **Verified:** yes (2026-11-24)

## Impact

A routine reopen raises a false split escalation, which teaches the operator to ignore the real ones.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | Claude Opus 5.5 | Neutralised on the operator's instruction: the consuming project's name replaced by 'a consuming project' before commit (the private-name rule; CR0612 is the filed fix for the filer). The finding is otherwise as filed by its session |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced both escalations at cecc9dfe through `critic.py record`; `delivery_rounds` already partitions the delivery, so the fix is in `escalation_notice` alone; criteria split into the split and twice-rejected cases plus a guard; Affects drops transition.py, test_transition.py and test_critic.py; Points 2 to 1, the partition being built |
